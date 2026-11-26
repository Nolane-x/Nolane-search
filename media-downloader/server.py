#!/usr/bin/env python3
"""Private, single-job HTTP service for the Nolane Search media container.

The HTTP listener is reachable only through its owning Durable Object's TCP port.
Every external HTTP(S) request made by yt-dlp is intercepted by the Worker egress
handler; the container starts with enableInternet=false and has no direct DNS.
"""
from __future__ import annotations

import json
import mimetypes
import os
import re
import shutil
import signal
import subprocess
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

PORT = 8080
DATA_ROOT = Path("/data/jobs")
MAX_REQUEST_BYTES = 8_000
MAX_OUTPUT_BYTES = 3 * 1024 * 1024 * 1024
MAX_DURATION_SECONDS = 2 * 60 * 60
JOB_ID_RE = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$", re.I)
ALLOWED_EXTENSIONS = {
    ".mp4", ".m4v", ".mkv", ".webm", ".mov",
    ".mp3", ".m4a", ".opus", ".ogg", ".wav", ".flac",
}
INTERNAL_TOKEN = os.environ.get("NOLANE_INTERNAL_TOKEN", "")

LOCK = threading.RLock()
JOBS: dict[str, dict[str, Any]] = {}
PROCESSES: dict[str, subprocess.Popen[str]] = {}


def valid_job_id(value: str) -> bool:
    return bool(JOB_ID_RE.fullmatch(value))


def safe_output_file(job_id: str) -> Path | None:
    if not valid_job_id(job_id):
        return None
    folder = DATA_ROOT / job_id
    try:
        folder_resolved = folder.resolve(strict=True)
        if folder_resolved.parent != DATA_ROOT.resolve(strict=True) or folder.is_symlink():
            return None
        candidates = [
            item for item in folder_resolved.iterdir()
            if item.is_file() and not item.is_symlink()
            and item.suffix.lower() in ALLOWED_EXTENSIONS
            and not item.name.endswith((".part", ".ytdl"))
        ]
        if len(candidates) != 1:
            return None
        output = candidates[0].resolve(strict=True)
        if output.parent != folder_resolved or output.is_symlink():
            return None
        size = output.stat().st_size
        if size < 1 or size > MAX_OUTPUT_BYTES:
            return None
        return output
    except (FileNotFoundError, OSError):
        return None


