# ClickZetta SQLAlchemy Adapter

`clickzetta-sqlalchemy` is a dialect adapter for ClickZetta Lakehouse provided for SQLAlchemy, allowing code or upper-layer applications written with the SQLAlchemy interface to easily interact with ClickZetta Lakehouse.

## Installation

Install `clickzetta-sqlalchemy` via pip:
```shell
pip install clickzetta-sqlalchemy
```
## Quick Start

### Execute SQL Query

#### Method 1: Using URL String

```python
from sqlalchemy import create_engine
from sqlalchemy import text
from urllib.parse import quote_plus

# If the password contains special characters (such as @, :, /), use quote_plus to encode it
password = quote_plus("your_password")

# Create an instance of the SQLAlchemy engine for ClickZetta Lakehouse
engine = create_engine(
    f"clickzetta://username:{password}@instance.region_id.api.clickzetta.com/workspace?schema=schema&vcluster=default"
)

# Execute SQL query
sql = text("SELECT * FROM ecommerce_events_multicategorystore_live;")

# Execute the query using the engine
with engine.connect() as conn:
    result = conn.execute(sql)
    for row in result:
        print(row)
```

> **Note**: If the password contains special characters (such as `@`, `:`, `/`, `#`), you must use `urllib.parse.quote_plus` to encode the password, otherwise the URL will be parsed incorrectly.

#### Method 2: Using URL.create (Recommended)

Using `URL.create` avoids manual URL encoding issues. SQLAlchemy handles special characters in the password automatically.

```python
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

url = URL.create(
    drivername='clickzetta',
    username='your_username',
    password='your_password',
    host='instance.region_id.api.clickzetta.com',
    database='your_workspace',
    query={
        'virtualcluster': 'default',
        'schema': 'public'
    }
)

engine = create_engine(url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    for row in result:
        print(row)
```

> **Note**: `URL.create` automatically handles special characters in the password (such as `@`, `:`, `/`), no need to manually call `quote_plus`.
### Example: Using PyGWalker for Visual Analysis of Lakehouse Data

[PyGWalker](https://github.com/Kanaries/pygwalker) is a tool that can convert pandas and polars data frames into a Tableau-style user interface for data visualization exploration. It simplifies the Jupyter Notebook data analysis and data visualization workflow, requiring only one line of code to implement.
```python
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import pygwalker as pyg

# Create an instance of the SQLAlchemy engine for ClickZetta Lakehouse
engine = create_engine(
    "clickzetta://username:password@instance.api.singdata.com/workspace?schema=schema&vcluster=default"
)

# Execute SQL query
sql = text("SELECT * FROM ecommerce_events_multicategorystore_live;")

# Execute the query using the engine and get the results
with engine.connect() as conn:
    result = conn.execute(sql)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

# Use PyGWalker for visual analysis of the DataFrame
walker = pyg.walk(df)
```