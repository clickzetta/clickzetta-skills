# SQL Execution and Data Exploration

This page covers cz-cli commands for SQL execution, schema and table management, job diagnostics, and workspace switching.

## cz-cli sql — Execute SQL

### Basic Usage

Synchronous execution, returns results directly (default):

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

### Sync vs Async

`cz-cli sql` executes synchronously by default (`--sync`), waiting for results before exiting. For long-running queries, you can submit asynchronously, get the job\_id, and then retrieve results:


Submit asynchronously, returns job\_id immediately:

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

Write operations such as INSERT, UPDATE, DELETE, CREATE, and DROP require the explicit `--write` flag to prevent accidental modifications:

```bash
cz-cli -p prod sql --write -e "CREATE TABLE IF NOT EXISTS public.demo (id INT, name STRING)"
cz-cli -p prod sql --write -e "INSERT INTO public.demo VALUES (1, 'test')"
cz-cli -p prod sql --write -e "DROP TABLE public.demo"
```

### Batch Execution of Multiple Statements

Use `--batch` to execute multiple semicolon-separated statements in sequence:

```bash
cz-cli -p prod sql --write --batch -e "
CREATE TABLE IF NOT EXISTS ods.events (id INT, ts TIMESTAMP, type STRING);
INSERT INTO ods.events VALUES (1, current_timestamp(), 'click');
INSERT INTO ods.events VALUES (2, current_timestamp(), 'view');
"
```

### Variable Substitution

Use `--variable KEY=VALUE` to inject variables, referenced in SQL with `%(KEY)s`, suitable for templated queries:

```bash
cz-cli -p prod sql "SELECT %(col)s FROM public.orders LIMIT 10" \
  --variable col=order_id

cz-cli -p prod sql "SELECT * FROM public.orders WHERE dt = '%(dt)s'" \
  --variable dt=2026-05-26
```

### Query Hints

Use `--set KEY=VALUE` to pass query-level hints, such as specifying a timezone:

```bash
cz-cli -p prod sql "SELECT current_timestamp()" \
  --set cz.sql.timezone=UTC
```

### Pre-execution Validation (dry-run)

Performs only syntax checking and EXPLAIN without actually executing, suitable for pre-deployment validation:

```bash
cz-cli -p prod sql --dry-run -f deploy.sql
```

### Output Control


Do not truncate long fields:

```bash
cz-cli -p prod sql "SELECT * FROM public.orders" --no-truncate
```

Remove row limit (default 100 rows):

```bash
cz-cli -p prod sql "SELECT * FROM public.orders" --no-limit
```

Do not output column names:

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
| --------- | ----------- | ------- |
| `--sync` / `--no-sync` | Wait synchronously for results | `true` |
| `--async` | Submit asynchronously, returns job\_id immediately | `false` |
| `--write` | Allow write operations (DDL/DML) | Off |
| `--batch` / `-B` | Execute multiple semicolon-separated statements in batch | `false` |
| `--variable KEY=VALUE` | Variable substitution, referenced in SQL with `%(KEY)s` | — |
| `--set KEY=VALUE` | Query hint | — |
| `--dry-run` | EXPLAIN only, no actual execution | `false` |
| `--timeout` | Job timeout in seconds | `300` |
| `--limit` / `--no-limit` | Auto-truncate to 100 rows | `true` |
| `--truncate` / `--no-truncate` | Truncate long fields (3000 characters) | `true` |
| `--header` / `--no-header` / `-N` | Whether to output column names | `true` |
| `-f, --file` | Read SQL from file | — |
| `-e, --execute` | SQL string (equivalent to positional argument) | — |
| `--stdin` | Read SQL from stdin | `false` |
| `--job-profile` | Query execution profile of a completed job | — |
| `--schema-context` | Attach schema information to response (for Agent use) | `false` |

***

## cz-cli schema — Schema Management

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

***

## cz-cli table — Table Management and Data Exploration


List all tables in the current schema:

```bash
cz-cli -p prod table list
```

List tables in a specific schema:

```bash
cz-cli -p prod -s dwd table list
```

View table structure (column names, types, comments):

```bash
cz-cli -p prod table describe public.orders
```

Preview table data (default 10 rows):

```bash
cz-cli -p prod table preview public.orders
```

View table row count and recent job statistics:

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

***

## cz-cli job — SQL Job Diagnostics

Asynchronously submitted queries return a job\_id; use the `job` command to track them:


View job status and execution summary:

```bash
cz-cli -p prod job status <job_id>
```

Get job query results (waits if still running):

```bash
cz-cli -p prod job result <job_id>
```

View job execution profile (analyze performance bottlenecks):

```bash
cz-cli -p prod sql --job-profile <job_id>
```

***

## cz-cli workspace — Workspace Switching


View current workspace:

```bash
cz-cli -p prod workspace current
```

List all available workspaces:

```bash
cz-cli -p prod workspace list
```

Temporarily switch workspace (current command only):

```bash
cz-cli -p prod workspace use analytics
```

Persistent switch (saved to profile):

```bash
cz-cli -p prod workspace use analytics --persist
```

***

## Common Use Cases

**Scenario 1: Exploring a new table**

```bash
cz-cli -p prod table describe public.orders
cz-cli -p prod table preview public.orders
cz-cli -p prod table stats public.orders
```

**Scenario 2: Debugging a slow query**


Submit asynchronously first:

```bash
cz-cli -p prod sql "SELECT * FROM huge_table GROUP BY ..." --async
```

Note the job\_id and view execution details:

```bash
cz-cli -p prod job status <job_id>
cz-cli -p prod sql --job-profile <job_id>
```

**Scenario 3: Executing DDL in CI/CD**


Validate syntax with dry-run first:

```bash
cz-cli -p prod sql --dry-run -f migrations/v2.sql
```

Execute after confirming no issues:

```bash
cz-cli -p prod sql --write --batch -f migrations/v2.sql
```

**Scenario 4: Templated queries (Agent scenario)**

```bash
cz-cli -p prod sql \
  "SELECT COUNT(*) FROM public.orders WHERE dt = '%(dt)s' AND status = '%(status)s'" \
  --variable dt=2026-05-26 \
  --variable status=completed
```

## Related Documentation

**cz-cli Documentation**

* [Installation and Configuration Guide](setup_cz_cli.md) — Installation, profile configuration
* [Studio Task Development and Operations](cz-cli-studio-tasks.md) — Task management, runs
* [AI Agent Integration](cz-cli-agent.md) — Agent LLM configuration, natural language operations

**Lakehouse Related Documentation**

* [Workspace](workspace-introduction.md) — Workspace concepts, user management, permission system
* [Virtual Cluster](virtual-cluster.md) — Virtual Cluster type selection, specification configuration
* [Schema](schema.md) — Schema creation and management
* [Time Travel](timetravel-summary.md) — Historical version queries (the underlying mechanism of the `table history` command)

^
