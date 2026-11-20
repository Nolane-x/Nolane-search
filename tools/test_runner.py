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
        self.assertIn("-three",output); self.assertIn("+two",output)
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


    def test_audio_video_silence_reports_and_video_frame_sampling(self):
        import types,zipfile
        media=self.write("capture.mp4","not real media; FFmpeg calls are mocked")
        probe={"format":{"duration":"12.0"},"streams":[{"codec_type":"video"},{"codec_type":"audio"}]}
        process=types.SimpleNamespace(
            returncode=0,
            stderr="[silencedetect] silence_start: 1.000\n[silencedetect] silence_end: 2.500 | silence_duration: 1.500\n",
        )
        captured=[]
        with patch.object(runner,"ffprobe",return_value=probe),patch.object(runner.subprocess,"run",return_value=process) as fake_run:
            audio=runner.audio_silence_report(media)
            video=runner.video_silence_report(media)
            self.assertEqual(fake_run.call_count,2)
            self.assertTrue(all("silencedetect=noise=-35dB:d=0.4" in call.args[0][call.args[0].index("-af")+1] for call in fake_run.call_args_list))
        self.assertIn("1.500 seconds",audio["summary"])
        self.assertIn("1.500 seconds",video["summary"])
        def fake_cmd(name,args,timeout=180):
            captured.append((name,args,timeout))
            output=Path(str(args[-1]).replace("%03d","001"))
            output.write_bytes(b"mock-jpeg-frame")
            return ""
        with patch.object(runner,"ffprobe",return_value=probe),patch.object(runner,"cmd",side_effect=fake_cmd):
            result=runner.video_frames(media)
        self.assertIn("-frames:v",captured[0][1])
        with zipfile.ZipFile(result["output_path"]) as archive:
            self.assertEqual(len(archive.namelist()),1)
            self.assertTrue(archive.namelist()[0].endswith(".jpg"))


    def test_pipeline_trace_records_step_timings_and_failure_details(self):
        source=self.write("trace.txt","Alpha\nBeta\nalpha\n")
        job={"toolId":"text-deduplicate","pipeline":[{"toolId":"text-deduplicate"}]}
        result=runner.run_tool_pipeline(job,source,self.input_dir.resolve())
        self.assertEqual(len(result["trace"]),1)
        step=result["trace"][0]
        self.assertEqual(step["status"],"completed")
        self.assertEqual(step["toolId"],"text-deduplicate")
        self.assertEqual(step["step"],1)
        self.assertEqual(step["total"],1)
        self.assertEqual(step["inputBytes"],source.stat().st_size)
        self.assertGreater(step["outputBytes"],0)
        self.assertGreaterEqual(step["durationMs"],0)
        self.assertTrue(Path(result["output_path"]).is_file())

        def fail(_path):
            raise RuntimeError("deliberate processor failure")
        with patch.dict(runner.TOOLS,{"text-deduplicate":fail}):
            with self.assertRaises(runner.PipelineExecutionError) as caught:
                runner.run_tool_pipeline(job,source,self.input_dir.resolve())
        self.assertEqual(caught.exception.trace[-1]["status"],"failed")
        self.assertEqual(caught.exception.trace[-1]["error"],"deliberate processor failure")
        self.assertEqual(caught.exception.trace[-1]["inputBytes"],source.stat().st_size)
        self.assertIn("[runner-path]", runner._safe_trace_text("failed /home/runner/work/nolane/tmp/file.pdf", self.input_dir))



    def test_cmd_run_writes_failure_trace_before_returning_nonzero(self):
        import argparse,json
        source=self.write("source.txt","Original\n")
        job_file=self.root/"job.json"
        job_file.write_text(json.dumps({"job":{"id":"12345678-1234-1234-1234-123456789abc","toolId":"text-deduplicate","pipeline":[{"toolId":"text-deduplicate"}]}}),encoding="utf-8")
        input_file=self.root/"input-path.txt"
        input_file.write_text(str(source),encoding="utf-8")
        result_file=self.root/"result.json"
        def fail(_path):
            raise RuntimeError("failed at /home/runner/work/private/source.txt")
        with patch.dict(runner.TOOLS,{"text-deduplicate":fail}):
            with self.assertRaises(runner.PipelineExecutionError):
                runner.cmd_run(argparse.Namespace(job_file=str(job_file),input_path_file=str(input_file),output=str(result_file)))
        result=json.loads(result_file.read_text(encoding="utf-8"))
        self.assertEqual(result["trace"][-1]["status"],"failed")
        self.assertIn("[runner-path]",result["error"])
        self.assertNotIn("/home/runner/work",result["error"])

    def test_runner_allowlist_and_handler_registry_are_identical(self):
        self.assertEqual(runner.RUNNERS,set(runner.TOOLS))
        self.assertGreaterEqual(len(runner.TOOLS),102)


    def test_pdf_rotation_and_blank_page_removal(self):
        import fitz
        source=self.input_dir/"pages.pdf"
        document=fitz.open()
        document.new_page(width=300,height=500)
        page=document.new_page(width=300,height=500)
        page.insert_text((40,80),"Visible content page")
        document.save(source); document.close()
        rotated=runner.pdf_rotate_cw(source)
        rotated_doc=fitz.open(rotated["output_path"])
        self.assertEqual(rotated_doc.page_count,2)
        self.assertEqual(rotated_doc[0].rotation,90)
        rotated_doc.close()
        cleaned=runner.pdf_remove_blank(source)
        output=fitz.open(cleaned["output_path"])
        self.assertEqual(output.page_count,1)
        self.assertIn("Visible content page",output[0].get_text())
        output.close()

    def test_image_trim_border_pixelate_and_pair_diff(self):
        import io,zipfile
        from PIL import Image,ImageDraw
        source=self.input_dir/"border.png"
        image=Image.new("RGB",(100,80),"white")
        ImageDraw.Draw(image).rectangle((20,15,79,64),fill=(20,80,160))
        image.save(source); image.close()
        trimmed=runner.image_trim_border(source)
        with Image.open(trimmed["output_path"]) as cropped:
            self.assertLess(cropped.width,100)
            self.assertLess(cropped.height,80)
            self.assertEqual(cropped.format,"PNG")
        pixelated=runner.image_pixelate(source)
        with Image.open(pixelated["output_path"]) as pixel:
            self.assertEqual(pixel.size,(100,80))
            self.assertEqual(pixel.format,"PNG")
        left=self.input_dir/"left.png"; right=self.input_dir/"right.png"
        Image.new("RGB",(20,20),"red").save(left)
        other=Image.new("RGB",(20,20),"red")
        other.putpixel((10,10),(0,0,255)); other.save(right); other.close()
        bundle=self.input_dir/"pair.zip"
        with zipfile.ZipFile(bundle,"w") as archive:
            archive.write(left,"a.png"); archive.write(right,"b.png")
        result=runner.image_diff(bundle)
        with zipfile.ZipFile(result["output_path"]) as archive:
            self.assertEqual(set(archive.namelist()),{"difference.png","overlay.png"})
            with Image.open(io.BytesIO(archive.read("difference.png"))) as diff:
                self.assertEqual(diff.size,(20,20))
                self.assertIsNotNone(diff.getbbox())

    def test_json_flatten_csv_sqlite_and_json_diff(self):
        import csv,sqlite3,zipfile
        source=self.write("nested.json",'{"name":"An","profile":{"age":17,"city":"Hai Phong"},"tags":["ai","python"]}')
        flattened=runner.json_flatten_csv(source)
        with open(flattened["output_path"],encoding="utf-8-sig",newline="") as handle:
            row=next(csv.DictReader(handle))
        self.assertEqual(row["profile.age"],"17")
        self.assertEqual(row["profile.city"],"Hai Phong")
        self.assertEqual(row["tags"],'["ai","python"]')
        csv_source=self.write("people.csv","name,age\nAn,17\nBinh,18\n")
        database=runner.csv_to_sqlite(csv_source)
        connection=sqlite3.connect(database["output_path"])
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM records").fetchone()[0],2)
            self.assertEqual(connection.execute('SELECT age FROM records WHERE name="An"').fetchone()[0],"17")
        finally:
            connection.close()
        first=self.input_dir/"first.json"; second=self.input_dir/"second.json"
        first.write_text('{"a":1,"b":2}',encoding="utf-8")
        second.write_text('{"a":1,"b":3}',encoding="utf-8")
        bundle=self.input_dir/"json-pair.zip"
        with zipfile.ZipFile(bundle,"w") as archive:
            archive.write(first,"a.json"); archive.write(second,"b.json")
        diff=runner.json_diff(bundle)
        self.assertIn('"b": 2',diff["summary"])
        self.assertIn('"b": 3',diff["summary"])

    def test_log_insights_groups_levels_and_repeated_errors(self):
        path=self.write("service.log",
            "2026-11-19T10:00:00Z ERROR database timeout request 12\n"
            "2026-11-19T10:01:00Z ERROR database timeout request 99\n"
            "2026-11-19T10:02:00Z WARNING slow query\n"
            "2026-11-19T10:03:00Z INFO ready\n")
        result=runner.log_insights(path)
        self.assertIn("ERROR: 2",result["summary"])
        self.assertIn("WARN: 1",result["summary"])
        self.assertIn("database timeout request #",result["summary"])
        self.assertIn("2 x",result["summary"])

    def test_audio_video_metadata_and_scene_tools_use_bounded_ffmpeg_calls(self):
        import zipfile
        audio=self.write("stereo.wav","mock audio")
        video=self.write("clip.mp4","mock video")
        audio_probe={"format":{"duration":"12"},"streams":[{"codec_type":"audio","channels":2,"channel_layout":"stereo"}]}
        video_probe={"format":{"duration":"12"},"streams":[{"codec_type":"video","width":640,"height":360}]}
        captured=[]
        def fake_cmd(name,args,timeout=180):
            captured.append((name,args,timeout))
            target=Path(args[-1])
            if "%03d" in str(target):
                target=Path(str(target).replace("%03d","001"))
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(b"mock-output")
            return ""
        with patch.object(runner,"ffprobe",return_value=audio_probe),patch.object(runner,"cmd",side_effect=fake_cmd):
            split=runner.audio_stereo_split(audio)
            cleaned_audio=runner.audio_metadata_clean(audio)
        with zipfile.ZipFile(split["output_path"]) as archive:
            self.assertEqual(set(archive.namelist()),{"left.mp3","right.mp3"})
        self.assertTrue(Path(cleaned_audio["output_path"]).is_file())
        self.assertTrue(any("-map_metadata" in call[1] for call in captured))
        captured.clear()
        with patch.object(runner,"ffprobe",return_value=video_probe),patch.object(runner,"cmd",side_effect=fake_cmd):
            scenes=runner.video_scene_frames(video)
            cleaned_video=runner.video_metadata_clean(video)
        with zipfile.ZipFile(scenes["output_path"]) as archive:
            self.assertTrue(any(name.endswith(".jpg") for name in archive.namelist()))
        self.assertTrue(cleaned_video["output_path"].endswith(".mkv"))
        self.assertTrue(Path(cleaned_video["output_path"]).is_file())
        self.assertTrue(any("select='gt(scene,0.35)'" in " ".join(call[1]) for call in captured))


    def test_workflow_dag_runs_ready_branches_concurrently_and_packages_outputs(self):
        import json, threading, time, zipfile
        source=self.write("clip.mp4","source-media")
        dag=[
            {"id":"source","toolId":"video-audio","dependsOn":[]},
            {"id":"transcript","toolId":"audio-transcribe","dependsOn":["source"]},
            {"id":"converted","toolId":"audio-convert","dependsOn":["source"]},
        ]
        lock=threading.Lock()
        active=0
        peak=0
        def fake_processor(path):
            nonlocal active,peak
            with lock:
                active+=1
                peak=max(peak,active)
            time.sleep(0.06)
            output=path.with_name(path.stem+"-processed.bin")
            output.write_bytes(path.read_bytes()+b"-processed")
            with lock:
                active-=1
            return {"summary":path.name+" processed","output_path":str(output)}
        with patch.dict(runner.TOOLS,{
            "video-audio":fake_processor,
            "audio-transcribe":fake_processor,
            "audio-convert":fake_processor,
        }):
            result=runner.run_tool_dag({"toolId":"video-audio","workflowDag":dag},source,self.input_dir.resolve())
        self.assertGreaterEqual(peak,2)
        self.assertLessEqual(peak,3)
        self.assertEqual({item["nodeId"] for item in result["trace"]},{"source","transcript","converted"})
        self.assertTrue(all(item["status"]=="completed" for item in result["trace"]))
        with zipfile.ZipFile(result["output_path"]) as archive:
            names=set(archive.namelist())
            self.assertIn("manifest.json",names)
            self.assertTrue(any(name.startswith("branches/transcript/") for name in names))
            self.assertTrue(any(name.startswith("branches/converted/") for name in names))
            manifest=json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["maxConcurrency"],3)
            self.assertEqual(set(manifest["terminalOutputs"]),{"transcript","converted"})

    def test_text_join_combines_utf8_files_in_order_and_rejects_binary_like_content(self):
        first=self.write("statistics.txt","Words: 12")
        second=self.write("unique.txt","Unique terms: 9")
        result=runner.text_join([first,second])
        output=Path(result["output_path"])
        merged=output.read_text(encoding="utf-8")
        self.assertIn("SOURCE 1: statistics.txt",merged)
        self.assertIn("SOURCE 2: unique.txt",merged)
        self.assertLess(merged.index("Words: 12"),merged.index("Unique terms: 9"))
        self.assertIn("2 nhánh văn bản",result["summary"])

        binary=self.input_dir/"binary.txt"
        binary.write_bytes(b"text"+bytes([0])+b"payload")
        with self.assertRaisesRegex(RuntimeError,"binary-like input"):
            runner.text_join([first,binary])

        with self.assertRaisesRegex(RuntimeError,"2 to 3"):
            runner.text_join([first])

    def test_text_join_cannot_run_as_a_single_file_pipeline(self):
        with self.assertRaisesRegex(RuntimeError,"only merge parent artifacts"):
            runner.validate_pipeline({"toolId":"text-join","pipeline":[{"toolId":"text-join"}]})

    def test_workflow_dag_merges_two_completed_parent_branches(self):
        import json, zipfile
        source=self.write("report.pdf","mock pdf bytes")
        dag=[
            {"id":"source","toolId":"pdf-text","dependsOn":[]},
            {"id":"clean","toolId":"text-clean","dependsOn":["source"]},
            {"id":"stats","toolId":"text-stats","dependsOn":["clean"]},
            {"id":"unique","toolId":"text-deduplicate","dependsOn":["clean"]},
            {"id":"merged","toolId":"text-join","dependsOn":["stats","unique"]},
        ]
        def fake_processor(tool_id):
            def process(path):
                output=path.with_name(path.stem+"-"+tool_id+".txt")
                output.write_text(tool_id+" output from "+path.name,encoding="utf-8")
                return {"summary":tool_id+" completed","output_path":str(output)}
            return process
        with patch.dict(runner.TOOLS,{
            "pdf-text":fake_processor("pdf-text"),
            "text-clean":fake_processor("text-clean"),
            "text-stats":fake_processor("text-stats"),
            "text-deduplicate":fake_processor("text-deduplicate"),
        }):
            result=runner.run_tool_dag({"toolId":"pdf-text","workflowDag":dag},source,self.input_dir.resolve())
        trace={item["nodeId"]:item for item in result["trace"]}
        self.assertEqual(set(trace),{"source","clean","stats","unique","merged"})
        self.assertTrue(all(item["status"]=="completed" for item in trace.values()))
        self.assertEqual(trace["merged"]["inputBytes"],trace["stats"]["outputBytes"]+trace["unique"]["outputBytes"])
        with zipfile.ZipFile(result["output_path"]) as archive:
            names=set(archive.namelist())
            self.assertIn("manifest.json",names)
            merged_name=next(name for name in names if name.startswith("branches/merged/"))
            merged_text=archive.read(merged_name).decode("utf-8")
            self.assertIn("SOURCE 1:",merged_text)
            self.assertIn("SOURCE 2:",merged_text)
            manifest=json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["terminalOutputs"],["merged"])
            merged_node=next(node for node in manifest["nodes"] if node["id"]=="merged")
            self.assertEqual(merged_node["dependsOn"],["stats","unique"])

    def test_validate_dag_restricts_fanin_to_text_join_and_three_parents(self):
        root={"id":"source","toolId":"pdf-text","dependsOn":[]}
        clean={"id":"clean","toolId":"text-clean","dependsOn":["source"]}
        stats={"id":"stats","toolId":"text-stats","dependsOn":["clean"]}
        unique={"id":"unique","toolId":"text-deduplicate","dependsOn":["clean"]}
        with self.assertRaisesRegex(RuntimeError,"only one parent"):
            runner.validate_dag({"toolId":"pdf-text","workflowDag":[
                root,clean,stats,unique,
                {"id":"merged","toolId":"text-clean","dependsOn":["stats","unique"]},
            ]})
        with self.assertRaisesRegex(RuntimeError,"between 2 and 3"):
            runner.validate_dag({"toolId":"pdf-text","workflowDag":[
                root,clean,stats,unique,
                {"id":"merged","toolId":"text-join","dependsOn":["stats"]},
            ]})
        four_stats=[
            {"id":"stat1","toolId":"text-stats","dependsOn":["clean"]},
            {"id":"stat2","toolId":"text-stats","dependsOn":["clean"]},
            {"id":"stat3","toolId":"text-stats","dependsOn":["clean"]},
            {"id":"stat4","toolId":"text-stats","dependsOn":["clean"]},
        ]
        with self.assertRaisesRegex(RuntimeError,"between 2 and 3"):
            runner.validate_dag({"toolId":"pdf-text","workflowDag":[
                root,clean,*four_stats,
                {"id":"merged","toolId":"text-join","dependsOn":["stat1","stat2","stat3","stat4"]},
            ]})

    def test_workflow_dag_stops_descendants_after_a_parallel_branch_failure(self):
        import threading,time
        source=self.write("clip.mp4","source-media")
        dag=[
            {"id":"source","toolId":"video-audio","dependsOn":[]},
            {"id":"transcript","toolId":"audio-transcribe","dependsOn":["source"]},
            {"id":"converted","toolId":"audio-convert","dependsOn":["source"]},
            {"id":"descendant","toolId":"text-clean","dependsOn":["transcript"]},
        ]
        lock=threading.Lock()
        active=0
        peak=0
        def succeed(path):
            nonlocal active,peak
            with lock:
                active+=1
                peak=max(peak,active)
            time.sleep(0.04)
            output=path.with_name(path.stem+"-ok.bin")
            output.write_bytes(path.read_bytes()+b"-ok")
            with lock:
                active-=1
            return {"summary":"completed","output_path":str(output)}
        def fail(path):
            with lock:
                active+=1
            time.sleep(0.04)
            with lock:
                active-=1
            raise RuntimeError("branch decode failed")
        with patch.dict(runner.TOOLS,{
            "video-audio":succeed,
            "audio-transcribe":fail,
            "audio-convert":succeed,
            "text-clean":succeed,
        }):
            with self.assertRaises(runner.PipelineExecutionError) as caught:
                runner.run_tool_dag({"toolId":"video-audio","workflowDag":dag},source,self.input_dir.resolve())
        trace=caught.exception.trace
        self.assertEqual({item["nodeId"] for item in trace},{"source","transcript","converted"})
        self.assertEqual(next(item for item in trace if item["nodeId"]=="transcript")["status"],"failed")
        self.assertEqual(next(item for item in trace if item["nodeId"]=="converted")["status"],"completed")
        self.assertNotIn("descendant",{item["nodeId"] for item in trace})
        self.assertLessEqual(peak,3)


    def test_markdown_outline_and_links_ignore_fenced_code(self):
        fence = chr(96) * 3
        path=self.write("README.md", "# Title\n\n## Setup\n\n" + fence + "md\n# Not a heading\n[bad](https://ignored.example)\n" + fence + "\n\n[Docs](https://example.com/docs) and ![logo](./logo.png)\n")
        outline=runner.markdown_outline(path)
        body=Path(outline["output_path"]).read_text(encoding="utf-8")
        self.assertIn("Title",body)
        self.assertIn("Setup",body)
        self.assertNotIn("Not a heading",body)
        links=runner.markdown_links(path)
        rows=list(__import__("csv").DictReader(Path(links["output_path"]).open(encoding="utf-8-sig")))
        self.assertEqual(len(rows),2)
        self.assertEqual({item["kind"] for item in rows},{"link","image"})
        self.assertNotIn("ignored.example",str(rows))

    def test_text_redact_masks_secrets_and_emails(self):
        raw="Contact person@example.com; Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456; api_key=super-secret-key-1234"
        path=self.write("notes.txt",raw)
        result=runner.text_redact(path)
        cleaned=Path(result["output_path"]).read_text(encoding="utf-8")
        self.assertNotIn("person@example.com",cleaned)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz123456",cleaned)
        self.assertNotIn("super-secret-key-1234",cleaned)
        self.assertIn("[REDACTED]",cleaned)
        self.assertNotIn("super-secret-key-1234",result["summary"])

    def test_text_extract_deduplicates_values_and_rejects_invalid_ipv4(self):
        path=self.write("references.txt","Visit https://example.com/docs twice https://example.com/docs\nEmail a@example.com\nIP 192.168.1.1 and 999.2.3.4")
        result=runner.text_extract(path)
        rows=list(__import__("csv").DictReader(Path(result["output_path"]).open(encoding="utf-8-sig")))
        values={(row["kind"],row["value"]):row["occurrences"] for row in rows}
        self.assertEqual(values[("URL","https://example.com/docs")],"2")
        self.assertEqual(values[("email","a@example.com")],"1")
        self.assertIn(("IPv4","192.168.1.1"),values)
        self.assertNotIn(("IPv4","999.2.3.4"),values)

    def test_code_import_report_is_static_for_python_and_javascript(self):
        py=self.write("module.py","import json\nfrom pathlib import Path\n")
        report=runner.code_imports(py)
        body=Path(report["output_path"]).read_text(encoding="utf-8")
        self.assertIn("json",body)
        self.assertIn("pathlib",body)
        js=self.write("main.ts",'import React from "react";\nconst fs = require("node:fs");\n')
        js_report=runner.code_imports(js)
        js_body=Path(js_report["output_path"]).read_text(encoding="utf-8")
        self.assertIn("react",js_body)
        self.assertIn("node:fs",js_body)

    def test_code_todo_report_includes_line_number_and_kind(self):
        path=self.write("task.py","# TODO: add validation\n# FIXME handle empty input\n# normal comment\n")
        result=runner.code_todos(path)
        body=Path(result["output_path"]).read_text(encoding="utf-8")
        self.assertIn("L1 [TODO]",body)
        self.assertIn("L2 [FIXME]",body)
        self.assertIn("TODO=1",body)

    def test_code_secret_scan_never_prints_detected_secret_values(self):
        token="ghp_"+"A"*36
        path=self.write("config.py",f'TOKEN = "{token}"\npassword = "this-is-a-long-password"\n')
        result=runner.code_secret_scan(path)
        body=Path(result["output_path"]).read_text(encoding="utf-8")
        self.assertIn("GitHub token",body)
        self.assertIn("Credential assignment",body)
        self.assertIn("[value withheld]",body)
        self.assertNotIn(token,body)
        self.assertNotIn("this-is-a-long-password",body)

    def test_log_timeline_groups_iso_timestamps_by_day_and_hour(self):
        path=self.write("service.log","2026-11-20T10:01:02Z INFO start\n2026-11-20 10:02:03 ERROR fail\n2026-11-21T11:00:00Z INFO done\n")
        result=runner.log_timeline(path)
        body=Path(result["output_path"]).read_text(encoding="utf-8")
        self.assertIn("Timestamp lines: 3",body)
        self.assertIn("2026-11-20: 2",body)
        self.assertIn("2026-11-21: 1",body)
        self.assertIn("2026-11-20 10:xx — 2 lines",body)


    def make_repository_archive(self, name="project.zip"):
        import json as json_module
        import zipfile
        path=self.input_dir/name
        token="ghp_"+"A"*36
        with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("project/README.md","# Sample project\n")
            archive.writestr("project/LICENSE","MIT License\nPermission is hereby granted, free of charge.\n")
            archive.writestr("project/package.json",json_module.dumps({
                "name":"sample-project","license":"MIT","dependencies":{"lodash":"^4.17.21"},
                "devDependencies":{"vitest":"^3.0.0"}
            }))
            archive.writestr("project/requirements.txt","requests>=2.31\npydantic==2.9.0\n")
            archive.writestr("project/src/app.py",f"# TODO: add validation\nTOKEN = '{token}'\npassword = 'this-is-a-long-password'\nprint('safe')\n")
            archive.writestr("project/src/duplicate.py","print('same content')\n")
            archive.writestr("project/docs/duplicate.py","print('same content')\n")
            archive.writestr("project/tests/test_app.py","def test_ok():\n    assert True\n")
            archive.writestr("project/.github/workflows/ci.yml","name: CI\non: [push]\n")
            archive.writestr("project/Dockerfile","FROM python:3.12\n")
            archive.writestr("project/.env.example","API_KEY=your_api_key_here\n")
            archive.writestr("project/pyproject.toml","[project]\nname = 'sample-project'\ndependencies = ['httpx>=0.27']\n")
        return path,token

    def test_repo_inventory_dependencies_and_license_reports(self):
        path,_=self.make_repository_archive()
        inventory=runner.repo_inventory(path)
        inventory_text=Path(inventory["output_path"]).read_text(encoding="utf-8")
        self.assertIn("Files: 12",inventory_text)
        self.assertIn(".py",inventory_text)
        self.assertIn("README.md",inventory_text)
        dependencies=runner.repo_dependencies(path)
        dependency_text=Path(dependencies["output_path"]).read_text(encoding="utf-8")
        self.assertIn("lodash",dependency_text)
        self.assertIn("requests",dependency_text)
        self.assertIn("httpx",dependency_text)
        licenses=runner.repo_license_report(path)
        license_text=Path(licenses["output_path"]).read_text(encoding="utf-8")
        self.assertIn("MIT",license_text)
        self.assertIn("package.json",license_text)
        self.assertIn("not legal advice",license_text.lower())

    def test_repo_secret_and_todo_scans_never_disclose_secret_values(self):
        path,token=self.make_repository_archive()
        secret=runner.repo_secret_scan(path)
        report=Path(secret["output_path"]).read_text(encoding="utf-8")
        self.assertIn("GitHub token",report)
        self.assertIn("[value withheld]",report)
        self.assertNotIn(token,report)
        self.assertNotIn("this-is-a-long-password",report)
        todos=runner.repo_todo_scan(path)
        todo_report=Path(todos["output_path"]).read_text(encoding="utf-8")
        self.assertIn("project/src/app.py:L1 [TODO]",todo_report)
        self.assertIn("add validation",todo_report)

    def test_repo_code_stats_config_audit_and_duplicate_hashes(self):
        path,_=self.make_repository_archive()
        stats=runner.repo_code_stats(path)
        stats_text=Path(stats["output_path"]).read_text(encoding="utf-8")
        self.assertIn(".py:",stats_text)
        self.assertIn("Total lines:",stats_text)
        audit=runner.repo_config_audit(path)
        audit_text=Path(audit["output_path"]).read_text(encoding="utf-8")
        self.assertIn("PRESENT · Automated tests",audit_text)
        self.assertIn("PRESENT · CI workflow",audit_text)
        self.assertIn("PRESENT · Container build",audit_text)
        duplicate=runner.repo_duplicates(path)
        rows=list(__import__("csv").DictReader(Path(duplicate["output_path"]).open(encoding="utf-8-sig")))
        duplicate_paths=[row["paths"] for row in rows]
        self.assertTrue(any("project/src/duplicate.py" in value and "project/docs/duplicate.py" in value for value in duplicate_paths))

    def test_repo_security_audit_detects_ci_container_kubernetes_and_iac_risks(self):
        import json as json_module
        import zipfile

        path = self.input_dir / "security-project.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("project/.github/workflows/ci.yml", """name: unsafe
