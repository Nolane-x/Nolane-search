from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import os
import queue
import re
import shutil
import signal
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import unicodedata
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import quote, urlsplit, urlunsplit

DATA_ROOT = Path(os.environ.get("NOLANE_MEDIA_DATA_DIR", Path(__file__).with_name("data"))).resolve()
DB_PATH = DATA_ROOT / "media-node.sqlite3"
PORT = int(os.environ.get("NOLANE_MEDIA_PORT", "8765"))
MAX_BODY_BYTES = 8 * 1024
MAX_OUTPUT_BYTES = 3 * 1024 * 1024 * 1024
MAX_EXTRACTOR_FILE_BYTES = 1400 * 1024 * 1024
MAX_SOURCE_DURATION_SECONDS = 2 * 60 * 60
JOB_TIMEOUT_SECONDS = 30 * 60
SHARE_TTL_SECONDS = 12 * 60 * 60
FILE_RETENTION_SECONDS = 12 * 60 * 60
MAX_OWNER_JOBS = 3
JOB_ID_RE = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$", re.I)
TOKEN_RE = re.compile(r"^[a-f0-9]{64}$", re.I)
HOST_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
ALLOWED_EXTENSIONS = {".mp4", ".webm", ".mkv", ".mov", ".mp3", ".m4a", ".opus", ".ogg", ".wav", ".flac"}
RESERVED_SUFFIXES = (
    ".localhost", ".local", ".internal", ".test", ".example", ".invalid",
    ".onion", ".arpa", ".home", ".lan", ".corp",
)

class SourceUrlError(ValueError):
    pass

class QueueFull(RuntimeError):
    pass

def is_public_ip(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value.split("%", 1)[0])
    except ValueError:
        return False
    if isinstance(address, ipaddress.IPv6Address):
        if address.ipv4_mapped is not None:
            return False
        special_v6 = (
            ipaddress.ip_network("64:ff9b::/96"),
            ipaddress.ip_network("2001::/23"),
            ipaddress.ip_network("2002::/16"),
        )
        if any(address in network for network in special_v6):
            return False
    return bool(address.is_global)

def resolve_public_candidates(host: str) -> list[str]:
    try:
        answers = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError as error:
        raise SourceUrlError("The source host could not be resolved.") from error
    addresses = sorted({item[4][0].split("%", 1)[0] for item in answers})
    if not addresses:
        raise SourceUrlError("The source host has no address records.")
    return addresses

def _looks_like_numeric_host(host: str) -> bool:
    try:
        socket.inet_aton(host)
        return True
    except OSError:
        pass
    if re.fullmatch(r"(?:0x[0-9a-f]+|[0-9]+)(?:\.(?:0x[0-9a-f]+|[0-9]+))*", host, re.I):
        return True
    return False

def normalize_source_url(
    value: object,
    resolver: Callable[[str], list[str]] = resolve_public_candidates,
) -> tuple[str, str]:
    if not isinstance(value, str):
        raise SourceUrlError("Enter a public video or audio page URL.")
    normalized = unicodedata.normalize("NFKC", value).strip()
    if len(normalized) < 12 or len(normalized) > 2048 or any(ord(ch) < 32 or ord(ch) == 127 for ch in normalized):
        raise SourceUrlError("The source URL length or characters are invalid.")
    try:
        parsed = urlsplit(normalized)
        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https"):
            raise SourceUrlError("Only public HTTP or HTTPS URLs are supported.")
        if parsed.username is not None or parsed.password is not None or "@" in parsed.netloc:
            raise SourceUrlError("URLs must not contain account credentials.")
        if parsed.fragment:
            raise SourceUrlError("URL fragments are not supported.")
        explicit_port = parsed.port
        if explicit_port is not None and explicit_port != (443 if scheme == "https" else 80):
            raise SourceUrlError("Custom network ports are not supported.")
        raw_host = parsed.hostname or ""
        host = raw_host.rstrip(".").lower().encode("idna").decode("ascii")
    except (ValueError, UnicodeError) as error:
        if isinstance(error, SourceUrlError):
            raise
        raise SourceUrlError("The source URL is invalid.") from error
    if not host or len(host) > 253 or "." not in host or ":" in host or _looks_like_numeric_host(host):
        raise SourceUrlError("IP literals and single-label hosts are not supported.")
    if host == "localhost" or any(host.endswith(suffix) for suffix in RESERVED_SUFFIXES):
        raise SourceUrlError("Private and special-use hostnames are not supported.")
    labels = host.split(".")
    if not all(1 <= len(label) <= 63 and HOST_LABEL_RE.fullmatch(label) for label in labels):
        raise SourceUrlError("The source hostname is invalid.")
    if labels[-1].isdigit() or labels[-1].startswith("0x"):
        raise SourceUrlError("Numeric hostnames are not supported.")
    addresses = resolver(host)
    if not addresses or any(not is_public_ip(address) for address in addresses):
        raise SourceUrlError("Every resolved address must be globally routable.")
    netloc = host
    path = parsed.path or "/"
    return urlunsplit((scheme, netloc, path, parsed.query, "")), host

