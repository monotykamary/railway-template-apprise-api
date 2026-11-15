"""Benign, isolated fixture contract tests. Run only on boat."""
import hashlib
import http.client
import json
import os
import threading
import unittest
from unittest.mock import patch
from receiver import Receiver, MAX_BODY, READ_TIMEOUT


class Contract(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, NOTIFICATION_NONCE="n" * 48,
                        RECEIPT_CONTROL_TOKEN="c" * 48):
            self.server = Receiver(("127.0.0.1", 0))
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(5)
        self.assertFalse(self.thread.is_alive())

    def req(self, method, path, body=None, auth=False, content_type="application/json"):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=6)
        headers = {"Content-Type": content_type}
        if auth:
            headers["Authorization"] = "Bearer " + "c" * 48
        try:
            conn.request(method, path, body=body, headers=headers)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def snapshot(self):
        status, body = self.req("GET", "/receipts", auth=True)
        self.assertEqual(status, 200)
        return body

    def test_three_phase_continuity_and_auth(self):
        self.assertEqual(self.req("GET", "/health"), (200, {"ok": True}))
        start = self.snapshot()
        for index, phase in enumerate(("published", "candidate", "redeploy"), 1):
            self.assertEqual(self.req("GET", "/receipts")[0], 403)
            self.assertEqual(self.req("POST", "/incorrect-nonce", b"{}")[0], 403)
            payload = {"title": phase, "message": "fixture " + phase}
            encoded = json.dumps(payload).encode()
            self.assertEqual(self.req("POST", "/" + "n" * 48, encoded)[0], 200)
            snap = self.snapshot()
            self.assertEqual(snap["instance_id"], start["instance_id"])
            self.assertEqual((snap["accepted"], snap["rejected"], snap["control_denied"]),
                             (index, index, index))
            self.assertEqual(snap["receipts"][-1]["payload"], payload)
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            self.assertEqual(snap["receipts"][-1]["sha256"], hashlib.sha256(canonical).hexdigest())
        self.assertEqual(len(self.snapshot()["receipts"]), 3)

    def test_bounded_inputs(self):
        path = "/" + "n" * 48
        body = json.dumps({"message": "x" * (MAX_BODY - 14)}, separators=(",", ":")).encode()
        self.assertEqual(len(body), MAX_BODY)
        self.assertEqual(self.req("POST", path, body)[0], 200)
        self.assertEqual(self.req("POST", path, b" " * (MAX_BODY + 1))[0], 413)
        self.assertEqual(self.req("POST", path, b"not-json")[0], 400)
        self.assertEqual(self.req("POST", path, b"[]")[0], 400)
        self.assertEqual(self.req("POST", path, b"{}", content_type="text/plain")[0], 415)
        snap = self.snapshot()
        self.assertEqual((snap["accepted"], snap["rejected"]), (1, 4))
        self.assertEqual(READ_TIMEOUT, 3)

    def test_body_read_timeout(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=6)
        try:
            conn.putrequest("POST", "/" + "n" * 48)
            conn.putheader("Content-Type", "application/json")
            conn.putheader("Content-Length", "2")
            conn.endheaders(b"{")
            response = conn.getresponse()
            self.assertEqual(response.status, 408)
            response.read()
        finally:
            conn.close()
        snap = self.snapshot()
        self.assertEqual((snap["accepted"], snap["rejected"]), (0, 1))

    def test_capacity_fails_closed(self):
        for _ in range(32):
            self.assertEqual(self.req("POST", "/" + "n" * 48, b"{}")[0], 200)
        self.assertEqual(self.req("POST", "/" + "n" * 48, b"{}")[0], 503)
        snap = self.snapshot()
        self.assertEqual((snap["accepted"], snap["rejected"], len(snap["receipts"])), (32, 1, 32))

    def test_restart_changes_identity(self):
        with patch.dict(os.environ, NOTIFICATION_NONCE="n" * 48, RECEIPT_CONTROL_TOKEN="c" * 48):
            other = Receiver(("127.0.0.1", 0))
        try:
            self.assertNotEqual(other.instance, self.server.instance)
        finally:
            other.server_close()

    def test_secrets_fail_closed(self):
        for nonce, control in (("short", "c" * 48), ("n" * 48, "n" * 48)):
            with patch.dict(os.environ, NOTIFICATION_NONCE=nonce, RECEIPT_CONTROL_TOKEN=control):
                with self.assertRaises(ValueError):
                    Receiver(("127.0.0.1", 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
