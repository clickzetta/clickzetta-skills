# Real-Time Data Synchronization from Oracle to Singdata Lakehouse via Bluepipe

## Solution Introduction

For over 30 years, Oracle has held a significant position in the relational database and data warehouse space. With the introduction of integrated systems such as Exadata, Exalytics, Exalogic, SuperCluster, and 12c Database, the tight integration of storage and compute enables faster processing of large amounts of data using on-premises infrastructure. However, the volume, velocity, and variety of data have dramatically increased, and the cloud brings more possibilities for modern data analytics. For example, by separating compute from storage, Singdata Lakehouse enables a new generation of cloud data platforms with automatic, instant scaling of compute and storage through a share-nothing data architecture.
![](.topwrite/assets/image_1718854284202.png)

## Solution Advantages

Bluepipe supports real-time data synchronization from Oracle to Singdata Lakehouse. Particularly in complex database environments with multiple instances and tables, Bluepipe achieves automated synchronization, greatly reducing the complexity and workload of manually configuring sync jobs. For source databases with tens of thousands of tables, Bluepipe can automatically configure synchronization tasks.

### Out-of-the-box, Ready in 10 Minutes

* `Bluepipe` can run on virtually any `Linux` system, supporting `x86` and `arm` chips; common rack-mounted servers, laptops, and even Raspberry Pi can be used for deployment;
* Minimal configuration process; default parameters achieve optimal performance.

### Full and Incremental Integration, Zero Ops Intervention

* Deep synergy between full and incremental sync, with almost no routine maintenance operations required;
* Efficient data comparison and hot-fix technology, always ensuring data consistency;
* Highly robust `Schema Evolution`.

### Push Data, Not Expose Ports

* `Bluepipe` is deployed together with your database in your internal network, with no need to expose ports externally;
* Elastic `buffer size` technology, automatically balancing between `Throughput` and `latency`.

## Unique Advantages of the Oracle Pipeline

`Bluepipe` captures change data based on `Oracle LogMiner`. At the same time, it has been deeply optimized in the following areas:

### Deep DDL Compatibility

Under the default `LogMiner` strategy, after a `DDL` operation occurs, subsequent `DML` operations on the related table cannot be correctly parsed, resulting in an inability to correctly capture changes.
`Bluepipe` maintains an automatic dictionary file build strategy to ensure that correct incremental data can still be captured after table structure changes.

### Large Transaction Optimization

`Oracle Redo Log` records the complete transaction process, but from a business perspective, only data after `commit` is typically desired. Therefore, a `buffer` is needed during transmission to temporarily store change records that have not yet been `commit`ted.
Based on unique memory management technology, `Bluepipe` can easily handle transactions involving tens of millions of records even on a single node.
Starting from `Oracle 12.2`, the maximum length for table names and column names is supported up to 128 bytes. However, for various reasons, `LogMiner` for instances without an `OGG LICENSE` still does not support DML parsing for tables containing long names. For details, refer to the [official documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/sutil/oracle-logminer-utility.html).
Based on efficient stream-batch fusion technology, `Bluepipe` fully supports incremental data capture and delivery in such scenarios.

### RAC Architecture Support

## Synchronization Results

LAG: approximately 10 seconds
Sync speed: 20,000 rows/second
![](.topwrite/assets/20240620154408_rec_.gif)

## Implementation Steps

### Install and Deploy Bluepipe

If you have not yet completed the installation and deployment of Bluepipe, please contact Singdata or Bluepipe.

### Configure Sync Data Sources in Bluepipe

#### Configure Oracle Data Source

![](.topwrite/assets/image_1718870633522.png)

##### Configuration Item Description

