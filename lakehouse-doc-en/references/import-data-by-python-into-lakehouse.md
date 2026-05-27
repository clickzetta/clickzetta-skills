# Data Import into Lakehouse: Through Python Scripts

In modern data processing, importing data into a database is a common requirement. Using Python scripts for data import brings many advantages and is suitable for various scenarios, such as automation, data processing, and multi-database support. This article uses a PostgreSQL database as an example to demonstrate how to import data into Singdata Lakehouse.

## Advantages

1. **Automation**: By creating automated tasks that run periodically or on demand, real-time data updates or migrations can be achieved.

2. **Data Processing**: Python has powerful data processing capabilities, allowing data to be preprocessed, cleaned, and transformed before importing into the database, improving data quality and import success rates.

3. **Multi-Database Support**: Python provides a wide range of database drivers and libraries, supporting relational databases (such as MySQL, PostgreSQL, SQLite, etc.) and non-relational databases (such as MongoDB, Redis, etc.).

4. **Error Handling and Logging**: When writing import scripts with Python, exceptions can be caught and detailed logs recorded, making it easier to track and resolve issues during the data import process.

## Applicable Scenarios

1. Import data from CSV or Excel files into a database.
2. Preprocess data by applying statistical methods or standardization techniques before importing it into the database.
3. Database migration tasks involving data validation and integrity checks.

## Operation Guide

### 1. Import Required Python Packages

```python
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import pygwalker as pyg
```

### 2. Create a Connection to the PostgreSQL Database and Read Source Table Data

```python
def create_conn_pg(database: str, user: str, password: str, host: str, port: str):
    connection = psycopg2.connect(
        dbname=database,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return connection
```

### 3. Use `pd.read_sql_query()` to Query Data from the Database and Store It in a DataFrame

```python
conn_pg = create_conn_pg("<database>", "<username>", "<password>", "<host>", "<port>")
query = "SELECT * FROM public.orders;"
df = pd.read_sql_query(query, conn_pg)
conn_pg.close()
```

### 4. View PostgreSQL Data and Perform Cleaning and Visual Analysis

```python
# View total row count
print(df.shape[0])

# Replace all NaN values with 0
df.fillna(0, inplace=True)

# Display the first 5 rows
print(df.head(5))
```

### 5. Use PyGWalker for Pivot Analysis (Optional)

```python
walker = pyg.walk(df)
```

### 6. Create a Target Table in Singdata Lakehouse

```python
engine_cz = create_engine("clickzetta://<username>:<password>@<instanceid>.<region_id>.api.clickzetta.com/<workspacename>?virtualcluster=<vcluster>&schema=<public>")
sql_cz = text("""
CREATE TABLE IF NOT EXISTS orders_tmp (
    id INT,
    user_id INT,
    product_id INT,
    subtotal DECIMAL(8, 2),
    tax DECIMAL(8, 2),
    total DECIMAL(16, 3),
    discount DECIMAL(8, 2),
    created_at TIMESTAMP,
    quantity INT
);
""")
with engine_cz.connect() as conn:
    results = conn.execute(sql_cz)
```

### 7. Write the Transformed Source Table Data to the Singdata Lakehouse Target Table

```python
conn_cz = connect(
    username="<username>",
    password="<password>",
    service="<region_id>.api.clickzetta.com",
    instance="<instanceid>",
    workspace="<workspacename>",
    schema="public",
    vcluster="default"
)
bulkload_stream = conn_cz.create_bulkload_stream(schema="public", table="orders")
writer = bulkload_stream.open_writer(0)
for index, row_data in df.iterrows():
    row = writer.create_row()
    row.set_value("id", row_data["id"])
    row.set_value("created_at", row_data["created_at"])
    row.set_value("user_id", row_data["user_id"])
    row.set_value("product_id", row_data["product_id"])
    row.set_value("subtotal", row_data["subtotal"])
    row.set_value("tax", row_data["tax"])
    row.set_value("total", row_data["total"])
    row.set_value("discount", row_data["discount"])
    row.set_value("quantity", row_data["quantity"])
    writer.write(row)
writer.close()
bulkload_stream.commit()
```

### 8. Clean Up Resources

```
# Drop Singdata Lakehouse target table
sql_cz = text("""drop table if exists orders ;""")
with engine_cz.connect() as conn:
    results = conn.execute(sql_cz)
```

^
