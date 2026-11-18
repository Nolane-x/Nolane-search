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


if __name__ == "__main__":
    unittest.main()
