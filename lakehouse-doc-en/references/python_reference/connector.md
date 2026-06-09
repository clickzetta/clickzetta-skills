# ClickZetta Connector Python SDK

`clickzetta-connector` is the official Python SDK for Singdata Lakehouse. It follows the PEP-249 specification and provides a SQL call interface compliant with the Python Database API style, supporting queries, writes, bulk inserts, and asynchronous execution.

**This document covers**: Installation → Establish connection → Execute queries → Parameter binding → Batch insert → Asynchronous execution.

> 💡 **Choosing the right interface**:
> - Need a DataFrame API (pandas-style operations) → use [Zettapark](../zettapark-quick-start.md)
> - Need ORM or BI tool connectivity → use [SQLAlchemy](../sqlalchemy.md)
> - Need high-speed bulk import (millions of rows) → use [BulkLoad](../java_reference/bulkload-upload.md)
> - Standard SQL execution, script automation → use this SDK

---

## Installation

```bash
pip install clickzetta-connector
```

Python version >= 3.10 is required.

If an older version is installed, uninstall it first to avoid conflicts:

```bash
pip uninstall clickzetta-connector clickzetta-connector-python clickzetta-sqlalchemy clickzetta-ingestion-python clickzetta-ingestion-python-v2 -y
```

---

## Establish Connection

```python
from clickzetta import connect

conn = connect(
    username='your_username',
    password='your_password',
    service='cn-shanghai-alicloud.api.singdata.com',  # Service endpoint
    instance='your_instance',                          # Instance name
    workspace='your_workspace',                        # Workspace name
    schema='public',                                   # Default schema
    vcluster='DEFAULT'                                 # Compute cluster name
)
```

**Connection parameters**

| Parameter | Required | Description |
|------|------|------|
| `username` | Yes | Username |
| `password` | Yes | Password |
| `service` | Yes | Service endpoint, format `region_id.api.singdata.com`, available in the JDBC connection string under Studio Management → Workspace |
| `instance` | Yes | Instance name, same location as above |
| `workspace` | Yes | Workspace name |
| `schema` | Yes | Default schema name |
| `vcluster` | Yes | Compute cluster name, use `default` as the default |
| `protocol` | No | Default `https`, supports `http` / `https` |

---

## Execute Queries

```python
cursor = conn.cursor()

```

Execute a query:

```python
cursor.execute('SELECT * FROM orders LIMIT 10')

```

Fetch results:

```python
results = cursor.fetchall()
for row in results:
    print(row)

```

Close when done:

```python
cursor.close()
conn.close()
```

**Save results to CSV:**

```python
import csv

cursor.execute('SELECT * FROM orders LIMIT 1000')
results = cursor.fetchall()

with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([col[0] for col in cursor.description])  # Write header
    writer.writerows(results)
```

---

## SQL Hints

Pass SQL hints via `parameters`, for example to set a timeout:

```python
params = {
    'hints': {
        'sdk.job.timeout': 30  # Timeout 30 seconds
    }
}
cursor.execute('SELECT * FROM large_table', parameters=params)
```

For supported parameters, see [Parameter Management](../set-properties.md).

---

## Parameter Binding

> ⚠️ Requires `clickzetta-connector >= 1.0.11`

Two styles are supported, following [PEP-249](https://peps.python.org/pep-0249/#paramstyle):

| Style | Placeholder | Example |
|------|--------|------|
| `qmark` | `?` | `INSERT INTO t VALUES (?, ?)` |
| `pyformat` | `%(name)s` | `INSERT INTO t VALUES (%(id)s, %(name)s)` |

**qmark style:**

```python
cursor.execute('INSERT INTO test (id, name) VALUES (?, ?)', binding_params=[1, 'test'])
```

**pyformat style:**

```python
data = {'id': 1, 'name': 'test'}
cursor.execute('INSERT INTO test (id, name) VALUES (%(id)s, "%(name)s")', data)
```

> ⚠️ In pyformat style, string parameters need quotes in the SQL: `"%(name)s"`

---

## Batch Insert

Use `executemany()` for efficient bulk writes:

```python
data = [
    (1, 'Alice'),
    (2, 'Bob'),
    (3, 'Charlie')
]
cursor.executemany('INSERT INTO users (id, name) VALUES (?, ?)', data)
```

**Automatic type conversion (tolerant mode):**

```python
hints = {'hints': {'cz.sql.type.conversion': 'tolerant'}}
cursor.executemany('INSERT INTO test (id, name) VALUES (int(?), string(?))', data, hints)
```

**Batch insert example with complex types (ARRAY / MAP / STRUCT / JSON):**

```python
import datetime

cursor.execute('''
    CREATE TABLE test_table (
        c_bigint  BIGINT,
        c_boolean BOOLEAN,
        c_date    DATE,
        c_decimal DECIMAL(20, 6),
        c_string  STRING,
        c_array   ARRAY<STRUCT<a: INT, b: STRING>>,
        c_map     MAP<STRING, STRING>,
        c_struct  STRUCT<a: INT, b: STRING, c: DOUBLE>,
        c_json    JSON
    )
''')

data = [(
    1, True,
    datetime.date(2024, 1, 1),
    1000.123456,
    'hello',
    [(1, 'A')],
    {'key': 'value'},
    (1, 'A', 2.0),
    "JSON '{\"id\": 1}'"
)]

cursor.executemany(
    'INSERT INTO test_table VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
    data
)
```

---

## Asynchronous Execution

Suitable for long-running queries to avoid blocking:

```python
import time

cursor.execute_async('SELECT count(*) FROM large_table')

while not cursor.is_job_finished():
    print("Executing...")
    time.sleep(1)

results = cursor.fetchall()
print(results)
```

---

## Notes

- `commit` and `rollback` interfaces are not supported
- For large result sets, use `fetchmany(size)` to fetch in batches and avoid memory overflow
- In production, use a connection pool to manage connections and avoid frequent creation and destruction

---

## Related Documentation

| Document | Description |
|------|------|
| [Zettapark](../zettapark-quick-start.md) | Python DataFrame API, pandas-style operations on Lakehouse data |
| [SQLAlchemy](../sqlalchemy.md) | ORM and BI tool connection configuration |
| [BulkLoad](../java_reference/bulkload-upload.md) | High-speed bulk writes at millions-of-rows scale |
| [Parameter Management](../set-properties.md) | SQL hints and session parameter reference |
| [Connect to Lakehouse](../tutorial_connect_to_lakehouse.md) | Overview of all connection methods |
| [**Usage Examples (complete scenarios)**](connector_examples.md) | Bulk writes, conditional queries, aggregation, CSV export, async execution, and more |
| [**Advanced Usage**](connector_advanced.md) | fetch_pandas, performance analysis, query cancellation, dynamic schema switching, and more |
