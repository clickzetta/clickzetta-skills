# Studio Python Task — Development Patterns & Practices

> Covers key patterns for developing and deploying **Python tasks** in ClickZetta Lakehouse Studio.
> Based on production experience with 202 Python tasks in the Venture migration project.

## Table of Contents

| Section | Content | Line |
|---------|---------|:----:|
| [1](#1-studio-session-creation-zero-credentials) | Studio session creation (`get_active_lakehouse_engine`) | L22 |
| [2](#2-task-types--deployment) | `save-script` vs `save-content`, Python file constraints | L85 |
| [3](#3-task-parameters-replacing-dbutilswidgets) | Task Parameters (replacing `dbutils.widgets`) | L127 |
| [4](#4-data-read--write) | `session.read.csv/parquet`, COPY INTO, MERGE INTO | L166 |
| [5](#5-file-operations-replacing-dbutilsfs) | `dbutils.fs` → `os.listdir` / `shutil.move` | L228 |
| [6](#6-logging--monitoring) | `print()` → `runs logs`, execution monitoring | L264 |
| [7](#7-etl-watermark-pattern) | Watermark table + UPDATE with INSERT fallback | L291 |
| [8](#8-common-pitfalls) | Hardcoded credentials, path prefixes, non-standard libs, Python version, multi-statement SQL, COPY INTO column alignment, session.close() | L348 |
| [9](#9-complete-template-examples) | incremental_copy 5-step, ForEach, File Batch | L446 |
| [10](#10-related-skills) | Related Skills index | L607 |

---

## 1. Studio Session Creation (Zero Credentials)

> ⚠️ **This is the most critical difference between Studio Python tasks and local development.**

In a Studio Python task, **never hardcode credentials** — username/password/service/instance/workspace are all injected by the Studio runtime via `clickzetta_dbutils`.

### Standard Template (used in all 202 tasks)

```python
from clickzetta_dbutils import get_active_lakehouse_engine
from clickzetta.zettapark.session import Session
from urllib.parse import urlparse, parse_qs

engine = get_active_lakehouse_engine()
url_str = str(engine.url)
# engine.url format: clickzetta://<instance>.<service>/<workspace>?magic_token=xxx&schema=public&virtualcluster=default
parsed = urlparse(url_str.replace('clickzetta://', 'https://'))
params = parse_qs(parsed.query)
parts = parsed.hostname.split('.', 1)   # parts[0]=instance, parts[1]=service

session = Session.builder.configs({
    "service":     parts[1],
    "instance":    parts[0],
    "magic_token": params['magic_token'][0],   # studio-injected temporary token, not a persistent password
    "workspace":   parsed.path.lstrip('/'),
    "schema":      params.get('schema', ['public'])[0],
    "vcluster":    params.get('virtualcluster', ['DEFAULT'])[0],
}).getOrCreate()
```

### Connection Parameter Source

| Parameter | Source | Description |
|-----------|--------|-------------|
| `service` | `engine.url` hostname, second segment | `cn-shanghai-alicloud.api.clickzetta.com` |
| `instance` | `engine.url` hostname, first segment | `f8866243` |
| `magic_token` | `engine.url` query param | Studio-injected temporary auth token |
| `workspace` | `engine.url` path | `quick_start` |
| `schema` | `engine.url` query param | Defaults to `public` |
| `vcluster` | `engine.url` query param | Defaults to `DEFAULT` |

### Studio vs Local

| | Studio Python task | Local Python script |
|---|---|---|
| Connection | `get_active_lakehouse_engine()` → magic_token | `Session.builder.configs({username, password, ...})` |
| Credentials | None (runtime injection) | Plaintext or env vars |
| Use case | Scheduled execution | Local dev / debugging |

---

## 2. Task Types & Deployment

### SQL vs Python vs Shell

| Task Type | Create Command | Save Command | File Format |
|-----------|---------------|-------------|-------------|
| SQL | `task create <name> --type SQL` | `task save-content --content "<sql>"` | Inline SQL text |
| Python | `task create <name> --type PYTHON` | `task save-script --script-file ./main.py` | Upload .py file |
| Shell | `task create <name> --type SHELL` | `task save-script --script-file ./run.sh` | Upload script file |

> ⚠️ **Python tasks must use `save-script`, not `save-content`.** This is the most common creation error.

### Python Task File Constraints

```python
# main.py — Studio Python task entry point
# ⚠️ Single-file execution — cannot import sibling modules (unless pre-installed in env)
# ⚠️ No requirements.txt — dependencies must be pre-installed in VCluster Python env
# ⚠️ Standard library available (os, json, shutil, urllib, datetime, re)
# ⚠️ clickzetta_dbutils & clickzetta_zettapark_python are pre-installed

from clickzetta_dbutils import get_active_lakehouse_engine
from clickzetta.zettapark.session import Session
from urllib.parse import urlparse, parse_qs
import os, json, shutil

# ... business logic ...

session.close()   # recommended: explicit close
```

### One-Step Creation (recommended)

```bash
cz-cli task create-setup my_etl_task \
  --type PYTHON --folder my_dw --vc default \
  --script-file ./main.py \
  --cron '0 0 6 * * * *'
```

---

## 3. Task Parameters (Replacing dbutils.widgets)

### Databricks → Lakehouse Equivalents

| Databricks | Lakehouse Studio Python task |
|-----------|-----------------------------|
| `dbutils.widgets.get("P_BATCH_ID")` | Task parameter `P_BATCH_ID` (defined in schedule config) |
| `dbutils.widgets.text("P_JOB_ID", "")` | Configure via `cz-cli task save-config --params` or Studio UI |
| `dbutils.widgets.removeAll()` | Not needed (parameters injected by scheduler engine, not maintained in code) |

### Reading Parameter Values

```python
# Option 1: Via environment variables (Studio injection)
import os
batch_id = os.environ.get('P_BATCH_ID', '1')
job_id = os.environ.get('P_JOB_ID', '0')
business_date = os.environ.get('P_BUSINESS_DATE_CODE', '')

# Option 2: Via task parameter config (cz-cli)
# cz-cli task save-config <task_id> --params '{"P_BATCH_ID":"1","P_JOB_ID":"290"}'
# Then read via system properties in code (mechanism depends on engine version)
```

### Databricks Notebook Migration

```python
# ❌ Databricks Notebook
P_BATCH_ID = dbutils.widgets.get('P_BATCH_ID').replace("'","")
P_JOB_ID = dbutils.widgets.get('P_JOB_ID').replace("'","")

# ✅ Lakehouse Studio Python task
import os
P_BATCH_ID = os.environ.get('P_BATCH_ID', '')
P_JOB_ID = os.environ.get('P_JOB_ID', '')
```

---

## 4. Data Read & Write

### Reading CSV/Parquet from Volume

```python
# ✅ Option 1: ZettaPark session.read
df = session.read.csv(
    f"vol://venture_bronze/venture_vol/Landing/FTP/20260601/",
    options={"header": "true", "delimiter": "|", "dateFormat": "dd.MM.yyyy"}
)
df = session.read.parquet(f"vol://venture_bronze/venture_vol/")

# ✅ Option 2: SQL COPY INTO
session.sql(f"""
    COPY INTO {BS}.stg_products
    FROM VOLUME venture_vol
    USING PARQUET
    SUBDIRECTORY 'products/2026/'
""").collect()
```

### Databricks → Lakehouse I/O Mapping

| Databricks | Lakehouse Studio Python task |
|-----------|-----------------------------|
| `spark.read.csv("dbfs://...", delimiter="\|", header=True)` | `session.read.csv("vol://...", options={"delimiter": "\|", "header": "true"})` |
| `spark.read.parquet("dbfs://...")` | `session.read.parquet("vol://...")` |
| `spark.table("tbl")` | `session.table("tbl")` |
| `spark.sql("...").collect()` | `session.sql("...").collect()` |
| `df.write.mode("overwrite").saveAsTable("tbl")` | `df.write.save_as_table("tbl", mode="overwrite")` |
| `df.write.mode("append").insertInto("tbl")` | `session.sql("INSERT INTO tbl SELECT ... FROM ...").collect()` |
| `df.count()` | `df.count()` ✅ same |
| `df.filter()/.withColumn()/.drop()` | ZettaPark uses snake_case: `df.filter()` ✅, `df.with_column()` |

### INSERT / MERGE INTO

```python
# Standard migration pattern: COPY INTO staging → MERGE INTO target
session.sql(f"""
    COPY INTO {BS}.stg_products
    FROM VOLUME venture_vol
    USING PARQUET
    SUBDIRECTORY 'products/'
""").collect()

stg_count = session.sql(f"SELECT COUNT(*) FROM {BS}.stg_products").collect()[0][0]

if stg_count > 0:
    session.sql(f"""
        MERGE INTO {BS}.products t
        USING {BS}.stg_products s
        ON t.product_id = s.product_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """).collect()
    print(f"[MERGE] {stg_count} source rows merged")
else:
    print(f"[MERGE] Skipped — staging is empty")
```

---

## 5. File Operations (Replacing dbutils.fs)

### Databricks → Lakehouse Equivalents

| Databricks | Lakehouse Studio Python task |
|-----------|-----------------------------|
| `dbutils.fs.ls("/mnt/...")` | `os.listdir("/path/in/volume")` or `session.sql("SHOW USER VOLUME DIRECTORY").collect()` |
| `dbutils.fs.mv(src, dst)` | `shutil.move(src, dst)` |
| `dbutils.fs.rm(path, recurse=True)` | `shutil.rmtree(path)` or `os.remove(path)` |
| `dbutils.fs.cp(src, dst)` | `shutil.copy2(src, dst)` |
| `dbutils.fs.head(path, 65536)` | `open(path).read(65536)` |
| `dbutils.fs.put("/local/file", "/mnt/...")` | `PUT '/local/file' TO VOLUME vol` (SQL) |

### Volume Paths

```python
# Volumes are exposed as filesystem paths inside Studio tasks
# Internal Volume: /vol/<schema>/<volume_name>/...
# User Volume: /user_vol/...

import os

# List files
files = os.listdir("/vol/venture_bronze/venture_vol/Landing/FTP/")
for f in files:
    print(f)

# Move files
import shutil
shutil.move("/vol/venture_bronze/venture_vol/Landing/file.parquet",
            "/vol/venture_bronze/venture_vol/Archive/file.parquet")
```

---

## 6. Logging & Monitoring

### Log Output

```python
# ✅ Studio Python task stdout/stderr is automatically captured in run logs
# Use print() for key steps; view with: cz-cli runs logs <run_id>

print(f"══ Task: {TASK_NAME} ══")
print(f"  [LookupOld] Watermark: {old_val}")
print(f"  [Copy] {file_count} files → staging")
print(f"  [MERGE] {merge_count} rows into target")
print(f"  [Watermark] updated to {new_val}")
print(f"══ {TABLE_NAME}: {merge_count} rows, watermark={new_val} ✅")
```

### Execution & Viewing

```bash
cz-cli task execute <task_id>                  # Ad-hoc execution
cz-cli runs list --task <task_id> --limit 10   # View history
cz-cli runs logs <run_id>                      # View log (NOT "task logs")
cz-cli runs detail <run_id>                    # View metadata
```

---

## 7. ETL Watermark Pattern

Watermark table for incremental sync state tracking:

```sql
-- ⚠️ Create the watermark table first
CREATE TABLE IF NOT EXISTS etl_watermark (
    table_name  STRING PRIMARY KEY,
    watermark_val STRING,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```python
# Read watermark
old_val = session.sql(f"""
    SELECT watermark_val FROM {BS}.etl_watermark
    WHERE table_name = '{table_name}'
""").collect()

if old_val:
    watermark = old_val[0][0]
    print(f"  [LookupOld] Watermark: {watermark}")
else:
    watermark = "1900-01-01 00:00:00"
    print(f"  [LookupOld] No watermark — first run, using 1900-01-01")

# Get new watermark
new_val = session.sql("SELECT CURRENT_TIMESTAMP").collect()[0][0]

# ... COPY INTO + MERGE INTO ...

# Update watermark — UPDATE with INSERT fallback (first run has no existing row)
wm_rows = session.sql(f"""
    SELECT COUNT(*) FROM {BS}.etl_watermark
    WHERE table_name = '{table_name}'
""").collect()[0][0]

if wm_rows > 0:
    session.sql(f"""
        UPDATE {BS}.etl_watermark
        SET watermark_val = '{new_val}', updated_at = CURRENT_TIMESTAMP
        WHERE table_name = '{table_name}'
    """).collect()
    print(f"  [Watermark] UPDATED → {new_val}")
else:
    session.sql(f"""
        INSERT INTO {BS}.etl_watermark (table_name, watermark_val)
        VALUES ('{table_name}', '{new_val}')
    """).collect()
    print(f"  [Watermark] INSERTED → {new_val}")
```

> ⚠️ **Always use UPDATE + INSERT fallback, never INSERT-only.** INSERT-only causes unbounded watermark table growth.

---

## 8. Common Pitfalls

### 1. Hardcoded Credentials ❌

```python
# ❌ Never do this — unsafe and non-portable inside a Studio task
session = Session.builder.configs({
    "username": "qiliang",
    "password": "xxx",
    "service": "cn-shanghai-alicloud.api.clickzetta.com",
    ...
}).create()

# ✅ Use get_active_lakehouse_engine()
from clickzetta_dbutils import get_active_lakehouse_engine
engine = get_active_lakehouse_engine()
# ... parse engine.url ...
```

### 2. Wrong Path Prefixes ❌

```python
# ❌ dbfs:// is Databricks-only
df = session.read.parquet("dbfs:///mnt/venture/data.parquet")

# ❌ s3a:// is a Hadoop S3 prefix — ZettaPark may not support it
df = session.read.parquet("s3a://bucket/path/data.parquet")

# ✅ Use vol:// prefix
df = session.read.parquet("vol://venture_bronze/venture_vol/data.parquet")
```

### 3. Non-Standard Library Dependencies ❌

```python
# ❌ These may not be installed in the Studio environment
import pandas as pd       # pandas may be unavailable
import numpy as np        # numpy may be unavailable
import requests           # requests may be unavailable

# ✅ Use standard library + ZettaPark
import os, json, shutil
from clickzetta.zettapark import functions as F
```

### 4. Python Version Compatibility ❌

```python
# ❌ Python 3.10+ syntax will fail on 3.9
match status:           # match-case requires 3.10+
    case "SUCCESS": ...

# ✅ Studio Python task environment may be Python 3.9+
# Use compatible syntax
if status == "SUCCESS":
    ...
```

### 5. Multi-Statement SQL ❌

```python
# ❌ Don't execute multiple DDL in a single sql() call
session.sql("DROP TABLE stg; CREATE TABLE stg (...);")

# ✅ Separate each statement with its own collect()
session.sql("DROP TABLE IF EXISTS stg").collect()
session.sql("CREATE TABLE stg (...)").collect()
```

### 6. COPY INTO Assumes Column Alignment ❌

```python
# ❌ Parquet → target direct COPY (assumes Parquet schema matches target exactly)
session.sql("COPY INTO venture_bronze.products FROM VOLUME vol USING PARQUET").collect()

# ✅ COPY INTO staging (STRING wide table) → MERGE INTO target (precise types)
session.sql("COPY INTO venture_bronze.stg_products FROM VOLUME vol USING PARQUET").collect()
session.sql("""
    MERGE INTO venture_bronze.products t
    USING venture_bronze.stg_products s ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""").collect()
```

### 7. Missing session.close()

```python
# ⚠️ Explicitly close the session at script end
# Studio tasks auto-clean on exit, but explicit close prevents resource leaks
try:
    # ... business logic ...
finally:
    session.close()
```

---

## 9. Complete Template Examples

### incremental_copy (5-Step Pattern)

```python
# ══ Incremental Copy: t_dgs3_products ══
# Factory: TebrauVer
# Pattern: Lookup(old WM) → Lookup(new WM) → COPY INTO staging → MERGE INTO target → UPDATE WM

from clickzetta_dbutils import get_active_lakehouse_engine
from clickzetta.zettapark.session import Session
from urllib.parse import urlparse, parse_qs

engine = get_active_lakehouse_engine()
url_str = str(engine.url)
parsed = urlparse(url_str.replace('clickzetta://', 'https://'))
params = parse_qs(parsed.query)
parts = parsed.hostname.split('.', 1)

session = Session.builder.configs({
    "service":     parts[1],
    "instance":    parts[0],
    "magic_token": params['magic_token'][0],
    "workspace":   parsed.path.lstrip('/'),
    "schema":      params.get('schema', ['public'])[0],
    "vcluster":    params.get('virtualcluster', ['DEFAULT'])[0],
}).getOrCreate()

BS = "venture_bronze"
TABLE_NAME = "t_dgs3_products"
STG_TABLE = f"{BS}.stg_{TABLE_NAME}"
TGT_TABLE = f"{BS}.{TABLE_NAME}"

print(f"══ {TABLE_NAME} ══")

# 1. Lookup old watermark
old = session.sql(f"""
    SELECT watermark_val FROM {BS}.etl_watermark
    WHERE table_name = '{TABLE_NAME}'
""").collect()
watermark = old[0][0] if old else "1900-01-01 00:00:00"
print(f"  [LookupOld] watermark = {watermark}")

# 2. Lookup new watermark
new_wm = session.sql("SELECT CURRENT_TIMESTAMP").collect()[0][0]
print(f"  [LookupNew] new watermark = {new_wm}")

# 3. COPY INTO staging (parquet files dropped by upstream Oracle→S3 pipeline)
stg_count = session.sql(f"SELECT COUNT(*) FROM {STG_TABLE}").collect()[0][0]
print(f"  [Copy] staging rows: {stg_count}")

# 4. MERGE INTO target
if stg_count > 0:
    session.sql(f"""
        MERGE INTO {TGT_TABLE} t
        USING {STG_TABLE} s
        ON t.id = s.id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """).collect()
    merge_result = session.sql(f"SELECT COUNT(*) FROM {TGT_TABLE}").collect()[0][0]
    print(f"  [MERGE] {merge_result} rows in target")
else:
    merge_result = session.sql(f"SELECT COUNT(*) FROM {TGT_TABLE}").collect()[0][0]
    print(f"  [MERGE] Skipped — no staging data")

# 5. UPDATE watermark (INSERT fallback for first run)
wm_rows = session.sql(f"""
    SELECT COUNT(*) FROM {BS}.etl_watermark
    WHERE table_name = '{TABLE_NAME}'
""").collect()[0][0]

if wm_rows > 0:
    session.sql(f"""
        UPDATE {BS}.etl_watermark
        SET watermark_val = '{new_wm}', updated_at = CURRENT_TIMESTAMP
        WHERE table_name = '{TABLE_NAME}'
    """).collect()
else:
    session.sql(f"""
        INSERT INTO {BS}.etl_watermark (table_name, watermark_val)
        VALUES ('{TABLE_NAME}', '{new_wm}')
    """).collect()

print(f"══ {TABLE_NAME}: {merge_result} rows, watermark={new_wm} ✅")
session.close()
```

### ForEach Pattern (Batch Processing)

```python
# ══ ForEach Pipeline: Process_Files ══
from clickzetta_dbutils import get_active_lakehouse_engine
from clickzetta.zettapark.session import Session
from urllib.parse import urlparse, parse_qs

# ... session setup (same as above) ...

# 1. List files
files = session.sql("SHOW USER VOLUME DIRECTORY").collect()
file_list = [str(r[0]) for r in files]
print(f"  [GetMetadata] Found {len(file_list)} file(s)")

# 2. ForEach file
for item_file in file_list:
    print(f"  Processing: {item_file}")
    
    # Inner: Copy activity
    session.sql(f"""
        COPY INTO {BS}.stg_orders
        FROM USER VOLUME
        USING CSV OPTIONS('header' = 'true')
        FILES('{item_file}')
    """).collect()
    
    # Inner: MERGE
    session.sql(f"""
        MERGE INTO {BS}.orders t
        USING {BS}.stg_orders s ON t.order_id = s.order_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """).collect()

print(f"══ File batch: {len(file_list)} files processed ✅")
session.close()
```

### File Batch Pattern (with Filtering)

```python
# ══ File Batch Process: FTP_Load ══
# ... session setup ...

# 1. List files
files = session.sql("SHOW USER VOLUME DIRECTORY").collect()
file_list = [str(r[0]) for r in files]

# 2. Filter: only process files matching prefix
prefix = f"{SOURCE_SYSTEM}_"
valid_files = [f for f in file_list if f.startswith(prefix)]
reject_files = [f for f in file_list if not f.startswith(prefix)]

if reject_files:
    print(f"  [Filter] Rejected {len(reject_files)} file(s): {reject_files}")

if not valid_files:
    print(f"  [Filter] No valid files — exiting")
    session.close()
    raise SystemExit(0)

# 3. ForEach valid file
for f in valid_files:
    print(f"  Processing: {f}")
    # ... Copy + MERGE ...

print(f"══ File batch: {len(valid_files)} processed, {len(reject_files)} rejected ✅")
session.close()
```

---

## 10. Related Skills

| Scenario | Skill |
|----------|-------|
| ZettaPark DataFrame API reference | `clickzetta-zettapark` |
| Studio task creation/scheduling/deps | `clickzetta-studio-task-manager` |
| Python connector (BulkLoad, IGS) | `clickzetta-app-python-sdk` |
| SQL migration (Databricks/Spark → Lakehouse) | `clickzetta-sql-migration` |