def content_type(path: Path) -> str:
    return {
        ".mp4": "video/mp4",
        ".m4v": "video/mp4",
        ".mkv": "video/x-matroska",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".opus": "audio/opus",
        ".ogg": "audio/ogg",
        ".wav": "audio/wav",
        ".flac": "audio/flac",
    }.get(path.suffix.lower(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")


def parse_range(value: str | None, size: int) -> tuple[int, int] | None:
    if not value:
        return (0, size - 1)
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", value.strip())
    if not match or (not match.group(1) and not match.group(2)):
        return None
    if not match.group(1):
        suffix = int(match.group(2))
        if suffix <= 0:
            return None
        return (max(0, size - suffix), size - 1)
    start = int(match.group(1))
    end = int(match.group(2)) if match.group(2) else size - 1
    if start >= size or end < start:
        return None
    return (start, min(end, size - 1))


def _progress_from_line(line: str) -> int | None:
    match = re.search(r"\[download\]\s+(\d+(?:\.\d+)?)%", line)
    if not match:
        return None
    return max(0, min(99, int(float(match.group(1)))))


def _command(job_id: str, url: str, media_format: str, quality: str) -> tuple[list[str], Path]:
    folder = DATA_ROOT / job_id
    folder.mkdir(mode=0o700, parents=True, exist_ok=False)
    output_template = str(folder / "%(id)s.%(ext)s")
    common = [
        "yt-dlp",
        "--ignore-config",
        "--no-playlist",
        "--newline",
        "--no-warnings",
        "--no-call-home",
        "--no-cache-dir",
        "--no-overwrites",
        "--no-continue",
        "--no-write-info-json",
        "--no-write-thumbnail",
        "--no-write-subs",
        "--no-write-auto-subs",
        "--no-write-comments",
        "--no-write-description",
        "--no-embed-metadata",
        "--no-embed-thumbnail",
        "--socket-timeout", "20",
        "--retries", "2",
        "--fragment-retries", "2",
        "--concurrent-fragments", "2",
        "--max-filesize", "1400M",
        "--match-filter", f"duration <= {MAX_DURATION_SECONDS}",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--ffmpeg-location", "/usr/bin/ffmpeg",
        "--output", output_template,
    ]
    if media_format == "audio":
        args = common + [
            "--extract-audio", "--audio-format", "mp3",
            "--audio-quality", "192K",
            "--format", "bestaudio/best",
        ]
    else:
        ceiling = "1080" if quality == "best" else quality
        args = common + [
            "--format", f"bv*[height<={ceiling}]+ba/b[height<={ceiling}]/b",
            "--merge-output-format", "mp4",
        ]
    args.append(url)
    return args, folder


def _run_job(job_id: str, url: str, media_format: str, quality: str) -> None:
    process: subprocess.Popen[str] | None = None
    watchdog: threading.Timer | None = None
    try:
        with LOCK:
            existing = JOBS.get(job_id)
            if not existing or existing.get("status") == "cancelled":
                return
            JOBS[job_id] = {
                "id": job_id, "status": "running", "progress": 0,
                "createdAt": existing.get("createdAt", int(time.time() * 1000)), "error": None,
            }
        args, folder = _command(job_id, url, media_format, quality)

        def limit_file_size() -> None:
            import resource
            resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES))

        process = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            cwd=str(folder),
            close_fds=True,
            start_new_session=True,
            preexec_fn=limit_file_size,
        )
        with LOCK:
            PROCESSES[job_id] = process
        watchdog = threading.Timer(30 * 60, lambda: _kill_process_group(process))
        watchdog.daemon = True
        watchdog.start()

        if process.stdout:
            for line in process.stdout:
                progress = _progress_from_line(line)
                if progress is not None:
                    with LOCK:
                        if job_id in JOBS:
                            JOBS[job_id]["progress"] = progress
                # Do not retain extractor output: it can contain signed source URLs.

        exit_code = process.wait(timeout=30)
        output = safe_output_file(job_id)
        if exit_code != 0 or output is None:
            raise RuntimeError("Extractor did not produce one valid media file.")
        size = output.stat().st_size
        with LOCK:
            JOBS[job_id].update({
                "status": "complete",
                "progress": 100,
                "fileName": "nolane-" + job_id + output.suffix.lower(),
                "extension": output.suffix.lower(),
                "contentType": content_type(output),
                "size": size,
                "completedAt": int(time.time() * 1000),
            })
    except subprocess.TimeoutExpired:
        if process:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        _fail_job(job_id, "timeout")
    except Exception as error:  # noqa: BLE001
        _fail_job(job_id, type(error).__name__)
    finally:
        if watchdog:
            watchdog.cancel()
        with LOCK:
            PROCESSES.pop(job_id, None)
            state = JOBS.get(job_id)
        if state and state.get("status") != "complete":
            shutil.rmtree(DATA_ROOT / job_id, ignore_errors=True)



