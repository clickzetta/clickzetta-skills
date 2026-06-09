# Python Task Usage Practice

In the task development module, the Python task provided is a specific task type under a lightweight resource container, designed to run Python code. It offers environment isolation between tasks and has basic environment customization capabilities. This article introduces some usage practices for Python tasks.

^

### Runtime Environment and Customization

Python tasks are executed in a system preset Pod environment, with the pre-installed Python version being Python 3 (current version is 3.10, which may be updated in the future).

The default system image includes some commonly used dependency packages to support connection and data access with Singdata Lakehouse, as well as operations on object storage services such as Alibaba Cloud OSS and Tencent Cloud COS. These dependencies include but are not limited to:

* clickzetta-connector
* clickzetta-sqlalchemy
* cos-python-sdk-v5
* numpy
* oss2
* pandas
* six
* urllib2
* ...

To meet specific runtime requirements, the Pod environment provides limited environment customization capabilities. You can perform custom installations under the `/home/system_normal` path. Below is a sample code snippet demonstrating how to install custom packages (lines 4 and 5) and use them in the Python environment. Please note that after the Python task is completed, the Pod environment will be destroyed, so any environment customizations will not be retained.

```py
import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python","--target", "/home/system_normal", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
sys.path.append('/home/system_normal')

import mysql.connector

```

Create connection:

```py
connection = mysql.connector.connect(
    host='127.0.0.1',   # Database host address
    user='****',       # Database username
    password='***********', # Database password
    database='demo'  # Name of the database to connect to
)

```

Create cursor:

```py
cursor = connection.cursor()

```

Execute query:

```py
query = "show tables"  # Replace with your SQL query
cursor.execute(query)

```

Fetch query results:

```py
results = cursor.fetchall()
print("Query results:")
for row in results:
    print(row)

```

Close cursor and connection:

```py
cursor.close()
connection.close()
```

^

### Adjusting Runtime Resource Size

By default, the Pod provides 0.5 CPU cores and 512MB of memory resources. If needed, you can adjust the resource allocation in the task scheduling configuration using the following parameters:

* `pod.limit.cpu`: Set the number of CPU cores. It must be a value greater than 0, such as 1, with a maximum setting of 4. The default value is 0.5.
* `pod.limit.memory`: Set the memory size, formatted as a value followed by a unit, such as 2G, with a maximum setting of 8G. The default value is 512M.

  ![](.topwrite/assets/image_1718339259582.png =513)

By configuring these parameters reasonably, you can ensure that Python tasks have sufficient resources to meet different computational needs while avoiding resource waste.

^

### More Use Cases

#### Querying Lakehouse Data Using Python Database API

```py
from clickzetta import connect

```

Establish connection:

```py
conn = connect(
    username='your_username',
    password='your_password',
    service='region_id.api.singdata.com',
    instance='your_instance',
    workspace='your_workspace',
    schema='public',
    vcluster='DEFAULT'
)

```

Create cursor object:

```py
cursor = conn.cursor()

```

Execute SQL query:

```py
cursor.execute('SELECT * FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live LIMIT 10;')

```

Fetch query results:

```py
results = cursor.fetchall()
for row in results:
    print(row)
```

^

#### Using SQLAlchemy Interface to Query Lakehouse Data

```py
from sqlalchemy import create_engine
from sqlalchemy import text

```

Create an instance of the SQLAlchemy engine for Singdata Lakehouse:

```py
engine = create_engine(
    "clickzetta://username:password@instance.api.clickzetta.com/workspace?schema=schema&vcluster=default"
)

```

Execute SQL query:

```py
sql = text("SELECT * FROM ecommerce_events_multicategorystore_live;")

```

Execute the query using the engine:

```py
with engine.connect() as conn:
    result = conn.execute(sql)
    for row in result:
        print(row)
```

#### Using Python to Batch Upload Data to Lakehouse

```py
from clickzetta import connect

conn = connect(
    username='your_username',
    password='your_password',
    service='region_id.api.singdata.com',
    instance='your_instance',
    workspace='your_workspace',
    schema='public',
    vcluster='DEFAULT'
)

bulkload_stream = conn.create_bulkload_stream(schema='public', table='bulkload_test')

writer = bulkload_stream.open_writer(0)
for index in range(1000000):
    row = writer.create_row()
    row.set_value('i', index)
    row.set_value('s', 'Hello')
    row.set_value('d', 123.456)
    writer.write(row)
writer.close()

bulkload_stream.commit()
```
