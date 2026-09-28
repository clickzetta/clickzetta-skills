# Testing clickzetta-ossie-interop

Six suites, in increasing order of what they need.

| Suite | Needs | Covers | Status (2026-09-28) |
|---|---|---|---|
| `run_offline_tests.sh` | python3 + pyyaml + jsonschema (+ sqlglot) | export, import, round trip, ontology derivation, all 8 converter fixtures, every CLI flag, every script's error handling and the exit-code contract, the live-suite lock | 74 pass, 0 fail |
| `scale/run_scale_test.py` | python3 + pyyaml | five synthetic models (5 → 100 datasets, 1224 fields, a 99-deep relationship chain) through the whole round trip, with a per-step time budget | 30 pass, 0 fail |
| `run_live_test.sh <profile>` | cz-cli + a Lakehouse profile | one full round trip against a real instance + 14 syntax probes + 8 query-equivalence pairs | 26 pass, 0 fail, 2 info |
| `flights/run_flights_test.sh <profile>` | same | ontology-heavy end-to-end: enrich → import → 13 queries against a sqlite baseline, plus 18 more covering `FACTS`, inner `WHERE` and outer SQL | 44 pass, 0 fail |
| `tpcds/run_tpcds_test.sh <profile>` | same | multi-table metrics, window metrics, `--source-map` on 3-part sources | 17 pass, 0 fail |
| `converters/run_converter_smoke.sh <profile>` | same | Databricks / Omni / NVIDIA / GoodData / OrionBelt output → view → create empty tables → every metric and dimension compiles → export equals the source | 29 pass, 0 fail |

```bash
bash tests/run_offline_tests.sh                       # no credentials, gates every change
python3 tests/scale/run_scale_test.py                 # no credentials
python3 tests/scale/run_scale_test.py --profile <p>   # adds the live sidecar phase
bash tests/run_live_test.sh  <profile>                # creates + drops schema ossie_skill_test
bash tests/flights/run_flights_test.sh <profile>      # creates + drops schema ossie_flights_test
bash tests/tpcds/run_tpcds_test.sh <profile>          # creates + drops schema ossie_skill_test
bash tests/converters/run_converter_smoke.sh <profile> # same schema, one fixture at a time
```

The four live suites each abort if their schema already exists, so they never touch objects they
did not create, and each drops everything on exit — including on failure. A leftover *empty* schema
from a killed run will therefore block the suite until someone drops it; that is deliberate, since
auto-dropping could destroy work.

`.github/workflows/ossie-interop-tests.yml` runs the offline suite and the scale test on every push
and pull request that touches `clickzetta-ossie-interop/`. The live suites are manual because they need a
profile.

## One fixture that is expected to fail to import

`orionbelt_obml` is a real converter output whose `calendar` has no `primary_key` and is reached by
**two** relationships through **different** columns (`sales_ym` → `ym` and `sales_date` → `date`).
Whichever key the importer infers, the other reference is invalid, and ClickZetta rejects the view
with `... dost not match any PRIMARY KEY or UNIQUE key of the referenced table`. Importing it needs a
human to say which column set identifies a row, so the importer reports that at **error** level
(exit 1, DDL still written for inspection) instead of passing it off as a warning and letting the
agent execute DDL that cannot run. The offline suite and the smoke test both assert that it stops
there — `EXPECT_IMPORT_ERROR` in `converters/run_converter_smoke.sh` and the fourth argument of
`conv()` in `run_offline_tests.sh`. If a future version resolves the key itself, those two
expectations fail on purpose, as the signal to remove them.

## One at a time: the profile lock

Run live suites **serially**. Two against the same profile do not corrupt anything, but they contend
for one vcluster and both start failing with `JOB_TIMEOUT` after a few minutes, which reads as a
product problem and is not.

`tests/lib/lock.sh` turns that into an immediate refusal. Each live suite takes a lock named after
its profile before creating anything and releases it from its own cleanup:

```
ABORT: another live suite is already running against profile '<profile>'.
       ... Wait for it, or remove the stale lock if that run died: tests/.locks/<profile>.lock
       lock held by: pid <pid> on <host>
```

Exit code 3. A lock left behind by a killed run is not detected as stale — remove the directory the
message names. `tests/.locks/` is gitignored, and `run_offline_tests.sh` covers the acquire /
refuse / independent-profile / release-by-holder behaviour without a database.

## One engine defect the live test tracks

