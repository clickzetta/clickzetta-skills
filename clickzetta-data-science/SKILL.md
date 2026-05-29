---
name: clickzetta-data-science
description: |
  End-to-end data science workflow guide for ClickZetta Lakehouse. Organized by
  work stage: environment setup (Python 3.10+ check/install), Jupyter Notebook
  configuration, project structure (Cookiecutter DS standard), data discovery,
  data quality assessment, data cleaning and integration, dataset construction,
  EDA, feature engineering (SQL + ZettaPark), and model inference deployment
  (BITMAP user profiling / UDF batch inference / vector search).
  Trigger when user mentions: "data science", "machine learning", "feature engineering",
  "EDA", "data exploration", "ZettaPark ML", "Jupyter connect Lakehouse", "notebook",
  "ipynb", "jupyter kernel", "%%sql", "magic command", "pandas read data",
  "data quality check", "data sampling", "TABLESAMPLE", "approx_percentile",
  "BITMAP user profile", "audience segmentation", "batch inference", "Python 3.10",
  "scikit-learn", "project directory structure", "config.json", ".env".
  Keywords: data science, Jupyter, EDA, feature engineering, ML, pandas, notebook
---

# ClickZetta Lakehouse Data Science Workflow

## Workflow Overview

```
Environment Setup → Jupyter Config → Project Structure → Data Discovery → Data Quality → Data Cleaning
                                                                                               ↓
                                           Model Inference ← Feature Engineering ← EDA ← Dataset Build
```

---

## Hard Prerequisite

**Python 3.10+** (required by ZettaPark). If the user's environment is 3.9 or lower, provide an upgrade path before continuing:

```bash
brew install pyenv && pyenv install 3.12.9 && pyenv local 3.12.9
python -m venv .venv && source .venv/bin/activate
```

See [references/setup.md](references/setup.md) for detailed setup steps.

---

## Project Structure

```
my-ds-project/
├── notebooks/          # 00-env-check.ipynb must be first
│   ├── 00-env-check.ipynb
│   ├── 01-data-discovery.ipynb
│   ├── 02-data-quality.ipynb
│   ├── 03-eda.ipynb
│   ├── 04-feature-engineering.ipynb
│   └── 05-modeling.ipynb
├── src/
│   ├── config.py       # connection config, see references/setup.md
│   ├── data/
│   └── features/
├── sql/
├── data/               # all in .gitignore
├── models/             # all in .gitignore
├── .env                # never commit to git
└── .env.example        # commit to git
```

Environment variable naming: `CLICKZETTA_SERVICE` / `CLICKZETTA_INSTANCE` / `CLICKZETTA_WORKSPACE` / `CLICKZETTA_USERNAME` / `CLICKZETTA_PASSWORD` / `CLICKZETTA_VCLUSTER` / `CLICKZETTA_SCHEMA`.

---

## Data Write Rules

| Method | Verdict |
|------|------|
| `session.create_dataframe(df).write.save_as_table()` | ✅ Recommended |
| `cursor` batch INSERT (500 rows per batch) | ✅ Fallback when Python 3.9 / ZettaPark unavailable |
| `df.to_sql(conn, ...)` | ❌ Forbidden — raises `'list' object has no attribute 'keys'` |
| SQLAlchemy `clickzetta://...` | ❌ Forbidden — dialect is unreliable |

See [references/write-and-infer.md](references/write-and-infer.md) for code templates.

---

## Data Viewing Rules

- Use `.show()` for quick inspection; avoid `.to_pandas()` when pandas is not needed
- Always add `TABLESAMPLE ROW(10)` when working with large tables to prevent OOM

---

## Data Validation Rules

After loading data, **immediately validate statistics against known baseline values** before proceeding with analysis.

Common pitfall: raw athlete/user-level data where each participant in a team event has one row — a direct `SUM` will double-count. Correct approach: `SELECT DISTINCT event, medal, ...` to deduplicate first, then aggregate.

---

## Unsupported ClickZetta SQL Syntax

| Not Supported | Alternative |
|--------|---------|
| `CREATE OR REPLACE TABLE` | `CREATE TABLE IF NOT EXISTS` (regular tables don't support OR REPLACE) |
| `ARRAY_AGG(col IGNORE NULLS)` | `MAX(col)` or `COALESCE()` |
| `QUALIFY` clause | Subquery + `WHERE rn = 1` |
| `UNION` / `INTERSECT` / `EXCEPT` | JOIN + application-layer merge |
| `BEGIN; COMMIT; ROLLBACK;` | Use MERGE for atomic operations |
| `NOW()` | `CURRENT_TIMESTAMP()` |

For other syntax errors, load the `clickzetta-sql-migration` skill to see Snowflake/Databricks/Spark vs. ClickZetta syntax differences.

---

## Schema Context

Always use fully qualified table names (`schema.table`) in SQL within Python code — do not rely on the current schema context.

---

## References

- [Environment Setup & Project Config](references/setup.md) — environment setup, config.py template, Jupyter configuration
- [Data Discovery / Quality / Cleaning / EDA Examples](references/data-patterns.md)
- [Data Write / Feature Engineering / Model Inference Examples](references/write-and-infer.md)
- [ZettaPark API](references/zettapark-api.md)
- [Statistical Analysis Functions](references/stats-functions.md)
- [BITMAP User Profiling](references/bitmap-profile.md)
