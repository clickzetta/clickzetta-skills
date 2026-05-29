# ZettaPark Quick Start

This guide helps you complete installation, establish a session, query data, and write to a table — the full workflow — in under 10 minutes.

## Prerequisites

- Python 3.10 or higher
- An existing Singdata Lakehouse account with the following connection details ready: instance name, workspace name, username, and password

## Installation

```bash
pip install clickzetta_zettapark_python
```

> 💡 **Tip**: In Jupyter Notebook, use `!pip install clickzetta_zettapark_python`.

## Establishing a Session

A session is the entry point for all operations. It connects to a specified Lakehouse instance and workspace.

```python
from clickzetta.zettapark.session import Session

session = Session.builder.configs({
    "username": "your_username",
    "password": "your_password",
    "service":  "cn-shanghai-alicloud.api.singdata.com",
    "instance": "your_instance",
    "workspace": "your_workspace",
    "schema":   "public",
    "vcluster": "default"
}).create()
```

Verify the connection:

```python
session.sql("SHOW SCHEMAS").show(3)
```

```
+-----------------+
|      schema_name|
+-----------------+
|           bronze|
|       cat_litter|
|clickzetta_doc_kb|
+-----------------+
```

## Querying Data

Create a DataFrame from an existing table and apply filters:

```python
from clickzetta.zettapark import functions as F

df = session.table("your_table")
df.filter(F.col("amount") > 100).select("id", "amount", "region").show(5)
```

You can also execute SQL directly:

```python
df = session.sql("SELECT region, SUM(amount) AS total FROM your_table GROUP BY region")
df.show()
```

> 💡 **Tip**: `show()` triggers execution and prints the results; `collect()` returns a list of `Row` objects; `to_pandas()` returns a pandas DataFrame.

## Writing to a Table

Write Python data to a Lakehouse table:

```python
from clickzetta.zettapark.types import IntegerType, StringType, StructType, StructField

schema = StructType([
    StructField("id",     IntegerType()),
    StructField("name",   StringType()),
    StructField("amount", IntegerType()),
])

df = session.create_dataframe(
    [[1, "Alice", 200], [2, "Bob", 150], [3, "Carol", 300]],
    schema=schema
)

df.write.save_as_table("my_first_table", mode="overwrite")
```

Verify the write result:

```python
session.table("my_first_table").show()
```

```
+---+-----+------+
| id| name|amount|
+---+-----+------+
|  1|Alice|   200|
|  2|  Bob|   150|
|  3|Carol|   300|
+---+-----+------+
```

## Closing a Session

```python
session.close()
```

## Next Steps

| Goal | Documentation |
|------|---------------|
| Learn the full DataFrame API | [DataFrame API Guide](zettapark-dataframe-guide.md) |
| Find built-in functions | [Functions Reference](zettapark-functions-guide.md) |
| Build a complete ETL pipeline | [Data Engineering in Practice](zettapark-etl-guide.md) |
| Work with Volume files | [Volume and File Operations](zettapark-volume-guide.md) |
| Download Jupyter Notebook examples | [clickzetta_quickstart](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Zettapark_quickstart.ipynb) |
