# Using Data Sources in Python/Shell Tasks

## Overview

Python/Shell tasks support the use of pre-configured [data sources](config-datasource.md). Through the built-in `clickzetta-dbutils` package in the runtime environment, you can reuse connection configurations from **Management → Data Sources** directly in your tasks — no need to hard-code connection details in your code. This improves the security of sensitive credentials and simplifies both development and management.

Currently supported data source types:

* Lakehouse data source
* MySQL data source
* PostgreSQL data source

## UI Guide

### Selecting a Data Source in a Python/Shell Task

In the configuration panel of a Python/Shell task, you can select one or more data sources to use (make sure the data source has already been created and connection-tested under Management → Data Sources). This configuration applies to both direct runs and scheduled runs of the task:

![](.topwrite/assets/image_1742284598370.png =560)

*Note: The default Lakehouse data source for the current workspace is accessible in code without needing to be added here.*

### Accessing a Data Source in Code

After adding a data source, you can start writing your Python/Shell task code. Call the `get_active_engine("your_datasource_name")` function from the `clickzetta_dbutils` library — just provide the data source name, with no need to specify the URL, password, or other connection details. You can also use the `Builder` pattern; see the API guide and code examples below.

## API Reference

### get\_active\_engine

A convenience function for creating a database engine in a Studio Python node. Currently supports MySQL, PostgreSQL, and Lakehouse data sources.

#### Function Signature

```py
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

#### Parameters

1. `ds_name` (str): Data source name. Required. Must match the name of the data source in Management → Data Sources.
2. `vcluster` (str, optional): Virtual cluster name for Singdata data sources. Required for Singdata data sources.
3. `workspace` (str, optional): Workspace name. Defaults to the current workspace.
4. `schema` (str, optional): Schema name to connect to. Defaults to `'public'`.
5. `options` (dict, optional): Additional connection options.
6. `query` (dict, optional): Additional query parameters for the SQLAlchemy URL.

#### Return Value

* A SQLAlchemy Engine instance.

#### Examples

* A Postgres data source named `"qiliang_test_pg"` has been added under Management → Data Sources.
* In the current Python node, `"qiliang_test_pg"` has been added as a data source, with the selected database `"answer"` and schema `public`.
* Access tables in `qiliang_test_pg → answer → public` directly via `get_active_engine`:

```
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine
pg_engine = get_active_engine("qiliang_test_pg")
```

Connect and run a query:

```
with pg_engine.connect() as pgconnection:
    result = pgconnection.execute(text("SELECT * FROM question limit 10;"))
    for row in result:
        print(row)
```

* Access a different database within `qiliang_test_pg` by passing parameters (requires that the data source in Management → Data Sources is configured to allow access to other authorized databases — for example, the PostgreSQL database `"sample"` with schema `"public"`):

```py
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine
pg_engine = get_active_engine("qiliang_test_pg",schema="sample",options={"search_path":"public"})
```

Connect and run a query:

```py
with pg_engine.connect() as pgconnection:
    result = pgconnection.execute(text("SELECT * FROM accounts limit 10;"))
    for row in result:
        print(row)
```

### get\_active\_lakehouse\_engine

A convenience function for creating a database engine for a Lakehouse data source.

#### Function Signature

```py
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

#### Parameters

1. `vcluster` (str, optional): Virtual cluster name for the Singdata data source. Required.
2. `workspace` (str, optional): Workspace name. Defaults to the current workspace.
3. `schema` (str, optional): Schema name to connect to. Defaults to `'public'`.
4. `options` (dict, optional): Additional connection options.
5. `query` (dict, optional): Additional query parameters for the SQLAlchemy URL.
6. `driver` (str, optional): Driver name for the connection.

#### Return Value

* A SQLAlchemy Engine instance.

#### Exceptions

* `DatabaseConnectionError`: Raised when no Lakehouse data source is found in the configuration.

#### Example

* The cluster to use is named `"default"` (visible under Compute → Clusters).
* The target data is in workspace `"ql_ws"`, schema `"brazilianecommerce"`, table `"olist_customers"` (visible under Development → Data).
* Access the table directly via `get_active_lakehouse_engine`:

```py
from sqlalchemy import text
import pandas as pd

from clickzetta_dbutils import get_active_lakehouse_engine

engine = get_active_lakehouse_engine(vcluster="default",schema="brazilianecommerce")
```

Connect and run a query:

```py
with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM olist_customers limit 10;"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        print(df.head(10))
```

