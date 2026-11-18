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


    def test_runner_allowlist_and_handler_registry_are_identical(self):
        self.assertEqual(runner.RUNNERS,set(runner.TOOLS))
        self.assertGreaterEqual(len(runner.TOOLS),38)


if __name__ == "__main__":
    unittest.main()
