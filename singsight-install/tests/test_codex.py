import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "codex"))
import relay
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
    ExportLogsServiceRequest,
)
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
)


def spans(raw):
    return [
        s
        for r in ExportTraceServiceRequest.FromString(raw).resource_spans
        for sc in r.scope_spans
        for s in sc.spans
    ]


class CodexMappingTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.queue = self.open_queue("project A")
        self.trace = uuid.uuid4().bytes
        self.session = str(uuid.uuid4())
        self.request = ExportTraceServiceRequest()
        self.batch = self.request.resource_spans.add().scope_spans.add()
        self.delivered = []

    def open_queue(self, project):
        queue = relay.UsageQueue(self.root, project)
        self.addCleanup(queue.db.close)
        return queue

    def log(self, session):
        msg = ExportLogsServiceRequest()
        row = (
            msg.resource_logs.add()
            .scope_logs.add()
            .log_records.add(trace_id=self.trace)
        )
        row.attributes.add(key="conversation.id").value.string_value = session
        raw = msg.SerializeToString()
        self.assertEqual(self.queue.route("/v1/logs", raw), raw)

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

    def send(self, path, raw):
        self.assertEqual(path, "/v1/traces")
        self.delivered.extend(spans(raw))
        return 200, b"", "application/x-protobuf"

    def route(self):
        return self.queue.route("/v1/traces", self.request.SerializeToString())

    def test_one_real_completion_counts_once_even_if_rebatched(self):
        self.log(self.session)
        native = self.add_span(
            "handle_responses",
            **{
                "gen_ai.usage.input_tokens": 27355,
                "gen_ai.usage.output_tokens": 5,
                "gen_ai.usage.cache_read.input_tokens": 12928,
            },
        )
        self.add_span("handle_responses")
        self.add_span("turn/start", **{"codex.turn.token_usage.total_tokens": 27360})
        self.assertEqual(
            [s.name for s in spans(self.route())], ["handle_responses", "turn/start"]
        )
        self.assertTrue(self.queue.flush_one(self.send))
        del self.batch.spans[1:]
        self.assertEqual(self.route(), b"")
        self.assertFalse(self.queue.flush_one(self.send))
        self.assertEqual([s.span_id for s in self.delivered], [native])
        attrs = relay.attributes(self.delivered[0])
        self.assertEqual(attrs["gen_ai.operation.name"], "chat")
        self.assertEqual(attrs["gen_ai.conversation.id"], self.session)
        self.assertEqual(
            attrs["gen_ai.usage.input_tokens"] + attrs["gen_ai.usage.output_tokens"],
            27360,
        )

    def test_late_log_after_restart_attributes_tokens_exactly_once(self):
        native = self.add_span(
            "handle_responses",
            **{"gen_ai.usage.input_tokens": 20, "gen_ai.usage.output_tokens": 3},
        )
        with patch.object(relay.time, "time", return_value=1000):
            self.assertEqual(self.route(), b"")
        with patch.object(relay.time, "time", return_value=1120):
            self.queue = self.open_queue("project A")
            self.assertFalse(self.queue.flush_one(self.send))
            self.log(self.session)
            self.assertTrue(self.queue.flush_one(self.send))
            self.route()
            self.assertFalse(self.queue.flush_one(self.send))
        self.assertEqual([s.span_id for s in self.delivered], [native])
        attrs = relay.attributes(self.delivered[0])
        self.assertEqual(attrs["session.id"], self.session)
        self.assertEqual(
            attrs["gen_ai.usage.input_tokens"] + attrs["gen_ai.usage.output_tokens"], 23
        )

    def test_conflicting_context_does_not_invent_session(self):
        self.log(self.session)
        self.log(str(uuid.uuid4()))
        self.add_span(
            "handle_responses", **{"gen_ai.usage.output_tokens": 5, "thread.id": "7"}
        )
        self.route()
        self.queue.flush_one(self.send)
        self.assertNotIn("session.id", relay.attributes(self.delivered[0]))

    def test_parent_can_arrive_later_in_same_batch(self):
        self.add_span("handle_responses", **{"gen_ai.usage.input_tokens": 12})
        self.add_span("codex.sampling", **{"conversation.id": self.session})
        self.route()
        self.queue.flush_one(self.send)
        self.assertEqual(
            relay.attributes(self.delivered[0])["session.id"], self.session
        )

    def test_pending_usage_is_isolated_by_project(self):
        self.log(self.session)
        self.add_span("handle_responses", **{"gen_ai.usage.output_tokens": 12})
        self.route()
        self.assertFalse(self.open_queue("project B").flush_one(self.send))
        self.assertTrue(self.queue.flush_one(self.send))

    def test_failed_send_retains_late_session_until_retry(self):
        def unavailable(path, data):
            raise ConnectionRefusedError("Collector unavailable")

        self.add_span("handle_responses", **{"gen_ai.usage.input_tokens": 2})
        with patch.object(relay.time, "time", return_value=1000):
            self.route()
            self.log(self.session)
            self.assertTrue(self.queue.flush_one(unavailable))
            self.assertFalse(self.queue.flush_one(self.send))
        with patch.object(relay.time, "time", return_value=1001 + relay.CONTEXT_TTL):
            self.queue.route("/v1/logs", b"")  # trigger cache expiry
            self.assertTrue(self.queue.flush_one(self.send))
            self.assertFalse(self.queue.flush_one(self.send))
        self.assertEqual(
            relay.attributes(self.delivered[0])["session.id"], self.session
        )

    def test_queue_full_rolls_back_before_exporter_retries(self):
        self.add_span("handle_responses", **{"gen_ai.usage.input_tokens": 12})
        with (
            patch.object(relay, "MAX_PENDING_SPANS", 0),
            self.assertRaises(relay.QueueFull),
        ):
            self.route()
        self.log(self.session)
        self.assertFalse(self.queue.flush_one(self.send))
        self.route()
        self.assertTrue(self.queue.flush_one(self.send))

    def test_log_after_context_ttl_still_attaches_to_usage(self):
        self.add_span("handle_responses", **{"gen_ai.usage.output_tokens": 1})
        with patch.object(relay.time, "time", return_value=1000):
            self.route()
        with patch.object(relay.time, "time", return_value=1001 + relay.CONTEXT_TTL):
            self.assertFalse(self.queue.flush_one(self.send))
            self.log(self.session)
            self.assertTrue(self.queue.flush_one(self.send))
        self.assertEqual(
            relay.attributes(self.delivered[0])["session.id"], self.session
        )

    def test_full_queue_commits_context_even_if_new_usage_is_rejected(self):
        first = self.add_span("handle_responses", **{"gen_ai.usage.output_tokens": 7})
        with patch.object(relay, "MAX_PENDING_SPANS", 1):
            self.route()
            self.assertFalse(self.queue.flush_one(self.send))
            del self.batch.spans[:]
            self.add_span("codex.sampling", **{"conversation.id": self.session})
            self.trace = uuid.uuid4().bytes
            second = self.add_span(
                "handle_responses", **{"gen_ai.usage.output_tokens": 3}
            )
            with self.assertRaises(relay.QueueFull):
                self.route()
            self.assertTrue(self.queue.flush_one(self.send))
            self.assertEqual(
                relay.attributes(self.delivered[0])["session.id"], self.session
            )
            self.route()
            self.log(self.session)
            self.assertTrue(self.queue.flush_one(self.send))
            self.assertFalse(self.queue.flush_one(self.send))
        self.assertEqual([s.span_id for s in self.delivered], [first, second])

    def test_ack_loss_survives_restart_without_double_submission(self):
        original = self.add_span(
            "handle_responses", **{"gen_ai.usage.output_tokens": 9}
        )
        self.log(self.session)
        self.route()

        def accepted_but_ack_lost(path, raw):
            self.send(path, raw)
            raise ConnectionResetError("receipt lost")

        self.assertTrue(self.queue.flush_one(accepted_but_ack_lost))
        self.queue = self.open_queue("project A")
        with patch.object(relay.time, "time", return_value=relay.time.time() + 172800):
            self.route()
            self.assertFalse(self.queue.flush_one(self.send))
            self.queue.receipts(received=[self.trace.hex(), original.hex()])
            self.route()
            self.assertFalse(self.queue.flush_one(self.send))
        self.assertEqual([s.span_id for s in self.delivered], [original])

    def test_unconfirmed_but_verified_absent_can_retry_once(self):
        original = self.add_span(
            "handle_responses", **{"gen_ai.usage.output_tokens": 9}
        )
        self.log(self.session)
        self.route()

        def uncertain(*args):
            raise TimeoutError()

        self.assertTrue(self.queue.flush_one(uncertain))
        self.queue.receipts(absent=[self.trace.hex(), original.hex()])
        self.assertTrue(self.queue.flush_one(self.send))
        self.assertFalse(self.queue.flush_one(self.send))
        self.assertEqual([s.span_id for s in self.delivered], [original])
