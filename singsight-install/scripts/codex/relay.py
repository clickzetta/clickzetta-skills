"""Forward native OTLP messages, enriching existing Codex spans in place."""

import gzip
import hashlib
import hmac
import io
import json
import os
import sqlite3
import threading
import time
import uuid
import zlib
from http.client import HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

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
# The pending queue and UUID cache belong to exactly one collector + ingest key.
CONTEXT_TTL = 900
MAX_PENDING_BYTES = 32 * 1024 * 1024
MAX_PENDING_SPANS = 4096
REPLAY_TTL = 86400


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
    def __init__(self, directory, target):
        project = hashlib.sha256(
            json.dumps(target, sort_keys=True).encode()
        ).hexdigest()
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

    def route(self, path, raw):
        msg = signals[path].FromString(raw)
        now = time.time()
        # Commit the outbox before acknowledging any native exporter. Replays
        # use the original trace/span identity, even if batched differently.
        with self.lock, self.db:
            if now - self.last_cleanup > 60:
                self.db.execute(
                    """DELETE FROM context WHERE seen < ? AND NOT EXISTS (
                         SELECT 1 FROM usage WHERE trace=context.trace AND packet IS NOT NULL
                       )""",
                    (now - CONTEXT_TTL,),
                )
                self.db.execute(
                    "DELETE FROM usage WHERE packet IS NULL AND queued < ?",
                    (now - REPLAY_TTL,),
                )
                self.last_cleanup = now
            if path == "/v1/logs":
                for r in msg.resource_logs:
                    for sc in r.scope_logs:
                        for log in sc.log_records:
                            self.remember(log, attributes(log), now)
                direct = raw
            else:
                direct = self.route_spans(msg, now)
        self.changed.set()
        return direct

    def route_spans(self, msg, now):
        count = 0
        inserted = False
        for r in msg.resource_spans:
            for sc in r.scope_spans:
                keep = []
                for sp in sc.spans:
                    attrs = attributes(sp)
                    self.remember(sp, attrs, now)
                    session = conversation(attrs)
                    add(sp, attrs, "gen_ai.conversation.id", session)
                    add(sp, attrs, "session.id", session)
                    if sp.name != "handle_responses" or not any(
                        k in attrs
                        for k in (
                            "gen_ai.usage.input_tokens",
                            "gen_ai.usage.output_tokens",
                        )
                    ):
                        keep.append(sp)
                        continue
                    packet = ExportTraceServiceRequest()
                    group = packet.resource_spans.add(
                        resource=r.resource, schema_url=r.schema_url
                    )
                    group.scope_spans.add(
                        scope=sc.scope, schema_url=sc.schema_url
                    ).spans.add().CopyFrom(sp)
                    result = self.db.execute(
                        "INSERT OR IGNORE INTO usage(trace, span, packet, queued) VALUES(?,?,?,?)",
                        (sp.trace_id, sp.span_id, packet.SerializeToString(), now),
                    )
                    inserted |= result.rowcount > 0
                del sc.spans[:]
                sc.spans.extend(keep)
                count += len(keep)
        if inserted:
            size, rows = self.db.execute(
                "SELECT coalesce(sum(length(packet)),0), count(*) FROM usage WHERE packet IS NOT NULL"
            ).fetchone()
            if size > MAX_PENDING_BYTES or rows > MAX_PENDING_SPANS:
                raise QueueFull()
        return msg.SerializeToString() if count else b""

    def flush_one(self, send):
        now = time.time()
        with self.lock:
            row = self.db.execute(
                """
                SELECT u.trace, u.span, u.packet, c.session, c.model
                FROM usage u LEFT JOIN context c ON c.trace = u.trace
                WHERE u.packet IS NOT NULL AND u.retry <= ?
                AND (c.trace IS NOT NULL OR u.queued <= ?)
                ORDER BY u.queued LIMIT 1
            """,
                (now, now - CONTEXT_TTL),
            ).fetchone()
        if row is None:
            return False
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
            if ExportTraceServiceResponse.FromString(
                body
            ).partial_success.rejected_spans:
                raise OSError("Collector rejected usage span")
        except (OSError, HTTPException, DecodeError):
            with self.lock, self.db:
                self.db.execute(
                    "UPDATE usage SET retry=? WHERE trace=? AND span=?",
                    (now + 30, trace, span),
                )
        else:
            with self.lock, self.db:
                self.db.execute(
                    "UPDATE usage SET packet=NULL, queued=? WHERE trace=? AND span=?",
                    (now, trace, span),
                )
        return True

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
    settings = json.loads(Path(__file__).with_name("relay.json").read_text())
    os.umask(0o077)
    server = ThreadingHTTPServer(("127.0.0.1", settings["port"]), Handler)
    queue = UsageQueue(Path(__file__).parent, settings["upstream"])
    threading.Thread(target=queue.run, args=(forward,), daemon=True).start()
    server.serve_forever()