### DatabaseConnectionManager

A database connection manager that supports chained configuration of connection parameters. The actual SQLAlchemy connection is only established when `build(self, *args, **kwargs)` is called.

#### use\_workspace

Sets the workspace for the connection. Only required for Lakehouse data sources.

```Python
def use_workspace(self, workspace: str) -> 'DatabaseConnectionManager'
```

#### use\_schema

Sets the schema for the connection.

```Python
def use_schema(self, schema: str) -> 'DatabaseConnectionManager'
```

*Note: Due to SQLAlchemy's design, for PostgreSQL, `use_schema` should be set to the database name.*

#### use\_vcluster

Sets the virtual cluster for the connection. Only required for Lakehouse data sources.

```Python
def use_vcluster(self, vcluster: str) -> 'DatabaseConnectionManager'
```

#### use\_options

Sets additional connection options.

```Python
def use_options(self, options: dict) -> 'DatabaseConnectionManager'
```

*Note: Due to SQLAlchemy's design, the PostgreSQL schema should be set to `undefined"})`*

#### use\_query

Sets query parameters for the connection.

```Python
def use_query(self, query: dict) -> 'DatabaseConnectionManager'
```

#### build

Creates a SQLAlchemy engine based on the data source name and optional configuration.

```Python
def build(self, *args, **kwargs) -> Engine
```

#### Usage Example

```py
from clickzetta_dbutils import DatabaseConnectionManager

```

Chained call example:

```py
engine = DatabaseConnectionManager("mysql_source_name")\
    .use_schema("test_schema")\
    .use_options({"charset": "utf8"})\
    .build()

```

Lakehouse connection example:

```py
engine = DatabaseConnectionManager("LAKEHOUSE_source_name")\
    .use_vcluster("default")\
    .use_workspace("test-workspace")\
    .use_schema("public")\
    .build()
```

> Note: `"LAKEHOUSE_source_name"` refers to the name of the Lakehouse data source in Data Source Management.

## Code Examples

### Using a PostgreSQL Data Source in a Python Node

This example retrieves all pg tables from the `postgres_source_name` data source:

```py
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine

```

Using the default schema:

```py
engine = get_active_engine("postgres_source_name")
with engine.connect() as conn:
    results = conn.execute(text("SELECT * FROM pg_tables WHERE schemaname = 'public';"))
    for row in results:
        print(row)

```

Specifying a database and schema via options:

```py
engine = get_active_engine("postgres_source_name", 
                          schema="pg_database", 
                          options={"search_path":"pg_schema"})
```

### Using a MySQL Data Source in a Python Node

```py
from sqlalchemy import text
from clickzetta_dbutils import DatabaseConnectionManager

```

View all available data source configurations:

```py
print(DatabaseConnectionManager.load_connection_configs())

```

Create a connection with a specified schema:

```py
manager = DatabaseConnectionManager("mysql_source_name")
manager.use_schema("test_schema")
engine = manager.build()

with engine.connect() as conn:
    result = conn.execute(text("select * from test_table limit 1;"))
```

### Using a Lakehouse Data Source in a Python Node

```py
from sqlalchemy import text
from clickzetta_dbutils import get_active_engine

```

Option 1: Using get_active_engine:

```py
engine = get_active_engine("LAKEHOUSE_source_name", 
                          vcluster="default", 
                          workspace="test-workspace", 
                          schema="public")

```

Option 2: Using get_active_lakehouse_engine:

```py
from clickzetta_dbutils import get_active_lakehouse_engine
engine = get_active_lakehouse_engine(vcluster="default", 
                                   workspace="test-workspace")
with engine.connect() as conn:
    results = conn.execute(text("select 1"))
    for row in results:
        print(row)
```

### Using a Data Source in a Shell Node

In a Shell node, you can use data sources by creating a Python script file:

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

## Notes

1. Data source configuration works in both ad-hoc execution and scheduled execution scenarios.
2. Using a data source name that does not exist will cause an error. Make sure to select the corresponding data source under Development → Python Task → Data Sources before use. PostgreSQL and MySQL data sources must be created and connection-tested under Management → Data Sources.
3. When using a Lakehouse data source, the `vcluster` parameter is required. The Lakehouse data source uses the built-in Lakehouse data source visible under Management → Data Sources.
4. Data source connection details are handled securely to prevent plaintext password exposure.
5. Multiple data sources of different types can be used within the same node.
