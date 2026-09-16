# Real-time Data Sync from Oracle Database to Singdata Lakehouse via BluePipe

## Solution Overview

For over 30 years, Oracle has held an important position in the relational database and data warehouse space. With the introduction of integrated systems such as Exadata, Exalytics, Exalogic, SuperCluster, and 12c Database, the tight integration of storage and compute has enabled faster processing of large volumes of data using on-premises infrastructure. However, the volume, velocity, and variety of data have grown dramatically, and the cloud has opened up new possibilities for modern data analytics. For example, by separating compute from storage, Singdata Lakehouse has realized a new generation of cloud data platform, achieving automatic and instant scaling of compute and storage with a share-nothing data architecture.
![](.topwrite/assets/image_1718854284202.png)

## Solution Advantages

BluePipe supports real-time data sync from Oracle to Singdata Lakehouse. Especially in complex database environments with multiple instances and many tables, BluePipe automates synchronization, greatly reducing the complexity and effort of manually configuring sync jobs. For source databases with tens of thousands of tables, BluePipe can automatically configure sync tasks.

### Ready Out of the Box — Configuration in 10 Minutes

* `BluePipe` can run on virtually any `Linux` system, supporting both `x86` and `arm` chips; common rack servers, laptops, and even Raspberry Pi can be used for deployment.
* A minimal configuration process — default parameters achieve optimal performance.

### Full and Incremental Sync Unified — No Operational Intervention Required

* Full sync and incremental sync are deeply coordinated, requiring almost no routine operations.
* Efficient data comparison and hot-fix technology, always guaranteeing data consistency.
* Highly robust `Schema Evolution` support.

### Push Data, Not Expose Ports

* `BluePipe` is deployed alongside your database in your internal network — no need to expose external ports.
* Elastic `buffer size` technology automatically balances between `Throughput` and `latency`.

## Unique Advantages of the Oracle Link

`BluePipe` implements change data capture based on `Oracle LogMiner`, with deep optimizations in the following areas:

### Deep Compatibility with DDL Operations

Under the default `LogMiner` strategy, after a `DDL` operation occurs, subsequent `DML` operations on the affected table cannot be correctly parsed, making it impossible to capture changes correctly.
`BluePipe` maintains an automated dictionary file construction strategy, ensuring that incremental data can still be captured correctly after schema changes.

### Large Transaction Optimization

`Oracle Redo Log` records the complete `Transaction` process, but business logic typically only requires data after `commit`. Therefore, a `buffer` is needed during transmission to temporarily hold uncommitted change records.
`BluePipe` uses unique memory management technology to handle large transactions with tens of millions of records on a single node with ease.
From `Oracle 12.2` onward, the maximum length for table names and column names was extended to 128 bytes. However, for various reasons, `LogMiner` on instances without an `OGG LICENSE` still does not support DML parsing for tables with long names. See the [official documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/sutil/oracle-logminer-utility.html) for details.
`BluePipe` uses efficient stream-batch fusion technology to fully support incremental data capture and delivery in such scenarios.

### Support for `RAC` Architecture

## Sync Performance

LAG: approximately 10 seconds
Sync speed: 20,000 rows/second
![](.topwrite/assets/20240620154408_rec_.gif)

## Implementation Steps

### Install and Deploy BluePipe

If you have not yet completed the installation and deployment of BluePipe, please contact Singdata or BluePipe.

### Configure the Sync Data Source in BluePipe

#### Configure Oracle Data Source

![](.topwrite/assets/image_1718870633522.png)

##### Configuration Item Descriptions

| Configuration Item | Description |
| ------ | ---------------------------------------------- |
| Connection String | The connection method for the data source, in the format: IP:PORT:SID, e.g., 127.0.0.1:1521:XE |
| Username | Username for connecting to the database, e.g., C##CDC\_USER |
| Password | The password corresponding to the database username, e.g., userpassword |
| Connection Name | A custom name for the data source for easy management, e.g., local test instance |
| Allow Batch Extraction | Read data tables via query, supports row-level filtering; enabled by default |
| Allow Streaming Extraction | Capture database changes in real time via CDC; enabled by default |
| Allow Data Write | Can be used as a target data source; enabled by default |

##### Basic Features

| Feature | Description |
| ------ | ----------------------------------------------- |
| Schema Migration | If the target table does not exist, automatically generates and executes the create statement based on source metadata combined with mappings |
| Full Data Migration | Logical migration, sequentially scans table data and writes data to the target database in batches |
| Incremental Real-time Sync | Supports common DML sync: **INSERT**, **UPDATE**, **DELETE** |

#### Configure Singdata Lakehouse as the Target

![](.topwrite/assets/image_1718870882049.png)

##### Configuration Item Descriptions

| Configuration Item | Description |
| ------ | ----------------------------------------------------------------------------------------------------------- |
| Connection String | The connection method for the data source, in the format: {instance}.{domain}/{workspace}, e.g., abcdef.cn-shanghai-alicloud.api.singdata.com/quick\_start |
| Virtual Cluster | Set the virtual cluster to run on; default value is `default` |
| Username | Username for connecting to the database, e.g., username |
| Password | The password corresponding to the database username, e.g., userpassword |
| Connection Name | A custom name for the data source for easy management, e.g., local test instance |
| Allow Batch Extraction | Read data tables via query, supports row-level filtering; extraction not yet supported |
| Allow Streaming Extraction | Capture database changes in real time via CDC; extraction not yet supported |
| Allow Data Write | Can be used as a target data source; enabled by default |

