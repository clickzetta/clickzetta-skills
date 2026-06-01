# Python Connector Advanced Usage

This page covers the advanced features of `clickzetta-connector`. For basic usage, see [Python Connector SDK](connector.md).

---

## Prerequisites: Establishing a Connection

```python
from clickzetta import connect
import datetime

conn = connect(
    username='your_username',
    password='your_password',
    service='cn-shanghai-alicloud.api.clickzetta.com',
    instance='your_instance',
    workspace='your_workspace',
    schema='public',
    vcluster='default'
)
cursor = conn.cursor()
```

---

## fetch_pandas — Return Results Directly as a DataFrame

Query results are converted directly to a pandas DataFrame, with no manual conversion needed:

```python
cursor.execute("""
    SELECT user_id, SUM(amount) AS total
    FROM orders
    WHERE status = 'paid'
    GROUP BY user_id
""")
df = cursor.fetch_pandas()

print(df.dtypes)
print(df.sort_values('total', ascending=False))

high_value = df[df['total'] > 10000]
print(f"High-value user count: {len(high_value)}")
```

> ⚠️ **Note**: pandas must be installed: `pip install pandas`
>
> TIMESTAMP columns are returned as `datetime64[us, UTC]` (UTC timezone). Be mindful of timezone conversion when processing.

---

## arraysize — Control the Default Batch Size for fetchmany

`cursor.arraysize` controls how many rows `fetchmany()` returns per call when no `size` argument is passed. The default value is 1:

```python
cursor.arraysize = 1000  # 1000 rows per batch

cursor.execute("SELECT * FROM large_table ORDER BY id")

batch_num = 0
while True:
    batch = cursor.fetchmany()  # Fetches arraysize rows each time
    if not batch:
        break
    batch_num += 1
    print(f"Processing batch {batch_num}, {len(batch)} rows")
    # Your processing logic
```

---

## get_job_id — Retrieve the Job ID for a Query

After each SQL execution, you can retrieve the corresponding Job ID for subsequent tracking or cancellation:

```python
cursor.execute("SELECT COUNT(*) FROM orders")
result = cursor.fetchall()

job_id = cursor.get_job_id()
print(f"Job ID: {job_id}")
```

Example output: `2026052700200276167224955`

---

## cancel — Cancel a Running Query

For async queries, you can cancel them during execution:

```python
cursor.execute_async("SELECT * FROM very_large_table")
job_id = cursor.get_job_id()

cursor.cancel(job_id)
print(f"Cancelled job: {job_id}")
```

---

## get_job_profile — Query Performance Analysis

After a query completes, retrieve detailed performance metrics to help diagnose slow queries:

```python
cursor.execute("""
    SELECT status, COUNT(*) AS cnt, SUM(amount) AS total
    FROM orders
    GROUP BY status
""")
cursor.fetchall()
job_id = cursor.get_job_id()

profile = conn.get_job_profile(job_id)
stats = profile.get('jobSummary', {}).get('stats', {}).get('inputOutputStats', {})

print(f"Rows scanned:    {stats.get('inputRowCount')}")
print(f"Rows output:     {stats.get('outputRowCount')}")
print(f"Bytes read:      {stats.get('inputBytes')}")
print(f"Cache hits:      {stats.get('inputCacheBytes')}")
print(f"Disk reads:      {stats.get('inputDiskBytes')}")
```

Cache hit ratio = `inputCacheBytes / inputBytes`. A higher ratio means data is already cached locally on the compute cluster, resulting in faster queries.

---

## get_full_sql_with_params — Debug Parameter Substitution

View the full SQL after parameter binding, useful for debugging:

```python
sql = "SELECT * FROM orders WHERE status = ? AND amount > ?"
params = ('paid', 1000)

full_sql = conn.get_full_sql_with_params(sql, params)
print(full_sql)
```

Output:

```Plain
SELECT * FROM orders WHERE status=paid AND amount>1000
```