def parse_range(header: str | None, size: int) -> tuple[int, int] | None:
    if size <= 0:
        return None
    if header is None:
        return (0, size - 1)
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", header.strip(), re.I)
    if not match or (not match.group(1) and not match.group(2)):
        return None
    first, last = match.groups()
    if not first:
        suffix = int(last)
        if suffix <= 0:
            return None
        return (max(0, size - suffix), size - 1)
    start = int(first)
    end = int(last) if last else size - 1
    if start >= size or end < start:
        return None
    return (start, min(end, size - 1))

def build_ytdlp_command(
    job_id: str,
    url: str,
    media_format: str,
    quality: str,
    output_dir: Path,
    python_executable: str | None = None,
    ffmpeg_path: str | None = None,
    node_path: str | None = None,
) -> list[str]:
    if not JOB_ID_RE.fullmatch(job_id):
        raise ValueError("Invalid job ID.")
    python_executable = python_executable or sys.executable
    ffmpeg_path = ffmpeg_path or shutil.which("ffmpeg") or "ffmpeg"
    node_path = node_path or shutil.which("node") or "node"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(title).120B [%(id)s].%(ext)s")
    args = [
        python_executable, "-m", "yt_dlp",
        "--ignore-config", "--no-playlist", "--no-cache-dir",
        "--socket-timeout", "20", "--retries", "2", "--fragment-retries", "2",
        "--concurrent-fragments", "2", "--newline", "--no-warnings",
        "--windows-filenames", "--restrict-filenames",
        "--max-filesize", str(MAX_EXTRACTOR_FILE_BYTES),
        "--match-filter", "duration <= " + str(MAX_SOURCE_DURATION_SECONDS),
        "--progress-template", "download:PROGRESS:%(progress._percent_str)s",
        "--ffmpeg-location", ffmpeg_path,
        "--js-runtimes", "node:" + node_path,
        "--remote-components", "ejs:github",
        "--output", output_template,
    ]
    if media_format == "audio":
        args.extend(["--extract-audio", "--audio-format", "mp3", "--audio-quality", "192K"])
    elif media_format == "video":
        if quality == "best":
            format_expression = "bv*+ba/b"
        else:
            height = int(quality)
            format_expression = "bv*[height<=" + str(height) + "]+ba/b[height<=" + str(height) + "]"
        args.extend(["--format", format_expression, "--merge-output-format", "mp4", "--remux-video", "mp4"])
    else:
        raise ValueError("Unsupported media format.")
    args.append(url)
    return args

def safe_output_file(root: Path, job_id: str) -> Path | None:
    if not JOB_ID_RE.fullmatch(job_id):
        return None
    root_resolved = root.resolve()
    folder = root_resolved / job_id
    try:
        if folder.is_symlink() or not folder.is_dir() or folder.resolve() != folder:
            return None
        outputs: list[Path] = []
        for candidate in folder.iterdir():
            if candidate.is_symlink() or not candidate.is_file():
                continue
            if candidate.suffix.lower() in ALLOWED_EXTENSIONS:
                if candidate.resolve().parent != folder:
                    return None
                outputs.append(candidate)
        if len(outputs) != 1:
            return None
        return outputs[0]
    except OSError:
        return None

