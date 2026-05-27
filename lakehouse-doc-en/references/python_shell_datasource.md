# Using Data Sources in Python/Shell Task

## Overview

Python/Shell tasks support the use of pre-configured [data sources](config-datasource.md). By leveraging the built-in `clickzetta-dbutils` package in the runtime environment, tasks can directly reuse the connection configurations from `Management -> Data Sources`, eliminating the need to repeatedly set up connections via code within the node. This approach enhances the security of sensitive information and streamlines development and management processes.

Currently supported data sources include:

* Lakehouse Data Source
* MySQL Data Source
* PostgreSQL Data Source

## Interface Operation Guide

### Selecting Data Sources in Python/Shell Tasks

In the configuration panel of Python/Shell tasks, you can select one or more data sources (ensure that the data sources have been created and tested for connectivity in `Management -> Data Sources`). This configuration will apply to both ad-hoc runs and scheduled runs of the current task:

![](.topwrite/assets/image_1742286995247.png =580)

*Note: The default Lakehouse data source of the current workspace can be accessed directly in the code without needing to add it here*.

### Accessing Data Sources in Code

After adding the data source, you can begin writing Python/Shell task code. To connect to a data source, call the `get_active_engine("your_datasource_name")` function from the `clickzetta_dbutils` Python library. You only need to provide the data source name, without specifying connection details such as the data source URL or password. Additionally, the `Builder` pattern is supported, as detailed in the following API usage guide and code examples.

## API Usage Guide

### get\_active\_engine

A convenient function for creating a database engine in Studio Python nodes (currently supports MySQL, PostgreSQL and Lakehouse data sources).

#### Function Signature

```python
def get_active_engine(
    ds_name: Optional[str] = None,
    vcluster: Optional[str] = None,
    workspace: Optional[str] = None,
    schema: Optional[str] = None,
    options: Optional[Dict[str, str]] = None,
    query: Optional[Dict[str, str]] = None,
    driver: Optional[str] = None,
    host: Optional[str] = None,
    *args, **kwargs
) -> Engine
```

#### Parameter Description

1. `ds_name` (str): The name of the data source, which must match the name in `Management -> Data Sources`.
2. `vcluster` (str, optional): The virtual cluster name for ClickZetta data sources (required for ClickZetta).
3. `workspace` (str, optional): The workspace name, defaulting to the current workspace.
4. `schema` (str, optional): The name of the schema to connect to, defaulting to 'public'.
5. `options` (dict, optional): Additional connection options.
6. `query` (dict, optional): Additional query parameters for the SQLAlchemy URL.

#### Return Value

* An SQLAlchemy Engine instance.

#### Example

* A PostgreSQL data source named "qiliang\_test\_pg" has been added in `Management -> Data Sources`.
* The database "answer" with schema "public" is selected for "qiliang\_test\_pg" in the current Python node.
* Accessing tables within `qiliang_test_pg -> answer -> public` using `get_active_engine`:

```python
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine
pg_engine = get_active_engine("qiliang_test_pg")
# Connect and execute a query
with pg_engine.connect() as pgconnection:
    result = pgconnection.execute(text("SELECT * FROM question limit 10;"))
    for row in result:
        print(row)
```

* Accessing tables in other databases within `qiliang_test_pg` using `get_active_engine` (requires configuring access to other permitted databases in `Management -> Data Sources`, e.g., database "sample" with schema "public"):

```python
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine
pg_engine = get_active_engine("qiliang_test_pg", schema="sample", options={"search_path": "public"})
# Connect and execute a query
with pg_engine.connect() as pgconnection:
    result = pgconnection.execute(text("SELECT * FROM accounts limit 10;"))
    for row in result:
        print(row)
```

### get\_active\_lakehouse\_engine

A convenient function for creating a Lakehouse data source database engine.

#### Function Signature

```python
def get_active_lakehouse_engine(
    vcluster: Optional[str] = None,
    workspace: Optional[str] = None,
    schema: Optional[str] = None,
    options: Optional[Dict[str, str]] = None,
    query: Optional[Dict[str, str]] = None,
    driver: Optional[str] = None,
    *args, **kwargs
) -> Engine
```

#### Parameter Description

1. `vcluster` (str, optional): The virtual cluster name for ClickZetta data sources (required).
2. `workspace` (str, optional): The workspace name, defaulting to the current workspace.
3. `schema` (str, optional): The name of the schema to connect to, defaulting to 'public'.
4. `options` (dict, optional): Additional connection options.
5. `query` (dict, optional): Additional query parameters for the SQLAlchemy URL.
6. `driver` (str, optional): The driver name for the connection.

#### Return Value

* An SQLAlchemy Engine instance.

#### Exception

* `DatabaseConnectionError`: Raised when the Lakehouse data source is not found in the configuration.

#### Example

