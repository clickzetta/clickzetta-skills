"""Exercise the documented prepare command and both OTLP routes on a project switch."""

import json
import os
import shlex
import shutil
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
    ExportLogsServiceRequest,
)
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
)

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts" / "codex"))


class ProjectSwitchTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.relay = self.root / "relay"
        shutil.copytree(SKILL / "scripts/codex", self.relay)
        python = self.relay / "venv/bin/python"
        python.parent.mkdir(parents=True)
        python.write_text("#!/bin/sh\nexec " + shlex.quote(sys.executable) + ' "$@"\n')
        python.chmod(0o700)
        self.receipts = []
        receipts = self.receipts
        drop_ack = self.drop_ack = threading.Event()

        class Collector(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                data = self.rfile.read(int(self.headers["Content-Length"]))
                receipts.append((self.path, self.headers["x-singsight-apikey"], data))
                if self.path == "/v1/traces" and drop_ack.is_set():
                    drop_ack.clear()
                    self.close_connection = True
                    return
                self.send_response(200)
                self.end_headers()

        key, cert = self.root / "tls.key", self.root / "tls.crt"
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-days",
                "1",
                "-subj",
                "/CN=localhost",
                "-addext",
                "subjectAltName=DNS:localhost",
                "-out",
                str(cert),
                "-keyout",
                str(key),
            ],
            check=True,
            capture_output=True,
        )
        collector = ThreadingHTTPServer(("127.0.0.1", 0), Collector)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert, key)
        collector.socket = ctx.wrap_socket(collector.socket, server_side=True)
        threading.Thread(target=collector.serve_forever, daemon=True).start()
        self.addCleanup(collector.server_close)
        self.addCleanup(collector.shutdown)
        self.env = {
            **os.environ,
            "HOME": str(self.root),
            "CODEX_HOME": str(self.root / "codex-home"),
            "relay_dir": str(self.relay),
            "ENDPOINT": f"https://localhost:{collector.server_port}",
            "SSL_CERT_FILE": str(cert),
        }
        self.env.pop("SINGSIGHT_INGEST_KEY", None)
        guide = (SKILL / "references/codex.md").read_text()
        self.command = next(
            line.strip()
            for line in guide.splitlines()
            if 'configure.py" prepare --endpoint' in line
        )
        self.proc = None
        self.addCleanup(self.stop_relay)

    def prepare(self, key, switch=False, rotate=False):
        cmd = (
            self.command
            + (" --switch-project" if switch else "")
            + (" --rotate-key" if rotate else "")
        )
        return subprocess.run(
            ["/bin/sh", "-c", cmd],
            check=False,
            env={**self.env, "API_KEY": key},
            stdin=subprocess.DEVNULL,
            capture_output=True,
            start_new_session=True,
            timeout=10,
        )

    def start_relay(self):
        settings = json.loads((self.relay / "relay.json").read_text())
        self.base = f"http://127.0.0.1:{settings['port']}"
        self.headers = {"x-local-token": settings["local_token"]}
        self.proc = subprocess.Popen(
            [sys.executable, str(self.relay / "relay.py")], env=self.env
        )
        for _ in range(100):
            try:
                with urlopen(
                    Request(self.base + "/ready", headers=self.headers), timeout=1
                ):
                    return
            except URLError:
                time.sleep(0.03)
        self.fail("Relay never became ready")

    def stop_relay(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)
            self.proc = None

    def submit(self, path, message):
        req = Request(
            self.base + path, data=message.SerializeToString(), headers=self.headers
        )
        with urlopen(req, timeout=5) as response:
            self.assertEqual(response.status, 200)

    def send_pair(self):
        for path, message in [
            ("/v1/logs", ExportLogsServiceRequest()),
            ("/v1/traces", ExportTraceServiceRequest()),
        ]:
            if path.endswith("logs"):
                message.resource_logs.add().scope_logs.add().log_records.add(
                    time_unix_nano=1
                )
            else:
                message.resource_spans.add().scope_spans.add().spans.add(name="test")
            self.submit(path, message)

    def test_explicit_switch_changes_both_signals_and_never_reuses_previous_key(self):
        self.assertEqual(self.prepare("test-project-A").returncode, 0)
        self.start_relay()
        self.send_pair()
        activate = [sys.executable, str(self.relay / "configure.py"), "activate"]
        subprocess.run(activate, env=self.env, check=True, capture_output=True)
        old_headers = dict(self.headers)
        old = (self.relay / "relay.json").read_bytes()
        self.assertNotEqual(self.prepare("test-project-B").returncode, 0)
        self.assertNotEqual(self.prepare("test-project-B", switch=True).returncode, 0)
        self.assertEqual((self.relay / "relay.json").read_bytes(), old)
        self.stop_relay()
        self.assertEqual(self.prepare("test-project-B", switch=True).returncode, 0)
        self.start_relay()
        for path in ("/ready", "/v1/logs", "/v1/traces"):
            with self.assertRaises(HTTPError) as refusal:
                urlopen(
                    Request(
                        self.base + path,
                        headers=old_headers,
                        data=None if path == "/ready" else b"old payload",
                    ),
                    timeout=2,
                )
            self.assertEqual(refusal.exception.code, 403)
            refusal.exception.close()
        subprocess.run(
            [*activate, "--replace-exporters"],
            env=self.env,
            check=True,
            capture_output=True,
        )
        from tomlkit import parse

        otel = parse((Path(self.env["CODEX_HOME"]) / "config.toml").read_text())["otel"]
        for field in ("exporter", "trace_exporter"):
            self.assertEqual(otel[field]["otlp-http"]["headers"], self.headers)
        self.send_pair()
        self.assertEqual(
            [(p, k) for p, k, _ in self.receipts],
            [
                ("/v1/logs", "test-project-A"),
                ("/v1/traces", "test-project-A"),
                ("/v1/logs", "test-project-B"),
                ("/v1/traces", "test-project-B"),
            ],
        )

    def test_rotate_key_keeps_legacy_queue_context_and_delivered_ids(self):
        from configure import credential_id
        from relay import UsageQueue

        self.assertEqual(self.prepare("first-key").returncode, 0)
        file = self.relay / "relay.json"
        legacy = json.loads(file.read_text())
        del legacy["project_id"], legacy["projects"]
        file.write_text(json.dumps(legacy))
        store = UsageQueue(self.relay, credential_id(legacy["upstream"]))
        trace = os.urandom(16)
        session = "00000000-0000-4000-8000-000000000002"

        def usage(trace, span):
            req = ExportTraceServiceRequest()
            entry = (
                req.resource_spans.add()
                .scope_spans.add()
                .spans.add(trace_id=trace, span_id=span, name="handle_responses")
            )
            entry.attributes.add(key="gen_ai.usage.output_tokens").value.int_value = 27
            return req

        def log(trace):
            req = ExportLogsServiceRequest()
            req.resource_logs.add().scope_logs.add().log_records.add(
                trace_id=trace
            ).attributes.add(key="conversation.id").value.string_value = session
            return req

        sent = usage(os.urandom(16), os.urandom(8))
        sent_trace = sent.resource_spans[0].scope_spans[0].spans[0].trace_id
        store.route("/v1/logs", log(sent_trace).SerializeToString())
        store.route("/v1/traces", sent.SerializeToString())
        self.assertTrue(
            store.flush_one(lambda *args: (200, b"", "application/x-protobuf"))
        )
        pending_id = os.urandom(8)
        pending = usage(trace, pending_id)
        store.route("/v1/traces", pending.SerializeToString())
        store.db.close()

        self.assertNotEqual(self.prepare("second-key").returncode, 0)
        self.assertEqual(self.prepare("second-key", rotate=True).returncode, 0)
        new = json.loads(file.read_text())
        self.assertEqual(new["project_id"], credential_id(legacy["upstream"]))
        self.assertEqual(new["local_token"], legacy["local_token"])
        self.start_relay()
        self.submit("/v1/traces", sent)
        self.submit("/v1/traces", pending)
        self.submit("/v1/logs", log(trace))
        for _ in range(100):
            if any(p == "/v1/traces" for p, _, _ in self.receipts):
                break
            time.sleep(0.05)
        received = [
            ExportTraceServiceRequest.FromString(raw)
            .resource_spans[0]
            .scope_spans[0]
            .spans[0]
            for p, _, raw in self.receipts
            if p == "/v1/traces"
        ]
        self.assertEqual([s.span_id for s in received], [pending_id])
        self.assertTrue(all(key == "second-key" for _, key, _ in self.receipts))
        attrs = {
            a.key: getattr(a.value, a.value.WhichOneof("value"))
            for a in received[0].attributes
        }
        self.assertEqual(
            (attrs["session.id"], attrs["gen_ai.usage.output_tokens"]), (session, 27)
        )

    def test_collector_accepts_then_closes_connection_without_ack(self):
        self.assertEqual(self.prepare("test-key").returncode, 0)
        self.start_relay()
        trace, span = os.urandom(16), os.urandom(8)
        usage = ExportTraceServiceRequest()
        entry = (
            usage.resource_spans.add()
            .scope_spans.add()
            .spans.add(trace_id=trace, span_id=span, name="handle_responses")
        )
        entry.attributes.add(
            key="conversation.id"
        ).value.string_value = "00000000-0000-4000-8000-000000000003"
        entry.attributes.add(key="gen_ai.usage.input_tokens").value.int_value = 21
        self.drop_ack.set()
        self.submit("/v1/traces", usage)
        for _ in range(100):
            if not self.drop_ack.is_set():
                break
            time.sleep(0.05)
        self.assertFalse(self.drop_ack.is_set())
        self.stop_relay()
        cmd = [sys.executable, str(self.relay / "relay.py"), "receipts"]
        listing = subprocess.run(
            cmd, env=self.env, check=True, capture_output=True, text=True
        )
        self.assertEqual(listing.stdout.split(), [trace.hex(), span.hex()])
        self.start_relay()
        self.submit("/v1/traces", usage)
        self.stop_relay()
        subprocess.run(
            [*cmd, "--received", trace.hex(), span.hex()], env=self.env, check=True
        )
        self.start_relay()
        self.submit("/v1/traces", usage)
        # A second distinct span completes a worker cycle after the replay.
        entry.span_id = os.urandom(8)
        self.submit("/v1/traces", usage)
        for _ in range(100):
            if len(self.receipts) >= 2:
                break
            time.sleep(0.05)
        submitted = [
            ExportTraceServiceRequest.FromString(data)
            .resource_spans[0]
            .scope_spans[0]
            .spans[0]
            .span_id
            for _, _, data in self.receipts
        ]
        self.assertEqual(submitted, [span, entry.span_id])

    def test_late_log_after_process_restart_releases_one_usage_record(self):
        self.assertEqual(self.prepare("test-project-A").returncode, 0)
        self.start_relay()
        trace = os.urandom(16)
        span = os.urandom(8)
        session = "00000000-0000-4000-8000-000000000001"
        usage = ExportTraceServiceRequest()
        sp = (
            usage.resource_spans.add()
            .scope_spans.add()
            .spans.add(trace_id=trace, span_id=span, name="handle_responses")
        )
        for k, v in (
            ("gen_ai.usage.input_tokens", 23),
            ("gen_ai.usage.output_tokens", 4),
        ):
            sp.attributes.add(key=k).value.int_value = v
        self.submit("/v1/traces", usage)
        self.stop_relay()
        self.start_relay()
        logs = ExportLogsServiceRequest()
        logs.resource_logs.add().scope_logs.add().log_records.add(
            trace_id=trace
        ).attributes.add(key="conversation.id").value.string_value = session
        self.submit("/v1/logs", logs)
        self.submit("/v1/traces", usage)
        for _ in range(100):
            if any(p == "/v1/traces" for p, _, _ in self.receipts):
                break
            time.sleep(0.05)
        forwarded = [
            ExportTraceServiceRequest.FromString(data)
            .resource_spans[0]
            .scope_spans[0]
            .spans[0]
            for p, _, data in self.receipts
            if p == "/v1/traces"
        ]
        self.assertEqual([s.span_id for s in forwarded], [span])
        attrs = {
            a.key: getattr(a.value, a.value.WhichOneof("value"))
            for a in forwarded[0].attributes
        }
        self.assertEqual(
            (attrs["session.id"], attrs["gen_ai.operation.name"]), (session, "chat")
        )
        self.assertEqual(
            attrs["gen_ai.usage.input_tokens"] + attrs["gen_ai.usage.output_tokens"], 27
        )
