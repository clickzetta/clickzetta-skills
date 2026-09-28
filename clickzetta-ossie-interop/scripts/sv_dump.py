#!/usr/bin/env python3
"""Dump a ClickZetta semantic view's metadata with cz-cli into one JSON file.

Runs (read-only; SHOW CREATE is passed --write only because cz-cli's keyword guard flags it):
  SHOW CREATE SEMANTIC VIEW <view>
  DESC EXTENDED <view>
  SHOW SEMANTIC TABLES | RELATIONSHIPS | FACTS | DIMENSIONS | METRICS IN <view>

Usage:
  python3 sv_dump.py --profile prod --view my_schema.my_view -o dump.json
  python3 sv_dump.py --view my_schema.my_view --cz-cli "cz-cli -p prod" -o dump.json

The output keeps every raw cz-cli stdout under "raw" so parsing problems can be
diagnosed without re-running the commands.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys

from czossie_common import CliError, parse_cli_rows, run_cli

COMMANDS = {
    "show_create": "SHOW CREATE SEMANTIC VIEW {v}",
    "desc_extended": "DESC EXTENDED {v}",
    "tables": "SHOW SEMANTIC TABLES IN {v}",
    "relationships": "SHOW SEMANTIC RELATIONSHIPS IN {v}",
    "facts": "SHOW SEMANTIC FACTS IN {v}",
    "dimensions": "SHOW SEMANTIC DIMENSIONS IN {v}",
    "metrics": "SHOW SEMANTIC METRICS IN {v}",
}


# cz-cli's read-only guard is a keyword check: it refuses SHOW CREATE ... ("Modification keyword:
# CREATE") unless --write is given. The statement is still read-only; only it gets the flag.
NEEDS_WRITE_FLAG = {"show_create"}


def run(cli: list[str], sql: str, write_flag: bool = False) -> str:
    cmd = cli + ["sql", "--no-limit", "--no-truncate"] + (["--write"] if write_flag else []) + ["-e", sql]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise CliError(f"cz-cli not found: {cli[0]!r}; put it on PATH or pass --cz-cli") from None
    if p.returncode != 0:
        # keep the raw output for diagnosis, but report one clean line
        sys.stderr.write(f"--- cz-cli output for: {sql}\n{p.stderr}{p.stdout}\n")
        detail = ((p.stderr or p.stdout or "").strip().splitlines() or ["no output"])[0]
        raise CliError(f"cz-cli failed ({p.returncode}) for: {sql} - {detail}")
    return p.stdout


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--view", required=True, help="schema.view_name")
    ap.add_argument("--profile", help="cz-cli profile (-p)")
    ap.add_argument("--cz-cli", default="cz-cli", help="cz-cli executable (may include global flags)")
    ap.add_argument("-o", "--output", required=True)
    a = ap.parse_args()

    cli = shlex.split(a.cz_cli)
    if a.profile:
        cli += ["-p", a.profile]
    dump: dict = {"view": a.view, "raw": {}}
    for key, tpl in COMMANDS.items():
        out = run(cli, tpl.format(v=a.view), key in NEEDS_WRITE_FLAG)
        dump["raw"][key] = out
        try:
            dump[key] = parse_cli_rows(out)
        except (ValueError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"warning: could not parse {key}: {exc}\n")
            dump[key] = []
    ddl_rows = dump.get("show_create") or []
    ddl = ""
    if ddl_rows:
        row = ddl_rows[0]
        ddl = row.get("sql") or row.get("create_statement") or next(iter(row.values()), "")
    dump["ddl"] = ddl
    with open(a.output, "w", encoding="utf-8") as fh:
        json.dump(dump, fh, indent=2, ensure_ascii=False)
    counts = {k: len(dump.get(k) or []) for k in ("tables", "relationships", "facts", "dimensions", "metrics")}
    print(f"wrote {a.output}: ddl={'yes' if ddl else 'NO'} {counts}")


if __name__ == "__main__":
    run_cli(main)
