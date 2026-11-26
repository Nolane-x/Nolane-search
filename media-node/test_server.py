from __future__ import annotations
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import server

class MediaNodePolicyTests(unittest.TestCase):
    def test_only_globally_routable_addresses_are_allowed(self):
        blocked = [
            "0.0.0.0", "10.0.0.1", "100.64.0.1", "127.0.0.1",
            "169.254.169.254", "172.16.0.1", "192.168.1.1",
            "192.0.2.1", "198.18.0.1", "203.0.113.1", "224.0.0.1",
            "::", "::1", "fc00::1", "fe80::1", "ff02::1",
            "::ffff:192.168.1.1", "64:ff9b::a00:1", "2001:db8::1",
            "2001::1", "2002:c000:0201::1",
        ]
        for address in blocked:
            with self.subTest(address=address):
                self.assertFalse(server.is_public_ip(address))
        for address in ["1.1.1.1", "8.8.8.8", "93.184.216.34",
                        "2001:4860:4860::8888", "2606:4700:4700::1111"]:
            with self.subTest(address=address):
                self.assertTrue(server.is_public_ip(address))

    def test_source_url_requires_public_http_host_and_all_public_dns_answers(self):
        resolver = lambda host: ["93.184.216.34"]
        normalized, host = server.normalize_source_url(
            "  https://Example.org/video?id=123  ", resolver=resolver
        )
        self.assertEqual(normalized, "https://example.org/video?id=123")
        self.assertEqual(host, "example.org")
        private_resolver = lambda host: ["93.184.216.34", "10.0.0.4"]
        with self.assertRaises(server.SourceUrlError):
            server.normalize_source_url("https://example.org/video", resolver=private_resolver)
        for value in [
            "file:///etc/passwd", "ftp://example.org/file",
            "https://user:pass@example.org/video", "https://example.org:8443/video",
            "https://example.org/video#fragment", "https://127.0.0.1/video",
            "http://2130706433/video", "http://0x7f000001/video",
            "https://localhost/video", "https://nas.local/video",
            "https://metadata.google.internal/latest",
        ]:
            with self.subTest(value=value):
                with self.assertRaises(server.SourceUrlError):
                    server.normalize_source_url(value, resolver=resolver)

    def test_byte_range_supports_normal_suffix_and_open_ended_ranges(self):
        self.assertEqual(server.parse_range(None, 100), (0, 99))
        self.assertEqual(server.parse_range("bytes=10-19", 100), (10, 19))
        self.assertEqual(server.parse_range("bytes=10-", 100), (10, 99))
        self.assertEqual(server.parse_range("bytes=-10", 100), (90, 99))
        self.assertIsNone(server.parse_range("bytes=100-", 100))
        self.assertIsNone(server.parse_range("bytes=20-10", 100))
        self.assertIsNone(server.parse_range("bytes=0-1,4-5", 100))
        self.assertIsNone(server.parse_range("items=0-1", 100))

    def test_downloader_command_is_argv_only_and_has_no_auth_or_proxy_inputs(self):
        url = "https://www.youtube.com/watch?v=abc123"
        with tempfile.TemporaryDirectory() as temp:
            args = server.build_ytdlp_command(
                job_id="7f3dd2d7-4d41-4ef9-9e18-b4f56a510c21",
                url=url, media_format="video", quality="720",
                output_dir=Path(temp), python_executable="python-test",
                ffmpeg_path="ffmpeg-test", node_path="node-test",
            )
        self.assertEqual(args[0:2], ["python-test", "-m"])
        self.assertEqual(args[-1], url)
        for flag in ["--no-playlist", "--ignore-config", "--max-filesize",
                     "--match-filter", "--js-runtimes"]:
            self.assertIn(flag, args)
        for forbidden in ["--cookies", "--cookies-from-browser", "--username",
                          "--password", "--proxy", "shell"]:
            self.assertNotIn(forbidden, args)

    def test_store_persists_jobs_and_keeps_owner_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            store = server.MediaNodeStore(Path(temp))
            job_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c21"
            store.enqueue(job_id, 123, "https://example.org/video", "video", "720", "example.org")
            self.assertEqual(store.get_job(job_id, 123)["status"], "queued")
            self.assertIsNone(store.get_job(job_id, 456))
            claimed = store.claim_next()
            self.assertEqual(claimed["job_id"], job_id)
            self.assertEqual(claimed["status"], "running")
            restarted = server.MediaNodeStore(Path(temp))
            self.assertEqual(restarted.get_job(job_id, 123)["status"], "running")
            restarted.update_progress(job_id, 42.5)
            self.assertEqual(restarted.get_job(job_id, 123)["progress"], 42.5)

    def test_store_bounds_the_owner_queue(self):
        with tempfile.TemporaryDirectory() as temp:
            store = server.MediaNodeStore(Path(temp), max_owner_jobs=3)
            for index in range(3):
                job_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c2" + str(index)
                store.enqueue(job_id, 123, "https://example.org/video", "video", "720", "example.org")
            with self.assertRaises(server.QueueFull):
                store.enqueue("7f3dd2d7-4d41-4ef9-9e18-b4f56a510c2a",
                              123, "https://example.org/video", "video", "720", "example.org")

    def test_share_token_is_hashed_expires_and_can_be_revoked(self):
        with tempfile.TemporaryDirectory() as temp:
            store = server.MediaNodeStore(Path(temp))
            job_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c21"
            store.enqueue(job_id, 123, "https://example.org/video", "video", "720", "example.org")
            store.claim_next()
            store.complete(job_id, "clip.mp4", "video/mp4", 1234, now=1_000_000)
            token = "a" * 64
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            share = store.renew_share(job_id, 123, token_hash, now=1_000_000)
            self.assertEqual(share["share_expires_at"], 1_000_000 + server.SHARE_TTL_SECONDS)
            self.assertEqual(store.authorize_share(job_id, 123, token, now=1_000_001)["file_name"], "clip.mp4")
            self.assertIsNone(store.authorize_share(job_id, 123, "b" * 64, now=1_000_001))
            self.assertIsNone(store.authorize_share(job_id, 123, token, now=1_000_000 + server.SHARE_TTL_SECONDS + 1))
            self.assertTrue(store.revoke(job_id, 123))
            self.assertIsNone(store.authorize_share(job_id, 123, token, now=1_000_002))

    def test_output_discovery_rejects_symlinks_and_ambiguous_files(self):
        job_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c21"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / job_id
            folder.mkdir()
            (folder / "clip.mp4").write_bytes(b"media")
            self.assertEqual(server.safe_output_file(root, job_id), folder / "clip.mp4")
            (folder / "track.mp3").write_bytes(b"audio")
            self.assertIsNone(server.safe_output_file(root, job_id))
            (folder / "track.mp3").unlink()
            outside = root / "outside.mp4"
            outside.write_bytes(b"outside")
            (folder / "linked.mp4").symlink_to(outside)
            self.assertIsNone(server.safe_output_file(root, job_id))

    def test_local_health_endpoint_requires_internal_token(self):
        with tempfile.TemporaryDirectory() as temp:
            store = server.MediaNodeStore(Path(temp))
            httpd = server.create_http_server(store, "c" * 64, port=0, start_worker=False)
            import threading
            import urllib.error
            import urllib.request
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                url = "http://127.0.0.1:" + str(httpd.server_port) + "/health"
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(url, timeout=2)
                self.assertEqual(error.exception.code, 401)
                request = urllib.request.Request(url, headers={"x-nolane-internal": "c" * 64})
                with urllib.request.urlopen(request, timeout=2) as response:
                    self.assertEqual(response.status, 200)
                    self.assertTrue(server.json.loads(response.read())["ok"])
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=2)

if __name__ == "__main__":
    unittest.main()
