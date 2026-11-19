from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runner


class ToolRunnerUnitTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.input_dir = self.root / "nolane-inputs"
        self.input_dir.mkdir()
        self.env = patch.dict(os.environ, {"RUNNER_TEMP": str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def write(self, name: str, content: str) -> Path:
        path = self.input_dir / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_text_clean_normalizes_unicode_and_whitespace(self):
        path = self.write("notes.txt", "\ufeffCafe\u0301  \t\n\n\nsecond\u200b line   ")
        result = runner.text_clean(path)
        output = Path(result["output_path"])
        cleaned = output.read_text(encoding="utf-8")
        self.assertIn("Café", cleaned)
        self.assertIn("second line", cleaned)
        self.assertNotIn("\u200b", cleaned)
        self.assertNotIn("\n\n\n", cleaned)

    def test_subtitle_text_removes_cues_timecodes_and_markup(self):
        path = self.write(
            "captions.vtt",
            "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n<v Speaker>Hello &amp; welcome</v>\n",
        )
        result = runner.subtitle_text(path)
        self.assertIn("Hello & welcome", result["summary"])
        self.assertNotIn("00:00:01", result["summary"])
        self.assertNotIn("<v", result["summary"])

    def test_html_text_skips_script_style_and_extracts_visible_text(self):
        path = self.write(
            "page.html",
            "<html><head><title>Hidden title</title></head><body>"
            "<h1>Visible &amp; useful</h1><script>secret_script()</script>"
            "<style>.hidden { display:none }</style><p>Paragraph</p></body></html>",
        )
        result = runner.html_text(path)
        self.assertIn("Visible & useful", result["summary"])
        self.assertIn("Paragraph", result["summary"])
        self.assertNotIn("secret_script", result["summary"])
        self.assertNotIn("display:none", result["summary"])

    def test_audio_normalize_builds_loudness_filter_command(self):
        path = self.write("podcast.wav", "not real media; command is mocked")
        captured = []
        def fake_cmd(name, args, timeout=180):
            captured.append((name, args, timeout))
            return ""
        with patch.object(runner, "cmd", side_effect=fake_cmd):
            result = runner.audio_normalize(path)
        self.assertEqual(captured[0][0], "ffmpeg")
        self.assertIn("loudnorm=I=-16:TP=-1.5:LRA=11", captured[0][1])
        self.assertTrue(result["output_path"].endswith("-normalized.mp3"))

    def test_video_audio_and_gif_commands_are_bounded(self):
        path = self.write("clip.mp4", "not real media; commands are mocked")
        captured = []
        def fake_cmd(name, args, timeout=180):
            captured.append((name, args, timeout))
            return ""
        with patch.object(runner, "cmd", side_effect=fake_cmd):
            audio = runner.video_audio(path)
            with patch.object(runner, "ffprobe", return_value={"format": {"duration": "12.0"}}):
                gif = runner.video_gif(path)
        self.assertIn("0:a:0", captured[0][1])
        self.assertTrue(audio["output_path"].endswith("-audio.mp3"))
        self.assertIn("-t", captured[1][1])
        self.assertIn("6.0", captured[1][1])
        self.assertIn("fps=10", captured[1][1][captured[1][1].index("-vf") + 1])
        self.assertTrue(gif["output_path"].endswith("-preview.gif"))


    def test_image_resize_webp_and_palette(self):
        from PIL import Image
        path=self.input_dir/"art.png"
        Image.new("RGBA",(2400,1200),(240,40,20,180)).save(path)
        resized=runner.image_resize(path)
        webp=runner.image_webp(path)
        palette=runner.image_palette(path)
        with Image.open(resized["output_path"]) as image:
            self.assertLessEqual(max(image.size),1920)
            self.assertEqual(image.format,"JPEG")
        with Image.open(webp["output_path"]) as image:
            self.assertEqual(image.format,"WEBP")
            self.assertIn("A",image.getbands())
        self.assertIn("#",palette["summary"])

    def test_sqlite_inspector_reads_database_without_writing(self):
        import sqlite3
        path=self.input_dir/"sample.sqlite"
        db=sqlite3.connect(path)
        db.execute("CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT)")
        db.executemany("INSERT INTO people(name) VALUES (?)",[("An",),("Bình",)])
        db.commit()
        db.close()
        result=runner.sqlite_inspect(path)
        self.assertIn("people",result["summary"])
        self.assertIn("rows=2",result["summary"])
        with self.assertRaises(sqlite3.OperationalError):
            db=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
            try:
                db.execute("INSERT INTO people(name) VALUES ('blocked')")
            finally:
                db.close()

    def test_epub_reader_respects_spine_order_and_skips_script(self):
        import zipfile
        path=self.input_dir/"book.epub"
        with zipfile.ZipFile(path,"w") as archive:
            archive.writestr("META-INF/container.xml",'<?xml version="1.0"?><container><rootfiles><rootfile full-path="OEBPS/content.opf"/></rootfiles></container>')
            archive.writestr("OEBPS/content.opf",'<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/"><metadata><dc:title>Demo Book</dc:title></metadata><manifest><item id="c1" href="chapter1.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="c1"/></spine></package>')
            archive.writestr("OEBPS/chapter1.xhtml","<html><body><h1>Chapter One</h1><script>secret()</script><p>Readable text</p></body></html>")
        result=runner.epub_text(path)
        self.assertIn("Demo Book",result["summary"])
        self.assertIn("Chapter One",result["summary"])
        self.assertIn("Readable text",result["summary"])
        self.assertNotIn("secret()",result["summary"])

    def test_yaml_formatter_uses_safe_yaml_loader(self):
        path=self.write("config.yml","name: Nolane\nitems:\n  - one\n  - two\n")
        result=runner.yaml_format(path)
        output=Path(result["output_path"]).read_text(encoding="utf-8")
        self.assertIn("Nolane",output)
        malicious=self.write("bad.yaml","!!python/object/apply:os.system ['echo unsafe']\n")
        with self.assertRaises(Exception):
            runner.yaml_format(malicious)

    def test_xml_formatter_blocks_dtd_and_formats_valid_xml(self):
        path=self.write("feed.xml","<root><item>value</item></root>")
        result=runner.xml_format(path)
        self.assertIn("<item>",Path(result["output_path"]).read_text(encoding="utf-8"))
        dangerous=self.write("danger.xml",'<!DOCTYPE root [<!ENTITY x "boom">]><root>&x;</root>')
        with self.assertRaises(RuntimeError):
            runner.xml_format(dangerous)

    def test_code_check_parses_but_never_executes_python(self):
        path=self.write("safe.py","raise RuntimeError('must not execute')\nvalue = 42\n")
        result=runner.code_check(path)
        self.assertIn("syntax OK",result["summary"])
        bad=self.write("broken.py","def x(:\n  pass\n")
        with self.assertRaises(SyntaxError):
            runner.code_check(bad)

    def test_xlsx_profiler_reports_missing_duplicates_and_numeric_ranges(self):
        from openpyxl import Workbook
        path=self.input_dir/"metrics.xlsx"
        wb=Workbook()
        ws=wb.active
        ws.title="Metrics"
        ws.append(["name","score"])
        ws.append(["A",10])
        ws.append(["B",None])
        ws.append(["A",10])
        wb.save(path)
        result=runner.xlsx_profile(path)
        self.assertIn("duplicate rows=1",result["summary"])
        self.assertIn("score",result["summary"])
        self.assertIn("missing 1/3",result["summary"])

    def test_archive_safe_extract_repackages_and_rejects_traversal(self):
        import zipfile
        good=self.input_dir/"good.zip"
        with zipfile.ZipFile(good,"w") as archive:
            archive.writestr("folder/hello.txt","hello")
        result=runner.archive_safe_extract(good)
        with zipfile.ZipFile(result["output_path"]) as archive:
            self.assertEqual(archive.read("folder/hello.txt"),b"hello")
        bad=self.input_dir/"bad.zip"
        with zipfile.ZipFile(bad,"w") as archive:
            archive.writestr("../escape.txt","no")
        with self.assertRaises(RuntimeError):
            runner.archive_safe_extract(bad)

    def test_pdf_compress_and_render_pages(self):
        import fitz
        path=self.input_dir/"document.pdf"
        doc=fitz.open()
        page=doc.new_page()
        page.insert_text((72,72),"Nolane PDF")
        doc.new_page()
        doc.save(path)
        doc.close()
        compressed=runner.pdf_compress(path)
        self.assertTrue(Path(compressed["output_path"]).is_file())
        rendered=runner.pdf_to_images(path)
        import zipfile
        with zipfile.ZipFile(rendered["output_path"]) as archive:
            self.assertEqual(len(archive.namelist()),2)

    def test_audio_subtitles_exports_srt_and_vtt(self):
        import types, zipfile
        class Segment:
            start=0.2
            end=1.5
            text=" Xin chào Nolane "
        class Info:
            language="vi"
        class FakeModel:
            def __init__(self,*args,**kwargs): pass
            def transcribe(self,*args,**kwargs): return iter([Segment()]),Info()
        fake=types.ModuleType("faster_whisper")
        fake.WhisperModel=FakeModel
        path=self.write("speech.wav","fake")
        with patch.dict(sys.modules,{"faster_whisper":fake}):
            result=runner.audio_subtitles(path)
        with zipfile.ZipFile(result["output_path"]) as archive:
            self.assertEqual(set(archive.namelist()),{"speech-transcript.srt","speech-transcript.vtt"})
            self.assertIn(b"Xin ch\xc3\xa0o Nolane",archive.read("speech-transcript.srt"))
            self.assertIn(b"WEBVTT",archive.read("speech-transcript.vtt"))

    def test_video_contact_sheet_and_compress_limits(self):
        path=self.write("clip.mp4","fake")
        captured=[]
        def fake_cmd(name,args,timeout=180):
            captured.append((name,args,timeout))
            Path(args[-1]).write_bytes(b"fake-output")
            return ""
        with patch.object(runner,"cmd",side_effect=fake_cmd),patch.object(runner,"ffprobe",return_value={"format":{"duration":"20"}}):
            sheet=runner.video_contact_sheet(path)
            compressed=runner.video_compress(path)
        self.assertTrue(Path(sheet["output_path"]).is_file())
        self.assertTrue(Path(compressed["output_path"]).is_file())
        self.assertIn("tile=4x3",captured[0][1][captured[0][1].index("-vf")+1])
        self.assertIn("libx264",captured[1][1])
        with patch.object(runner,"ffprobe",return_value={"format":{"duration":"500"}}):
            with self.assertRaises(RuntimeError):
                runner.video_compress(path)


    def test_new_csv_json_and_excel_converters(self):
        import zipfile
        csv_path=self.write("people.csv","name,score\nAn,7\nBình,8\n")
        cleaned=runner.csv_clean(csv_path)
        self.assertTrue(Path(cleaned["output_path"]).is_file())
        xlsx=runner.csv_to_xlsx(csv_path)
        self.assertTrue(Path(xlsx["output_path"]).is_file())
        exported=runner.xlsx_to_csv(Path(xlsx["output_path"]))
        with zipfile.ZipFile(exported["output_path"]) as archive:
            self.assertEqual(len(archive.namelist()),1)
            self.assertIn("Bình",archive.read(archive.namelist()[0]).decode("utf-8-sig"))
        json_path=self.write("records.json",'[{"name":"An","score":7},{"name":"Bình","score":8}]')
        converted=runner.json_to_csv(json_path)
        self.assertIn("Bình",Path(converted["output_path"]).read_text(encoding="utf-8-sig"))
        unsafe=self.write("formula.csv","name\n=HYPERLINK(\"https://evil.example\")\n")
        safe=runner.csv_clean(unsafe)
        self.assertIn("'=HYPERLINK",Path(safe["output_path"]).read_text(encoding="utf-8"))
        bad_header=self.write("formula-header.csv","=HYPERLINK,score\nhttps://evil.example,1\n")
        safe_header=runner.csv_clean(bad_header)
        self.assertIn("'=HYPERLINK",Path(safe_header["output_path"]).read_text(encoding="utf-8"))

    def test_image_png_preserves_alpha(self):
        from PIL import Image
        source=self.input_dir/"transparent.png"
        Image.new("RGBA",(32,32),(255,0,0,120)).save(source)
        result=runner.image_png(source)
        with Image.open(result["output_path"]) as converted:
            self.assertEqual(converted.format,"PNG")
            self.assertIn("A",converted.getbands())

    def test_pdf_split_creates_one_pdf_per_page(self):
        import fitz,zipfile
        path=self.input_dir/"pages.pdf"
        doc=fitz.open()
        for number in range(3):
            page=doc.new_page()
            page.insert_text((72,72),f"Page {number+1}")
        doc.save(path); doc.close()
        result=runner.pdf_split(path)
        with zipfile.ZipFile(result["output_path"]) as archive:
            self.assertEqual(len(archive.namelist()),3)
            for name in archive.namelist():
                page=fitz.open(stream=archive.read(name),filetype="pdf")
                self.assertEqual(page.page_count,1)
                page.close()

    def test_audio_convert_uses_bounded_mono_wav_command(self):
        path=self.write("speech.mp3","fake audio")
        captured=[]
        def fake_cmd(name,args,timeout=180):
            captured.append((name,args,timeout))
            Path(args[-1]).write_bytes(b"wav")
            return ""
        with patch.object(runner,"ffprobe",return_value={"format":{"duration":"120"}}),patch.object(runner,"cmd",side_effect=fake_cmd):
            result=runner.audio_convert(path)
        args=captured[0][1]
        self.assertIn("16000",args)
        self.assertIn("pcm_s16le",args)
        self.assertIn("1",args)
        self.assertTrue(result["output_path"].endswith(".wav"))

    def test_pipeline_validation_rejects_unknown_repeated_and_unsupported_edges(self):
        job={"toolId":"video-audio","pipeline":[
            {"toolId":"video-audio"},{"toolId":"audio-convert"},{"toolId":"audio-transcribe"}]}
        self.assertEqual([step["toolId"] for step in runner.validate_pipeline(job)],
                         ["video-audio","audio-convert","audio-transcribe"])
        for invalid in (
            [{"toolId":"video-info"},{"toolId":"audio-transcribe"}],
            [{"toolId":"video-audio"},{"toolId":"video-audio"}],
            [{"toolId":"video-audio"},{"toolId":"not-a-tool"}],
            [{"toolId":"video-audio"}]*5,
        ):
            with self.assertRaises(RuntimeError):
                runner.validate_pipeline({"toolId":invalid[0]["toolId"],"pipeline":invalid})

    def test_runner_executes_pipeline_steps_in_order_and_delivers_only_final_artifact(self):
        video=self.write("clip.mp4","input")
        order=[]
        def extract(path):
            self.assertEqual(path.suffix,".mp4")
            out=self.input_dir/"stage-a.mp3"; out.write_bytes(b"mp3")
            order.append("video-audio")
            return {"summary":"audio extracted","output_path":str(out)}
        def convert(path):
            self.assertEqual(path.suffix,".mp3")
            out=self.input_dir/"stage-b.wav"; out.write_bytes(b"wav")
            order.append("audio-convert")
            return {"summary":"converted to 16 kHz","output_path":str(out)}
        def transcribe(path):
            self.assertEqual(path.suffix,".wav")
            out=self.input_dir/"transcript.txt"; out.write_text("Xin chao Nolane",encoding="utf-8")
            order.append("audio-transcribe")
            return {"summary":"transcription ready","output_path":str(out)}
        job={"toolId":"video-audio","pipeline":[
            {"toolId":"video-audio"},{"toolId":"audio-convert"},{"toolId":"audio-transcribe"}]}
        with patch.dict(runner.TOOLS,{"video-audio":extract,"audio-convert":convert,"audio-transcribe":transcribe}):
            result=runner.run_tool_pipeline(job,video,self.input_dir.resolve())
        self.assertEqual(order,["video-audio","audio-convert","audio-transcribe"])
        self.assertEqual(Path(result["output_path"]).name,"transcript.txt")
        self.assertIn("Step 1/3",result["summary"])
        self.assertIn("Step 3/3",result["summary"])

    def test_pipeline_materializes_text_result_for_next_text_processor(self):
        source=self.write("photo.jpg","fake")
        seen=[]
        def ocr(path):
            return {"summary":"OCR result: Café\nLine two","output_path":""}
        def clean(path):
            seen.append(path.read_text(encoding="utf-8"))
            out=self.input_dir/"cleaned.txt"; out.write_text(seen[-1].replace("OCR result: ",""),encoding="utf-8")
            return {"summary":"text cleaned","output_path":str(out)}
        job={"toolId":"image-ocr","pipeline":[{"toolId":"image-ocr"},{"toolId":"text-clean"}]}
        with patch.dict(runner.TOOLS,{"image-ocr":ocr,"text-clean":clean}):
            result=runner.run_tool_pipeline(job,source,self.input_dir.resolve())
        self.assertIn("Café",seen[0])
        self.assertEqual(Path(result["output_path"]).name,"cleaned.txt")


    def test_csv_to_json_rejects_duplicate_headers_and_preserves_unicode(self):
        path=self.write("people.csv","name,city\nMai,Hải Phòng\nAn,Hà Nội\n")
        result=runner.csv_to_json(path)
        import json
        payload=json.loads(Path(result["output_path"]).read_text(encoding="utf-8"))
        self.assertEqual(payload[0],{"name":"Mai","city":"Hải Phòng"})
        duplicate=self.write("duplicate.csv","name,name\nA,B\n")
        with self.assertRaisesRegex(RuntimeError,"header trùng"):
            runner.csv_to_json(duplicate)

    def test_jsonl_formatter_reports_line_and_normalizes_records(self):
        path=self.write("events.jsonl",'{"a":1}\n\n{"name":"Hải Phòng"}\n')
        result=runner.jsonl_format(path)
        content=Path(result["output_path"]).read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(content),2)
        import json
        self.assertEqual(json.loads(content[1]),{"name":"Hải Phòng"})
        invalid=self.write("bad.jsonl",'{"ok":true}\nnot-json\n')
        with self.assertRaisesRegex(RuntimeError,"dòng 2"):
            runner.jsonl_format(invalid)

    def test_yaml_and_xml_conversion_are_safe_and_preserve_repeated_elements(self):
        yaml_path=self.write("config.yaml","name: Nolane\nitems:\n  - one\n  - two\n")
        yaml_result=runner.yaml_to_json(yaml_path)
        import json
        self.assertEqual(json.loads(Path(yaml_result["output_path"]).read_text(encoding="utf-8"))["items"],["one","two"])
        xml_path=self.write("feed.xml",'<root id="7"><item>A</item><item>B</item><empty /></root>')
        xml_result=runner.xml_to_json(xml_path)
        xml_payload=json.loads(Path(xml_result["output_path"]).read_text(encoding="utf-8"))
        self.assertEqual(xml_payload["root"]["item"],["A","B"])
        unsafe=self.write("unsafe.xml",'<!DOCTYPE root [<!ENTITY x "bad">]><root>&x;</root>')
        with self.assertRaisesRegex(RuntimeError,"DTD/ENTITY"):
            runner.xml_to_json(unsafe)

    def test_sqlite_export_packages_tables_as_csv_without_modifying_database(self):
        import sqlite3, zipfile, csv
        database=self.input_dir/"report.sqlite"
        connection=sqlite3.connect(database)
        connection.execute("CREATE TABLE people(name TEXT, score INTEGER)")
        connection.executemany("INSERT INTO people VALUES (?,?)",[("Mai",9),("An",8)])
        connection.commit(); connection.close()
        before=database.stat().st_mtime_ns
        result=runner.sqlite_export(database)
        with zipfile.ZipFile(result["output_path"]) as archive:
            name=archive.namelist()[0]
            rows=list(csv.reader(archive.open(name).read().decode("utf-8-sig").splitlines()))
        self.assertEqual(rows[1],["Mai","9"])
        self.assertEqual(database.stat().st_mtime_ns,before)

    def test_xlsx_to_json_exports_sheet_rows_and_disambiguates_headers(self):
        from openpyxl import Workbook
        import json
        path=self.input_dir/"sheet.xlsx"
        book=Workbook(); sheet=book.active; sheet.title="Sales"
        sheet.append(["name","name"]); sheet.append(["Mai","An"])
        book.save(path); book.close()
        result=runner.xlsx_to_json(path)
        payload=json.loads(Path(result["output_path"]).read_text(encoding="utf-8"))
        self.assertEqual(payload["sheets"][0]["columns"],["name","name_2"])
        self.assertEqual(payload["sheets"][0]["rows"][0],{"name":"Mai","name_2":"An"})

    def test_pdf_extract_images_returns_embedded_raster_assets(self):
        import fitz
        from PIL import Image
        import io, zipfile
        image=Image.new("RGB",(8,8),(200,30,20))
        buffer=io.BytesIO(); image.save(buffer,format="PNG")
        path=self.input_dir/"embedded.pdf"
        doc=fitz.open(); page=doc.new_page(); page.insert_image(fitz.Rect(10,10,80,80),stream=buffer.getvalue())
        doc.save(path); doc.close()
        result=runner.pdf_extract_images(path)
        with zipfile.ZipFile(result["output_path"]) as archive:
            self.assertEqual(len(archive.namelist()),1)
            self.assertTrue(archive.read(archive.namelist()[0]).startswith(b"\x89PNG"))

    def test_archive_manifest_hashes_members_and_rejects_traversal(self):
        import zipfile, hashlib, csv, io
        path=self.input_dir/"bundle.zip"
        payload=b"hello nolane"
        with zipfile.ZipFile(path,"w") as archive:
            archive.writestr("folder/readme.txt",payload)
        result=runner.archive_manifest(path)
        with open(result["output_path"],encoding="utf-8-sig",newline="") as handle:
            rows=list(csv.DictReader(handle))
        self.assertEqual(rows[0]["sha256"],hashlib.sha256(payload).hexdigest())
        self.assertEqual(rows[0]["path"],"folder/readme.txt")
        unsafe=self.input_dir/"unsafe.zip"
        with zipfile.ZipFile(unsafe,"w") as archive:
            archive.writestr("../escape.txt",payload)
        with self.assertRaises(RuntimeError):
            runner.archive_manifest(unsafe)

    def test_text_statistics_and_grayscale_image_output(self):
        from PIL import Image
        text_path=self.write("essay.txt","Café là đẹp. Café rất đẹp!\n\nMột đoạn khác.")
        report=runner.text_stats(text_path)["summary"]
        self.assertIn("Words:",report)
        self.assertIn("Unique words:",report)
        image_path=self.input_dir/"color.png"
        Image.new("RGBA",(12,12),(255,0,0,90)).save(image_path)
        result=runner.image_grayscale(image_path)
        with Image.open(result["output_path"]) as gray:
            # Pillow's compact LA mode is a valid grayscale+alpha representation.
            self.assertEqual(gray.mode,"LA")
            luminance,alpha=gray.getpixel((0,0))
            self.assertGreaterEqual(luminance,0)
            self.assertEqual(alpha,90)


    def test_pdf_merge_metadata_clean_and_outline(self):
        import fitz,zipfile
        first=fitz.open(); page=first.new_page(); page.insert_text((72,72),"First page")
        first.set_metadata({"title":"Private title","author":"Private author"})
        first_bytes=first.tobytes(); first.close()
        second=fitz.open(); page=second.new_page(); page.insert_text((72,72),"Second page")
        second_bytes=second.tobytes(); second.close()
        bundle=self.input_dir/"pdfs.zip"
        with zipfile.ZipFile(bundle,"w") as archive:
            archive.writestr("02-second.pdf",second_bytes); archive.writestr("01-first.pdf",first_bytes)
        merged=runner.pdf_merge(bundle)
        document=fitz.open(merged["output_path"])
        self.assertEqual(document.page_count,2)
        self.assertIn("First page",document[0].get_text())
        document.close()
        cleaned=runner.pdf_metadata_clean(Path(merged["output_path"]))
        document=fitz.open(cleaned["output_path"])
        self.assertFalse((document.metadata or {}).get("author"))
        document.close()
        outline=runner.pdf_outline(Path(merged["output_path"]))
        self.assertIn("PDF không có bookmark",outline["summary"])

    def test_image_contact_sheet_and_duplicate_detection(self):
        import io,zipfile,csv
        from PIL import Image
        buffer=io.BytesIO(); Image.new("RGB",(32,32),(200,20,30)).save(buffer,format="PNG")
        payload=buffer.getvalue(); bundle=self.input_dir/"images.zip"
        with zipfile.ZipFile(bundle,"w") as archive:
            archive.writestr("one.png",payload); archive.writestr("copy.png",payload)
            other=io.BytesIO(); Image.new("RGB",(32,32),(20,30,200)).save(other,format="PNG")
            archive.writestr("other.png",other.getvalue())
        sheet=runner.image_contact_sheet(bundle)
        with Image.open(sheet["output_path"]) as image: self.assertGreater(image.width,0)
        duplicates=runner.image_duplicates(bundle)
        with open(duplicates["output_path"],encoding="utf-8-sig",newline="") as handle:
            rows=list(csv.DictReader(handle))
        self.assertTrue(any(row["match_type"]=="exact-sha256" for row in rows))
        unsafe=self.input_dir/"symlink.zip"
        import stat
        with zipfile.ZipFile(unsafe,"w") as archive:
            info=zipfile.ZipInfo("link.png")
            info.external_attr=(stat.S_IFLNK|0o777)<<16
            archive.writestr(info,b"not an image")
        with self.assertRaisesRegex(RuntimeError,"symlink"):
            runner.image_contact_sheet(unsafe)

    def test_csv_split_join_json_schema_and_json_to_yaml(self):
        import zipfile,csv,json
        csv_path=self.write("rows.csv","name,score\nMai,9\nAn,8\n")
        split=runner.csv_split(csv_path)
        with zipfile.ZipFile(split["output_path"]) as archive: self.assertEqual(len(archive.namelist()),1)
        bundle=self.input_dir/"csvs.zip"
        with zipfile.ZipFile(bundle,"w") as archive:
            archive.writestr("b.csv","name,score\nAn,8\n"); archive.writestr("a.csv","name,score\nMai,9\n")
        joined=runner.csv_join(bundle)
        with open(joined["output_path"],encoding="utf-8-sig",newline="") as handle:
            rows=list(csv.reader(handle))
        self.assertEqual(rows[1],["Mai","9"]); self.assertEqual(rows[2],["An","8"])
        json_path=self.write("schema.json",'[{"name":"Mai","score":9},{"name":"An","score":null}]')
        schema=runner.json_schema(json_path)
        result=json.loads(Path(schema["output_path"]).read_text(encoding="utf-8"))
        self.assertEqual(result["type"],"array")
        self.assertIn("name",result["items"]["properties"])
        self.assertEqual(result["items"]["properties"]["score"]["type"],["integer","null"])
        converted=runner.json_to_yaml(self.write("settings.json",'{"name":"Hải Phòng","enabled":true}'))
        self.assertIn("Hải Phòng",Path(converted["output_path"]).read_text(encoding="utf-8"))

    def test_sqlite_integrity_text_deduplicate_diff_and_code_metrics(self):
        import sqlite3,zipfile
        db=self.input_dir/"integrity.sqlite"
        connection=sqlite3.connect(db)
        connection.execute("CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT)")
        connection.execute("INSERT INTO items(name) VALUES ('Nolane')")
        connection.commit(); connection.close()
        report=runner.sqlite_integrity(db)["summary"]
        self.assertIn("integrity check passed",report)
        source=self.write("repeat.txt","Alpha\nBeta\nalpha\nGamma\n")
        result=runner.text_deduplicate(source)
        self.assertEqual(Path(result["output_path"]).read_text(encoding="utf-8"),"Alpha\nBeta\nGamma\n")
        bundle=self.input_dir/"diff.zip"
        with zipfile.ZipFile(bundle,"w") as archive:
            archive.writestr("old.txt","one\ntwo\n"); archive.writestr("new.txt","one\nthree\n")
        output=Path(runner.text_diff(bundle)["output_path"]).read_text(encoding="utf-8")
        self.assertIn("-two",output); self.assertIn("+three",output)
        code=self.write("source.py","x = 1  \n\n# note\nprint(x)\n")
        metrics=runner.code_size_report(code)["summary"]
        self.assertIn("Total lines: 4",metrics); self.assertIn("Trailing whitespace: 1",metrics)

    def test_subtitle_conversion_and_extended_pipeline(self):
        source=self.write("captions.srt","1\n00:00:01,000 --> 00:00:02,500\nXin chào\n")
        converted=runner.subtitle_convert(source)
        output=Path(converted["output_path"]).read_text(encoding="utf-8")
        self.assertTrue(output.startswith("WEBVTT"))
        self.assertIn("00:00:01.000 --> 00:00:02.500",output)
        job={"toolId":"video-audio","pipeline":[
            {"toolId":"video-audio"},{"toolId":"audio-convert"},{"toolId":"audio-transcribe"},
            {"toolId":"text-clean"},{"toolId":"text-deduplicate"},{"toolId":"text-stats"}]}
        self.assertEqual(len(runner.validate_pipeline(job)),6)
        source_code=self.write("metrics.py","value = 42\nprint(value)\n")
        chain={"toolId":"code-size-report","pipeline":[
            {"toolId":"code-size-report"},{"toolId":"text-clean"}]}
        output=runner.run_tool_pipeline(chain,source_code,self.input_dir.resolve())
        self.assertTrue(Path(output["output_path"]).is_file())
        self.assertIn("Total lines:",Path(output["output_path"]).read_text(encoding="utf-8"))
        stats_source=self.write("stats.txt","Nolane Search\nNolane Tools\n")
        stats_chain={"toolId":"text-stats","pipeline":[
            {"toolId":"text-stats"},{"toolId":"text-clean"}]}
        stats_output=runner.run_tool_pipeline(stats_chain,stats_source,self.input_dir.resolve())
        self.assertIn("Words:",Path(stats_output["output_path"]).read_text(encoding="utf-8"))

    def test_runner_allowlist_and_handler_registry_are_identical(self):
        self.assertEqual(runner.RUNNERS,set(runner.TOOLS))
        self.assertGreaterEqual(len(runner.TOOLS),72)


if __name__ == "__main__":
    unittest.main()
