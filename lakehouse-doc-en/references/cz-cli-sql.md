# SQL Execution and Data Exploration

This page covers cz-cli commands for SQL execution, schema and table management, job diagnostics, and workspace switching.

## cz-cli sql — Execute SQL

### Basic Usage

```bash
```

Synchronous execution, returns results immediately (default):

```bash
cz-cli -p prod sql "SELECT current_timestamp()"

```

Pass SQL with -e:

```bash
cz-cli -p prod sql -e "SELECT * FROM public.orders LIMIT 10"

```

Read SQL from a file:

```bash
cz-cli -p prod sql -f query.sql
```

### Synchronous vs Asynchronous

`cz-cli sql` runs synchronously by default (`--sync`), waiting for results before exiting. For long-running queries, submit asynchronously to get a job_id and retrieve results later:

```bash
```

Async submit, returns job_id immediately:

```bash
cz-cli -p prod sql "SELECT * FROM huge_table" --async

```

Check job status:

```bash
cz-cli -p prod sql status <job_id>

```

Or use the job command:

```bash
cz-cli -p prod job status <job_id>
cz-cli -p prod job result <job_id>
```

### Write Protection

INSERT, UPDATE, DELETE, CREATE, DROP, and other write operations require the explicit `--write` flag to prevent accidental changes:

```bash
cz-cli -p prod sql --write -e "CREATE TABLE IF NOT EXISTS public.demo (id INT, name STRING)"
cz-cli -p prod sql --write -e "INSERT INTO public.demo VALUES (1, 'test')"
cz-cli -p prod sql --write -e "DROP TABLE public.demo"
```

### Batch Execution

Use `--batch` to execute multiple semicolon-separated statements in sequence:

```bash
cz-cli -p prod sql --write --batch -e "
CREATE TABLE IF NOT EXISTS ods.events (id INT, ts TIMESTAMP, type STRING);
INSERT INTO ods.events VALUES (1, current_timestamp(), 'click');
INSERT INTO ods.events VALUES (2, current_timestamp(), 'view');
"
```

### Variable Substitution

Use `--variable KEY=VALUE` to inject variables; reference them in SQL with `%(KEY)s`. Useful for templated queries:

```bash
cz-cli -p prod sql "SELECT %(col)s FROM public.orders LIMIT 10" \
  --variable col=order_id

cz-cli -p prod sql "SELECT * FROM public.orders WHERE dt = '%(dt)s'" \
  --variable dt=2026-05-26
```

### Query Hints

Use `--set KEY=VALUE` to pass query-level hints, such as setting the timezone:

```bash
cz-cli -p prod sql "SELECT current_timestamp()" \
  --set cz.sql.timezone=UTC
```

### Dry Run

Validate syntax and run EXPLAIN without actually executing — useful for pre-deployment checks:

```bash
cz-cli -p prod sql --dry-run -f deploy.sql
```

### Output Control

```bash
```

Do not truncate long fields:

```bash
cz-cli -p prod sql "SELECT * FROM public.orders" --no-truncate

```

Remove row limit (default is 100 rows):

```bash
cz-cli -p prod sql "SELECT * FROM public.orders" --no-limit

```

Suppress column headers:

```bash
cz-cli -p prod sql "SELECT id, name FROM public.orders" --no-header

```

Specify output format:

```bash
cz-cli -p prod sql "SELECT * FROM public.orders LIMIT 5" -o table
cz-cli -p prod sql "SELECT * FROM public.orders LIMIT 5" -o csv
```

### Full Parameter Reference

| Parameter | Description | Default |
|------|------|--------|
| `--sync` / `--no-sync` | Wait synchronously for results | `true` |
| `--async` | Async submit, returns job_id immediately | `false` |
| `--write` | Allow write operations (DDL/DML) | off |
| `--batch` / `-B` | Execute multiple semicolon-separated statements | `false` |
| `--variable KEY=VALUE` | Variable substitution; use `%(KEY)s` in SQL | — |
| `--set KEY=VALUE` | Query hint | — |
| `--dry-run` | EXPLAIN only, no actual execution | `false` |
| `--timeout` | Job timeout in seconds | `300` |
| `--limit` / `--no-limit` | Auto-truncate to 100 rows | `true` |
| `--truncate` / `--no-truncate` | Truncate long fields (3000 chars) | `true` |
| `--header` / `--no-header` / `-N` | Output column headers | `true` |
| `-f, --file` | Read SQL from a file | — |
| `-e, --execute` | SQL string (equivalent to positional argument) | — |
| `--stdin` | Read SQL from stdin | `false` |
| `--job-profile` | Retrieve execution profile for a completed job | — |
| `--schema-context` | Attach schema information to the response (for agent use) | `false` |