def _kill_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _fail_job(job_id: str, error_code: str) -> None:
    with LOCK:
        if job_id in JOBS:
            JOBS[job_id].update({
                "status": "failed", "progress": 0,
                "error": error_code, "completedAt": int(time.time() * 1000),
            })


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "NolaneMedia/1"

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def _authorized(self) -> bool:
        supplied = self.headers.get("x-nolane-internal", "")
        return len(supplied) == len(INTERNAL_TOKEN) and __import__("hmac").compare_digest(supplied, INTERNAL_TOKEN)

    def _json(self, value: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("cache-control", "no-store")
        self.send_header("x-content-type-options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _read_json(self) -> dict[str, Any] | None:
        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError:
            return None
        if length < 1 or length > MAX_REQUEST_BYTES:
            return None
        try:
            data = json.loads(self.rfile.read(length))
            return data if isinstance(data, dict) else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

    def _route(self) -> tuple[str, list[str]]:
        parsed = urlsplit(self.path)
        if parsed.scheme or parsed.netloc:
            return "", []
        return parsed.path, [part for part in parsed.path.split("/") if part]

    def do_GET(self) -> None:  # noqa: N802
        self._handle()

    def do_HEAD(self) -> None:  # noqa: N802
        self._handle()

    def do_POST(self) -> None:  # noqa: N802
        self._handle()

    def do_DELETE(self) -> None:  # noqa: N802
        self._handle()

    def _handle(self) -> None:
        if not self._authorized():
            self._json({"error": "unauthorized"}, 401)
            return
        path, parts = self._route()
        if path == "/health" and self.command in ("GET", "HEAD"):
            self._json({"ok": True, "service": "nolane-media-downloader"})
            return
        if path == "/jobs" and self.command == "POST":
            body = self._read_json()
            if not body:
                self._json({"error": "invalid_request"}, 400)
                return
            job_id = str(body.get("id", ""))
            url = body.get("url")
            media_format = body.get("format")
            quality = body.get("quality", "720")
            if not valid_job_id(job_id) or not isinstance(url, str) or len(url) > 2048:
                self._json({"error": "invalid_request"}, 400)
                return
            if media_format not in ("video", "audio") or quality not in ("best", "1080", "720", "480"):
                self._json({"error": "invalid_options"}, 400)
                return
            with LOCK:
                running = any(job.get("status") in ("queued", "running") for job in JOBS.values())
                if running:
                    self._json({"error": "job_in_progress"}, 409)
                    return
                if job_id in JOBS or (DATA_ROOT / job_id).exists():
                    self._json({"error": "job_exists"}, 409)
                    return
                JOBS[job_id] = {"id": job_id, "status": "queued", "progress": 0, "createdAt": int(time.time() * 1000)}
            thread = threading.Thread(
                target=_run_job, args=(job_id, url, media_format, quality),
                name="media-" + job_id[:8], daemon=True,
            )
            thread.start()
            self._json({"id": job_id, "status": "queued"}, 202)
            return
        if len(parts) == 2 and parts[0] == "jobs" and self.command == "GET":
            job_id = parts[1]
            if not valid_job_id(job_id):
                self._json({"error": "not_found"}, 404)
                return
            with LOCK:
                state = JOBS.get(job_id)
                safe_state = dict(state) if state else None
            if not safe_state:
                self._json({"error": "not_found"}, 404)
                return
            self._json(safe_state)
            return
        if len(parts) == 3 and parts[0] == "jobs" and parts[2] == "cancel" and self.command in ("POST", "DELETE"):
            job_id = parts[1]
            if not valid_job_id(job_id):
                self._json({"error": "not_found"}, 404)
                return
            with LOCK:
                process = PROCESSES.get(job_id)
                state = JOBS.get(job_id)
                if not state or state.get("status") not in ("queued", "running"):
                    self._json({"error": "not_cancellable"}, 409)
                    return
                state["status"] = "cancelled"
            if process:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            shutil.rmtree(DATA_ROOT / job_id, ignore_errors=True)
            self._json({"id": job_id, "status": "cancelled"})
            return
        if len(parts) == 2 and parts[0] == "files" and self.command in ("GET", "HEAD"):
            job_id = parts[1]
            path_obj = safe_output_file(job_id)
            if not path_obj:
                self._json({"error": "not_found"}, 404)
                return
            self._serve_file(path_obj)
            return
        self._json({"error": "not_found"}, 404)

    def _serve_file(self, path: Path) -> None:
        size = path.stat().st_size
        selected = parse_range(self.headers.get("range"), size)
        if selected is None:
            self.send_response(416)
            self.send_header("content-range", f"bytes */{size}")
            self.send_header("content-length", "0")
            self.send_header("accept-ranges", "bytes")
            self.send_header("cache-control", "private, no-store")
            self.end_headers()
            return
        start, end = selected
        length = end - start + 1
        partial = self.headers.get("range") is not None
        self.send_response(206 if partial else 200)
        self.send_header("content-type", content_type(path))
        self.send_header("content-length", str(length))
        self.send_header("accept-ranges", "bytes")
        if partial:
            self.send_header("content-range", f"bytes {start}-{end}/{size}")
        self.send_header("content-disposition", f'inline; filename="nolane-media{path.suffix.lower()}"')
        self.send_header("cache-control", "private, no-store")
        self.send_header("x-content-type-options", "nosniff")
        self.send_header("referrer-policy", "no-referrer")
        self.end_headers()
        if self.command == "HEAD":
            return
        try:
            with path.open("rb") as file:
                file.seek(start)
                remaining = length
                while remaining:
                    block = file.read(min(1024 * 1024, remaining))
                    if not block:
                        break
                    self.wfile.write(block)
                    remaining -= len(block)
        except (BrokenPipeError, ConnectionResetError):
            return


class Server(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> None:
    if len(INTERNAL_TOKEN) < 32:
        raise RuntimeError("NOLANE_INTERNAL_TOKEN must contain at least 32 characters.")
    DATA_ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    server = Server(("0.0.0.0", PORT), Handler)
    server.serve_forever(poll_interval=0.25)


if __name__ == "__main__":
    main()