on:
  pull_request_target:
    types: [opened]
jobs:
  test:
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "${{ github.event.pull_request.title }}"
""")
            archive.writestr("project/Dockerfile", """FROM node:latest
ARG API_KEY=never-print-this-secret
RUN curl -fsSL https://example.invalid/install.sh | bash
USER root
""")
            archive.writestr("project/deploy/pod.yaml", """apiVersion: v1
kind: Pod
metadata:
  name: risky
spec:
  hostNetwork: true
  containers:
    - name: app
      image: example.invalid/app:1
      securityContext:
        privileged: true
        allowPrivilegeEscalation: true
        runAsUser: 0
        capabilities:
          add:
            - SYS_ADMIN
  volumes:
    - name: host
      hostPath:
        path: /host
""")
            archive.writestr("project/infra/main.tf", """data "aws_iam_policy_document" "wide" {
  statement {
    actions = ["*"]
    resources = ["*"]
  }
}
resource "aws_security_group_rule" "ssh" {
  from_port = 22
  to_port = 22
  cidr_blocks = ["0.0.0.0/0"]
}
resource "aws_s3_bucket_acl" "public" {
  acl = "public-read"
}
""")

        result = runner.repo_security_audit(path)
        self.assertTrue(Path(result["output_path"]).is_file())
        with zipfile.ZipFile(result["output_path"]) as package:
            names = set(package.namelist())
            self.assertEqual(names, {"security-audit.md", "security.sarif", "security-findings.json"})
            report = package.read("security-audit.md").decode("utf-8")
            sarif = json_module.loads(package.read("security.sarif"))
            findings = json_module.loads(package.read("security-findings.json"))
        rule_ids = {item["ruleId"] for item in findings["findings"]}
        self.assertTrue({
            "NOLANE-GHA-001", "NOLANE-GHA-002", "NOLANE-GHA-003",
            "NOLANE-CTR-001", "NOLANE-CTR-002", "NOLANE-CTR-003",
            "NOLANE-CTR-004", "NOLANE-K8S-001", "NOLANE-K8S-002",
            "NOLANE-K8S-003", "NOLANE-K8S-004", "NOLANE-K8S-005",
            "NOLANE-K8S-006", "NOLANE-IAC-001", "NOLANE-IAC-002",
            "NOLANE-IAC-003",
        }.issubset(rule_ids))
        self.assertEqual(sarif["version"], "2.1.0")
        self.assertEqual(len(sarif["runs"][0]["results"]), len(findings["findings"]))
        self.assertNotIn("never-print-this-secret", report)
        self.assertNotIn("never-print-this-secret", json_module.dumps(findings))

    def test_repo_supply_chain_inventory_pairs_lockfiles_and_redacts_urls(self):
        import json as json_module
        import zipfile

        path = self.input_dir / "supply-chain-project.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("project/frontend/package.json", json_module.dumps({
                "name": "frontend",
                "dependencies": {
                    "lodash": "^4.0.0",
                    "private-lib": "https://user:private-password@example.invalid/lib.tgz",
                },
                "scripts": {"preinstall": "node install.js"},
            }))
            archive.writestr("project/frontend/package-lock.json", "{}")
            archive.writestr("project/service/pyproject.toml", """[project]
