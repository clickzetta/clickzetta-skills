# Incremental Sync from External Data Sources in Practice

This article demonstrates a complete two-stage incremental sync pipeline: a **Shell task** pulls raw data from an external HTTP API and writes it to the Lakehouse raw layer, and a **Python task** reads from the raw layer, cleans and standardizes the data, and writes it to the clean layer. The two tasks are chained via a dependency relationship and execute automatically every day.

The example uses the **GitHub Releases API** as the data source, syncing version release records for dbt-clickzetta.

---

## Pipeline Architecture

```
External HTTP API (GitHub Releases)
    ↓ Shell task (pulls daily, writes to raw layer)
doc_github_raw (raw JSON fields, full history retained)
    ↓ Python task (deduplication, version number parsing, writes to clean layer)
doc_github_clean (standardized fields, ready for direct query and analysis)
```

**Why two tasks instead of one?**

- The raw layer retains original data; if something goes wrong, you can rerun the cleaning task without re-calling the API
- Shell and Python each do what they do best: Shell excels at calling external commands and writing files; Python excels at data processing logic
- The two tasks can be debugged and rerun independently

---

## Shell Task: Pull Raw Data

### Script

The Shell layer sets task parameters and calls embedded Python:

```bash
#!/bin/bash
BIZ_DATE='${biz_date}'
echo "Fetch date: $BIZ_DATE"
```

The embedded Python code handles table creation, API fetching, and writing to the raw layer (executed via `python3 - << PYEOF ... PYEOF` heredoc):

```python
import urllib.request, json
from clickzetta_dbutils import get_active_lakehouse_engine
from sqlalchemy import text

biz_date = '$BIZ_DATE'

engine = get_active_lakehouse_engine(schema="doc_connector_demo")
with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS doc_connector_demo"))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS doc_connector_demo.doc_github_raw (
            load_date    STRING,
            repo         STRING,
            tag_name     STRING,
            name         STRING,
            published_at STRING,
            body         STRING,
            raw_json     STRING
        )
    """))

url = "https://api.github.com/repos/clickzetta/dbt-clickzetta/releases?per_page=10"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    releases = json.loads(r.read())
print(f"API returned {len(releases)} records")

with engine.connect() as conn:
    conn.execute(text(f"DELETE FROM doc_connector_demo.doc_github_raw WHERE load_date = '{biz_date}'"))
    for rel in releases:
        tag  = rel['tag_name'].replace("'", "''")
        name = rel['name'].replace("'", "''")[:100]
        pub  = rel['published_at'][:10]
        body = (rel.get('body') or '').replace("'", "''")[:200].replace('\n', ' ')
        raw  = json.dumps({'id': rel['id'], 'tag': rel['tag_name']}).replace("'", "''")
        conn.execute(text(
            f"INSERT INTO doc_connector_demo.doc_github_raw VALUES "
            f"('{biz_date}', 'clickzetta/dbt-clickzetta', '{tag}', '{name}', '{pub}', '{body}', '{raw}')"
        ))
print(f"Wrote {len(releases)} raw records, load_date={biz_date}")

with engine.connect() as conn:
    result = conn.execute(text(
        f"SELECT tag_name, published_at FROM doc_connector_demo.doc_github_raw "
        f"WHERE load_date = '{biz_date}' ORDER BY published_at DESC LIMIT 3"
    ))
    for row in result:
        print(f"  {row[0]:15s} {row[1]}")
```

### Creating and Executing the Task

**Studio UI**

1. Go to **Data Development → New Task**, select **Shell** type, and name it `github_raw_fetch`
2. Paste the script above
3. Click the **Parameters** button and assign `biz_date` the value `$[yyyy-MM-dd]`
4. Click **Schedule** and configure Cron `0 1 * * *` (1 AM every day)
5. Click **Publish**, then click **Run** and enter `biz_date=2024-12-01` to verify

**cz-cli** (see [Studio Task Development and Operations](cz-cli-studio-tasks.md))

```bash
cz-cli task create github_raw_fetch --type shell --profile <your-profile>
cz-cli task save-content github_raw_fetch --file github_raw_fetch.sh \
  --params '{"biz_date": "$[yyyy-MM-dd]"}' --profile <your-profile>
cz-cli task save-config github_raw_fetch --vcluster DEFAULT --retry-count 1 --profile <your-profile>
cz-cli task save-cron github_raw_fetch --cron "0 1 * * *" --profile <your-profile>
cz-cli task online github_raw_fetch -y --profile <your-profile>
cz-cli task execute github_raw_fetch --param "biz_date=2024-12-01" --profile <your-profile>
```

### Execution Results

```
Fetch date: 2024-12-01
API returned 10 records
Wrote 10 raw records, load_date=2024-12-01
  v1.7.10         2026-05-31
  v1.7.9          2026-05-31
  v1.7.8          2026-05-31
```

---

## Python Task: Clean and Standardize

### Script

Task parameters and Session creation:

```python
from clickzetta_dbutils import get_active_lakehouse_engine
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F
from urllib.parse import urlparse, parse_qs
import re

biz_date = '${biz_date}'
print(f"Cleaning date: {biz_date}")

engine = get_active_lakehouse_engine(schema="doc_connector_demo")
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

print(f"Session ready: {session.get_current_catalog()}.{session.get_current_schema()}")
```

Read from the raw layer and convert to pandas for cleaning:

