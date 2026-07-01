# Zettapark Table Stream (CDC Incremental Processing)

Table Stream records incremental changes (INSERT / UPDATE / DELETE) on a table. Zettapark lets you read a Stream directly with `session.table()`, treating the change data as a DataFrame to build incremental ETL pipelines.

---

## Prerequisites

```python
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F

session = Session.builder.configs({
    "username": "your_username",
    "password": "your_password",
    "service":  "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "your_instance",
    "workspace": "your_workspace",
    "schema":   "public",
    "vcluster": "DEFAULT"
}).create()
```

---

## Create the Source Table and Stream

Create the source table and enable change tracking:

```python
session.sql("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT, name STRING, amount DECIMAL(10,2), status STRING
    )
""").collect()

session.sql("""
    ALTER TABLE orders SET PROPERTIES ('change_tracking' = 'true')
""").collect()
```

Insert initial data:

```python
session.sql("""
    INSERT INTO orders VALUES
    (1, 'Alice', 1000.00, 'active'),
    (2, 'Bob',   2000.00, 'active'),
    (3, 'Carol',  500.00, 'active')
""").collect()
```

Create a Table Stream (STANDARD mode, captures INSERT/UPDATE/DELETE):

```python
session.sql("""
    CREATE TABLE STREAM orders_stream ON TABLE orders
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD')
""").collect()
```

> 💡 `change_tracking` must be enabled via `ALTER TABLE SET PROPERTIES`. Specifying it at table creation time has no effect.

---

## Read Stream Changes

Use `session.table()` to read the Stream directly, returning a DataFrame:

```python
stream_df = session.table("orders_stream")
stream_df.printSchema()
```

The Stream DataFrame includes the following metadata columns:

| Column | Type | Description |
|--------|------|-------------|
| `__change_type` | STRING | Change type: `INSERT` / `UPDATE_BEFORE` / `UPDATE_AFTER` / `DELETE` |
| `__commit_version` | BIGINT | Commit version number |
| `__commit_timestamp` | TIMESTAMP | Commit timestamp |
| All original table columns | — | Data of the changed row |

---

## Produce Changes and Consume

Produce changes:

```python
session.sql("INSERT INTO orders VALUES (4, 'Dave', 3000.00, 'active')").collect()
session.sql("UPDATE orders SET amount = 1500.00 WHERE id = 1").collect()
session.sql("DELETE FROM orders WHERE id = 3").collect()
```

Read all changes:

```python
stream_df = session.table("orders_stream")
stream_df.show()
```

```Plain
+-------------+----------------+--------------------+---+-----+-------+------+
|__change_type|__commit_version|  __commit_timestamp| id| name| amount|status|
+-------------+----------------+--------------------+---+-----+-------+------+
| UPDATE_AFTER|               5|2024-01-15 10:00:...|  1|Alice|1500.00|active|
|       INSERT|               4|2024-01-15 10:00:...|  4| Dave|3000.00|active|
|UPDATE_BEFORE|               3|2024-01-15 09:59:...|  1|Alice|1000.00|active|
|       DELETE|               3|2024-01-15 09:59:...|  3|Carol| 500.00|active|
+-------------+----------------+--------------------+---+-----+-------+------+
```

---

## Filter by Change Type

Keep only inserts and post-update rows (ignore UPDATE_BEFORE and DELETE):

```python
inserts_and_updates = stream_df.filter(
    F.col("`__change_type`").isin(["INSERT", "UPDATE_AFTER"])
).select("id", "name", "amount", "status")
```

Keep only deleted rows:

```python
deletes = stream_df.filter(
    F.col("`__change_type`") == "DELETE"
).select("id")
```

> ⚠️ The `__change_type` column name contains double underscores. Reference it with backticks: `` F.col("`__change_type`") ``

---

## Full CDC Incremental Pipeline

Write Stream changes to a target table for incremental synchronization.

Create the target table:

```python
session.sql("""
    CREATE TABLE IF NOT EXISTS orders_target (
        id INT, name STRING, amount DECIMAL(10,2), status STRING
    )
""").collect()
```

Read the Stream and filter for valid changes:

```python
stream_df = session.table("orders_stream")
changes = stream_df.filter(
    F.col("`__change_type`").isin(["INSERT", "UPDATE_AFTER"])
).select("id", "name", "amount", "status")
```

Write to the target table:

```python
changes.write.save_as_table("orders_target", mode="append")
```

After consumption, the Stream offset advances automatically. The next read returns only new changes.

**For production, use MERGE INTO for upsert semantics:**

Write Stream changes to a staging table, then merge with SQL MERGE INTO:

```python

session.sql("""
    MERGE INTO orders_target AS t
    USING orders_changes_tmp AS s
    ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET
        t.name = s.name, t.amount = s.amount, t.status = s.status
    WHEN NOT MATCHED THEN INSERT (id, name, amount, status)
        VALUES (s.id, s.name, s.amount, s.status)
""").collect()

session.sql("DROP TABLE IF EXISTS orders_changes_tmp").collect()
```

---

## Notes

- **Stream offset advancement**: After each read of the Stream followed by an action (`collect()`, `save_as_table()`, etc.), the offset advances automatically. The next read returns only new changes.
- **UPDATE produces two records**: `UPDATE_BEFORE` (pre-update) and `UPDATE_AFTER` (post-update). You typically only need `UPDATE_AFTER`.
- **Stream does not store data**: A Stream is a cursor object. Data remains in the source table and no extra storage is consumed.
- **`change_tracking` cannot be set at table creation**: You must enable it after table creation using `ALTER TABLE SET PROPERTIES`.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Table Stream](table-stream-title.md) | Table Stream concepts and SQL syntax |
| [Zettapark Data Engineering Guide](zettapark-etl-guide.md) | Multi-table joins, window functions, and more |
| [Dynamic Table](dynamic-table.md) | Automatic incremental refresh as an alternative to manual scheduling |