name = "service"
dependencies = ["requests>=2.0", "httpx"]
""")
            archive.writestr("project/service/requirements.txt", "requests==2.31.0\nhttps://user:private-password@example.invalid/pkg.whl\n")

        result = runner.repo_supply_chain(path)
        with zipfile.ZipFile(result["output_path"]) as package:
            data = json_module.loads(package.read("supply-chain.json"))
            report = package.read("supply-chain.md").decode("utf-8")
        self.assertEqual(data["counts"]["manifests"], 3)
        self.assertGreaterEqual(data["counts"]["lockfiles"], 1)
        self.assertEqual(data["counts"]["lifecycle_hooks"], 1)
        self.assertGreaterEqual(data["counts"]["remote_sources"], 2)
        self.assertGreaterEqual(data["counts"]["manifests_without_nearby_lockfile"], 2)
        self.assertTrue(any(item["lockfile_status"] == "paired" for item in data["manifests"]))
        self.assertTrue(any(item["name"] == "private-lib" and item["requirement"] == "[remote URL/reference omitted]" for item in data["dependencies"]))
        combined = report + json_module.dumps(data, ensure_ascii=False)
        self.assertNotIn("private-password", combined)
        self.assertNotIn("user:private", combined)
        self.assertIn("lockfile", report.lower())

    def test_repo_analysis_rejects_path_traversal_without_extracting(self):
        import zipfile
        path=self.input_dir/"unsafe-project.zip"
        with zipfile.ZipFile(path,"w") as archive:
            archive.writestr("../outside.txt","must not escape")
            archive.writestr("safe/README.md","hello")
        with self.assertRaises(RuntimeError):
            runner.repo_inventory(path)
        self.assertFalse((self.root/"outside.txt").exists())


    def test_github_source_ref_validation_and_archive_redirect_allowlist(self):
        self.assertTrue(runner._github_ref("main"))
        self.assertTrue(runner._github_ref("feature/new-ui"))
        self.assertFalse(runner._github_ref("../private"))
        self.assertFalse(runner._github_ref("feature\\escape"))
        self.assertFalse(runner._github_ref("branch name"))
        self.assertEqual(runner._github_identity("acme", "project"), "https://api.github.com/repos/acme/project")
        with self.assertRaises(RuntimeError):
            runner._github_identity("bad/owner", "project")

        redirect = runner._GitHubArchiveRedirect()
        with self.assertRaises(RuntimeError):
            redirect.redirect_request(None, None, 302, "Found", {}, "https://evil.example/archive.zip")
        with self.assertRaises(RuntimeError):
            redirect.redirect_request(None, None, 302, "Found", {}, "http://codeload.github.com/acme/project/zip/main")
        with self.assertRaises(RuntimeError):
            redirect.redirect_request(None, None, 302, "Found", {}, "https://codeload.github.com:8443/acme/project/zip/main")

    def test_repo_intelligence_packages_static_reports_and_module_graph(self):
        import json as json_module
        import zipfile

        path = self.input_dir / "intelligence-project.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("project/README.md", "# Sample project\n")
            archive.writestr("project/package.json", '{"name":"sample","dependencies":{"vitest":"^3.0.0"}}')
            archive.writestr("project/src/main.py", "from src.helper import run\n")
            archive.writestr("project/src/helper.py", "def run():\n    return 1\n")
            archive.writestr("project/src/index.ts", 'import { run } from "./lib/run";\n')
            archive.writestr("project/src/lib/run.ts", "export function run() { return 1; }\n")
            archive.writestr("project/.github/workflows/ci.yml", "name: CI\n")
            archive.writestr("project/.env.example", "TOKEN=your_token_here\n")

        metadata_dir = self.root / "nolane-inputs"
        metadata_dir.mkdir(exist_ok=True)
        (metadata_dir / "github-source-metadata.json").write_text(json_module.dumps({
            "repository": {
                "full_name": "acme/project",
                "html_url": "https://github.com/acme/project",
                "default_branch": "main",
                "analyzed_ref": "feature/demo",
                "stars": 10,
                "forks": 2,
                "open_issues": 1,
                "language": "Python",
                "pushed_at": "2026-11-20T00:00:00Z",
            },
            "commits": [{
                "sha": "0123456789abcdef",
                "date": "2026-11-19T12:00:00Z",
                "author": "Nolane",
                "message": "Fix import graph",
                "url": "https://github.com/acme/project/commit/0123456",
            }],
            "compare": {
                "base": "main",
                "head": "feature/demo",
                "status": "ahead",
                "ahead_by": 2,
                "behind_by": 0,
                "total_commits": 2,
                "files": [{
                    "filename": "src/main.py", "status": "modified",
                    "additions": 5, "deletions": 1, "changes": 6,
                }],
            },
        }, ensure_ascii=False), encoding="utf-8")

        result = runner.repo_intelligence(path)
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertIn("2 local import edges", result["summary"])
        with zipfile.ZipFile(result["output_path"]) as archive:
            names = set(archive.namelist())
            self.assertIn("report/repository-intelligence.md", names)
            self.assertIn("architecture/module-graph.json", names)
            self.assertIn("github/github-metadata.json", names)
            self.assertIn("reports/secret-scan.txt", names)
            self.assertIn("reports/dependencies.txt", names)
            self.assertIn("reports/security-audit.zip", names)
            self.assertIn("reports/supply-chain.zip", names)
            report = archive.read("report/repository-intelligence.md").decode("utf-8")
            graph = json_module.loads(archive.read("architecture/module-graph.json"))
            self.assertIn("acme/project", report)
            self.assertIn("main → feature/demo", report)
            self.assertIn("Fix import graph", report)
            self.assertEqual(len(graph["edges"]), 2)
            edge_pairs = {(edge["from"], edge["to"]) for edge in graph["edges"]}
            self.assertIn(("project/src/main.py", "project/src/helper.py"), edge_pairs)
            self.assertIn(("project/src/index.ts", "project/src/lib/run.ts"), edge_pairs)

    def test_pipeline_reports_bounded_live_progress_checkpoints(self):
        source=self.write("notes.txt","A sample text file with enough content.\n")
        job={
            "id":"12345678-1234-1234-1234-123456789abc",
            "toolId":"text-clean",
            "pipeline":[{"toolId":"text-clean"},{"toolId":"text-stats"}],
        }
        with patch.object(runner,"callback") as callback:
            runner.run_tool_pipeline(job,source,self.input_dir.resolve())
        payloads=[call.args[1] for call in callback.call_args_list]
        self.assertEqual([item["status"] for item in payloads],["progress"]*4)
        self.assertEqual(payloads[0]["progress"],{"completed":0,"total":2,"currentToolIds":["text-clean"]})
        self.assertEqual(payloads[1]["progress"]["completed"],1)
        self.assertEqual(payloads[2]["progress"]["currentToolIds"],["text-stats"])
        self.assertEqual(payloads[3]["progress"]["completed"],2)
        self.assertEqual(payloads[3]["progress"]["currentToolIds"],[])




if __name__ == "__main__":
    unittest.main()