class MediaNodeStore:
    def __init__(self, root: Path, max_owner_jobs: int = MAX_OWNER_JOBS):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "jobs").mkdir(exist_ok=True)
        self.db_path = self.root / "media-node.sqlite3"
        self.max_owner_jobs = max(1, int(max_owner_jobs))
        self._initialize()
        self.recover_interrupted()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    owner_id INTEGER NOT NULL,
                    source_url TEXT NOT NULL,
                    source_host TEXT NOT NULL,
                    media_format TEXT NOT NULL,
                    quality TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    started_at REAL,
                    completed_at REAL,
                    cleanup_at REAL,
                    file_name TEXT,
                    content_type TEXT,
                    size INTEGER,
                    share_token_hash TEXT,
                    share_expires_at REAL,
                    cancel_requested INTEGER NOT NULL DEFAULT 0,
                    error TEXT
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS jobs_owner_queue ON jobs(owner_id, status, created_at)")
            db.execute("CREATE INDEX IF NOT EXISTS jobs_cleanup ON jobs(cleanup_at)")

    @staticmethod
    def _job_view(row: sqlite3.Row | None) -> dict | None:
        if row is None:
            return None
        return {
            "job_id": row["job_id"], "owner_id": row["owner_id"],
            "source_host": row["source_host"], "media_format": row["media_format"],
            "quality": row["quality"], "status": row["status"],
            "progress": float(row["progress"]), "created_at": row["created_at"],
            "updated_at": row["updated_at"], "started_at": row["started_at"],
            "completed_at": row["completed_at"], "cleanup_at": row["cleanup_at"],
            "file_name": row["file_name"], "content_type": row["content_type"],
            "size": row["size"], "share_expires_at": row["share_expires_at"],
            "cancel_requested": bool(row["cancel_requested"]), "error": row["error"],
        }

    def enqueue(self, job_id: str, owner_id: int, source_url: str, media_format: str, quality: str, source_host: str) -> None:
        if not JOB_ID_RE.fullmatch(job_id) or not isinstance(owner_id, int) or owner_id <= 0:
            raise ValueError("Invalid job identity.")
        if media_format not in ("video", "audio") or quality not in ("best", "1080", "720", "480"):
            raise ValueError("Invalid media selection.")
        now = time.time()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            count = db.execute(
                "SELECT COUNT(*) AS n FROM jobs WHERE owner_id=? AND status IN ('queued','running')",
                (owner_id,),
            ).fetchone()["n"]
            if count >= self.max_owner_jobs:
                db.execute("ROLLBACK")
                raise QueueFull("The owner's Media Node queue is full.")
            try:
                db.execute("""
                    INSERT INTO jobs(
                        job_id, owner_id, source_url, source_host, media_format, quality,
                        status, progress, created_at, updated_at
                    ) VALUES(?,?,?,?,?,?,'queued',0,?,?)
                """, (job_id, owner_id, source_url, source_host, media_format, quality, now, now))
            except sqlite3.IntegrityError as error:
                db.execute("ROLLBACK")
                raise ValueError("Job already exists.") from error
            db.execute("COMMIT")

    def claim_next(self) -> dict | None:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY created_at LIMIT 1").fetchone()
            if row is None:
                db.execute("COMMIT")
                return None
            now = time.time()
            changed = db.execute(
                "UPDATE jobs SET status='running', started_at=?, updated_at=? WHERE job_id=? AND status='queued'",
                (now, now, row["job_id"]),
            ).rowcount
            fresh = db.execute("SELECT * FROM jobs WHERE job_id=?", (row["job_id"],)).fetchone() if changed else None
            db.execute("COMMIT")
            return self._job_view(fresh)

    def get_job(self, job_id: str, owner_id: int) -> dict | None:
        if not JOB_ID_RE.fullmatch(job_id):
            return None
        with self._connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=? AND owner_id=?", (job_id, owner_id)).fetchone()
            result = self._job_view(row)
            if result is not None:
                raw = db.execute("SELECT source_url FROM jobs WHERE job_id=?", (job_id,)).fetchone()
                result["source_url"] = raw["source_url"] if raw else ""
            return result

    def get_source_url(self, job_id: str) -> str | None:
        with self._connect() as db:
            row = db.execute("SELECT source_url FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            return row["source_url"] if row else None

    def update_progress(self, job_id: str, progress: float) -> None:
        now = time.time()
        bounded = max(0.0, min(100.0, float(progress)))
        with self._connect() as db:
            db.execute(
                "UPDATE jobs SET progress=?, updated_at=? WHERE job_id=? AND status='running' AND cancel_requested=0",
                (bounded, now, job_id),
            )

    def complete(self, job_id: str, file_name: str, content_type: str, size: int, now: float | None = None) -> bool:
        moment = time.time() if now is None else float(now)
        if size < 1 or size > MAX_OUTPUT_BYTES:
            return False
        with self._connect() as db:
            changed = db.execute("""
                UPDATE jobs SET status='complete', progress=100, updated_at=?, completed_at=?,
                    cleanup_at=?, file_name=?, content_type=?, size=?, error=NULL
                WHERE job_id=? AND status='running' AND cancel_requested=0
            """, (moment, moment, moment + FILE_RETENTION_SECONDS, file_name, content_type, size, job_id)).rowcount
            return changed == 1

    def fail(self, job_id: str, safe_error: str = "The media source could not be downloaded.") -> None:
        with self._connect() as db:
            db.execute("""
                UPDATE jobs SET status=CASE WHEN cancel_requested=1 THEN 'cancelled' ELSE 'failed' END,
                    updated_at=?, error=? WHERE job_id=? AND status='running'
            """, (time.time(), safe_error[:180], job_id))

    def mark_cancelled(self, job_id: str) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE jobs SET status='cancelled', updated_at=?, cancel_requested=1 WHERE job_id=? AND status IN ('queued','running')",
                (time.time(), job_id),
            )

    def request_cancel(self, job_id: str, owner_id: int) -> dict | None:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE job_id=? AND owner_id=?", (job_id, owner_id)).fetchone()
            if row is None:
                db.execute("COMMIT")
                return None
            if row["status"] == "queued":
                db.execute(
                    "UPDATE jobs SET status='cancelled', cancel_requested=1, updated_at=? WHERE job_id=?",
                    (time.time(), job_id),
                )
            elif row["status"] == "running":
                db.execute(
                    "UPDATE jobs SET cancel_requested=1, updated_at=? WHERE job_id=?",
                    (time.time(), job_id),
                )
            fresh = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            db.execute("COMMIT")
            return self._job_view(fresh)

    def renew_share(self, job_id: str, owner_id: int, token_hash: str, now: float | None = None) -> dict | None:
        if not TOKEN_RE.fullmatch(token_hash):
            return None
        moment = time.time() if now is None else float(now)
        expires = moment + SHARE_TTL_SECONDS
        with self._connect() as db:
            changed = db.execute("""
                UPDATE jobs SET share_token_hash=?, share_expires_at=?, updated_at=?
                WHERE job_id=? AND owner_id=? AND status='complete' AND cleanup_at>?
            """, (token_hash.lower(), expires, moment, job_id, owner_id, moment)).rowcount
            if changed != 1:
                return None
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            view = self._job_view(row)
            return view

    def authorize_share(self, job_id: str, owner_id: int, token: str, now: float | None = None) -> dict | None:
        if not TOKEN_RE.fullmatch(token):
            return None
        moment = time.time() if now is None else float(now)
        with self._connect() as db:
            row = db.execute("""
                SELECT * FROM jobs WHERE job_id=? AND owner_id=? AND status='complete'
                    AND share_token_hash IS NOT NULL AND share_expires_at>? AND cleanup_at>?
            """, (job_id, owner_id, moment, moment)).fetchone()
            if row is None:
                return None
            supplied = hashlib.sha256(token.encode("ascii")).hexdigest()
            if not hmac.compare_digest(supplied, row["share_token_hash"]):
                return None
            return self._job_view(row)

    def revoke(self, job_id: str, owner_id: int) -> bool:
        with self._connect() as db:
            changed = db.execute("""
                UPDATE jobs SET share_token_hash=NULL, share_expires_at=NULL, updated_at=?
                WHERE job_id=? AND owner_id=? AND share_token_hash IS NOT NULL
            """, (time.time(), job_id, owner_id)).rowcount
            return changed == 1

    def recover_interrupted(self) -> None:
        with self._connect() as db:
            db.execute("""
                UPDATE jobs SET status='failed', updated_at=?, error='Media Node restarted while this task was running.'
                WHERE status='running'
            """, (time.time(),))

    def expire_due(self) -> None:
        now = time.time()
        with self._connect() as db:
            rows = db.execute(
                "SELECT job_id FROM jobs WHERE cleanup_at IS NOT NULL AND cleanup_at<=? AND status='complete'",
                (now,),
            ).fetchall()
            old_ids = [row["job_id"] for row in rows]
            for job_id in old_ids:
                shutil.rmtree(self.root / "jobs" / job_id, ignore_errors=True)
            if old_ids:
                db.executemany(
                    "UPDATE jobs SET status='expired', share_token_hash=NULL, share_expires_at=NULL, updated_at=? WHERE job_id=?",
                    [(now, job_id) for job_id in old_ids],
                )
            db.execute("DELETE FROM jobs WHERE updated_at<? AND status IN ('failed','cancelled','expired')", (now - 7 * 86400,))

