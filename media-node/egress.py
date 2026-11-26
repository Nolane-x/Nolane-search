from __future__ import annotations

import select
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import urlsplit

CONNECT_TIMEOUT_SECONDS = 15
PROXY_IDLE_TIMEOUT_SECONDS = 120
MAX_PROXY_REQUEST_BODY = 1024 * 1024

class EgressProxyError(ValueError):
    pass

def resolve_public_addresses(
    host: str,
    resolver: Callable[[str], list[str]],
    is_public_ip: Callable[[str], bool],
) -> list[str]:
    try:
        answers = resolver(host)
    except Exception as error:
        raise EgressProxyError("The source host could not be resolved.") from error
    addresses = sorted({str(address).split("%", 1)[0] for address in answers})
    if not addresses:
        raise EgressProxyError("The source host has no address records.")
    # Fail closed if DNS returns even one local, special-use, or otherwise
    # non-public address. Never silently discard an unsafe answer.
    if any(not is_public_ip(address) for address in addresses):
        raise EgressProxyError("Every DNS answer must be globally routable.")
    return addresses

def connect_public_host(
    host: str,
    port: int,
    resolver: Callable[[str], list[str]],
    is_public_ip: Callable[[str], bool],
    connector: Callable[..., socket.socket] = socket.create_connection,
) -> socket.socket:
    if port not in (80, 443):
        raise EgressProxyError("Only standard HTTP and HTTPS ports are allowed.")
    addresses = resolve_public_addresses(host, resolver, is_public_ip)
    last_error: OSError | None = None
    for address in addresses:
        try:
            # The socket connects to the exact numeric result returned above.
            # The OS cannot perform a second hostname lookup here.
            return connector((address, port), timeout=CONNECT_TIMEOUT_SECONDS)
        except OSError as error:
            last_error = error
    raise EgressProxyError("No validated public source address could be reached.") from last_error

def create_egress_proxy(
    *,
    host: str,
    port: int,
    resolver: Callable[[str], list[str]],
    normalize_url: Callable[..., tuple[str, str]],
    is_public_ip: Callable[[str], bool],
    connector: Callable[..., socket.socket] = socket.create_connection,
) -> ThreadingHTTPServer:
    class ProxyHandler(BaseHTTPRequestHandler):
        server_version = "NolaneMediaEgress/1"
        sys_version = ""
        protocol_version = "HTTP/1.1"
        # Do not buffer past the CONNECT request headers. TLS ClientHello bytes
        # may already be waiting immediately after the header terminator.
        rbufsize = 0
        wbufsize = 0

        def log_message(self, format: str, *args) -> None:
            # Proxy request targets may contain signed media URLs and secrets.
            return

        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(PROXY_IDLE_TIMEOUT_SECONDS)

        def _reject(self, status: int, message: str = "Destination is not allowed.") -> None:
            self.close_connection = True
            self.send_error(status, message)

        def do_CONNECT(self) -> None:
            authority = self.path.strip()
            if not authority or "@" in authority or authority.startswith("[") or authority.count(":") != 1:
                self._reject(403)
                return
            target_host, separator, raw_port = authority.rpartition(":")
            if not separator or not raw_port.isdigit() or int(raw_port) != 443:
                self._reject(403)
                return
            try:
                _, normalized_host = normalize_url(
                    "https://" + target_host + "/",
                    resolver=resolver,
                )
                upstream = connect_public_host(
                    normalized_host, 443, resolver, is_public_ip, connector, connector,
                )
            except (EgressProxyError, ValueError, OSError):
                self._reject(403)
                return

            try:
                self.send_response(200, "Connection Established")
                self.end_headers()
                self.close_connection = True
                self._relay(upstream)
            except (BrokenPipeError, ConnectionResetError, OSError):
                return
            finally:
                upstream.close()

        def _relay(self, upstream: socket.socket) -> None:
            peers = (self.connection, upstream)
            while True:
                readable, _, _ = select.select(peers, (), (), PROXY_IDLE_TIMEOUT_SECONDS)
                if not readable:
                    return
                for source in readable:
                    data = source.recv(256 * 1024)
                    if not data:
                        return
                    destination = upstream if source is self.connection else self.connection
                    destination.sendall(data)

        def do_GET(self) -> None:
            self._forward_http()

        def do_HEAD(self) -> None:
            self._forward_http()

        def do_POST(self) -> None:
            self._forward_http()

        def _forward_http(self) -> None:
            upstream: socket.socket | None = None
            try:
                normalized_url, normalized_host = normalize_url(
                    self.path,
                    resolver=resolver,
                )
                parsed = urlsplit(normalized_url)
                if parsed.scheme != "http":
                    self._reject(400)
                    return
                if self.headers.get("Transfer-Encoding", "").lower() not in ("", "identity"):
                    self._reject(501, "Chunked proxy request bodies are not supported.")
                    return
                try:
                    body_length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    self._reject(400)
                    return
                if body_length < 0 or body_length > MAX_PROXY_REQUEST_BODY:
                    self._reject(413, "Proxy request body is too large.")
                    return

                upstream = connect_public_host(
                    normalized_host, 80, resolver, is_public_ip, connector, connector,
                )
                upstream.settimeout(PROXY_IDLE_TIMEOUT_SECONDS)
                request_target = parsed.path or "/"
                if parsed.query:
                    request_target += "?" + parsed.query
                outgoing = [
                    self.command + " " + request_target + " HTTP/1.1",
                    "Host: " + normalized_host,
                ]
                excluded = {
                    "host", "connection", "proxy-connection", "proxy-authorization",
                    "proxy-authenticate", "keep-alive", "upgrade", "transfer-encoding",
                    "te", "trailer",
                }
                for name, value in self.headers.items():
                    if name.lower() in excluded or name.lower() == "content-length":
                        continue
                    if "\r" in name or "\n" in name or "\r" in value or "\n" in value:
                        self._reject(400)
                        return
                    outgoing.append(name + ": " + value)
                if body_length:
                    outgoing.append("Content-Length: " + str(body_length))
                outgoing.append("Connection: close")
                upstream.sendall(("\r\n".join(outgoing) + "\r\n\r\n").encode("latin-1"))

                remaining = body_length
                while remaining:
                    chunk = self.rfile.read(min(64 * 1024, remaining))
                    if not chunk:
                        self._reject(400, "Incomplete proxy request body.")
                        return
                    upstream.sendall(chunk)
                    remaining -= len(chunk)

                self.close_connection = True
                while True:
                    chunk = upstream.recv(256 * 1024)
                    if not chunk:
                        break
                    self.connection.sendall(chunk)
            except (EgressProxyError, ValueError):
                self._reject(403)
            except (BrokenPipeError, ConnectionResetError, TimeoutError, OSError):
                self.close_connection = True
            finally:
                if upstream is not None:
                    upstream.close()

    class BoundedProxyServer(ThreadingHTTPServer):
        request_queue_size = 8
        daemon_threads = True

        def __init__(self, address, handler):
            self._request_slots = threading.BoundedSemaphore(16)
            super().__init__(address, handler)

        def process_request(self, request, client_address):
            if not self._request_slots.acquire(blocking=False):
                self.shutdown_request(request)
                return
            try:
                super().process_request(request, client_address)
            except BaseException:
                self._request_slots.release()
                raise

        def process_request_thread(self, request, client_address):
            try:
                super().process_request_thread(request, client_address)
            finally:
                self._request_slots.release()

    return BoundedProxyServer((host, port), ProxyHandler)
