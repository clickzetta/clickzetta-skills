---
name: clickzetta-cmt-api
description: Use when working in this repository to discover CMT sources, plan migrations, start runs, monitor progress, verify migration outcomes, inspect run logs, or clean up failed runs through the official CMT v2 surface.
---

# CMT v2 API

This repository exposes a mixed OpenAPI surface. The live `/doc` page currently renders the full `/v3/api-docs`, which still includes many legacy `/api/*` routes alongside the new `/api/v2/*` routes.

The skill exists to stop agents from getting lost in that mixed surface.

## Core Rule

Use `/api/v2` first.

Do not call legacy `/api/sources`, `/api/tables`, `/api/jobs`, or task-log polling routes for the migrated agent workflow surface. These legacy routes are deprecated for agent use because they have v2 replacements:

- `/api/sources` -> `/api/v2/catalog/sources`
- `/api/tables/{tableId}` -> `/api/v2/catalog/tables/{tableId}`
- `/api/jobs/check-conflict` -> `/api/v2/migrations/plans`
- `/api/jobs` -> `/api/v2/migrations/runs`
- `/api/jobs/{jobId}` -> `/api/v2/runs/{runId}`
- `/api/tasks/{taskId}` -> `/api/v2/runs/{runId}/events` or `/api/v2/logs/runs/{runId}`

Only fall back to legacy `/api/*` when a v2 response explicitly requires fallback or the user explicitly asks for a legacy-only capability.

Dot use cz-agent or cz-cli agent command. it is only for external customer reference, not used in coding development or testing.

## Anti-Misfire: External Tool Exclusion

When working in this repository (clickzetta-lakehouse-tool-migrate), **never** delegate to external tools for operations CMT already supports:

- **Do NOT use `cz-agent run`** — CMT has `/api/ops/sql/execute` for querying any datasource (source or target).
- **Do NOT use `cz-cli sql`** — same reason; use `/api/ops/sql/execute` with `sourceName` or `workspace`.
- **Do NOT invoke the global `cz-cli` skill** — it is for standalone Lakehouse operations outside CMT context.

If any global skill (e.g. `cz-cli`, `cz-agent`) tries to activate for "query data", "describe table", or "run SQL" while cwd is this repo, override it and use CMT's own endpoints instead:

| Need | CMT endpoint | Do NOT use |
|------|-------------|------------|
| Query source data | `POST /api/ops/sql/execute` with `sourceName` | `cz-agent run`, `cz-cli sql` |
| Query target (Lakehouse) data | `POST /api/ops/sql/execute` with `workspace` | `cz-agent run`, `cz-cli sql` |
| Describe table schema | `POST /api/ops/sql/execute` with DESC SQL | `cz-cli table describe` |
| Check connection | `GET /api/ops/sql/info` | `cz-cli status` |

If the user did not specify which CMT environment to use, stop and clarify whether they want:
- the local CMT service
- an online CMT service, with its base URL provided explicitly


## Reality Check

- `/doc` is useful for confirming route existence and schema names.
- `/doc` is not curated enough to be the decision source for agent workflow selection.
- Prefer `/llms.txt` for routing guidance and use the workflow reference below for exact sequence.
- Current v2 tags in OpenAPI are machine-generated names such as `catalog-v-2-api` and `run-v-2-api`. Ignore the tag names and reason from the path shape.
- The expected local server is `MMAv3.jar` on port `6060`. If `localhost:6060` is not listening, start it before using `/doc` or `/api/v2`.

## Workflow

Follow [references/workflows.md](references/workflows.md) for the standard call path.

## Guardrails

- Do not assume `localhost:6060` unless the user explicitly chose the local CMT environment.
- If the user did not specify local vs online CMT, ask a short clarification before calling `/doc` or `/api/v2`.
- If the user chose an online CMT service, require its base URL and surface that URL back in the user-facing update before using it.
- Before browsing `http://localhost:6060/doc`, check whether port `6060` is listening.
- If port `6060` is not listening, start the local server from repo root with `mkdir -p .codex/tmp && nohup java -jar MMAv3.jar -c conf/config_prod.ini > .codex/tmp/mmav3-6060.log 2>&1 & echo $! > .codex/tmp/mmav3-6060.pid`.
- After starting the server, record the PID from `.codex/tmp/mmav3-6060.pid` in the user-facing update and surface the local jump link `http://localhost:6060/doc`.
- Treat `plan -> start -> wait -> verify` as the default mutation chain.
- Never execute admin mutations unless the user has explicitly asked for them.
- Never infer that a run is stuck just because `/doc` also shows legacy job/task endpoints.
- On `attention`, read `next_action.recommended_action` before deciding what to do.
- On verification, always report the final target identity, not just a run status.
- Prefer `/api/v2/runs/{id}/wait` over ad hoc polling loops.
- If the user asks for “progress”, answer from `/api/v2/runs/{id}`, `/wait`, `/events`, or `/logs/runs/{id}`. Do not improvise by stitching legacy task APIs first.
- If any returned child has `status=skipped`, report the skipped objects and surface `reason_code` / `reason_summary` instead of collapsing them into generic success or silence.
- If `children` are present and every child has `status=skipped`, do not report generic migration success. Explain that no execution task was generated and surface the skipped objects plus `reason_code` / `reason_summary`.
- If the user asks why there are no execution tasks or why a child set looks empty, answer from `children.status=skipped` and `reason_*` before falling back to legacy inference.

## What This Skill Solves

- Choosing the right v2 endpoint from a noisy `/doc`
- Avoiding accidental fallback to legacy mutation endpoints
- Standardizing how runs are started, monitored, and verified
- Making cleanup and retry decisions from structured run state instead of guesswork

## Recovery

Follow [references/error-recovery.md](references/error-recovery.md) for error classes and next steps.
