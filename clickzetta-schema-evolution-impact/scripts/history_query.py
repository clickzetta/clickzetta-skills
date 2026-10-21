#!/usr/bin/env python3
"""Generate scoped read-only history aggregation SQL. Never executes SQL or cz-cli."""
from __future__ import annotations

import argparse
import re
from datetime import datetime

_OBJECT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\Z")


def build_query(objects: list[str], direction: str, start: str, end: str) -> str:
    if direction not in {"readers", "writers"}:
        raise ValueError("direction must be readers or writers")
    if not objects or any(not _OBJECT.fullmatch(obj) for obj in objects):
        raise ValueError("objects must be simple workspace.schema.table identifiers")
    objects = list(dict.fromkeys(objects))
    try:
        first = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        last = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    except ValueError as error:
        raise ValueError("timestamps must use YYYY-MM-DD HH:MM:SS in the documented query timezone") from error
    if first >= last:
        raise ValueError("start must precede end")
    # Reformat validated times: never interpolate unchecked SQL literals.
    start = first.strftime("%Y-%m-%d %H:%M:%S")
    end = last.strftime("%Y-%m-%d %H:%M:%S")
    member = "input_objects" if direction == "readers" else "output_objects"
    grouped = "output_objects" if direction == "readers" else "input_objects"
    sources = "\n  UNION ALL ".join(
        f"SELECT '{obj}' AS source_object" for obj in objects
    )
    return f"""WITH sources AS (
  {sources}
), matched AS (
  SELECT s.source_object, j.*
  FROM information_schema.job_history j
  JOIN sources s
    ON INSTR(CONCAT(',', COALESCE(j.{member}, ''), ','),
             CONCAT(',', s.source_object, ',')) > 0
  WHERE j.pt_date >= '{first:%Y-%m-%d}' AND j.pt_date <= '{last:%Y-%m-%d}'
    AND j.start_time >= CAST('{start}' AS TIMESTAMP)
    AND j.start_time < CAST('{end}' AS TIMESTAMP)
)
SELECT source_object, {grouped}, job_type, job_sub_type, job_creator,
       status, COUNT(*) AS jobs, MIN(start_time) AS first_time,
       MAX(start_time) AS last_time, MAX(job_id) AS sample_job_id,
       MAX(query_tag) AS sample_query_tag
FROM matched
GROUP BY source_object, {grouped}, job_type, job_sub_type, job_creator, status
ORDER BY source_object, jobs DESC"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", action="append", required=True, dest="objects")
    parser.add_argument("--direction", choices=("readers", "writers"), required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()
    try:
        statement = build_query(args.objects, args.direction, args.start, args.end)
    except ValueError as error:
        parser.error(str(error))
    print(statement)


if __name__ == "__main__":
    main()