| Item Name | Description                                             |
| --------- | ------------------------------------------------------- |
| Connection String | The connection method for the data source, format: IP:PORT:SID, e.g., 127.0.0.1:1521:XE |
| Username  | The username for connecting to the database, e.g., C##CDC_USER |
| Password  | The password corresponding to the database username, e.g., userpassword |
| Connection Name | A custom name for the data source, convenient for future management, e.g., Local Test Instance |
| Allow Batch Extraction | Read data tables by query, supports row-level filtering, enabled by default |
| Allow Streaming Extraction | Capture database changes in real time via CDC, enabled by default |
| Allow Data Writing | Can serve as a target data source, enabled by default |

##### Basic Features

| Feature             | Description                                              |
| ------------------- | -------------------------------------------------------- |
| Schema Migration    | If the target does not have the selected table, automatically generate and execute the creation statement based on source metadata and mapping |
| Full Data Migration | Logical migration, sequentially scanning table data and writing data in batches to the target database |
| Incremental Real-Time Sync | Supports **INSERT**, **UPDATE**, **DELETE** common DML sync |

#### Configure Singdata Lakehouse as Target

![](.topwrite/assets/image_1718870882049.png)

##### Configuration Item Description

| Item Name           | Description                                                                                                          |
| ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Connection String   | The connection method for the data source, format: {instance}.{domain}/{workspace}, e.g., abcdef.cn-shanghai-alicloud.api.singdata.com/quick_start |
| Virtual Cluster     | Set the running virtual cluster, default value is default                                                            |
| Username            | The username for connecting to the database, e.g., username                                                           |
| Password            | The password corresponding to the database username, e.g., userpassword                                               |
| Connection Name     | A custom name for the data source, convenient for future management, e.g., Local Test Instance                        |
| Allow Batch Extraction | Read data tables by query, supports row-level filtering, extraction not currently supported                        |
| Allow Streaming Extraction | Capture database changes in real time via CDC, extraction not currently supported                             |
| Allow Data Writing  | Can serve as a target data source, enabled by default                                                                 |

### Create Tables in Oracle Database

```sql
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

### Create a New Sync Job in Bluepipe

Please note:

1. When selecting the source, the `{namespace}` in the target table name `{namespace}/{table}` can be replaced with your desired schema name, such as `bluepipe_oracle_staging`.
2. In the design phase, select "Use CDC technology for real-time replication" for incremental replication.
   After successfully creating the sync job, the effect is as shown below:
   ![](.topwrite/assets/image_1718871018707.png)
   The new job will automatically start and begin full data synchronization, followed by ongoing incremental real-time synchronization.

### Data Generation

Run the following Python code to insert data into the Oracle source table `employees` in real time:

```python
import oracledb
import random
import time,datetime
db_user = "SYSTEM"
db_password = ""
db_host = ""
db_port = "1521"
db_service_name = "XE"
# Connect to Oracle database and get cursor
connection = oracledb.connect(f"{db_user}/{db_password}@{db_host}:{db_port}/{db_service_name}")
cursor = connection.cursor()
# Total number of records to insert
total_records = 1000000
batch_size = 1000 # Number of records inserted per batch
inserted_rows = 0
start_time = time.time()
for batch_start in range(1, total_records + 1, batch_size):
    batch_end = min(batch_start + batch_size - 1, total_records)
    hire_date = random.randint(1, 200)
    # Build insert statement
    insert_sql = f"""
    INSERT INTO metabase.employees (
        employee_id, first_name, last_name, hire_date, salary, department_id,
        email, phone_number, address, job_title, manager_id, commission_pct,
        birth_date, marital_status, nationality
    )
    SELECT
        LEVEL,
        'Name' || LEVEL,
        'Surname' || LEVEL,
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
    # Execute insert
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
print(f"Total rows inserted: {inserted_rows}")
print(f"Average insert speed: {average_insert_speed:.2f} rows/second")
# Close cursor and connection
cursor.close()
connection.close()
```

### Observe Source and Target Data via Metabase

![](.topwrite/assets/image_1718872014999.png)
Please refer to: [Metabase Installation and Deployment](metabase.md)