```python
raw = session.table("doc_connector_demo.doc_github_raw").filter(
    F.col("load_date") == biz_date
)
print(f"Raw layer record count: {raw.count()}")

df = raw.to_pandas()

df = df.drop_duplicates(subset=['tag_name'], keep='first')
print(f"After deduplication: {len(df)} records")

def parse_version(tag):
    m = re.match(r'v?(\d+)\.(\d+)\.(\d+)', tag)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None, None, None

df[['major', 'minor', 'patch']] = df['tag_name'].apply(
    lambda t: parse_version(t)
).apply(lambda x: x if x else (None, None, None)).tolist()

df = df.dropna(subset=['major'])
df['major'] = df['major'].astype(int)
df['minor'] = df['minor'].astype(int)
df['patch'] = df['patch'].astype(int)
print(f"Valid versions: {len(df)} records")
```

Create table, write back to clean layer, and print summary:

```python
session.sql("""
    CREATE TABLE IF NOT EXISTS doc_connector_demo.doc_github_clean (
        load_date    STRING,
        repo         STRING,
        tag_name     STRING,
        name         STRING,
        published_at STRING,
        major        INT,
        minor        INT,
        patch        INT
    )
""").collect()

session.sql(f"DELETE FROM doc_connector_demo.doc_github_clean WHERE load_date = '{biz_date}'").collect()

result_df = session.create_dataframe(
    df[['load_date', 'repo', 'tag_name', 'name', 'published_at', 'major', 'minor', 'patch']]
)
result_df.write.mode("append").save_as_table("doc_connector_demo.doc_github_clean")
print(f"Wrote to clean layer: {len(df)} records, load_date={biz_date}")

summary = (
    session.table("doc_connector_demo.doc_github_clean")
    .filter(F.col("load_date") == biz_date)
    .sort(F.col("published_at").desc(), F.col("patch").desc())
    .select("tag_name", "published_at", "major", "minor", "patch")
)
print("\nLatest 5 versions:")
summary.show(5)

session.close()
```

### Creating and Executing the Task

**Studio UI**

1. Go to **Data Development → New Task**, select **Python** type, and name it `github_clean`
2. Paste the script above
3. Click the **Parameters** button and assign `biz_date` the value `$[yyyy-MM-dd]`
4. Click **Schedule** and configure Cron `0 2 * * *` (2 AM, after the Shell task)
5. In **Dependencies**, add the upstream task `github_raw_fetch` to ensure the Shell task completes before this one runs
6. Click **Publish**, then click **Run** and enter `biz_date=2024-12-01` to verify

**cz-cli**

First get the task_id of `github_raw_fetch` (needed for configuring the dependency):

```bash
cz-cli task list --profile <your-profile>
```

Then create the task and configure the dependency:

```bash
cz-cli task create github_clean --type python --profile <your-profile>
cz-cli task save-content github_clean --file github_clean.py \
  --params '{"biz_date": "$[yyyy-MM-dd]"}' --profile <your-profile>
cz-cli task save-config github_clean --vcluster DEFAULT --retry-count 1 \
  --deps replace \
  --dep-tasks '[{"taskId": <github_raw_fetch_task_id>, "taskName": "github_raw_fetch"}]' \
  --profile <your-profile>
cz-cli task save-cron github_clean --cron "0 2 * * *" --profile <your-profile>
cz-cli task online github_clean -y --profile <your-profile>
cz-cli task execute github_clean --param "biz_date=2024-12-01" --profile <your-profile>
```

### Execution Results

```
Cleaning date: 2024-12-01
Session ready: quick_start.doc_connector_demo
Raw layer record count: 10
After deduplication: 10 records
Valid versions: 10 records
Wrote to clean layer: 10 records, load_date=2024-12-01

Latest 5 versions:
--------------------------------------------------------------
|"TAG_NAME"|"PUBLISHED_AT"|"MAJOR"|"MINOR"|"PATCH"|
--------------------------------------------------------------
|v1.7.10   |2026-05-31    |1      |7      |10     |
|v1.7.9    |2026-05-31    |1      |7      |9      |
|v1.7.8    |2026-05-31    |1      |7      |8      |
|v1.7.7    |2026-05-30    |1      |7      |7      |
|v1.7.6    |2026-05-30    |1      |7      |6      |
--------------------------------------------------------------
```

Verify the clean layer:

```sql
SELECT tag_name, published_at, major, minor, patch
FROM doc_connector_demo.doc_github_clean
WHERE load_date = '2024-12-01'
ORDER BY published_at DESC, patch DESC
LIMIT 5;
```

```
tag_name  published_at  major  minor  patch
v1.7.10   2026-05-31    1      7      10
v1.7.9    2026-05-31    1      7      9
v1.7.8    2026-05-31    1      7      8
v1.7.7    2026-05-30    1      7      7
v1.7.6    2026-05-30    1      7      6
```

---

## Key Design Principles

**Idempotent writes**: Before each execution, run `DELETE WHERE load_date = '${biz_date}'`, then insert. Reruns do not produce duplicate data.

**Raw layer retains original data**: The raw layer performs no transformations — only the original fields are stored. When cleaning logic has issues, only the Python task needs to be rerun; the API does not need to be called again.

**Task dependency**: The Python task is configured to depend on the Shell task. The scheduling system ensures the Shell task succeeds before triggering the Python task. If the Shell task fails, the Python task will not execute.

**Consistent parameters**: Both tasks use the same `biz_date` parameter, ensuring the raw layer and clean layer process data for the same day.

---

## Related Documentation

- [Studio Shell Task Development Guide](studio-shell-task.md)
- [Studio Python Task Development Guide (ZettaPark)](studio-python-task-zettapark.md)
- [Task Parameter Syntax Reference](task_param_reference.md)
- [Task Scheduling and Dependencies](task_scheduling_dependency.md)
- [Studio Task Development and Operations (cz-cli)](cz-cli-studio-tasks.md)
