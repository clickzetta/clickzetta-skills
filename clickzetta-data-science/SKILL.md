---
name: clickzetta-data-science
description: |
  End-to-end data science workflow guide for ClickZetta Lakehouse, covering environment setup, data discovery, feature engineering (SQL + ZettaPark), and model inference deployment.
  Details: Python 3.10+/Jupyter/ZettaPark setup, project structure, data quality assessment, and inference (BITMAP profiling, UDF batch inference, vector search).
  Trigger when the user wants to do data science, ML, or analytical work using
  ClickZetta Lakehouse — connecting Jupyter to Lakehouse, doing EDA, building features,
  running ML inference, user profiling, audience segmentation, or batch scoring.
  Keywords: data science, ML, ZettaPark, Jupyter, feature engineering, EDA, profiling, inference
---

# clickzetta-data-science

See [references/setup.md](references/setup.md) for environment setup and Jupyter kernel configuration.
See [references/zettapark-api.md](references/zettapark-api.md) for ZettaPark DataFrame API reference.
See [references/data-patterns.md](references/data-patterns.md) for data discovery, quality, and feature engineering patterns.
See [references/stats-functions.md](references/stats-functions.md) for statistical analysis SQL functions.
See [references/write-and-infer.md](references/write-and-infer.md) for writing results back to Lakehouse and model inference patterns.
See [references/bitmap-profile.md](references/bitmap-profile.md) for BITMAP-based user profiling and audience segmentation.

---

## Goal

Help the user complete their data science workflow end-to-end using ClickZetta Lakehouse as the data backend.
Meet the user where they are — whether they're setting up for the first time or already mid-project.

## Workflow

**Assess state → Fill gaps → Execute work stage**

### Step 0: Assess where the user is

Before diving in, quickly determine:
- **Environment ready?** Python 3.10+, ZettaPark installed, Jupyter kernel configured?
- **Which stage?** Setup / data discovery / feature engineering / model inference?
- **Experience level?** First time with ZettaPark, or already familiar?

If environment is not ready, go to Setup first — ZettaPark requires Python 3.10+ and will silently fail on 3.9.

### Step 1: Environment Setup (if needed)

See [references/setup.md](references/setup.md) for full steps. Quick check:

```bash
python --version          # must be 3.10+
pip show clickzetta-zettapark  # check if installed
```

If not ready:
```bash
pip install clickzetta-zettapark jupyter
```

Then configure the Jupyter kernel to connect to Lakehouse (connection params: instance, workspace, vcluster, username, password).

### Step 2: Project Structure

Use the Cookiecutter Data Science standard layout — keeps notebooks, data, and models organized:

```
{project}/
├── notebooks/          # Jupyter notebooks (exploration, EDA)
├── src/                # reusable Python modules
├── data/
│   ├── raw/            # original extracts (never modify)
│   └── processed/      # cleaned / feature tables
├── models/             # trained model artifacts
├── config.json         # Lakehouse connection config (gitignored)
└── .env                # secrets (gitignored)
```

### Step 3: Data Discovery & Quality

Use ZettaPark or `%%sql` magic to explore tables. Key patterns in [references/data-patterns.md](references/data-patterns.md):
- Schema and table discovery
- Row count, null rate, cardinality checks
- Distribution sampling with `TABLESAMPLE`
- Approximate statistics with `approx_percentile`, `approx_count_distinct`

### Step 4: Feature Engineering

Two approaches — choose based on data volume:
- **SQL-first** (recommended for large tables): write feature logic as SQL, materialize as Lakehouse table
- **ZettaPark DataFrame** (for complex Python logic): use ZettaPark API, push computation to Lakehouse

See [references/zettapark-api.md](references/zettapark-api.md) for DataFrame API patterns.

### Step 5: Model Inference & Write-back

After training, write predictions back to Lakehouse. Three patterns in [references/write-and-infer.md](references/write-and-infer.md):
- **UDF batch inference**: register Python model as UDF, run inference in SQL
- **BITMAP user profiling**: high-performance audience segmentation — see [references/bitmap-profile.md](references/bitmap-profile.md)
- **Vector search**: store embeddings in Lakehouse, query with cosine similarity

## Data Write Rules

- Always use `CREATE TABLE IF NOT EXISTS` — ClickZetta regular tables don't support `CREATE OR REPLACE TABLE`
- For incremental writes, use `INSERT INTO` or ZettaPark `df.write.mode("append")`
- For full refresh, `TRUNCATE TABLE` then `INSERT INTO` (safer than DROP + CREATE)

## Unsupported ClickZetta SQL Syntax

| Not Supported | Alternative |
|---|---|
| `CREATE OR REPLACE TABLE` | `CREATE TABLE IF NOT EXISTS` |
| `ARRAY_AGG(col IGNORE NULLS)` | `MAX(col)` or `COALESCE()` |
| `QUALIFY` clause | Subquery + `WHERE rn = 1` |
| `UNION` / `INTERSECT` / `EXCEPT` | JOIN + application-layer merge |
| `BEGIN; COMMIT; ROLLBACK;` | Use MERGE for atomic operations |
| `NOW()` | `CURRENT_TIMESTAMP()` |

For other syntax errors, load `clickzetta-sql-migration` to see Snowflake/Databricks/Spark vs. ClickZetta differences.

## Routing

| Scenario | Route to |
|---|---|
| Need to ingest raw data into Lakehouse first | `clickzetta-data-ingest-pipeline` |
| Want to build dbt models from the feature tables | `clickzetta-dbt-modeling` |
| Need to connect a BI tool to visualize results | `lakehouse-doc-en` official BI / JDBC / SQLAlchemy connection docs |
| SQL syntax errors beyond the table above | `clickzetta-sql-migration` |
