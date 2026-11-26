from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

os.environ["NOLANE_INTERNAL_TOKEN"] = "test-internal-token-" + ("x" * 40)
MODULE_PATH = Path(__file__).with_name("server.py")
SPEC = importlib.util.spec_from_file_location("nolane_media_downloader_server", MODULE_PATH)
assert SPEC and SPEC.loader
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


class MediaDownloaderServerTests(unittest.TestCase):
    def test_range_parser_supports_full_open_ended_and_suffix_ranges(self):
        self.assertEqual(server.parse_range(None, 100), (0, 99))
        self.assertEqual(server.parse_range("bytes=10-19", 100), (10, 19))
        self.assertEqual(server.parse_range("bytes=10-", 100), (10, 99))
        self.assertEqual(server.parse_range("bytes=-10", 100), (90, 99))
        self.assertEqual(server.parse_range("bytes=-200", 100), (0, 99))
        self.assertIsNone(server.parse_range("bytes=100-", 100))
        self.assertIsNone(server.parse_range("bytes=20-10", 100))
        self.assertIsNone(server.parse_range("bytes=0-1,4-5", 100))
        self.assertIsNone(server.parse_range("bytes=-0", 100))
        self.assertIsNone(server.parse_range("items=0-1", 100))

    def test_job_id_validation_requires_uuid_v4_shape(self):
        self.assertTrue(server.valid_job_id(str(uuid.uuid4())))
        self.assertFalse(server.valid_job_id("../etc/passwd"))
        self.assertFalse(server.valid_job_id("0" * 32))
        self.assertFalse(server.valid_job_id(""))

    def test_media_command_uses_argument_array_and_public_input_position(self):
        job_id = str(uuid.uuid4())
        url = "https://www.youtube.com/watch?v=abc123"
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(server, "DATA_ROOT", Path(temp)):
                args, folder = server._command(job_id, url, "video", "720")
                self.assertEqual(folder.parent, Path(temp))
                self.assertEqual(args[-1], url)
                self.assertIn("--ignore-config", args)
                self.assertIn("--no-playlist", args)
                self.assertIn("--no-cache-dir", args)
                self.assertIn("--remote-components", args)
                self.assertIn("ejs:github", args)
                self.assertIn("--ffmpeg-location", args)
                self.assertIn("--max-filesize", args)
                self.assertNotIn("--cookies", args)
                self.assertNotIn("--cookies-from-browser", args)
                self.assertNotIn("--username", args)
                self.assertNotIn("--password", args)
                self.assertNotIn("shell", args)

    def test_audio_command_uses_mp3_extraction(self):
        job_id = str(uuid.uuid4())
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(server, "DATA_ROOT", Path(temp)):
                args, _ = server._command(job_id, "https://soundcloud.com/artist/track", "audio", "720")
        self.assertIn("--extract-audio", args)
        self.assertIn("--audio-format", args)
        self.assertIn("mp3", args)
        self.assertIn("192K", args)

    def test_file_lookup_rejects_unknown_extensions_and_multiple_outputs(self):
        job_id = str(uuid.uuid4())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / job_id
            folder.mkdir()
            (folder / "output.mp4").write_bytes(b"video")
            with patch.object(server, "DATA_ROOT", root):
                self.assertEqual(server.safe_output_file(job_id), folder / "output.mp4")
                (folder / "metadata.json").write_text("{}", encoding="utf-8")
                self.assertEqual(server.safe_output_file(job_id), folder / "output.mp4")
                (folder / "audio.mp3").write_bytes(b"audio")
                self.assertIsNone(server.safe_output_file(job_id))

    def test_file_lookup_rejects_symlinks(self):
        job_id = str(uuid.uuid4())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / job_id
            folder.mkdir()
            external = root / "outside.mp4"
            external.write_bytes(b"not inside the job")
            (folder / "linked.mp4").symlink_to(external)
            with patch.object(server, "DATA_ROOT", root):
                self.assertIsNone(server.safe_output_file(job_id))

    def test_content_types_are_explicit_for_common_media_formats(self):
        self.assertEqual(server.content_type(Path("video.mp4")), "video/mp4")
        self.assertEqual(server.content_type(Path("audio.mp3")), "audio/mpeg")
        self.assertEqual(server.content_type(Path("clip.webm")), "video/webm")
        self.assertEqual(server.content_type(Path("track.flac")), "audio/flac")


if __name__ == "__main__":
    unittest.main()
