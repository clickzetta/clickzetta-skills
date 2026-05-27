# Lakehouse Python SDK

Singdata Lakehouse Python SDK is a toolkit designed for Python developers to simplify the interaction process with Singdata Lakehouse. This SDK includes two main Python packages: clickzetta-connector and clickzetta-sqlalchemy. These two packages provide different programming interfaces to meet the needs of different scenarios.

## clickzetta-connector

clickzetta-connector follows the PEP-249 specification and provides a SQL call interface in the style of the Python Database API. By using this interface, you can easily perform SQL queries, inserts, updates, and deletes in Python applications.

In addition, clickzetta-connector also supports bulk data upload (bulkload) functionality, which can significantly improve data import speed. This is particularly useful for scenarios involving large amounts of data.

### Usage Example

1. Install clickzetta-connector, Python version 3.6 or above is required:
```bash
pip install clickzetta-connector
```
2. Connect to Singdata Lakehouse instance:
```python
from clickzetta import connect

# Establish connection
conn = connect(username='username',
               password='password',
               service='api.singdata.com',
               instance='instance',
               workspace='quickstart_ws',
               schema='public',
               vcluster='default')
```

| **Parameter** | **Required** | **Description** |
| ------------- | ------------ | --------------- |
| username      | Y            | Username |
| password      | Y            | Password |
| service       | Y            | Address to connect to the Lakehouse, region.api.singdata.com. You can find the JDBC connection string in Lakehouse Studio under Management -> Workspace |
| instance      | Y            | Instance name. You can find it in the JDBC connection string in Lakehouse Studio under Management -> Workspace |
| workspace     | Y            | Workspace in use |
| vcluster      | Y            | Virtual Cluster in use |
| schema        | Y            | Name of the schema to access |

3. Execute SQL statements:
```python
# Execute query
cursor = conn.cursor()
cursor.execute("SELECT * FROM your_table")
rows = cursor.fetchall()

# Print query results
for row in rows:
    print(row)

# Close connection
cursor.close()
conn.close()
```

## clickzetta-sqlalchemy

clickzetta-sqlalchemy provides SQLAlchemy adaptation, allowing you to interact with Singdata Lakehouse using the SQLAlchemy style programming interface. This makes it easy to integrate Singdata Lakehouse into SQLAlchemy-based upper-layer applications, such as Superset, Streamlit, etc.

### Usage Example

1. Install clickzetta-sqlalchemy:
```bash
pip install clickzetta-sqlalchemy
```

2. Configure SQLAlchemy:
```python
from sqlalchemy import create_engine
from sqlalchemy import text

# Establish connection, using the clickzetta:// prefix
engine = create_engine("clickzetta://username:password@instance.api.singdata.com/workspace?schema=schema&vcluster=default")
```

3. Using SQLAlchemy for data operations:
```python
sql = text('select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live;')

# Execute and get results
with engine.connect() as conn:
    results = conn.execute(sql)
    for r in results:
        print(r)
```

Through these two Python packages, you can easily interact with Singdata Lakehouse in your Python applications to meet various data processing needs.