`run_live_test.sh` records `probe p_cross_metric by child dimension` as `INFO`, never as a failure.
Grouping an imported multi-table metric by a finer-grain dimension crashes the planner with
`CZLH-65000 Compiler internal error`, where the same grain violation queried directly returns a
clear `CZLH-42000`. That is an engine defect, reproduced in isolation from three tables and two
metrics; `references/mapping.md` has the repro and the workaround (`SHOW SEMANTIC DIMENSIONS … FOR
METRIC`). If a future engine release fixes it the probe flips to its other `INFO` text, which is the
signal to delete this note.

## Reading results

The offline suite prints `PASS`, `FAIL` or `KNOWN` per assertion, and there are currently **no
KNOWN lines**. The helper stays because it is the escape hatch for a defect that is real but is not
the test's job to fix: `known "..."` records it without failing the run, so CI stays usable while
the problem stays visible. Every `KNOWN` line is a bug to fix, not a tolerated behaviour.

## Exit codes

Every script in `scripts/` follows the same contract, and section 10 asserts it case by case:

| Code | Meaning | Example |
|---|---|---|
| 0 | ran, nothing to report | a model validates; a diff is equivalent |
| 1 | ran, and found problems | a model is invalid; a diff shows differences; an import raised error-level issues |
| 2 | could not run at all | file missing, not UTF-8, malformed YAML/JSON, empty file, a directory, no `semantic_model`, a dump with no `ddl`, bad usage |

`2` always comes with a single `error: <sentence>` line on stderr — never a Python traceback.
`CliError` and `run_cli` in `czossie_common.py` are what make that uniform: raise `CliError` where
input turns out to be unusable, wrap the script body in `run_cli(main)`, and the message and the
code follow. A file that is merely *invalid* is `1`, not `2`, so `2` keeps its meaning.

## What each suite deliberately pins

The offline suite asserts on **generated SQL text**, so several assertions name a whole expression
rather than a prefix. That is on purpose: a qualification pass that treats the `ROW` keyword as a
bare column produced `... AND CURRENT store_sales.ROW`, which ClickZetta rejects at CREATE time
with `expected.keyword, ROW, store_sales`. Grepping only the `ORDER BY` prefix missed it, and it
took the live `tpcds` suite to surface the break. When adding an assertion here, prefer the whole
expression.

`run_offline_tests.sh` also ends with a **sensitivity check**: it mutates one token of an exported
model and requires `ossie_diff.py` to report a difference. A round-trip check that cannot fail
proves nothing, so that assertion guards the guard.

## Scale, and the sidecar's chunk limit

`tests/scale/gen_model.py` builds a synthetic model of any size in the shape of a **chain** —
`ds_i` carries a foreign key to `ds_{i-1}` — so the relationship depth grows with the model and the
importer has to resolve a 99-deep chain rather than one hop from a hub.

The reason the scale test exists is the **sidecar**. `ossie_to_sv.py` stores the Ossie-only
metadata as base64 in view properties, chunked at 2000 characters (`SIDECAR_CHUNK`), and nothing had
ever pushed more than three chunks through a real `ALTER SEMANTIC VIEW ... SET PROPERTIES`. A
100-dataset model produces nine. The `sidecar` tier (12 datasets × 100 fields) is shaped to produce
seven chunks from only twelve tables, and the live phase applies it to a real instance, dumps it
back, and requires the round trip to stay EQUIVALENT — which it does, so a large imported model is
not silently truncated.

Every step has a 30-second ceiling. That is not a benchmark; it is there so a pathological slowdown
in the importer or the exporter fails the run instead of hanging CI.

## Not covered

- **Permissions.** `GRANT` / `REVOKE SELECT ON SEMANTIC VIEW` and `SHOW GRANTS` are not exercised;
  the live suite does not touch privileges. Deferred deliberately — role lifecycle needs a
  disposable instance, and the zero-side-effect half (`SHOW GRANTS` on your own view, rejection of
  `INSERT`/`UPDATE`/`DELETE`) has not been added either.
- **Memory.** The scale test asserts time, not peak RSS.
- **Multi-table metrics at scale.** `--multitable` exercises the PRIVATE-split path on the `wide`
  tier only; a model with hundreds of them is not tried.
- **Agent behaviour.** The judgement calls `SKILL.md` delegates (rewriting a vendor expression,
  wording an ontology `verbalizes`) have no golden-file test. These have no single right answer, so
  they belong in an eval with a rubric rather than in assertions.