---

## cz-cli schema — Schema Management

```bash
```

List all schemas:

```bash
cz-cli -p prod schema list

```

View schema details (including table list):

```bash
cz-cli -p prod schema describe public

```

Create a schema:

```bash
cz-cli -p prod schema create dwd

```

Drop a schema (requires confirmation):

```bash
cz-cli -p prod schema drop old_schema
```

---

## cz-cli table — Table Management and Data Exploration

```bash
```

List all tables in the current schema:

```bash
cz-cli -p prod table list

```

List tables in a specific schema:

```bash
cz-cli -p prod -s dwd table list

```

View table structure (columns, types, comments):

```bash
cz-cli -p prod table describe public.orders

```

Preview table data (default 10 rows):

```bash
cz-cli -p prod table preview public.orders

```

View row count and recent job statistics:

```bash
cz-cli -p prod table stats public.orders

```

View table version history (Time Travel support):

```bash
cz-cli -p prod table history public.orders

```

Create a table from DDL:

```bash
cz-cli -p prod table create --write "CREATE TABLE public.test (id INT, name STRING)"

```

Drop a table (requires confirmation):

```bash
cz-cli -p prod table drop public.test
```

---

## cz-cli job — SQL Job Diagnostics

Asynchronously submitted queries return a job_id. Use the `job` command to track them:

```bash
```

View job status and execution summary:

```bash
cz-cli -p prod job status <job_id>

```

Retrieve job query results (waits if still running):

```bash
cz-cli -p prod job result <job_id>

```

View job execution profile (analyze performance bottlenecks):

```bash
cz-cli -p prod sql --job-profile <job_id>
```

---

## cz-cli workspace — Workspace Switching

```bash
```

View current workspace:

```bash
cz-cli -p prod workspace current

```

List all available workspaces:

```bash
cz-cli -p prod workspace list

```

Temporarily switch workspace (this command only):

```bash
cz-cli -p prod workspace use analytics

```

Persist the switch (save to profile):

```bash
cz-cli -p prod workspace use analytics --persist
```

---

## Common Use Cases

**Case 1: Explore a new table**

```bash
cz-cli -p prod table describe public.orders
cz-cli -p prod table preview public.orders
cz-cli -p prod table stats public.orders
```

**Case 2: Debug a slow query**

```bash
```

Submit asynchronously first:

```bash
cz-cli -p prod sql "SELECT * FROM huge_table GROUP BY ..." --async
```

Note the job_id, then check execution details:

```bash
cz-cli -p prod job status <job_id>
cz-cli -p prod sql --job-profile <job_id>
```

**Case 3: Execute DDL in CI/CD**

```bash
```

Validate syntax with dry-run first:

```bash
cz-cli -p prod sql --dry-run -f migrations/v2.sql

```

Execute after confirming no issues:

```bash
cz-cli -p prod sql --write --batch -f migrations/v2.sql
```

**Case 4: Templated queries (agent scenario)**

```bash
cz-cli -p prod sql \
  "SELECT COUNT(*) FROM public.orders WHERE dt = '%(dt)s' AND status = '%(status)s'" \
  --variable dt=2026-05-26 \
  --variable status=completed
```

## Related Documentation

**cz-cli Documentation**

- [Installation and Configuration Guide](setup_cz_cli.md) — Installation, profile configuration
- [Studio Task Development and Operations](cz-cli-studio-tasks.md) — Task management, runs
- [AI Agent Integration](cz-cli-agent.md) — Agent LLM configuration, natural language operations

**Lakehouse Documentation**

- [Workspace](workspace-introduction.md) — Workspace concepts, user management, permission model
- [Compute Cluster](virtual-cluster.md) — VCluster type selection, spec configuration
- [Schema](schema.md) — Schema creation and management
- [Time Travel](timetravel-summary.md) — Historical version queries (the underlying mechanism behind `table history`)