def _safe_process_environment(job_dir: Path, ffmpeg_path: str, node_path: str) -> dict[str, str]:
    allowed_names = (
        "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "USERPROFILE",
        "APPDATA", "LOCALAPPDATA", "PROGRAMDATA",
    )
    result = {name: os.environ[name] for name in allowed_names if os.environ.get(name)}
    search_dirs = [str(Path(ffmpeg_path).parent), str(Path(node_path).parent)]
    result["PATH"] = os.pathsep.join(search_dirs + [os.environ.get("PATH", "")])
    result["HOME"] = str(job_dir)
    result["TMPDIR"] = str(job_dir)
    result["TEMP"] = str(job_dir)
    result["TMP"] = str(job_dir)
    result["PYTHONNOUSERSITE"] = "1"
    result["PYTHONUTF8"] = "1"
    return result

def _directory_size(path: Path) -> int:
    total = 0
    try:
        for item in path.iterdir():
            if item.is_symlink():
                continue
            if item.is_file():
                total += item.stat().st_size
    except OSError:
        pass
    return total

def _terminate_process_tree(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=8, check=False,
            )
        else:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        try:
            process.kill()
        except OSError:
            pass

class MediaWorker:
    def __init__(self, store: MediaNodeStore):
        self.store = store
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, name="nolane-media-worker", daemon=True)
        self.process_lock = threading.Lock()
        self.processes: dict[str, subprocess.Popen] = {}

    def start(self) -> None:
        if not self.thread.is_alive():
            self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        with self.process_lock:
            active = list(self.processes.values())
        for process in active:
            _terminate_process_tree(process)
        if self.thread.is_alive():
            self.thread.join(timeout=5)

    def cancel(self, job_id: str) -> None:
        with self.process_lock:
            process = self.processes.get(job_id)
        if process is not None:
            _terminate_process_tree(process)

    def _run(self) -> None:
        next_cleanup = 0.0
        while not self.stop_event.is_set():
            job = self.store.claim_next()
            if job is None:
                if time.time() >= next_cleanup:
                    self.store.expire_due()
                    next_cleanup = time.time() + 60
                self.stop_event.wait(0.75)
                continue
            self._process(job)

    def _process(self, job: dict) -> None:
        job_id = job["job_id"]
        job_dir = self.store.root / "jobs" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        url = self.store.get_source_url(job_id)
        if not url:
            self.store.fail(job_id)
            return
        ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
        node = shutil.which("node") or "node"
        command = build_ytdlp_command(
            job_id, url, job["media_format"], job["quality"],
            job_dir, sys.executable, ffmpeg, node,
        )
        kwargs = {
            "cwd": str(job_dir),
            "env": _safe_process_environment(job_dir, ffmpeg, node),
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "bufsize": 1,
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            kwargs["start_new_session"] = True
        try:
            process = subprocess.Popen(command, **kwargs)
        except (OSError, subprocess.SubprocessError):
            self.store.fail(job_id, "The downloader runtime is not available on this Media Node.")
            return
        with self.process_lock:
            self.processes[job_id] = process
        lines: queue.Queue[str] = queue.Queue(maxsize=100)
        def read_output() -> None:
            if process.stdout is None:
                return
            for line in process.stdout:
                try:
                    lines.put_nowait(line.rstrip("\r\n"))
                except queue.Full:
                    pass
        reader = threading.Thread(target=read_output, name="nolane-media-output", daemon=True)
        reader.start()
        started = time.monotonic()
        timed_out = False
        too_large = False
        cancelled = False
        while process.poll() is None:
            row = self.store.get_job(job_id, job["owner_id"])
            if row is None or row["cancel_requested"]:
                cancelled = True
                _terminate_process_tree(process)
                break
            if time.monotonic() - started > JOB_TIMEOUT_SECONDS:
                timed_out = True
                _terminate_process_tree(process)
                break
            if _directory_size(job_dir) > MAX_OUTPUT_BYTES:
                too_large = True
                _terminate_process_tree(process)
                break
            try:
                line = lines.get(timeout=0.4)
            except queue.Empty:
                continue
            progress = re.search(r"PROGRESS:\s*([0-9]+(?:\.[0-9]+)?)%", line)
            if progress:
                self.store.update_progress(job_id, float(progress.group(1)))
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _terminate_process_tree(process)
        reader.join(timeout=1)
        with self.process_lock:
            self.processes.pop(job_id, None)
        if cancelled or row is not None and row["cancel_requested"]:
            shutil.rmtree(job_dir, ignore_errors=True)
            self.store.mark_cancelled(job_id)
            return
        if timed_out or too_large or process.returncode != 0:
            shutil.rmtree(job_dir, ignore_errors=True)
            self.store.fail(job_id,
                "The media job exceeded its time limit." if timed_out else
                "The media output exceeded the size limit." if too_large else
                "The source is unavailable or cannot be processed.")
            return
        output = safe_output_file(self.store.root / "jobs", job_id)
        if output is None:
            self.store.fail(job_id, "The downloader did not produce one supported media file.")
            return
        size = output.stat().st_size
        if size < 1 or size > MAX_OUTPUT_BYTES:
            shutil.rmtree(job_dir, ignore_errors=True)
            self.store.fail(job_id, "The media output exceeded the size limit.")
            return
        extension = output.suffix.lower()
        content_types = {
            ".mp4": "video/mp4", ".webm": "video/webm", ".mkv": "video/x-matroska",
            ".mov": "video/quicktime", ".mp3": "audio/mpeg", ".m4a": "audio/mp4",
            ".opus": "audio/opus", ".ogg": "audio/ogg", ".wav": "audio/wav",
            ".flac": "audio/flac",
        }
        if not self.store.complete(job_id, output.name, content_types[extension], size):
            shutil.rmtree(job_dir, ignore_errors=True)
            self.store.mark_cancelled(job_id)

def create_http_server(
    store: MediaNodeStore,
    token: str,
    port: int = PORT,
    start_worker: bool = True,
) -> ThreadingHTTPServer:
    if not TOKEN_RE.fullmatch(token):
        raise ValueError("NOLANE_INTERNAL_TOKEN must be a 256-bit hex secret.")
    worker = MediaWorker(store)

    class Handler(BaseHTTPRequestHandler):
        server_version = "NolaneMediaNode/1"
        sys_version = ""

        def log_message(self, format: str, *args) -> None:
            # Access tokens, source URLs and query strings must never reach logs.
            return

        def _write_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _read_json(self) -> dict | None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return None
            if length < 0 or length > MAX_BODY_BYTES:
                return None
            try:
                value = json.loads(self.rfile.read(length) or b"{}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
            return value if isinstance(value, dict) else None

        def _owner(self) -> int | None:
            raw = self.headers.get("x-nolane-owner-id", "")
            if not re.fullmatch(r"[1-9][0-9]{0,19}", raw):
                return None
            try:
                owner_id = int(raw)
            except ValueError:
                return None
            return owner_id if owner_id <= 9_223_372_036_854_775_807 else None

        def _authenticated(self, owner_required: bool = True) -> int | None:
            supplied = self.headers.get("x-nolane-internal", "")
            if not hmac.compare_digest(supplied, token):
                self._write_json(401, {"error": "Unauthorized."})
                return None
            if not owner_required:
                return 0
            owner_id = self._owner()
            if owner_id is None:
                self._write_json(400, {"error": "A valid owner identity is required."})
                return None
            return owner_id

        def _job_id(self, part: str) -> str | None:
            return part if JOB_ID_RE.fullmatch(part) else None

        def do_GET(self) -> None:
            self._handle()

        def do_HEAD(self) -> None:
            self._handle()

        def do_POST(self) -> None:
            self._handle()

        def do_DELETE(self) -> None:
            self._handle()

        def _handle(self) -> None:
            path = urlsplit(self.path).path
            if path == "/health" and self.command in ("GET", "HEAD"):
                if self._authenticated(owner_required=False) is None:
                    return
                self._write_json(200, {"ok": True, "service": "nolane-media-node", "version": 1})
                return
            owner_id = self._authenticated(owner_required=True)
            if owner_id is None:
                return
            parts = path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "internal":
                action = parts[1]
                if action == "start" and len(parts) == 2 and self.command == "POST":
                    self._start_job(owner_id)
                    return
                if action == "status" and len(parts) == 3 and self.command == "GET":
                    self._status(owner_id, parts[2])
                    return
                if action == "cancel" and len(parts) == 3 and self.command == "POST":
                    self._cancel(owner_id, parts[2])
                    return
                if action == "renew-share" and len(parts) == 3 and self.command == "POST":
                    self._renew_share(owner_id, parts[2])
                    return
                if action == "revoke" and len(parts) == 3 and self.command == "DELETE":
                    self._revoke(owner_id, parts[2])
                    return
                if action == "share-info" and len(parts) == 3 and self.command == "GET":
                    self._share_info(owner_id, parts[2])
                    return
                if action == "share-file" and len(parts) == 3 and self.command in ("GET", "HEAD"):
                    self._share_file(owner_id, parts[2])
                    return
            self._write_json(404, {"error": "Not found."})

        def _start_job(self, owner_id: int) -> None:
            body = self._read_json()
            if body is None or body.get("ownerId") != owner_id:
                self._write_json(400, {"error": "The media request is invalid."})
                return
            job_id = body.get("jobId")
            if not isinstance(job_id, str) or not JOB_ID_RE.fullmatch(job_id):
                self._write_json(400, {"error": "The media request is invalid."})
                return
            media_format = body.get("format")
            quality = body.get("quality", "720")
            if media_format not in ("video", "audio") or quality not in ("best", "1080", "720", "480"):
                self._write_json(400, {"error": "The media format or quality is invalid."})
                return
            if media_format == "audio":
                quality = "720"
            try:
                source_url, source_host = normalize_source_url(body.get("url"))
            except SourceUrlError as error:
                self._write_json(400, {"error": str(error)[:180]})
                return
            try:
                store.enqueue(job_id, owner_id, source_url, media_format, quality, source_host)
            except QueueFull:
                self._write_json(429, {"error": "The Media Node queue is full. Wait for a current job to finish."})
                return
            except ValueError:
                self._write_json(409, {"error": "This media job already exists or is invalid."})
                return
            self._write_json(202, {"jobId": job_id, "status": "queued", "progress": 0})

        def _status(self, owner_id: int, job_id: str) -> None:
            valid_id = self._job_id(job_id)
            state = store.get_job(valid_id, owner_id) if valid_id else None
            if state is None:
                self._write_json(404, {"error": "Job not found."})
                return
            payload = {
                "jobId": state["job_id"], "status": state["status"],
                "progress": state["progress"], "sourceHost": state["source_host"],
                "createdAt": int(state["created_at"] * 1000),
                "updatedAt": int(state["updated_at"] * 1000),
                "fileName": state["file_name"], "contentType": state["content_type"],
                "size": state["size"],
                "shareExpiresAt": int(state["share_expires_at"] * 1000) if state["share_expires_at"] else None,
                "error": state["error"],
            }
            self._write_json(200, payload)

        def _cancel(self, owner_id: int, job_id: str) -> None:
            valid_id = self._job_id(job_id)
            state = store.request_cancel(valid_id, owner_id) if valid_id else None
            if state is None:
                self._write_json(404, {"error": "Job not found."})
                return
            if state["cancel_requested"]:
                worker.cancel(valid_id)
            self._write_json(200, {"ok": True, "status": state["status"]})

        def _renew_share(self, owner_id: int, job_id: str) -> None:
            valid_id = self._job_id(job_id)
            body = self._read_json()
            token_hash = body.get("tokenHash") if body else None
            if not valid_id or not isinstance(token_hash, str) or not TOKEN_RE.fullmatch(token_hash):
                self._write_json(400, {"error": "The share request is invalid."})
                return
            state = store.renew_share(valid_id, owner_id, token_hash)
            if state is None:
                self._write_json(409, {"error": "A completed, unexpired file is required before sharing."})
                return
            self._write_json(200, {
                "ok": True, "shareExpiresAt": int(state["share_expires_at"] * 1000),
                "fileName": state["file_name"], "size": state["size"],
            })

        def _revoke(self, owner_id: int, job_id: str) -> None:
            valid_id = self._job_id(job_id)
            if not valid_id or not store.revoke(valid_id, owner_id):
                self._write_json(404, {"error": "Share not found."})
                return
            self._write_json(200, {"ok": True, "status": "revoked"})

        def _share_info(self, owner_id: int, job_id: str) -> None:
            valid_id = self._job_id(job_id)
            token_value = self.headers.get("x-nolane-share-token", "")
            state = store.authorize_share(valid_id, owner_id, token_value) if valid_id else None
            if state is None:
                self._write_json(404, {"error": "Share not found or expired."})
                return
            self._write_json(200, {
                "fileName": state["file_name"], "contentType": state["content_type"],
                "size": state["size"], "shareExpiresAt": int(state["share_expires_at"] * 1000),
            })

        def _share_file(self, owner_id: int, job_id: str) -> None:
            valid_id = self._job_id(job_id)
            token_value = self.headers.get("x-nolane-share-token", "")
            state = store.authorize_share(valid_id, owner_id, token_value) if valid_id else None
            if state is None:
                self._write_json(404, {"error": "Share not found or expired."})
                return
            file_path = safe_output_file(store.root / "jobs", valid_id)
            if file_path is None:
                self._write_json(404, {"error": "The temporary media file is unavailable."})
                return
            size = file_path.stat().st_size
            range_header = self.headers.get("Range")
            interval = parse_range(range_header, size)
            if range_header is not None and interval is None:
                self.send_response(416)
                self.send_header("Content-Range", "bytes */" + str(size))
                self.send_header("Content-Length", "0")
                self.send_header("Cache-Control", "private, no-store")
                self.end_headers()
                return
            start, end = interval or (0, size - 1)
            length = end - start + 1
            name = file_path.name.replace("\r", "").replace("\n", "").replace('"', "")
            ascii_name = "nolane-media" + file_path.suffix.lower()
            self.send_response(206 if range_header is not None else 200)
            self.send_header("Content-Type", state["content_type"])
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "private, no-store, max-age=0")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Disposition", "inline; filename=\"" + ascii_name + "\"; filename*=UTF-8''" + quote(name))
            if range_header is not None:
                self.send_header("Content-Range", "bytes " + str(start) + "-" + str(end) + "/" + str(size))
            self.end_headers()
            if self.command == "HEAD":
                return
            try:
                with file_path.open("rb") as source:
                    source.seek(start)
                    remaining = length
                    while remaining > 0:
                        chunk = source.read(min(1024 * 1024, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            except (BrokenPipeError, ConnectionResetError, OSError):
                return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    server.media_worker = worker
    if start_worker:
        worker.start()
    return server

def main() -> int:
    token = os.environ.get("NOLANE_INTERNAL_TOKEN", "")
    if not TOKEN_RE.fullmatch(token):
        print("NOLANE_INTERNAL_TOKEN must be a 64-character hexadecimal secret.", file=sys.stderr)
        return 2
    store = MediaNodeStore(DATA_ROOT)
    httpd = create_http_server(store, token, PORT, start_worker=True)
    print("Nolane Media Node listening on 127.0.0.1:" + str(PORT))
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
        httpd.server_close()
        httpd.media_worker.stop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
