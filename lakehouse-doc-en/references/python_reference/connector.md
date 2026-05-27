# Singdata Connector Official Python SDK

`clickzetta-connector` is the official Python SDK for Singdata Lakehouse. It follows the PEP-249 specification and provides a SQL call interface compliant with the Python Database API style. With this SDK, you can easily execute SQL queries, inserts, updates, and deletes in Python applications.
It also supports bulk data upload (bulkload) functionality, which can significantly increase data import speed, making it especially useful for scenarios involving large volumes of data.

### Usage Example

0. Remove Old Version Dependencies

If an older version of the SDK is installed, please uninstall it first to avoid conflicts:

```shell
pip uninstall clickzetta-connector clickzetta-connector-python clickzetta-sqlalchemy clickzetta-ingestion-python clickzetta-ingestion-python-v2 -y
```

> Please record the old version package information before uninstalling, in case you need to roll back. Command to view installed package versions:

```shell
pip show clickzetta-connector clickzetta-sqlalchemy clickzetta-ingestion-python clickzetta-ingestion-python-v2 clickzetta-connector-python
```


1. Install clickzetta-connector, Python version requirement (>= 3.7):

```shell
pip install clickzetta-connector
```

## Quick Start

### Execute SQL Query

The following is a simple example showing how to use `clickzetta-connector` to execute SQL queries:

```python
from clickzetta import connect

### Establish Connection
conn = connect(
    username='your_username',
    password='your_password',
    service='region_id.api.singdata.com',
    instance='your_instance',
    workspace='your_workspace',
    schema='public',
    vcluster='default'
)

```

| **Parameter** | **Required** | **Description**                                                                                                                              |
|-----------|----------|----------------------------------------------------------------------------------------------------------------------------------- |
| username  | Y        | Username                                                                                                                                 |
| password  | Y        | Password                                                                                                                                  |
| service   | Y        | Address to connect to the Lakehouse, region_id.api.singdata.com. You can view the JDBC connection string in Lakehouse Studio Management -> Workspace ![](../.topwrite/assets/image_1728887857029.png) |
| instance  | Y        | You can view the JDBC connection string in Lakehouse Studio Management -> Workspace ![](../.topwrite/assets/image_1729051500396.png)                                            |
| workspace | Y        | Workspace in use                                                                                                                             |
| vcluster  | Y        | VC in use                                                                                                                               |
| schema    | Y        | Name of the schema to access                                                                                                                          |
| protocol  | N        | Default value is 'https', supports 'http' and 'https'                                                                                                     |

### Simple Query Example

```python
# Create a cursor object
cursor = conn.cursor()
# Execute SQL query
cursor.execute('SELECT * FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live LIMIT 10;')
# Fetch query results
results = cursor.fetchall()
for row in results:
    print(row)
```

### Using SQL Hints

In JDBC, SQL hints set through the set command can be passed via the `parameters` parameter. For supported parameters, refer to [Parameter Management](../sql-parmaters.md). Below is an example:

```python
# Set the job run timeout to 30 seconds
my_param = {
    'hints': {
        'sdk.job.timeout': 30
    }
}
cursor.execute('YOUR_SQL_QUERY', parameters=my_param)
```

### Usage

## More Examples

### 1. Handling Query Results

The following example demonstrates how to handle query results, such as saving the results to a CSV file:

```python
import csv

# Execute query
cursor.execute('SELECT * FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live LIMIT 10;')

# Fetch query results
results = cursor.fetchall()

# Save results to CSV file
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow([column[0] for column in cursor.description])
    csv_writer.writerows(results)
# Close connection
cursor.close()
conn.close()
```

### Advanced Features

> Note: The following advanced features require `clickzetta-connector-python >= 0.8.82` or `clickzetta-connector >= 1.0.11`.

#### Parameter Binding

