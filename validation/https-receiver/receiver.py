"""Test-only HTTP receiver; real TLS is terminated by Railway, never here.
Original validation fixture, licensed under the repository MIT license.
"""
import hashlib
import hmac
import json
import os
import secrets
import socket
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

MAX_BODY = 65536
MAX_RECEIPTS = 32
READ_TIMEOUT = 3


def required_secret(name):
    value = os.environ.get(name, "")
    if len(value) < 32 or not value.isascii() or not value.isalnum():
        raise ValueError("receiver secrets must be distinct alphanumeric values of at least 32 characters")
    return value


class Receiver(HTTPServer):
    def __init__(self, address):
        self.nonce = required_secret("NOTIFICATION_NONCE")
        self.control = required_secret("RECEIPT_CONTROL_TOKEN")
        if hmac.compare_digest(self.nonce, self.control):
            raise ValueError("receiver secrets must be distinct")
        self.instance = secrets.token_hex(24)
        self.accepted = 0
        self.rejected = 0
        self.control_denied = 0
        self.receipts = []
        super().__init__(address, Handler)

    def handle_error(self, request, client_address):
        # Never print request data, credentials, paths, or client identities.
        pass


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    server_version = "ValidationReceiver"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(READ_TIMEOUT)

    def log_message(self, *args):
        pass

    def reply(self, status, body=None):
        encoded = json.dumps(body if body is not None else {}, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)
        self.close_connection = True

    def send_error(self, code, message=None, explain=None):
        self.reply(code)

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"ok": True})
        if self.path != "/receipts":
            return self.reply(404)
        supplied = self.headers.get_all("Authorization", [])
        expected = "Bearer " + self.server.control
        if len(supplied) != 1 or not hmac.compare_digest(supplied[0].encode(), expected.encode()):
            self.server.control_denied += 1
            return self.reply(403)
        self.reply(200, {"instance_id": self.server.instance,
                         "accepted": self.server.accepted, "rejected": self.server.rejected,
                         "control_denied": self.server.control_denied,
                         "receipts": self.server.receipts})

    def reject(self, status):
        self.server.rejected += 1
        self.reply(status)

    def do_POST(self):
        if not hmac.compare_digest(self.path.encode(), ("/" + self.server.nonce).encode()):
            return self.reject(403)
        lengths = self.headers.get_all("Content-Length", [])
        if self.headers.get("Transfer-Encoding") is not None or len(lengths) != 1:
            return self.reject(400)
        if not lengths[0].isascii() or not lengths[0].isdigit():
            return self.reject(400)
        length = int(lengths[0])
        if length > MAX_BODY:
            return self.reject(413)
        if self.headers.get_content_type() != "application/json":
            return self.reject(415)
        deadline = time.monotonic() + READ_TIMEOUT
        data = bytearray()
        try:
            while len(data) < length:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return self.reject(408)
                self.connection.settimeout(remaining)
                part = self.rfile.read1(min(8192, length - len(data)))
                if not part:
                    return self.reject(400)
                data.extend(part)
        except (TimeoutError, socket.timeout):
            return self.reject(408)
        try:
            payload = json.loads(bytes(data))
            if not isinstance(payload, dict):
                return self.reject(400)
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=True, allow_nan=False).encode()
        except (ValueError, UnicodeError, RecursionError):
            return self.reject(400)
        if len(self.server.receipts) >= MAX_RECEIPTS:
            return self.reject(503)
        self.server.accepted += 1
        self.server.receipts.append({"sequence": self.server.accepted,
                                    "sha256": hashlib.sha256(canonical).hexdigest(),
                                    "payload": payload})
        self.reply(200, {"ok": True})


if __name__ == "__main__":
    Receiver(("0.0.0.0", int(os.environ.get("PORT", "8000")))).serve_forever()