* The cluster name to be used is "default" in `Compute -> Clusters`.
* The data to be accessed is in the schema "brazilianecommerce" within the workspace "ql\_ws", specifically the table "olist\_customers".
* Accessing tables within `qiliang_test_pg -> answer -> public` using `get_active_lakehouse_engine`:

```python
from sqlalchemy import text
import pandas as pd
from clickzetta_dbutils import get_active_lakehouse_engine

engine = get_active_lakehouse_engine(vcluster="default", schema="brazilianecommerce")
# Connect and execute a query
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM olist_customers limit 10;"))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    print(df.head(10))
```

### DatabaseConnectionManager

A database connection manager that supports chainable configuration of connection parameters. The actual SQLAlchemy connection is triggered only when `build(self, *args, **kwargs)` is called.

#### use\_workspace

Sets the workspace for the connection, required only for Lakehouse data sources.

```python
def use_workspace(self, workspace: str) -> 'DatabaseConnectionManager'
```

#### use\_schema

Sets the schema for the connection.

```python
def use_schema(self, schema: str) -> 'DatabaseConnectionManager'
```

*Note*: *For PostgreSQL*, \`\` *should be set to the database name due to SQLAlchemy design*.

#### use\_vcluster

Sets the virtual cluster for the connection, required only for Lakehouse data sources.

```python
def use_vcluster(self, vcluster: str) -> 'DatabaseConnectionManager'
```

#### use\_options

Sets additional connection options.

```python
def use_options(self, options: dict) -> 'DatabaseConnectionManager'
```

*Note*: *For PostgreSQL, schema should be set using* `undefined"})`.

#### use\_query

Sets additional query parameters for the connection.

```python
def use_query(self, query: dict) -> 'DatabaseConnectionManager'
```

#### build

Creates an SQLAlchemy engine based on the data source name and optional configurations.

```python
def build(self, *args, **kwargs) -> Engine
```

#### Usage Example

```python
from clickzetta_dbutils import DatabaseConnectionManager

# Chainable call example
engine = DatabaseConnectionManager("mysql_source_name")\
    .use_schema("test_schema")\
    .use_options({"charset": "utf8"})\
    .build()

# Lakehouse connection example
engine = DatabaseConnectionManager("LAKEHOUSE_source_name")\
    .use_vcluster("default")\
    .use_workspace("test-workspace")\
    .use_schema("public")\
    .build()
```

## Code Examples

### Example of Using PostgreSQL Data Source in Python Node

Example of retrieving all PostgreSQL tables for `postgres_source_name`:

```python
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine

# Using the default schema
engine = get_active_engine("postgres_source_name")
with engine.connect() as conn:
    results = conn.execute(text("SELECT * FROM pg_tables WHERE schemaname = 'public';"))
    for row in results:
        print(row)

# Specifying the database and schema via options
engine = get_active_engine("postgres_source_name", 
                          schema="pg_database", 
                          options={"search_path": "pg_schema"})
```

### Example of Using MySQL Data Source in Python Node

```python
from sqlalchemy import text
from clickzetta_dbutils import DatabaseConnectionManager

# View all available data source configurations
print(DatabaseConnectionManager.load_connection_configs())

# Create a connection and specify the schema
manager = DatabaseConnectionManager("mysql_source_name")
manager.use_schema("test_schema")
engine = manager.build()

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM test_table LIMIT 1;"))
```

### Example of Using Lakehouse Data Source in Python Node

```python
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine

# Method 1: Using `get_active_engine`
engine = get_active_engine("LAKEHOUSE_source_name", 
                          vcluster="default", 
                          workspace="test-workspace", 
                          schema="public")

# Method 2: Using `get_active_lakehouse_engine`
from clickzetta_dbutils import get_active_lakehouse_engine
engine = get_active_lakehouse_engine(vcluster="default", 
                                   workspace="test-workspace")
with engine.connect() as conn:
    results = conn.execute(text("SELECT 1"))
    for row in results:
        print(row)
```

### Example of Using Data Sources in Shell Node

In Shell nodes, data sources can be used by creating a Python script file:

```bash
cat >> /tmp/db_utils_demo.py << EOF
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine

engine = get_active_engine("postgres_source_name")
with engine.connect() as conn:
    results = conn.execute(text("SELECT * FROM test_table;"))
    for row in results:
        print(row)
EOF

python /tmp/db_utils_demo.py
```

## Precautions

1. Data source configurations support both Adhoc execution and scheduled execution scenarios.
2. Using a non-existent data source name will result in an error. Please ensure that before using it, the corresponding data source is selected in the Studio under `Development -> Python Task -> Data Source`. For Postgres and MySQL data sources, they must be created and tested for connectivity under `Management -> Data Source` to ensure successful connection.
3. When using Lakehouse data sources, the `vcluster` parameter must be configured. Lakehouse data sources directly use the built-in Lakehouse data source seen in `Management -> Data Sources`.
4. Connection information for data sources is securely handled to prevent plaintext password leaks.
5. Multiple data sources of different types can be used within the same node.

^
