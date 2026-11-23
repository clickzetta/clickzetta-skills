"""Tests for scripts/singsight.py. Run: python3 -m unittest discover -s clickzetta-singsight-operate/scripts/tests"""

import contextlib
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import singsight  # noqa: E402

TIME = {"time_start": "2026-11-19T00:00:00Z", "time_end": "2026-11-20T00:00:00Z"}


class FakeSingSight(BaseHTTPRequestHandler):
    requests: list = []
    tokens_issued = 0
    reject_first_bearer = False

    def log_message(self, *args):
        pass

    def _reply(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self, method):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length)) if length else None
        cls = type(self)
        if self.path.startswith("/open/api/v1/appSecretKey/generateAuthToken"):
            cls.tokens_issued += 1
            return self._reply(200, {"success": True, "data": {"token": f"t{cls.tokens_issued}"}})
        cls.requests.append({"method": method, "path": self.path, "body": body,
                             "auth": self.headers.get("Authorization")})
        if cls.reject_first_bearer and self.headers.get("Authorization") == "Bearer t1":
            return self._reply(401, {"success": False, "code": "401", "message": "expired"})
        if method == "DELETE":
            return self._reply(200, {"success": True, "data": None})
        if self.path in FakeSingSight.fixtures:
            return self._reply(200, {"success": True, "data": FakeSingSight.fixtures[self.path]})
        if self.path.startswith("/open/api/v1/eval/jobs/404"):
            return self._reply(200, {"success": False, "code": "8003", "message": "eval job not found"})
        if self.path.startswith("/open/api/v1/mcp/schema-context"):
            return self._reply(200, {"success": True, "data": {"schema": "proj_schema"}})
        if self.path.startswith("/open/api/v1/eval/jobs/7"):
            return self._reply(200, {"success": True, "data": {"id": 7, "status": "COMPLETE"}})
        return self._reply(200, {"success": True, "data": {"items": list(range(150)), "echo": body}})

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_DELETE(self):
        self._handle("DELETE")

    def do_PUT(self):
        self._handle("PUT")


FakeSingSight.fixtures = {
    "/open/api/v1/eval/jobs": [
        {"id": 7, "status": "COMPLETE", "datasetId": 5, "evaluatorId": 3},
        {"id": 8, "status": "RUNNING", "datasetId": None, "evaluatorId": 4},
    ],
    "/open/api/v1/eval/jobs/8": {"id": 8, "status": "RUNNING"},
    "/open/api/v1/eval/jobs/11": {"id": 11, "name": "created only", "status": "ACTIVE"},
    "/open/api/v1/eval/datasets/5": {"id": 5, "name": "used", "activeImports": 0},
    "/open/api/v1/eval/datasets/6": {"id": 6, "name": "free", "datasetTag": "free", "activeImports": 0},
    "/open/api/v1/evaluator": [
        {"id": 1, "name": "Builtin", "builtIn": True},
        {"id": 3, "name": "Used", "builtIn": False},
        {"id": 9, "name": "Free", "builtIn": False},
    ],
}


class SingSightCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeSingSight)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        FakeSingSight.requests = []
        FakeSingSight.tokens_issued = 0
        FakeSingSight.reject_first_bearer = False
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.config = root / "singsight.toml"
        self.config.write_text(
            'default_project = "a"\n'
            f'[projects.a]\nbase_url = "http://127.0.0.1:{self.server.server_port}"\napi_key_env = "SS_KEY"\n'
            'cz_profile = "prof"\nworkspace = "ws"\n'
            '[projects.b]\nbase_url = "http://127.0.0.1:1"\napi_key = "k"\n')
        self.config.chmod(0o600)
        self.env = mock.patch.dict(os.environ, {"SINGSIGHT_CONFIG": str(self.config), "SS_KEY": "sk_test"})
        self.env.start()
        self.cache = mock.patch.object(singsight, "CACHE_DIR", root / "cache")
        self.cache.start()

    def tearDown(self):
        self.cache.stop()
        self.env.stop()
        self.tmp.cleanup()

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = singsight.main(list(argv))
        def parse(text):
            try:
                return json.loads(text) if text.strip() else None
            except ValueError:
                raise AssertionError(f"non-JSON output: {text[:300]!r}")
        return code, parse(out.getvalue()), parse(err.getvalue())

    def test_global_options_work_before_and_after_subcommand(self):
        _, before, _ = self.run_cli("--project", "b", "config")
        _, after, _ = self.run_cli("config", "--project", "b")
        self.assertEqual(before["data"]["name"], "b")
        self.assertEqual(after["data"]["name"], "b")
        self.assertEqual(before["data"]["api_key"], "(set)")
        self.assertNotIn("sk_test", json.dumps(before))

    def test_world_readable_config_with_api_key_warns(self):
        self.config.chmod(0o644)
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            singsight.main(["--project", "b", "config"])
        self.assertIn("chmod 600", err.getvalue())

    def test_token_is_cached_and_refreshed_on_401(self):
        self.run_cli("datasets")
        self.run_cli("datasets")
        self.assertEqual(FakeSingSight.tokens_issued, 1)
        token_files = list((Path(self.tmp.name) / "cache").glob("token-*.json"))
        self.assertEqual(oct(token_files[0].stat().st_mode & 0o777), "0o600")

        FakeSingSight.reject_first_bearer = True
        code, out, _ = self.run_cli("datasets")
        self.assertEqual(code, 0)
        self.assertEqual(FakeSingSight.tokens_issued, 2)
        self.assertEqual(FakeSingSight.requests[-1]["auth"], "Bearer t2")

    def test_upstream_failure_is_reported_on_stderr(self):
        code, out, err = self.run_cli("eval-status", "404")
        self.assertEqual(code, 1)
        self.assertIsNone(out)
        self.assertEqual(err, {"success": False, "code": "8003", "message": "eval job not found", "retryable": False})

    def test_large_lists_are_truncated(self):
        _, out, _ = self.run_cli("eval-jobs")
        self.assertTrue(out["truncated"])
        self.assertEqual(len(out["data"]["items"]), 100)
        self.assertEqual(FakeSingSight.requests[-1]["path"], "/open/api/v1/eval/jobs/page?page=1&pageSize=50")

    def test_oversized_output_goes_to_private_file(self):
        _, out, _ = self.run_cli("eval-jobs", "--max-bytes", "100")
        path = Path(out["output_file"])
        self.assertEqual(len(json.loads(path.read_text())["items"]), 150)
        self.assertEqual(oct(path.stat().st_mode & 0o777), "0o600")

    def test_write_commands_dry_run_without_yes(self):
        code, out, _ = self.run_cli("trigger-eval", "--name", " job ", "--evaluator-id", "3",
                                    "--filter", json.dumps(TIME), "--sampling-rate", "0.5")
        self.assertEqual(code, 0)
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["request"]["body"], {"name": "job", "evaluatorId": 3, "granularity": "TRACE",
                                                  "samplingRate": 0.5, "filter": TIME})
        self.assertEqual(FakeSingSight.requests, [])

        self.run_cli("trigger-eval", "--name", "job", "--evaluator-id", "3", "--dataset-id", "9", "--yes")
        self.assertEqual(FakeSingSight.requests[-1]["body"]["datasetId"], 9)
        self.assertNotIn("filter", FakeSingSight.requests[-1]["body"])

    def test_trigger_eval_can_create_without_running(self):
        _, out, _ = self.run_cli("trigger-eval", "--name", "job", "--evaluator-id", "3",
                                 "--filter", json.dumps(TIME), "--no-run")
        self.assertEqual(out["request"]["path"], "/open/api/v1/eval/jobs?runNow=false")
        _, out, _ = self.run_cli("trigger-eval", "--name", "job", "--evaluator-id", "3", "--filter", json.dumps(TIME))
        self.assertEqual(out["request"]["path"], "/open/api/v1/eval/jobs")

    def test_rerun_dry_run_then_queue(self):
        code, out, _ = self.run_cli("rerun", "7")
        self.assertEqual(code, 0)
        self.assertTrue(out["dry_run"])
        self.assertNotIn("irreversible", out)
        self.assertEqual(out["target"]["status"], "COMPLETE")
        self.assertFalse(any(r["method"] == "POST" for r in FakeSingSight.requests))

        self.run_cli("rerun", "7", "--yes")
        self.assertEqual((FakeSingSight.requests[-1]["method"], FakeSingSight.requests[-1]["path"],
                          FakeSingSight.requests[-1]["body"]), ("POST", "/open/api/v1/eval/jobs/7/runs", {}))
        _, out, _ = self.run_cli("rerun", "7", "--source-run-id", "3")
        self.assertEqual(out["request"]["body"], {"sourceRunId": 3})
        self.assertIn("sourceRun", out["target"])

    def test_rerun_refuses_a_job_with_an_active_run(self):
        code, _, err = self.run_cli("rerun", "8")
        self.assertEqual((code, err["code"]), (1, "TARGET_BUSY"))

    def test_stop_eval_only_for_active_jobs(self):
        code, _, err = self.run_cli("stop-eval", "7")
        self.assertEqual(err["code"], "TARGET_NOT_RUNNING")
        _, out, _ = self.run_cli("stop-eval", "8")
        self.assertEqual(out["request"], {"method": "PUT", "path": "/open/api/v1/eval/jobs/8/stop", "body": None})
        self.assertFalse(any(r["method"] == "PUT" for r in FakeSingSight.requests))
        self.run_cli("stop-eval", "8", "--yes")
        self.assertEqual(FakeSingSight.requests[-1]["method"], "PUT")

    def test_run_history_and_results_of_a_run(self):
        self.run_cli("eval-runs", "7")
        self.assertEqual(FakeSingSight.requests[-1]["path"], "/open/api/v1/eval/jobs/7/runs?page=1&pageSize=20")
        self.run_cli("eval-run", "7", "3")
        self.assertEqual(FakeSingSight.requests[-1]["path"], "/open/api/v1/eval/jobs/7/runs/3")
        self.run_cli("eval-results", "7", "--run-id", "3", "--order-by", "score", "--order", "ASC")
        self.assertEqual(FakeSingSight.requests[-1]["path"],
                         "/open/api/v1/eval/jobs/7/results?page=1&pageSize=20&runId=3&orderBy=score&order=ASC")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit_info:
            singsight.main(["eval-results", "7", "--order-by", "raw_result"])
        self.assertEqual(exit_info.exception.code, 2)

    def test_job_created_without_a_run_is_idle(self):
        _, out, _ = self.run_cli("eval-status", "11", "--wait", "30")
        self.assertEqual(out["data"]["status"], "ACTIVE")
        self.assertNotIn("wait_timed_out", out["data"])
        _, out, _ = self.run_cli("delete-eval-job", "11")
        self.assertTrue(out["dry_run"])

    def test_eval_source_must_be_exactly_one(self):
        code, _, err = self.run_cli("preview", "--filter", json.dumps(TIME), "--dataset-id", "1")
        self.assertEqual((code, err["code"]), (2, "INVALID_ARGUMENT"))
        code, _, _ = self.run_cli("preview")
        self.assertEqual(code, 2)

    def test_filter_validation(self):
        cases = [
            {**TIME, "unknown": 1},
            {"time_start": "2026-11-19T00:00:00", "time_end": TIME["time_end"]},
            {"time_start": TIME["time_end"], "time_end": TIME["time_start"]},
            {**TIME, "service_name": "svc"},
            {**TIME, "service_name": {"any_of": ["svc"]}},
            {**TIME, "has_error": "yes"},
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(singsight.SingSightError):
                singsight.validate_filter(case, require_time=True)
        ok = {**TIME, "service_name": {"none_of": ["a"]}, "raw_span_attributes": {"k": "v"}}
        self.assertEqual(singsight.validate_filter(ok, require_time=True), ok)

    def test_filter_options_sends_compact_filter(self):
        self.run_cli("filter-options", "--filter", json.dumps(TIME))
        self.assertIn("filter=%7B%22time_start%22", FakeSingSight.requests[-1]["path"])

    def test_add_traces_payloads(self):
        _, out, _ = self.run_cli("add-traces", "5", "--eval-job-id", "7", "--max-score", "0.5")
        self.assertEqual(out["request"]["body"], {"evalJobId": 7, "jobScope": "RESULTS", "maxScore": 0.5})
        _, out, _ = self.run_cli("add-traces", "5", "--eval-job-id", "7", "--run-id", "3")
        self.assertEqual(out["request"]["body"], {"evalJobId": 7, "jobScope": "RESULTS", "runId": 3})
        ids = "a" * 32 + "," + "b" * 32 + "," + "a" * 32
        _, out, _ = self.run_cli("add-traces", "5", "--trace-ids", ids)
        self.assertEqual(out["request"]["body"], {"traceIds": ["a" * 32, "b" * 32]})
        for argv in (["--eval-job-id", "7", "--job-scope", "FILTER", "--min-score", "0.1"],
                     ["--eval-job-id", "7", "--job-scope", "FILTER", "--run-id", "3"],
                     ["--trace-ids", "a" * 32, "--run-id", "3"],
                     ["--eval-job-id", "7", "--trace-ids", "a" * 32],
                     ["--trace-ids", "xyz"],
                     ["--trace-ids", ",".join(f"{i:032x}" for i in range(101))]):
            with self.subTest(argv=argv):
                code, _, _ = self.run_cli("add-traces", "5", *argv)
                self.assertEqual(code, 2)

    def test_custom_evaluator_translation(self):
        spec = {"name": " E ", "evaluator_config": {"step_prompts": [{"step": " s1 ", "prompt": "p"}]},
                "score_type": "BOOLEAN", "score_prompt": "sp"}
        self.assertEqual(singsight.validate_custom_evaluator(spec), {
            "name": "E", "evaluatorConfig": {"stepPrompts": [{"step": "s1", "prompt": "p"}]},
            "scoreType": "BOOLEAN", "scoreMin": 0.0, "scoreMax": 1.0, "scorePrompt": "sp"})
        bad = {**spec, "evaluator_config": {"step_prompts": [{"step": "s", "prompt": "p"}] * 2}}
        with self.assertRaises(singsight.SingSightError):
            singsight.validate_custom_evaluator(bad)

    def test_wait_returns_on_terminal_status(self):
        _, out, _ = self.run_cli("eval-status", "7", "--wait", "30")
        self.assertEqual(out["data"]["status"], "COMPLETE")
        self.assertEqual(len(FakeSingSight.requests), 1)

    def test_delete_dry_run_shows_target_and_yes_sends_delete(self):
        code, out, _ = self.run_cli("delete-eval-job", "7")
        self.assertEqual(code, 0)
        self.assertTrue(out["dry_run"] and out["irreversible"])
        self.assertEqual(out["target"]["status"], "COMPLETE")
        self.assertFalse(any(r["method"] == "DELETE" for r in FakeSingSight.requests))

        for argv, path in ((["delete-eval-job", "7"], "/open/api/v1/eval/jobs/7"),
                           (["delete-dataset", "6"], "/open/api/v1/eval/datasets/6"),
                           (["delete-evaluator", "9"], "/open/api/v1/evaluator/9")):
            with self.subTest(argv=argv):
                code, out, _ = self.run_cli(*argv, "--yes")
                self.assertEqual(code, 0)
                self.assertEqual(FakeSingSight.requests[-1]["method"], "DELETE")
                self.assertEqual(FakeSingSight.requests[-1]["path"], path)
                self.assertIn("deleted", out["data"])

    def test_delete_guards(self):
        cases = [
            (["delete-eval-job", "8"], "TARGET_BUSY"),
            (["delete-dataset", "5"], "TARGET_IN_USE"),
            (["delete-evaluator", "3"], "TARGET_IN_USE"),
            (["delete-evaluator", "1"], "BUILT_IN_EVALUATOR"),
            (["delete-evaluator", "2"], "NOT_FOUND"),
        ]
        for argv, expected in cases:
            with self.subTest(argv=argv):
                code, _, err = self.run_cli(*argv, "--yes")
                self.assertEqual((code, err["code"]), (1, expected))
        self.assertIn("[7]", self.run_cli("delete-dataset", "5")[2]["message"])
        self.assertFalse(any(r["method"] == "DELETE" for r in FakeSingSight.requests))

    def test_sql_is_pinned_to_project_binding(self):
        with mock.patch.object(singsight.subprocess, "run", return_value=mock.Mock(returncode=0)) as run:
            code, _, _ = self.run_cli("sql", "SELECT 1")
        self.assertEqual(code, 0)
        self.assertEqual(run.call_args.args[0], [
            "cz-cli", "sql", "-p", "prof", "--workspace", "ws", "-s", "proj_schema",
            "--format", "json", "-e", "SELECT 1"])
        code, _, err = self.run_cli("sql", "--project", "b", "SELECT 1")
        self.assertEqual((code, err["code"]), (1, "SINGSIGHT_NOT_CONFIGURED"))


if __name__ == "__main__":
    unittest.main()
