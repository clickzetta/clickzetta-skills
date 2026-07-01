# Workflows

## Live `/doc` Interpretation

The current `/doc` page shows:

- v2 routes
- legacy routes
- raw OpenAPI tags such as `migration-v-2-api`

Read it as a schema browser, not as a workflow guide.

## Environment Selection

1. If the user did not specify which CMT environment to use, ask whether they want:
   - the local CMT service
   - an online CMT service, with its base URL
2. Do not assume `localhost:6060` until the user explicitly chose the local environment.
3. If the user chose an online CMT service, repeat the chosen base URL in the user-facing update before using `/doc`, `/llms.txt`, or `/api/v2/*`.

## Local Service Bootstrap

1. Only use this section after the user explicitly chose the local CMT environment.
2. Before calling `/doc`, `/llms.txt`, or `/api/v2/*`, check whether port `6060` is listening.
3. If `6060` is not listening, start the local server from repo root with:

```bash
mkdir -p .codex/tmp && nohup java -jar MMAv3.jar -c conf/config_prod.ini > .codex/tmp/mmav3-6060.log 2>&1 & echo $! > .codex/tmp/mmav3-6060.pid
```

4. Record the PID written to `.codex/tmp/mmav3-6060.pid`.
5. Wait for the port to accept connections, then surface the jump links:
   - `http://localhost:6060/doc`
   - `http://localhost:6060/llms.txt`
6. If `6060` is already listening, reuse the running service instead of starting a duplicate process.

## Route Matrix

| Goal | Route | Notes |
| --- | --- | --- |
| list sources | `/api/v2/catalog/sources` | first read step |
| inspect one table | `/api/v2/catalog/tables/{tableId}` | use when table id is already known |
| explain intent | `/api/v2/migrations/plans` | use before any start |
| start run | `/api/v2/migrations/runs` | returns `run_id` and run URLs |
| inspect run | `/api/v2/runs/{runId}` | current summary |
| wait on run | `/api/v2/runs/{runId}/wait` | preferred progress path |
| structured events | `/api/v2/runs/{runId}/events` | progress timeline |
| run logs facade | `/api/v2/logs/runs/{runId}` | log-oriented read path |
| verify result | `/api/v2/verifications/runs/{runId}` | final target identity and checks |
| cleanup run | `/api/v2/admin/runs/{runId}/cleanup` | explicit user intent only |
| execute SQL (any datasource) | `POST /api/ops/sql/execute` | unified query: pass `sourceName` for source, or `workspace`+`schema` for Lakehouse target |
| sql endpoint info | `GET /api/ops/sql/info` | returns default workspace, schema, vcluster, limits |

## Deprecated Legacy Mappings

| Deprecated legacy route | Use instead |
| --- | --- |
| `/api/sources` | `/api/v2/catalog/sources` |
| `/api/tables/{tableId}` | `/api/v2/catalog/tables/{tableId}` |
| `/api/jobs/check-conflict` | `/api/v2/migrations/plans` |
| `/api/jobs` | `/api/v2/migrations/runs` |
| `/api/jobs/{jobId}` | `/api/v2/runs/{runId}` |
| `/api/tasks/{taskId}` | `/api/v2/runs/{runId}/events` or `/api/v2/logs/runs/{runId}` |

## Default Migration Sequence

1. Read `/llms.txt` when routing is unclear.
2. Discover the source with `/api/v2/catalog/sources`.
3. If the user already gave a table id, inspect `/api/v2/catalog/tables/{tableId}`.
4. Create a plan with `/api/v2/migrations/plans`.
5. Review `precheck`, `resolved_targets`, and `execution_strategy`.
6. Start with `/api/v2/migrations/runs`.
7. Monitor with `/api/v2/runs/{runId}/wait`.
8. If more detail is needed, read `/api/v2/runs/{runId}/events` or `/api/v2/logs/runs/{runId}`.
9. Finish with `/api/v2/verifications/runs/{runId}`.

## Request Shapes

### Plan

`POST /api/v2/migrations/plans`

```json
{
  "source": {
    "source_id": "src_databricks_az",
    "schema": "demo_table_type_examples",
    "tables": ["basic_scalar_types"]
  },
  "target": {
    "workspace": "sample_workspace",
    "schema": "public"
  },
  "options": {
    "refresh_mode": "none",
    "schema_evolution": true,
    "verification_mode": "row_count"
  }
}
```

### Start

`POST /api/v2/migrations/runs`

```json
{
  "intent": {
    "source": {
      "source_id": "src_databricks_az",
      "schema": "demo_table_type_examples",
      "tables": ["basic_scalar_types"]
    },
    "target": {
      "workspace": "sample_workspace",
      "schema": "public"
    },
    "options": {
      "refresh_mode": "none",
      "schema_evolution": true,
      "verification_mode": "row_count"
    }
  },
  "refresh_before_submit": false
}
```

### Execute SQL (source or target)

`POST /api/ops/sql/execute`

Query a **source** (Databricks, MC, Doris, etc.):
```json
{
  "sql": "SELECT * FROM demo_table_type_examples.basic_scalar_types ORDER BY id",
  "sourceName": "databricks_az",
  "limit": 100
}
```

Query the **Lakehouse target**:
```json
{
  "sql": "SELECT * FROM demo_table_type_examples.basic_scalar_types ORDER BY id",
  "workspace": "wanxin-test-ws-03",
  "schema": "demo_table_type_examples",
  "limit": 100
}
```

Response includes `columns` (name + type), `rows`, `rowCount`, `elapsedMs`, and `jobId`.

## Progress Policy

- Prefer `wait` for “monitor until something changes”.
- Prefer `getRun` for “tell me the current state now”.
- Prefer `events` or `logs` for “why is it slow”, “what failed”, or “summarize what happened”.
- Treat `children.status=skipped` as a first-class child outcome, not as missing task data, and surface `reason_code` / `reason_summary` when reporting those children.
- If a run is `succeeded` and all returned children are `skipped`, report that the run reached terminal state without generating executable tasks.

## Anti-Patterns

- Do not jump from `/doc` to legacy `/api/jobs` just because it is more detailed.
- Do not use deprecated legacy source/table/job/task-log routes when the mapped `/api/v2` route exists.
- Do not start a run without first materializing a plan unless the user explicitly wants a direct fire-and-monitor flow.
- Do not claim migration success from `succeeded` alone. Always read verification.
- Do not interpret `children=[]` from `wait` with default params as evidence that there were no child outcomes; call `getRun` or `wait?include_children=true` before concluding that.
