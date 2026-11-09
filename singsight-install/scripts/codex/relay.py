"""Forward native OTLP messages, enriching existing Codex spans in place."""

import argparse
import gzip
import hmac
import io
import os
import socket
import sqlite3
import sys
import threading
import time
import uuid
import zlib
from http.client import HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from configure import ROOT, configuration_lock, load_settings, require_stopped
from google.protobuf.message import DecodeError
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
    ExportLogsServiceRequest,
)
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
    ExportTraceServiceResponse,
)

signals = {
    "/v1/traces": ExportTraceServiceRequest,
    "/v1/logs": ExportLogsServiceRequest,
}
# Keep unresolved usage across separate exporter batches and process restarts.
# The pending queue and UUID cache belong to one logical project across key rotations.
CONTEXT_TTL = 900
MAX_PENDING_BYTES = 32 * 1024 * 1024
MAX_PENDING_SPANS = 4096


class QueueFull(Exception):
    pass


def attributes(item):
    return {
        a.key: getattr(a.value, a.value.WhichOneof("value"))
        for a in item.attributes
        if a.value.WhichOneof("value")
    }


def add(item, attrs, key, value):
    if key not in attrs and value:
        item.attributes.add(key=key).value.string_value = str(value)


def conversation(attrs):
    for key in ("gen_ai.conversation.id", "conversation.id", "thread_id", "thread.id"):
        try:
            return str(uuid.UUID(str(attrs.get(key))))
        except ValueError:
            pass


