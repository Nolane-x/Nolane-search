from __future__ import annotations
import hashlib
import socket
import sys
import threading
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
                          "--password", "shell"]:
            self.assertNotIn(forbidden, args)
        self.assertIn("--proxy", args)
        self.assertIn(server.MEDIA_PROXY_URL, args)
        self.assertNotIn("--remote-components", args)

        with tempfile.TemporaryDirectory() as temp:
            best_args = server.build_ytdlp_command(
                job_id="7f3dd2d7-4d41-4ef9-9e18-b4f56a510c26",
                url=url, media_format="video", quality="best",
                output_dir=Path(temp), python_executable="python-test",
                ffmpeg_path="ffmpeg-test", node_path="node-test",
            )
        self.assertIn("bv*[height<=1080]+ba/b[height<=1080]", best_args)

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
            partial = Path(temp) / "jobs" / job_id
            partial.mkdir(parents=True, exist_ok=True)
            (partial / "clip.mp4.part").write_bytes(b"partial")
            restarted = server.MediaNodeStore(Path(temp))
            self.assertEqual(restarted.get_job(job_id, 123)["status"], "failed")
            self.assertFalse((Path(temp) / "jobs" / job_id).exists())
            next_job = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c22"
            restarted.enqueue(next_job, 123, "https://example.org/video", "video", "720", "example.org")
            restarted.claim_next()
            restarted.update_progress(next_job, 42.5)
            self.assertEqual(restarted.get_job(next_job, 123)["progress"], 42.5)

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

    def test_share_renewal_never_outlives_local_file_retention(self):
        with tempfile.TemporaryDirectory() as temp:
            store = server.MediaNodeStore(Path(temp))
            job_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c27"
            start = 2_000_000
            store.enqueue(job_id, 123, "https://example.org/video", "video", "720", "example.org")
            store.claim_next()
            store.complete(job_id, "clip.mp4", "video/mp4", 1234, now=start)
            refreshed_token = "d" * 64
            refreshed_hash = hashlib.sha256(refreshed_token.encode()).hexdigest()
            near_expiry = start + server.FILE_RETENTION_SECONDS - 60
            share = store.renew_share(job_id, 123, refreshed_hash, now=near_expiry)
            self.assertEqual(share["share_expires_at"], start + server.FILE_RETENTION_SECONDS)
            self.assertIsNotNone(store.authorize_share(job_id, 123, refreshed_token, now=near_expiry + 1))
            self.assertIsNone(store.authorize_share(job_id, 123, refreshed_token, now=start + server.FILE_RETENTION_SECONDS + 1))

    def test_output_discovery_rejects_symlinks_and_ambiguous_files(self):
        job_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c21"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / job_id
            folder.mkdir()
            (folder / "clip.mp4").write_bytes(b"media")
            self.assertEqual(server.safe_output_file(root, job_id), folder.resolve() / "clip.mp4")
            (folder / "track.mp3").write_bytes(b"audio")
            self.assertIsNone(server.safe_output_file(root, job_id))
            (folder / "track.mp3").unlink()
            (folder / "clip.mp4").rename(folder / "clip.mkv")
            self.assertIsNone(server.safe_output_file(root, job_id))
            (folder / "clip.mkv").rename(folder / "clip.mp4")
            outside = root / "outside.mp4"
            outside.write_bytes(b"outside")
            (folder / "linked.mp4").symlink_to(outside)
            self.assertIsNone(server.safe_output_file(root, job_id))

    def test_cancelled_job_cannot_be_completed_and_owner_scope_is_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            store = server.MediaNodeStore(Path(temp))
            running_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c24"
            queued_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c23"
            store.enqueue(running_id, 123, "https://example.org/video", "video", "720", "example.org")
            store.enqueue(queued_id, 123, "https://example.org/video", "video", "720", "example.org")
            store.claim_next()
            self.assertIsNone(store.request_cancel(running_id, 456))
            cancelled = store.request_cancel(running_id, 123)
            self.assertTrue(cancelled["cancel_requested"])
            self.assertFalse(store.complete(running_id, "clip.mp4", "video/mp4", 100))
            queued = store.request_cancel(queued_id, 123)
            self.assertEqual(queued["status"], "cancelled")

    def test_local_health_endpoint_requires_internal_token(self):
        with tempfile.TemporaryDirectory() as temp:
            store = server.MediaNodeStore(Path(temp))
            httpd = server.create_http_server(store, "c" * 64, port=0, start_worker=False)
            self.assertTrue(httpd.server_address[0].startswith("127."))
            self.assertEqual(httpd.request_queue_size, 16)
            import threading
            import urllib.error
            import urllib.request
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            job_id = "7f3dd2d7-4d41-4ef9-9e18-b4f56a510c25"
            store.enqueue(job_id, 123, "https://example.org/video", "video", "720", "example.org")
            store.claim_next()
            job_folder = Path(temp) / "jobs" / job_id
            job_folder.mkdir(parents=True, exist_ok=True)
            (job_folder / "clip.mp4").write_bytes(b"media")
            self.assertTrue(store.complete(job_id, "clip.mp4", "video/mp4", 5))
            share_token = "b" * 64
            share_hash = hashlib.sha256(share_token.encode()).hexdigest()
            store.renew_share(job_id, 123, share_hash)

            try:
                url = "http://127.0.0.1:" + str(httpd.server_port) + "/health"
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(url, timeout=2)
                self.assertEqual(error.exception.code, 401)
                request = urllib.request.Request(url, headers={"x-nolane-internal": "c" * 64})
                with urllib.request.urlopen(request, timeout=2) as response:
                    self.assertEqual(response.status, 200)
                    self.assertTrue(server.json.loads(response.read())["ok"])

                file_url = "http://127.0.0.1:" + str(httpd.server_port) + "/internal/share-file/" + job_id
                headers = {
                    "x-nolane-internal": "c" * 64,
                    "x-nolane-owner-id": "123",
                    "x-nolane-share-token": share_token,
                    "Range": "bytes=1-3",
                }
                request = urllib.request.Request(file_url, headers=headers)
                with urllib.request.urlopen(request, timeout=2) as response:
                    self.assertEqual(response.status, 206)
                    self.assertEqual(response.headers.get("Content-Range"), "bytes 1-3/5")
                    self.assertEqual(response.read(), b"edi")
                bad_owner = urllib.request.Request(
                    file_url,
                    headers={**headers, "x-nolane-owner-id": "456"},
                )
                with self.assertRaises(urllib.error.HTTPError) as forbidden:
                    urllib.request.urlopen(bad_owner, timeout=2)
                self.assertEqual(forbidden.exception.code, 404)

                invalid_range = urllib.request.Request(
                    file_url,
                    headers={**headers, "Range": "bytes=50-60"},
                )
                with self.assertRaises(urllib.error.HTTPError) as unsatisfied:
                    urllib.request.urlopen(invalid_range, timeout=2)
                self.assertEqual(unsatisfied.exception.code, 416)
                self.assertEqual(unsatisfied.exception.headers.get("Content-Range"), "bytes */5")

                head = urllib.request.Request(
                    file_url,
                    headers={**headers, "Range": "bytes=0-0"},
                    method="HEAD",
                )
                with urllib.request.urlopen(head, timeout=2) as response:
                    self.assertEqual(response.status, 206)
                    self.assertEqual(response.headers.get("Content-Length"), "1")
                    self.assertEqual(response.read(), b"")
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=2)


    def test_public_dns_results_are_validated_as_a_complete_set(self):
        public_resolver = lambda host: ["93.184.216.34", "2606:4700:4700::1111"]
        self.assertEqual(
            server.resolve_public_addresses("example.org", resolver=public_resolver, is_public_ip=server.is_public_ip),
            ["2606:4700:4700::1111", "93.184.216.34"],
        )
        mixed_resolver = lambda host: ["93.184.216.34", "169.254.169.254"]
        with self.assertRaises(server.EgressProxyError):
            server.resolve_public_addresses("example.org", resolver=mixed_resolver, is_public_ip=server.is_public_ip)

    def test_upstream_connection_uses_the_pinned_numeric_address(self):
        calls = []
        sentinel = object()
        result = server.connect_public_host(
            "example.org", 443,
            resolver=lambda host: ["93.184.216.34"],
            is_public_ip=server.is_public_ip,
            connector=lambda address, timeout: calls.append((address, timeout)) or sentinel,
        )
        self.assertIs(result, sentinel)
        self.assertEqual(calls[0][0], ("93.184.216.34", 443))
        self.assertEqual(calls[0][1], 15)

    def test_upstream_connection_never_attempts_a_mixed_private_dns_answer(self):
        calls = []
        with self.assertRaises(server.EgressProxyError):
            server.connect_public_host(
                "example.org", 443,
                resolver=lambda host: ["93.184.216.34", "10.1.2.3"],
                is_public_ip=server.is_public_ip,
                connector=lambda address, timeout: calls.append(address),
            )
        self.assertEqual(calls, [])

    def test_local_egress_proxy_rejects_private_https_connect_targets(self):
        proxy = server.create_egress_proxy(
            host="127.0.0.1", port=0,
            resolver=lambda host: ["127.0.0.1"],
            normalize_url=server.normalize_source_url,
            is_public_ip=server.is_public_ip,
        )
        thread = threading.Thread(target=proxy.serve_forever, daemon=True)
        thread.start()
        try:
            with socket.create_connection(proxy.server_address, timeout=2) as client:
                client.sendall(
                    b"CONNECT example.org:443 HTTP/1.1\\r\\n"
                    b"Host: example.org:443\\r\\n\\r\\n"
                )
                response = client.recv(2048)
                self.assertIn(b"403", response.split(b"\\r\\n", 1)[0])
        finally:
            proxy.shutdown()
            proxy.server_close()
            thread.join(timeout=2)

    def test_local_egress_proxy_rejects_private_http_destinations(self):
        proxy = server.create_egress_proxy(
            host="127.0.0.1", port=0,
            resolver=lambda host: ["192.168.1.1"],
            normalize_url=server.normalize_source_url,
            is_public_ip=server.is_public_ip,
        )
        thread = threading.Thread(target=proxy.serve_forever, daemon=True)
        thread.start()
        try:
            with socket.create_connection(proxy.server_address, timeout=2) as client:
                client.sendall(
                    b"GET http://example.org/video HTTP/1.1\\r\\n"
                    b"Host: example.org\\r\\n\\r\\n"
                )
                response = client.recv(2048)
                self.assertIn(b"403", response.split(b"\\r\\n", 1)[0])
        finally:
            proxy.shutdown()
            proxy.server_close()
            thread.join(timeout=2)

    def test_proxy_factory_binds_only_to_loopback(self):
        proxy = server.create_egress_proxy(
            host="127.0.0.1", port=0,
            resolver=lambda host: ["93.184.216.34"],
            normalize_url=server.normalize_source_url,
            is_public_ip=server.is_public_ip,
        )
        try:
            self.assertEqual(proxy.server_address[0], "127.0.0.1")
        finally:
            proxy.server_close()


    def test_local_egress_proxy_forwards_http_to_the_pinned_ip_only(self):
        class FakeUpstream:
            def __init__(self):
                self.sent = []
                self.responses = [
                    b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok",
                    b"",
                ]
            def settimeout(self, value):
                pass
            def sendall(self, data):
                self.sent.append(data)
            def recv(self, size):
                return self.responses.pop(0)
            def close(self):
                pass

        upstream = FakeUpstream()
        connect_calls = []
        proxy = server.create_egress_proxy(
            host="127.0.0.1", port=0,
            resolver=lambda host: ["93.184.216.34"],
            normalize_url=server.normalize_source_url,
            is_public_ip=server.is_public_ip,
            connector=lambda address, timeout: connect_calls.append((address, timeout)) or upstream,
        )
        thread = threading.Thread(target=proxy.serve_forever, daemon=True)
        thread.start()
        try:
            with socket.create_connection(proxy.server_address, timeout=2) as client:
                client.settimeout(2)
                client.sendall(
                    b"GET http://example.org/watch?v=abc HTTP/1.1\r\n"
                    b"Host: example.org\r\n"
                    b"Accept: */*\r\n"
                    b"Cookie: session=secret\r\n"
                    b"Authorization: Bearer secret\r\n"
                    b"X-Forwarded-For: 127.0.0.1\r\n\r\n"
                )
                received = b""
                while True:
                    chunk = client.recv(4096)
                    if not chunk:
                        break
                    received += chunk
            self.assertIn(b"HTTP/1.1 200 OK", received)
            self.assertTrue(received.endswith(b"ok"))
            self.assertEqual(connect_calls[0][0], ("93.184.216.34", 80))
            forwarded = b"".join(upstream.sent)
            self.assertIn(b"GET /watch?v=abc HTTP/1.1", forwarded)
            self.assertIn(b"Host: example.org", forwarded)
            self.assertIn(b"Connection: close", forwarded)
            self.assertNotIn(b"Cookie:", forwarded)
            self.assertNotIn(b"Authorization:", forwarded)
            self.assertNotIn(b"X-Forwarded-For:", forwarded)
        finally:
            proxy.shutdown()
            proxy.server_close()
            thread.join(timeout=2)

    def test_local_egress_proxy_tunnels_https_without_re_resolving_hostnames(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        upstream_address = listener.getsockname()
        received_from_client = []
        def accept_and_echo():
            accepted, _ = listener.accept()
            with accepted:
                accepted.settimeout(2)
                received_from_client.append(accepted.recv(32))
                accepted.sendall(b"tls-response")
                accepted.shutdown(socket.SHUT_WR)
        upstream_thread = threading.Thread(target=accept_and_echo, daemon=True)
        upstream_thread.start()
        connect_calls = []
        proxy = server.create_egress_proxy(
            host="127.0.0.1", port=0,
            resolver=lambda host: ["93.184.216.34"],
            normalize_url=server.normalize_source_url,
            is_public_ip=server.is_public_ip,
            connector=lambda address, timeout: (
                connect_calls.append((address, timeout))
                or socket.create_connection(upstream_address, timeout=timeout)
            ),
        )
        proxy_thread = threading.Thread(target=proxy.serve_forever, daemon=True)
        proxy_thread.start()
        try:
            with socket.create_connection(proxy.server_address, timeout=2) as client:
                client.settimeout(2)
                client.sendall(
                    b"CONNECT example.org:443 HTTP/1.1\r\n"
                    b"Host: example.org:443\r\n\r\n"
                )
                handshake = client.recv(1024)
                self.assertIn(b"200 Connection Established", handshake)
                client.sendall(b"tls-client-data")
                self.assertEqual(client.recv(1024), b"tls-response")
            upstream_thread.join(timeout=2)
            self.assertEqual(received_from_client, [b"tls-client-data"])
            self.assertEqual(connect_calls[0][0], ("93.184.216.34", 443))
        finally:
            proxy.shutdown()
            proxy.server_close()
            proxy_thread.join(timeout=2)
            listener.close()
            upstream_thread.join(timeout=2)

    def test_instance_lock_rejects_a_second_node_in_the_same_process(self):
        with tempfile.TemporaryDirectory() as temp:
            lock_path = Path(temp) / "media-node.lock"
            first = server.InstanceLock(lock_path)
            try:
                with self.assertRaises(server.InstanceAlreadyRunning):
                    server.InstanceLock(lock_path)
            finally:
                first.close()
            second = server.InstanceLock(lock_path)
            second.close()

if __name__ == "__main__":
    unittest.main()