clickzetta-connector supports two parameter binding styles, following the [PEP-249](https://peps.python.org/pep-0249/#paramstyle) specification:

| paramstyle | Description                             | Example                                |
| ---------- | ------------------------------ | ------------------------------------- |
| qmark      | Uses question mark (?) as a parameter placeholder                | `INSERT INTO test VALUES (?)`         |
| pyformat   | Uses Python extended format codes, e.g., `%(name)s` | `INSERT INTO test VALUES (%(value)s)` |

##### Using Question Mark Style (qmark)

```python
# Simple example
cursor.execute('INSERT INTO test (id, name) VALUES (?, ?)', binding_params=[1, 'test'])

# JSON type example
json_data = "JSON '" + '{"id": 2, "value": "100", "comment": "JSON Sample data"}' + "'"
my_param = {
    'hints': {
        'sdk.job.timeout': 30
    }
}
cursor.execute('INSERT INTO test (id, json_col) VALUES (?, ?)', my_param, binding_params=[1, json_data])
```

##### Batch Insert Using qmark Style

The `executemany()` method supports efficient batch insert operations using the qmark style:

```python
# Prepare data
data = [
    (1, 'test1'),
    (2, 'test2'),
    (3, 'test3')
]

# Execute batch insert
cursor.executemany('INSERT INTO test (id, name) VALUES (?, ?)', data)
```

To enable automatic type conversion of input data based on the table structure, enable the `tolerant` parameter and specify types:

```python
# Prepare data
data = [
    (1, 'test1'),
    (2, 0),
    (3, 0.1)
]

hints = {'hints': {
    "cz.sql.type.conversion": "tolerant"
}}

# Execute batch insert
cursor.executemany('INSERT INTO test (id, name) VALUES (int(?), string(?))', data, hints)
```

##### Using Python Format Style (pyformat)

```python
# Use named parameters
data = {'id': 1, 'name': 'test'}
cursor.execute('INSERT INTO test (id, name) VALUES (%(id)s, "%(name)s")', data)
```

> Note: In pyformat style, string parameter values need to be enclosed in quotes.

##### Complete Example: Batch Insert of Complex Data Types

The following example demonstrates how to use `executemany` to insert data containing various data types:

```python
table = 'test_table'
cursor.execute(f'''
    CREATE TABLE {table} (
        c_bigint BIGINT,
        c_boolean BOOLEAN,
        c_binary BINARY,
        c_char CHAR,
        c_date DATE,
        c_decimal DECIMAL(20, 6),
        c_double DOUBLE,
        c_float FLOAT,
        c_int INT,
        c_interval INTERVAL DAY,
        c_smallint SMALLINT,
        c_string STRING,
        c_timestamp TIMESTAMP,
        c_tinyint TINYINT,
        c_array ARRAY<STRUCT<a: INT, b: STRING>>,
        c_map MAP<STRING, STRING>,
        c_struct STRUCT<a: INT, b: STRING, c: DOUBLE>,
        c_varchar VARCHAR(1024),
        c_json JSON
    )
''')

data = [
    (
        1,
        True,
        b'\x01',
        'a',
        datetime.date(2022, 2, 1),
        1000.123456,
        2.0,
        1.5,
        42,
        'INTERVAL 1 DAY',
        103,
        'test string 1',
        datetime.datetime.now(),
        11,
        [(1, 'A')],
        {'key1': 'value1'},
        (1, 'A', 2.0),
        'varchar example 1',
        ("JSON '" + '{"id": 2, "value": "100", "comment": "JSON Sample data"}' + "'")
    )
]
sql = f'''
    INSERT INTO {table} (
        c_bigint, c_boolean, c_binary, c_char, c_date, c_decimal, c_double, 
        c_float, c_int, c_interval, c_smallint, c_string, c_timestamp, 
        c_tinyint, c_array, c_map, c_struct, c_varchar, c_json
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
'''

cursor.executemany(sql, data)
my_param = {'hints': {}}

# Fetch results
cursor.execute(f'SELECT * FROM {table}', my_param)
result = cursor.fetchall()
```

#### Asynchronous Execution (execute_async)

The `execute_async()` method supports asynchronous execution of SQL queries, especially suitable for long-running queries:

```python
# Execute query asynchronously
cursor.execute_async('SELECT * FROM large_table')

# Check if the query is complete
while not cursor.is_job_finished():
    print("Query executing...")
    time.sleep(1)

# Fetch results
results = cursor.fetchall()
```

#### Notes

* The commit and rollback interfaces are not supported

^
