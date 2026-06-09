# Studio Shell Task Development Guide

Studio Shell tasks run Bash scripts in a server-side Linux environment, with pre-installed tools including `curl`, `wget`, `awk`, `sed`, `grep`, and `python3`.

**When to choose a Shell task vs. a Python task**:

| Scenario | Recommended |
|---|---|
| Team already has bash scripts and wants to plug them into the scheduling system | Shell task |
| Text processing with `awk`/`sed`/pipes where shell logic is more concise | Shell task |
| Need to call system binary tools (`ffmpeg`, `convert`, etc.) | Shell task |
| Developing new data processing logic that requires complex computation or DataFrame operations | Python task |
| Need the ZettaPark DataFrame API | Python task |

Shell tasks and Python tasks have highly overlapping capabilities — Shell tasks can embed `python3` code, and Python tasks can call shell commands via `subprocess`. The choice is primarily based on **the form of existing code** and **team conventions**, not functional differences.

---

## Runtime Environment

Shell tasks run in a Linux Pod managed by Studio. A new Pod is started for each execution and destroyed after completion.

| Item | Description |
|---|---|
| Operating system | Linux x86_64 (kernel 5.10) |
| Running user | `system_normal` |
| Python version | Python 3.10.0 |
| Pre-installed CLI tools | `python3`, `curl`, `wget`, `awk`, `sed`, `grep`, `find`, `tar`, `gzip` |
| Pre-installed Python packages | `clickzetta`, `clickzetta_dbutils`, `pandas`, `requests`, `boto3`, `oss2` |

> 💡 **Tip**: The Pod environment is not preserved after destruction. If you need to install additional packages, use `pip install --target /home/system_normal <pkg>` at the beginning of the script, and add `sys.path.append('/home/system_normal')` in your Python code.

**Connecting to Lakehouse**: Obtain a connection via `clickzetta_dbutils` — no need to hardcode credentials:

```python
from clickzetta_dbutils import get_active_lakehouse_engine
from sqlalchemy import text

engine = get_active_lakehouse_engine(schema="your_schema")
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
```

---

## Scenario: Integrating an Existing Shell Script into the Scheduling System

A typical scenario: the team has a batch of shell scripts that process logs or CSV files using `awk`/`sed`, and wants to plug them directly into the Studio scheduling system, writing the processed results to Lakehouse.

The following example simulates a common pattern: download a CSV file → filter and clean with `awk` → write to Lakehouse with `python3`.

### Complete Script

```bash
#!/bin/bash
# Task parameter: biz_date = $[yyyy-MM-dd, -1d]
BIZ_DATE='${biz_date}'
echo "Processing date: $BIZ_DATE"

# ── 1. Download raw data file ──────────────────────────────────────────────
wget -q "https://jsonplaceholder.typicode.com/posts" -O /tmp/posts.json
echo "Download complete: $(wc -c < /tmp/posts.json) bytes"

# ── 2. Parse JSON with python3 + filter with awk (posts where userId <= 3) ─
python3 -c "
import json
posts = json.load(open('/tmp/posts.json'))
for p in posts:
    print(f\"{p['id']},{p['userId']},{p['title'][:30].replace(',','')}\")
" | awk -F, '$2 <= 3 {print}' > /tmp/posts_filtered.csv

echo "Filtered row count: $(wc -l < /tmp/posts_filtered.csv)"

# ── 3. Write results to Lakehouse with python3 ───────────────────────────
python3 - << PYEOF
from clickzetta_dbutils import get_active_lakehouse_engine
from sqlalchemy import text

biz_date = '$BIZ_DATE'
engine = get_active_lakehouse_engine(schema="doc_connector_demo")

with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS doc_connector_demo"))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS doc_connector_demo.doc_shell_posts (
            post_id   INT,
            user_id   INT,
            title     STRING,
            load_date STRING
        )
    """))
    conn.execute(text(f"DELETE FROM doc_connector_demo.doc_shell_posts WHERE load_date = '{biz_date}'"))

    rows = 0
    with open('/tmp/posts_filtered.csv') as f:
        for line in f:
            parts = line.strip().split(',', 2)
            if len(parts) == 3:
                post_id, user_id, title = parts
                title = title.replace("'", "''")
                conn.execute(text(
                    f"INSERT INTO doc_connector_demo.doc_shell_posts VALUES "
                    f"({post_id}, {user_id}, '{title}', '{biz_date}')"
                ))
                rows += 1

print(f"Wrote {rows} rows, load_date={biz_date}")

with engine.connect() as conn:
    result = conn.execute(text(
        f"SELECT COUNT(*) as cnt, COUNT(DISTINCT user_id) as users "
        f"FROM doc_connector_demo.doc_shell_posts WHERE load_date = '{biz_date}'"
    ))
    row = result.fetchone()
    print(f"Verified: {row[0]} records, {row[1]} users")
PYEOF
```

### Creating and Executing the Task

**Studio UI**

1. Go to **Data Development → New Task**, select **Shell** type, and enter a task name
2. Paste the script above into the editor
3. Click the **Parameters** button on the right; the system automatically detects `${biz_date}` and assigns it the value `$[yyyy-MM-dd, -1d]` (yesterday's date)
4. Click the **Schedule** button, configure the VCluster (select general-purpose `DEFAULT`) and Cron expression (e.g., `0 1 * * *`)
5. Click **Publish**, then click **Run** → enter `biz_date=2024-12-01` in the dialog to verify

**cz-cli** (suitable for CI/CD or bulk management scenarios; see [Studio Task Development and Operations](cz-cli-studio-tasks.md))

```bash
# Create the task
cz-cli task create shell_etl --type shell --profile <your-profile>

# Upload the script and configure parameters
cz-cli task save-content shell_etl --file shell_etl.sh \
  --params '{"biz_date": "$[yyyy-MM-dd, -1d]"}' \
  --profile <your-profile>

# Configure scheduling
cz-cli task save-config shell_etl --vcluster DEFAULT --retry-count 1 --profile <your-profile>
cz-cli task save-cron shell_etl --cron "0 1 * * *" --profile <your-profile>

# Publish and run a one-time execution to verify
cz-cli task online shell_etl -y --profile <your-profile>
cz-cli task execute shell_etl --param "biz_date=2024-12-01" --profile <your-profile>
```

### Execution Results

```
Processing date: 2024-12-01
Download complete: 27520 bytes
Filtered row count: 30
Wrote 30 rows, load_date=2024-12-01
Verified: 30 records, 3 users
```

Verify the written results:

```sql
SELECT user_id, COUNT(*) AS post_count
FROM doc_connector_demo.doc_shell_posts
WHERE load_date = '2024-12-01'
GROUP BY user_id
ORDER BY user_id;
```

```
user_id  post_count
1        10
2        10
3        10
```

---

## Notes

- The task parameter `${biz_date}` is a string substitution at the Shell level; pass it to embedded Python using `'$BIZ_DATE'` to reference the Shell variable
- `python3 - << PYEOF ... PYEOF` is the standard heredoc pattern for embedding Python in a shell script
- The Pod environment is brand new on each execution; files in `/tmp` are not preserved across runs
- `cz-cli` is not supported inside the script; Lakehouse operations are performed via `clickzetta_dbutils` + SQLAlchemy

---

## Related Documentation

- [Task Parameter Syntax Reference](task_param_reference.md)
- [Studio Python Task Development Guide (Python Connector)](studio-python-task-connector.md)
- [Studio Task Development and Operations (cz-cli)](cz-cli-studio-tasks.md)