> ⚠️ **Note**: The returned SQL is for debugging purposes only. String parameters are shown without quotes and cannot be executed directly.

---

## Dynamic Schema Switching

Switch the default schema within the same connection so subsequent queries do not need to use the fully qualified `schema.table` form:

```python
cursor.execute("USE SCHEMA ods")
cursor.execute("SELECT * FROM raw_orders LIMIT 10")  # Equivalent to ods.raw_orders

cursor.execute("USE SCHEMA ads")
cursor.execute("SELECT * FROM order_summary LIMIT 10")  # Equivalent to ads.order_summary
```

> ⚠️ **Note**: Assigning via `conn.use_schema = 'schema_name'` **does not work**. You must use the `USE SCHEMA` SQL command to switch schemas.

---

## rowcount — Get the Number of Affected Rows

After a DML operation (INSERT / UPDATE / DELETE), use `rowcount` to get the number of affected rows:

```python
cursor.execute("UPDATE orders SET status = 'shipped' WHERE status = 'paid'")
print(f"Updated {cursor.rowcount} rows")

cursor.execute("DELETE FROM orders WHERE status = 'cancelled'")
print(f"Deleted {cursor.rowcount} rows")
```

---

## Complete Example: ETL Data Processing Pipeline

Combining the advanced features above to implement a complete ETL workflow:

```python
from clickzetta import connect
import datetime, time

conn = connect(
    username='your_username',
    password='your_password',
    service='cn-shanghai-alicloud.api.clickzetta.com',
    instance='your_instance',
    workspace='your_workspace',
    schema='public',
    vcluster='default'
)
cursor = conn.cursor()

print("Step 1: Writing raw data...")
cursor.execute("USE SCHEMA ods")
raw_data = [
    (1001, 101, 9999.00, 'paid',    datetime.date(2024, 1, 15)),
    (1002, 102, 4999.00, 'paid',    datetime.date(2024, 1, 15)),
    (1003, 103,  299.00, 'pending', datetime.date(2024, 1, 15)),
]
cursor.executemany(
    'INSERT INTO raw_orders (order_id, user_id, amount, status, created_at) VALUES (?,?,?,?,?)',
    raw_data
)
print(f"  Inserted {len(raw_data)} raw records")

print("Step 2: Async aggregation...")
cursor.execute("USE SCHEMA dws")
cursor.execute_async("""
    INSERT INTO order_stats
    SELECT
        created_at       AS stat_date,
        COUNT(*)         AS order_count,
        SUM(amount)      AS total_amount
    FROM ods.raw_orders
    WHERE status = 'paid'
    GROUP BY created_at
""")
job_id = cursor.get_job_id()

while not cursor.is_job_finished():
    time.sleep(1)
print(f"  Aggregation complete, Job ID: {job_id}")

profile = conn.get_job_profile(job_id)
stats = profile.get('jobSummary', {}).get('stats', {}).get('inputOutputStats', {})
input_bytes = int(stats.get('inputBytes', 0))
cache_bytes = int(stats.get('inputCacheBytes', 0))
cache_ratio = cache_bytes / input_bytes * 100 if input_bytes > 0 else 0
print(f"  Cache hit ratio: {cache_ratio:.1f}%")

cursor.execute("USE SCHEMA dws")
cursor.execute("SELECT * FROM order_stats ORDER BY stat_date DESC LIMIT 7")
df = cursor.fetch_pandas()
print(f"\nStep 4: Last 7 days summary:\n{df}")

cursor.close()
conn.close()
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Python Connector SDK](connector.md) | Installation, connection parameters, and basic API |
| [Python Connector Usage Examples](connector_examples.md) | Common business scenario examples |
| [Zettapark](../zettapark-quick-start.md) | Python DataFrame API for pandas-style operations |
| [BulkLoad](../java_reference/bulkload-upload.md) | High-speed writes for millions of rows |
