import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codex"))
import relay
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
    ExportLogsServiceRequest,
)
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
)


class CodexMappingTest(unittest.TestCase):
    def setUp(self):
        self.trace = uuid.uuid4().bytes
        self.session = str(uuid.uuid4())
        self.request = ExportTraceServiceRequest()
        self.batch = self.request.resource_spans.add().scope_spans.add()

    def log(self, session):
        msg = ExportLogsServiceRequest()
        row = (
            msg.resource_logs.add()
            .scope_logs.add()
            .log_records.add(trace_id=self.trace)
        )
        row.attributes.add(key="conversation.id").value.string_value = session
        raw = msg.SerializeToString()
        self.assertEqual(relay.enrich("/v1/logs", raw), raw)

    def add_span(self, name, **attrs):
        sp = self.batch.spans.add(
            name=name, trace_id=self.trace, span_id=uuid.uuid4().bytes[:8]
        )
        for k, v in attrs.items():
            field = sp.attributes.add(key=k).value
            if isinstance(v, int):
                field.int_value = v
            else:
                field.string_value = v
        return sp.span_id

    def result(self):
        raw = self.request.SerializeToString()
        mapped = relay.enrich("/v1/traces", raw)
        self.assertEqual(mapped, relay.enrich("/v1/traces", mapped))
        return (
            ExportTraceServiceRequest.FromString(mapped)
            .resource_spans[0]
            .scope_spans[0]
            .spans
        )

    def test_one_real_completion_counts_once(self):
        self.log(self.session)
        native = self.add_span(
            "handle_responses",
            **{
                "gen_ai.usage.input_tokens": 27355,
                "gen_ai.usage.output_tokens": 5,
                "gen_ai.usage.cache_read.input_tokens": 12928,
            },
        )
        self.add_span("handle_responses")  # streaming fragment
        self.add_span("turn/start", **{"codex.turn.token_usage.total_tokens": 27360})
        spans = self.result()
        self.assertEqual(len(spans), 3)
        chats = [
            s
            for s in spans
            if relay.attributes(s).get("gen_ai.operation.name") == "chat"
        ]
        self.assertEqual([s.span_id for s in chats], [native])
        attrs = relay.attributes(chats[0])
        self.assertEqual(attrs["session.id"], self.session)
        self.assertEqual(attrs["gen_ai.conversation.id"], self.session)
        self.assertEqual(
            attrs["gen_ai.usage.input_tokens"] + attrs["gen_ai.usage.output_tokens"],
            27360,
        )

    def test_conflicting_context_does_not_invent_session(self):
        self.log(self.session)
        self.log(str(uuid.uuid4()))
        self.add_span(
            "handle_responses", **{"gen_ai.usage.output_tokens": 5, "thread.id": "7"}
        )
        self.assertNotIn("session.id", relay.attributes(self.result()[0]))

    def test_parent_can_arrive_later_in_same_batch(self):
        self.add_span("handle_responses", **{"gen_ai.usage.input_tokens": 12})
        self.add_span("codex.sampling", **{"conversation.id": self.session})
        self.assertEqual(relay.attributes(self.result()[0])["session.id"], self.session)
