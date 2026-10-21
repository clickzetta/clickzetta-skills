"""Offline semantics; SQLite fixtures are not ClickZetta syntax verification."""
import importlib.util
import re
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "history_query.py"
SPEC = importlib.util.spec_from_file_location("history_query", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_query = MODULE.build_query
A = "demo.raw.events"
B = "demo.billing_dt.effective"
START, END = "2026-10-13 20:00:00", "2026-10-20 20:00:00"


def execute_fixture(sql, records):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.create_function("CONCAT", -1, lambda *parts: "".join(parts))
    connection.execute("ATTACH DATABASE ':memory:' AS information_schema")
    connection.execute("""CREATE TABLE information_schema.job_history(
        job_id TEXT, input_objects TEXT, output_objects TEXT, start_time TEXT,
        pt_date TEXT, job_type TEXT, job_sub_type TEXT, job_creator TEXT,
        status TEXT, query_tag TEXT)""")
    connection.executemany(
        "INSERT INTO information_schema.job_history VALUES (?,?,?,?,?,?,?,?,?,?)",
        records,
    )
    # ISO fixture timestamps need no CAST in SQLite; the generated SQL is unchanged.
    fixture_sql = re.sub(r"CAST\('([^']+)' AS TIMESTAMP\)", r"'\1'", sql)
    try:
        return [dict(row) for row in connection.execute(fixture_sql)]
    finally:
        connection.close()


def record(job, inputs, outputs, timestamp="2026-10-14 00:00:00", status="SUCCEED"):
    return (job, inputs, outputs, timestamp, timestamp[:10], "SQL_JOB",
            "DEFAULT_JOB_SUB_TYPE", "actor", status, None)


class HistoryQueryTests(unittest.TestCase):
    def test_exact_membership_multiple_roots_and_empty_outputs(self):
        records = [
            record("both", A + "," + B, "demo.public.out"),
            record("similar", "demo.rawXevents", "demo.public.wrong"),
            record("correction", A + "_corrections", "demo.public.wrong"),
            record("null", None, "demo.public.wrong"),
            record("empty", A, "", status="FAILED"),
            record("nullout", A, None),
        ]
        rows = execute_fixture(build_query([A, B], "readers", START, END), records)
        self.assertEqual(sum(r["jobs"] for r in rows if r["source_object"] == A), 3)
        self.assertEqual(sum(r["jobs"] for r in rows if r["source_object"] == B), 1)
        self.assertFalse(any(r["output_objects"] == "demo.public.wrong" for r in rows))
        self.assertTrue(any(r["status"] == "FAILED" and r["output_objects"] == "" for r in rows))
        self.assertTrue(any(r["output_objects"] is None for r in rows))

    def test_underscore_is_literal_and_all_list_positions_match(self):
        target = "demo.raw.event_details_all"
        records = [
            record("wildcard", "demo.raw.eventXdetailsXall", "demo.public.wrong"),
            record("first", target + ",demo.raw.other", "demo.public.out"),
            record("last", "demo.raw.other," + target, "demo.public.out"),
            record("middle", "demo.raw.left," + target + ",demo.raw.right", "demo.public.out"),
        ]
        rows = execute_fixture(build_query([target], "readers", START, END), records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["jobs"], 3)

    def test_half_open_window(self):
        records = [
            record("start", A, "demo.public.out", START),
            record("before", A, "demo.public.out", "2026-10-13 19:59:59"),
            record("end", A, "demo.public.out", END),
        ]
        rows = execute_fixture(build_query([A], "readers", START, END), records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["jobs"], 1)
        self.assertEqual(rows[0]["sample_job_id"], "start")

    def test_writers_group_inputs_for_each_matching_output(self):
        records = [
            record("write", "demo.raw.source", A + "," + B),
            record("read", A, "demo.public.other"),
        ]
        rows = execute_fixture(build_query([A, B], "writers", START, END), records)
        self.assertEqual({r["source_object"] for r in rows}, {A, B})
        self.assertTrue(all(r["input_objects"] == "demo.raw.source" and r["jobs"] == 1 for r in rows))

    def test_internal_output_lists_are_preserved(self):
        outputs = "demo.public.out,demo.public.123__incr__456"
        rows = execute_fixture(build_query([A], "readers", START, END),
                               [record("refresh", A, outputs)])
        self.assertEqual(rows[0]["output_objects"], outputs)

    def test_duplicate_roots_do_not_multiply_counts(self):
        rows = execute_fixture(build_query([A, A], "readers", START, END),
                               [record("one", A, "demo.public.out")])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["jobs"], 1)

    def test_invalid_inputs_are_rejected(self):
        invalid = [
            ([], "readers", START, END),
            (["demo.raw.x'; DROP TABLE x"], "readers", START, END),
            (["demo.raw.x\n"], "readers", START, END),
            (["raw.table"], "readers", START, END),
            (["demo.raw.`quoted`"], "readers", START, END),
            ([A], "delete", START, END),
            ([A], "readers", END, START),
            ([A], "readers", START, START),
            ([A], "readers", "2026-02-30 00:00:00", END),
            ([A], "readers", "2026-10-13 00:00:00'; SELECT 1", END),
        ]
        for args in invalid:
            with self.subTest(args=args), self.assertRaises(ValueError):
                build_query(*args)

    def test_cli_only_emits_sql(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--direction", "readers",
             "--object", A, "--start", START, "--end", END],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(result.stdout, build_query([A], "readers", START, END) + "\n")
        self.assertEqual(result.stderr, "")

    def test_cli_invalid_input_fails_without_sql(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--direction", "readers",
             "--object", "bad;sql", "--start", START, "--end", END],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