class UsageQueue:
    def __init__(self, directory, project):
        self.db = sqlite3.connect(
            directory / f"usage-{project}.sqlite3", check_same_thread=False
        )
        self.lock = threading.Lock()
        self.changed = threading.Event()
        self.last_cleanup = 0
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS context (
                trace BLOB PRIMARY KEY, session TEXT, model TEXT, seen REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS usage (
                trace BLOB, span BLOB, packet BLOB, queued REAL, retry REAL DEFAULT 0,
                PRIMARY KEY(trace, span)
            );
            CREATE INDEX IF NOT EXISTS pending_usage ON usage(queued) WHERE packet IS NOT NULL;
        """)

    def remember(self, item, attrs, now):
        session = conversation(attrs)
        if session and item.trace_id:
            self.db.execute(
                """
                INSERT INTO context VALUES (?, ?, ?, ?)
                ON CONFLICT(trace) DO UPDATE SET
                  session = CASE WHEN context.seen < ? OR context.session = excluded.session
                                 THEN excluded.session ELSE NULL END,
                  model = coalesce(excluded.model, context.model), seen = excluded.seen
            """,
                (item.trace_id, session, attrs.get("model"), now, now - CONTEXT_TTL),
            )
        return session

    def route(self, path, raw):
        msg = signals[path].FromString(raw)
        now = time.time()
        pending = []
        # Commit correlation independently. Even a rejected full batch can
        # unlock older usage and make room for the exporter's retry.
        with self.lock:
            with self.db:
                if now - self.last_cleanup > 60:
                    self.db.execute(
                        """DELETE FROM context WHERE seen < ? AND NOT EXISTS (
                            SELECT 1 FROM usage WHERE trace=context.trace AND packet IS NOT NULL
                        )""",
                        (now - CONTEXT_TTL,),
                    )
                    self.last_cleanup = now
                if path == "/v1/logs":
                    for r in msg.resource_logs:
                        for sc in r.scope_logs:
                            for log in sc.log_records:
                                self.remember(log, attributes(log), now)
                    direct = raw
                else:
                    direct, pending = self.split_spans(msg, now)
            self.changed.set()
            if pending:
                with self.db:
                    inserted = self.db.executemany(
                        "INSERT OR IGNORE INTO usage(trace, span, packet, queued) VALUES(?,?,?,?)",
                        pending,
                    ).rowcount
                    if inserted:
                        size, rows = self.db.execute(
                            "SELECT sum(length(packet)), count(*) FROM usage WHERE packet IS NOT NULL"
                        ).fetchone()
                        if size > MAX_PENDING_BYTES or rows > MAX_PENDING_SPANS:
                            raise QueueFull()
        return direct

    def split_spans(self, msg, now):
        direct_count = 0
        pending = []
        for resource in msg.resource_spans:
            for scope in resource.scope_spans:
                direct = []
                for span in scope.spans:
                    attrs = attributes(span)
                    session = self.remember(span, attrs, now)
                    if span.name == "handle_responses" and (
                        "gen_ai.usage.input_tokens" in attrs
                        or "gen_ai.usage.output_tokens" in attrs
                    ):
                        packet = ExportTraceServiceRequest()
                        group = packet.resource_spans.add(
                            resource=resource.resource, schema_url=resource.schema_url
                        )
                        group.scope_spans.add(
                            scope=scope.scope, schema_url=scope.schema_url
                        ).spans.add().CopyFrom(span)
                        pending.append(
                            (
                                span.trace_id,
                                span.span_id,
                                packet.SerializeToString(),
                                now,
                            )
                        )
                    else:
                        add(span, attrs, "gen_ai.conversation.id", session)
                        add(span, attrs, "session.id", session)
                        direct.append(span)
                del scope.spans[:]
                scope.spans.extend(direct)
                direct_count += len(direct)
        return msg.SerializeToString() if direct_count else b"", pending

    def flush_one(self, send):
        now = time.time()
        with self.lock, self.db:
            row = self.db.execute(
                """SELECT u.trace, u.span, u.packet, c.session, c.model
                   FROM usage u JOIN context c ON c.trace = u.trace
                   WHERE u.packet IS NOT NULL AND u.retry <= ?
                   ORDER BY u.queued LIMIT 1""",
                (now,),
            ).fetchone()
            if row is None:
                return False
            # Claim durably before the network call. A crash or a lost response
            # leaves a receipt to reconcile, never a blind second submission.
            self.db.execute(
                "UPDATE usage SET retry=NULL WHERE trace=? AND span=?", row[:2]
            )
        trace, span, raw, session, model = row
        packet = ExportTraceServiceRequest.FromString(raw)
        item = packet.resource_spans[0].scope_spans[0].spans[0]
        attrs = attributes(item)
        session = conversation(attrs) or session
        model = attrs.get("gen_ai.request.model") or attrs.get("model") or model
        add(item, attrs, "gen_ai.conversation.id", session)
        add(item, attrs, "session.id", session)
        add(item, attrs, "gen_ai.operation.name", "chat")
        add(item, attrs, "gen_ai.request.model", model)
        item.name = "chat " + model if model else "chat"
        try:
            _, body, _ = send("/v1/traces", packet.SerializeToString())
            rejected = ExportTraceServiceResponse.FromString(
                body
            ).partial_success.rejected_spans
        except (OSError, HTTPException, DecodeError) as exc:
            reason = exc.reason if isinstance(exc, URLError) else exc
            rejected = isinstance(
                reason, (ConnectionRefusedError, socket.gaierror)
            ) or (isinstance(exc, HTTPError) and exc.code in (401, 403, 429))
            if not rejected:
                print(
                    "Unconfirmed usage receipt:",
                    trace.hex(),
                    span.hex(),
                    file=sys.stderr,
                    flush=True,
                )
                return True
        with self.lock, self.db:
            if rejected:
                self.db.execute(
                    "UPDATE usage SET retry=? WHERE trace=? AND span=?",
                    (now + 30, trace, span),
                )
            else:
                self.db.execute(
                    "UPDATE usage SET packet=NULL WHERE trace=? AND span=?",
                    (trace, span),
                )
        return True

    def receipts(self, received=None, absent=None):
        if not (received or absent):
            for trace, span in self.db.execute(
                "SELECT trace, span FROM usage WHERE packet IS NOT NULL AND retry IS NULL ORDER BY queued"
            ):
                print(trace.hex(), span.hex())
            return
        try:
            trace, span = (bytes.fromhex(v) for v in (received or absent))
        except ValueError as exc:
            raise SystemExit("Expected hexadecimal trace and span IDs.") from exc
        with self.db:
            assignment = "packet=NULL" if received else "retry=0"
            result = self.db.execute(
                f"UPDATE usage SET {assignment} WHERE trace=? AND span=? AND packet IS NOT NULL AND retry IS NULL",
                (trace, span),
            )
            if result.rowcount != 1:
                raise SystemExit(
                    "No unconfirmed receipt matches these IDs in the current project."
                )

    def run(self, send):
        while True:
            self.changed.clear()
            try:
                while self.flush_one(send):
                    pass
            except sqlite3.OperationalError:
                # The committed packet remains available when storage recovers.
                time.sleep(5)
            self.changed.wait(5)


class NoRedirect(HTTPRedirectHandler):
    # Never send the ingest credential to a redirect destination.
    def redirect_request(self, *args):
        return None


upstream = build_opener(NoRedirect)


def forward(path, data):
    target = settings["upstream"][path]
    req = Request(
        target["endpoint"],
        data=data,
        headers={**target["headers"], "Content-Type": "application/x-protobuf"},
    )
    with upstream.open(req, timeout=15) as response:
        return (
            response.status,
            response.read(),
            response.headers.get("Content-Type", "application/x-protobuf"),
        )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/ready":
            return self.send_error(404)
        if not hmac.compare_digest(
            self.headers.get("x-local-token", ""), settings["local_token"]
        ):
            return self.send_error(403)
        self.send_response(204)
        self.end_headers()

    def log_message(self, *args):
        pass

    def do_POST(self):
        if self.path not in signals:
            return self.send_error(404)
        if not hmac.compare_digest(
            self.headers.get("x-local-token", ""), settings["local_token"]
        ):
            return self.send_error(403)
        try:
            size = int(self.headers["Content-Length"])
            if not 0 < size <= 67108864:
                return self.send_error(413)
            raw = self.rfile.read(size)
            if self.headers.get("Content-Encoding") == "gzip":
                with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                    raw = stream.read(67108865)
                if len(raw) > 67108864:
                    return self.send_error(413)
            data = queue.route(self.path, raw)
        except (QueueFull, sqlite3.Error):
            return self.send_error(503)
        except (DecodeError, ValueError, TypeError, EOFError, OSError, zlib.error):
            return self.send_error(400)
        try:
            if data:
                status, body, typ = forward(self.path, data)
            else:
                status, body, typ = 200, b"", "application/x-protobuf"
        except HTTPError as e:
            return self.send_error(e.code)
        except (OSError, HTTPException):
            return self.send_error(503)
        self.send_response(status)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    inspect = parser.add_subparsers(dest="command").add_parser("receipts")
    action = inspect.add_mutually_exclusive_group()
    action.add_argument("--received", nargs=2, metavar=("TRACE", "SPAN"))
    action.add_argument("--absent", nargs=2, metavar=("TRACE", "SPAN"))
    args = parser.parse_args()
    os.umask(0o077)
    with configuration_lock():
        settings = load_settings()
        if args.command == "receipts":
            if args.received or args.absent:
                require_stopped(settings)
            UsageQueue(ROOT, settings["project_id"]).receipts(
                args.received, args.absent
            )
            sys.exit(0)
        server = ThreadingHTTPServer(("127.0.0.1", settings["port"]), Handler)
        queue = UsageQueue(ROOT, settings["project_id"])
    threading.Thread(target=queue.run, args=(forward,), daemon=True).start()
    server.serve_forever()
