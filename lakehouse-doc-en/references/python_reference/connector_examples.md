# Python Connector Usage Examples

This page provides complete, runnable examples of `clickzetta-connector` for common business scenarios.

For connection configuration and basic usage, see [Singdata Connector Python SDK](connector.md).

---

## Prerequisites: Establishing a Connection

All examples below share this connection:

```python
from clickzetta import connect
import datetime, csv

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

## Scenario 1: Bulk Insert Order Data

Create the table:

```python
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id   BIGINT,
        user_id    BIGINT,
        product    STRING,
        amount     DECIMAL(10, 2),
        status     STRING,
        created_at TIMESTAMP
    )
''')
```

Bulk insert:

```python
data = [
    (1001, 101, 'iPhone 15',   7999.00, 'paid',      datetime.datetime(2024, 1, 15, 10, 30, 0)),
    (1002, 102, 'MacBook Pro', 14999.00, 'paid',      datetime.datetime(2024, 1, 15, 11,  0, 0)),
    (1003, 101, 'AirPods Pro', 1799.00, 'pending',   datetime.datetime(2024, 1, 15, 14, 20, 0)),
    (1004, 103, 'iPad Pro',    8999.00, 'paid',      datetime.datetime(2024, 1, 16,  9,  0, 0)),
    (1005, 102, 'Apple Watch', 3299.00, 'cancelled', datetime.datetime(2024, 1, 16, 10,  0, 0)),
]

cursor.executemany(
    'INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)',
    data
)
print(f"Inserted {len(data)} records")
```

> 💡 Write `datetime.datetime` objects to TIMESTAMP columns. When reading back, the values are returned with timezone info (`tzinfo=Asia/Shanghai`) — this is expected behavior.

---

## Scenario 2: Conditional Query and Result Processing

```python
cursor.execute("""
    SELECT order_id, product, amount
    FROM orders
    WHERE status = 'paid'
    ORDER BY amount DESC
""")

rows = cursor.fetchall()
for row in rows:
    print(f"Order {row[0]}: {row[1]} - ¥{row[2]}")
```

Output:

```Plain
Order 1002: MacBook Pro - ¥14999.00
Order 1004: iPad Pro - ¥8999.00
Order 1001: iPhone 15 - ¥7999.00
```

**Use `cursor.description` to get column names:**

```python
cursor.execute("SELECT * FROM orders LIMIT 1")
col_names = [col[0] for col in cursor.description]
print(col_names)
```

Output:

```Plain
['order_id', 'user_id', 'product', 'amount', 'status', 'created_at']
```

---

## Scenario 3: Aggregate Statistics

```python
cursor.execute("""
    SELECT
        user_id,
        COUNT(*)       AS order_count,
        SUM(amount)    AS total_amount,
        MAX(amount)    AS max_order
    FROM orders
    WHERE status = 'paid'
    GROUP BY user_id
    ORDER BY total_amount DESC
""")

rows = cursor.fetchall()
for row in rows:
    print(f"User {row[0]}: {row[1]} orders, total ¥{row[2]}, largest order ¥{row[3]}")
```

---

## Scenario 4: Fetch Large Result Sets in Batches

When the query result is large, use `fetchmany(size)` to process in batches and avoid memory overflow:

```python
cursor.execute("SELECT * FROM orders ORDER BY order_id")

batch_size = 1000
while True:
    batch = cursor.fetchmany(batch_size)
    if not batch:
        break
    # Process this batch
    print(f"Processing {len(batch)} rows...")
    for row in batch:
        pass  # Your processing logic
```

---

## Scenario 5: Export Query Results to CSV

```python
cursor.execute("SELECT * FROM orders WHERE status = 'paid'")
rows = cursor.fetchall()
col_names = [col[0] for col in cursor.description]

with open('paid_orders.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(col_names)   # Write header
    writer.writerows(rows)       # Write data

print(f"Exported {len(rows)} rows to paid_orders.csv")
```

---

## Scenario 6: UPDATE and DELETE

```python
cursor.execute("UPDATE orders SET status = 'shipped' WHERE order_id = 1001")
cursor.execute("DELETE FROM orders WHERE status = 'cancelled'")

cursor.execute("SELECT COUNT(*) FROM orders")
count = cursor.fetchone()[0]
print(f"Current order count: {count}")  # 4
```

---

## Scenario 7: Async Execution of Long-running Queries

Suitable for queries with large data volumes and long execution times, avoiding blocking the main thread:

```python
import time

cursor.execute_async("""
    SELECT status, COUNT(*) AS cnt, SUM(amount) AS total
    FROM orders
    GROUP BY status
""")

while not cursor.is_job_finished():
    print("Query running...")
    time.sleep(1)

results = cursor.fetchall()
for row in results:
    print(f"status={row[0]}, count={row[1]}, amount={row[2]}")
```

---

## Scenario 8: Using SQL Hints to Control Execution Behavior

Set query timeout (in seconds):

```python
params = {'hints': {'sdk.job.timeout': 60}}
cursor.execute('SELECT count(*) FROM large_table', parameters=params)
```

Set parallelism:

```python
params = {'hints': {'sdk.job.timeout': 120, 'cz.sql.shuffle.partitions': '200'}}
cursor.execute('SELECT * FROM large_table GROUP BY category', parameters=params)
```

For supported hints parameters, see [Parameter Management](../set-properties.md).

---

## Notes

- **TIMESTAMP returns with timezone**: When reading TIMESTAMP columns, the returned value includes `tzinfo=Asia/Shanghai`. Be mindful of timezone conversion when processing.
- **Decimal type**: DECIMAL columns return Python `Decimal` objects, not `float`. Be aware of precision when using them directly in calculations.
- **Transactions not supported**: The `commit()` and `rollback()` interfaces are not supported. Each SQL statement is auto-committed.
- **Large result sets**: Avoid using `fetchall()` to pull very large result sets. Use `fetchmany(size)` to process in batches instead.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Python Connector SDK](connector.md) | Installation, connection parameters, and full API reference |
| [Zettapark](../zettapark-quick-start.md) | Python DataFrame API for pandas-style operations |
| [BulkLoad](../java_reference/bulkload-upload.md) | High-speed writes for millions of rows |
| [Parameter Management](../set-properties.md) | SQL hints parameter reference |
