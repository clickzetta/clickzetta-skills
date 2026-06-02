---
name: clickzetta-table-lineage
description: |
  Table lineage visualization tool for ClickZetta Lakehouse. Retrieves table dependency relationships
  and cost data by analyzing actual jobs (information_schema.job_history), exports CSV and embeds
  into an HTML template to generate an interactive lineage graph.
  Trigger when user says "table lineage", "dependency graph", "data flow", "upstream/downstream analysis",
  "lineage visualization", or "pipeline visualization".
  Keywords: table lineage, dependency graph, data flow, upstream, downstream, visualization
---

# Table Lineage Visualization Workflow

## Reference Files

| File | Description |
|------|-------------|
| `references/normalize_func.sql` | Normalization UDF definitions (`__normalize_table` and `__normalize_objects`) |
| `references/table_relation.sql` | Table relationship query SQL (depends on UDF, `{N}` is a day-count placeholder) |
| `references/table_cost.sql` | Table cost query SQL (depends on UDF, `{N}` is a day-count placeholder) |
| `references/table_lineage_standalone.html` | Visualization HTML template |

## Instructions

### Step 0: Determine Time Range

Ask the user how many days of lineage data to analyze. Default is 1 day. User can specify days such as 1, 7, 30, etc.
The `{N}` placeholder in SQL will be replaced with the user-specified number of days.

### Step 1: Create and Validate Normalization UDFs

Create UDFs using `references/normalize_func.sql` (skip if already exists).
Validate UDF using sql `select public.__normalize_table('foo.bar.ods_rt_$kafka$_a9f5be53aeacae016431332a528d11bd')` should return 'KAFKA.foo.bar.ods_t'.

### Step 2: Export Table Relationship Data

Read `references/table_relation.sql`, replace `{N}` with the user-specified number of days, execute via cz-cli sql --no-limit, and save the result as `table_relation.csv`.

### Step 3: Export Table Cost Data

Read `references/table_cost.sql`, replace `{N}` with the user-specified number of days, execute via cz-cli sql --no-limit, and save the result as `table_cost.csv`.

### Step 4: Generate Visualization Page

1. Read `references/table_lineage_standalone.html` as the template
2. Find the line containing the comment `<!-- Data injection point`, and insert **after** it:

```html
<script>
window.LINEAGE_DATA = {
  relation: `...table_relation.csv raw text...`,
  cost: `...table_cost.csv raw text...`
};
</script>
```

3. Write the result to the target file (e.g., `table_lineage.html`) and open it in a browser.

The page detects `window.LINEAGE_DATA` and renders automatically, skipping the file picker.

### Step 5: Guide User Through Visualization Features

- **Click a node**: Highlights the full upstream (orange) and downstream (cyan) dependency paths
- **Search**: Top search box filters table names (shortcut `/` or `Cmd+K`)
- **Zoom/Pan**: Mouse wheel to zoom, drag to pan, `F` key to fit screen
- **Minimap (bottom-right)**: Click or drag for quick navigation
- **Theme toggle**: Supports light/dark themes
- **Hover for details**: DML CRU/day, cumulative cost, query cost metrics

## Platform-Specific Knowledge

- `information_schema.job_history`'s `input_objects` and `output_objects` are comma-separated table name lists
- Normalization is done via UDFs `public.__normalize_table` and `public.__normalize_objects`; must be created before first use
- Kafka source table name format: `xxx_$kafka$_yyy`, normalized to `KAFKA.xxx`
- Volume source table name format: `xxx_t_<32-char hash>`, normalized to `VOLUME.xxx`
- Intermediate tables/directories `__delta__`, `__incr__`, `__DIRECTORY__EXTERNAL__` are filtered out
- `COMPACTION_JOB` type jobs are excluded from lineage construction
- Jobs with output are treated as production jobs (DML); jobs without output are treated as query jobs
- Cost data is a daily average: total divided by the number of queried days

## Troubleshooting

Visualization is empty
Cause: No job execution history available
Solution: First confirm that the table relationship and table cost SQL queries run correctly. If results are empty, this is expected behavior.

Too many nodes causing lag
Cause: Browser rendering too many DOM nodes
Solution: Add schema filter conditions to the SQL queries to narrow the analysis scope

job_history query timeout
Cause: Data volume too large
Solution: Shorten the time window, e.g., change `interval 30 day` to `interval 1 day`