### Create Tables in Oracle Database

```
CREATE TABLE metabase.people_with_pk (
    id INTEGER PRIMARY KEY,
    age INTEGER,
    name VARCHAR(32),
    create_date DATE DEFAULT GETDATE()
);

CREATE TABLE metabase.employees (
    employee_id INTEGER  PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    hire_date DATE,
    salary INTEGER,
    department_id INTEGER,
    email VARCHAR(100),
    phone_number VARCHAR(20),
    address VARCHAR(200),
    job_title VARCHAR(100),
    manager_id INTEGER,
    commission_pct DECIMAL,
    birth_date DATE,
    marital_status VARCHAR(10),
    nationality VARCHAR(50),
    create_date DATE DEFAULT GETDATE()
);
CREATE TABLE  metabase.departments (
    department_id INTEGER  PRIMARY KEY,
    department_name VARCHAR(100),
    location VARCHAR(200),
    manager_id INTEGER,
    created_date DATE,
    description VARCHAR(500),
    budget INTEGER,
    status VARCHAR(20),
    contact_person VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(200),
    start_date DATE,
    end_date DATE,
    num_employees INTEGER,
    create_date DATE DEFAULT GETDATE()
);
```

### Create a New Sync Job in BluePipe

Please note:

1. When selecting the source, the `{namespace}` in the target table name `{namespace}/{table}` can be replaced with the schema name you want, such as `bluepipe_oracle_staging`.
2. In the design step, for incremental replication, select "Real-time replication using CDC technology".
   The result after successfully creating a new sync job is shown below:
   ![](.topwrite/assets/image_1718871018707.png)
   The new job will start automatically and begin a full data sync, followed by continuous real-time incremental data sync.

### Data Generation

Run the following Python code to insert data in real time into the Oracle source table `employees`:

```
import oracledb
import random
import time,datetime
db_user = "SYSTEM"
db_password = ""
db_host = "
db_port = "1521"
db_service_name = "XE"
```

Connect to the Oracle database and obtain a cursor:

```
connection = oracledb.connect(f"{db_user}/{db_password}@{db_host}:{db_port}/{db_service_name}")
cursor = connection.cursor()
```

Total number of records to insert:

```
total_records = 1000000
batch_size = 1000 # Number of records per batch
inserted_rows = 0
start_time = time.time()
for batch_start in range(1, total_records + 1, batch_size):
batch_end = min(batch_start + batch_size - 1, total_records)
hire_date = random.randint(1, 200)
```

Build the insert statement:

```
insert_sql = f"""
INSERT INTO metabase.employees (
employee_id, first_name, last_name, hire_date, salary, department_id,
email, phone_number, address, job_title, manager_id, commission_pct,
birth\_date, marital_status, nationality
)
SELECT
LEVEL,
'FirstName' || LEVEL,
'LastName' || LEVEL,
SYSDATE - {hire_date},
5000 + LEVEL * 1000,
MOD(LEVEL, 5) + 1,
'employee' || LEVEL || '@example.com',
'123-456-' || LPAD(LEVEL, 3, '0'),
'Address' || LEVEL,
CASE MOD(LEVEL, 3)
WHEN 0 THEN 'Manager'
WHEN 1 THEN 'Analyst'
WHEN 2 THEN 'Clerk'
END,
CASE WHEN LEVEL > 1 THEN TRUNC((LEVEL - 1) / 5) END,
0.1 * LEVEL,
SYSDATE - (LEVEL * 100),
CASE MOD(LEVEL, 2)
WHEN 0 THEN 'Single'
WHEN 1 THEN 'Married'
END,
CASE MOD(LEVEL, 4)
WHEN 0 THEN 'China'
WHEN 1 THEN 'USA'
WHEN 2 THEN 'UK'
WHEN 3 THEN 'Australia'
END
FROM DUAL
CONNECT BY LEVEL <= {batch_size}
"""
```

Execute the insert:

```
cursor.execute(insert_sql)
connection.commit()
inserted_rows = inserted_rows + batch_size
end_time = time.time()
total_time = end_time - start_time
average_insert_speed = inserted_rows / total_time
print(f"Total rows inserted: {inserted_rows}")
print(f"Average insert speed: {average_insert_speed:.2f} rows/second")
time.sleep(0.5)
end_time = time.time()
total_time = end_time - start_time
average_insert_speed = inserted_rows / total_time
print(f"Total rows inserted: {inserted\_rows}")
print(f"Average insert speed: {average\_insert\_speed:.2f} rows/second")
```

Close the cursor and connection:

```
cursor.close()
connection.close()
```

### Observe Source and Target Data via Metabase

![](.topwrite/assets/image_1718872014999.png)
See also: [Metabase Installation and Deployment](metabase.md)
