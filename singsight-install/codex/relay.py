"""Forward native OTLP messages, enriching existing Codex spans in place."""

import gzip
import hmac
import io
import json
import threading
import time
import uuid
import zlib
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
)

signals = {
    "/v1/traces": ExportTraceServiceRequest,
    "/v1/logs": ExportLogsServiceRequest,
}
context = {}
condition = threading.Condition()


def attributes(item):
    return {
        a.key: getattr(a.value, a.value.WhichOneof("value"))
        for a in item.attributes
        if a.value.WhichOneof("value")
    }


def add(item, attrs, key, value):
    if key not in attrs and value:
        field = item.attributes.add(key=key)
        field.value.string_value = str(value)


def conversation(attrs):
    for key in ("gen_ai.conversation.id", "conversation.id", "thread_id", "thread.id"):
        value = attrs.get(key)
        try:
            return str(uuid.UUID(str(value)))
        except ValueError:
            pass


def remember(trace, session, model):
    if not trace or not session:
        return
    with condition:
        now = time.monotonic()
        if len(context) >= 8192:
            for key in sorted(context, key=lambda k: context[k][2])[:1024]:
                del context[key]
        old = context.get(trace)
        if old and now - old[2] < 900 and old[0] != session:
            session = None  # Never guess between multiple conversations.
        context[trace] = (session, model or (old and old[1]), now)
        condition.notify_all()


def lookup(trace, wait=0):
    with condition:
        if wait and trace not in context:
            condition.wait_for(lambda: trace in context, timeout=wait)
        value = context.get(trace)
        return (
            value[:2] if value and time.monotonic() - value[2] < 900 else (None, None)
        )


def enrich(path, payload):
    msg = signals[path].FromString(payload)
    if path == "/v1/logs":
        for resource in msg.resource_logs:
            for scope in resource.scope_logs:
                for item in scope.log_records:
                    attrs = attributes(item)
                    remember(item.trace_id, conversation(attrs), attrs.get("model"))
        return payload
    items = [sp for r in msg.resource_spans for sc in r.scope_spans for sp in sc.spans]
    for sp in items:
        attrs = attributes(sp)
        remember(sp.trace_id, conversation(attrs), attrs.get("model"))
    deadline = time.monotonic() + 1.5
    for sp in items:
        attrs = attributes(sp)
        chat = sp.name == "handle_responses" and any(
            k in attrs
            for k in ("gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens")
        )
        session = conversation(attrs)
        linked, model = lookup(
            sp.trace_id,
            max(0, deadline - time.monotonic()) if chat and not session else 0,
        )
        if chat:
            session = session or linked
        add(sp, attrs, "gen_ai.conversation.id", session)
        add(sp, attrs, "session.id", session)
        if chat:
            model = attrs.get("gen_ai.request.model") or attrs.get("model") or model
            add(sp, attrs, "gen_ai.operation.name", "chat")
            add(sp, attrs, "gen_ai.request.model", model)
            sp.name = "chat" if not model else "chat " + model
    return msg.SerializeToString()


class NoRedirect(HTTPRedirectHandler):
    # Never send the ingest credential to a redirect destination.
    def redirect_request(self, *args):
        return None


upstream = build_opener(NoRedirect)


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
            data = enrich(self.path, raw)
        except (DecodeError, ValueError, TypeError, EOFError, OSError, zlib.error):
            return self.send_error(400)
        target = settings["upstream"][self.path]
        req = Request(
            target["endpoint"],
            data=data,
            headers={**target["headers"], "Content-Type": "application/x-protobuf"},
        )
        try:
            with upstream.open(req, timeout=15) as res:
                status, body, typ = (
                    res.status,
                    res.read(),
                    res.headers.get("Content-Type", "application/x-protobuf"),
                )
        except HTTPError as e:
            return self.send_error(e.code)
        except OSError:
            return self.send_error(503)
        self.send_response(status)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    settings = json.loads(Path(__file__).with_name("relay.json").read_text())
    ThreadingHTTPServer(("127.0.0.1", settings["port"]), Handler).serve_forever()
