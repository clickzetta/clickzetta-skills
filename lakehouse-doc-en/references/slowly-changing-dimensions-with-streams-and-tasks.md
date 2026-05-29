# Implementing Data Warehouse Slowly Changing Dimensions (SCD) on Lakehouse Using Streams, Pipes, and SQL Tasks

This article addresses the problem: customer, product, and other data in dimension tables changes over time. How do you correctly handle these changes in a data warehouse while preserving historical records?

After completing this guide, you will have a runnable SCD Type 1 / Type 2 implementation based on Singdata Lakehouse's Table Stream + MERGE INTO, capable of automatically capturing dimension changes and writing them to history tables.

**Prerequisites**: Understanding of basic SQL operations, a Singdata Lakehouse account, and AK information for accessing Alibaba Cloud OSS.

## About SCD

Slowly Changing Dimensions (SCD) is a key concept in data warehouse design, used for managing how data in dimension tables is handled as it changes over time. Dimension tables contain descriptive data, such as customer information and product information, which may change over time. SCD provides methods for handling and recording these changes so that both historical and current data in the data warehouse remain consistent and accurate.

SCD is typically divided into several types:

### SCD Type 1

SCD Type 1 handles changes by overwriting old data. This means that when dimension data changes, the old data is overwritten by the new data, so no historical records are preserved. This method is simple and fast, but historical data is lost.

**Example**: Suppose a customer's address changes. SCD Type 1 will directly update the customer's address field, and the old address information will be overwritten by the new address.

### SCD Type 2

SCD Type 2 handles changes by creating new rows to preserve historical records. This method adds a new record to the dimension table and updates it with the new data, while retaining the old data row, and may use effective date columns or version columns to track different versions of the data.

**Example**: When a customer's address changes, SCD Type 2 inserts a new record into the dimension table containing the new address, and may add an effective date range to indicate the validity period of that address.

### SCD Type 3

SCD Type 3 handles changes by adding additional columns to the table to preserve limited history. This method adds a new column to the dimension table to store the old data. When a change occurs, the old data is moved to the new column, and the new data overwrites the original position.

**Example**: If a customer's address changes, SCD Type 3 adds an "old address" column to the table, stores the old address in that column, and stores the new address in the original column.

### Comparison of the Three Types

| SCD Type | Handling Method | Preserves History | Storage Overhead | Suitable Scenarios |
|----------|-----------------|-------------------|------------------|--------------------|
| Type 1 | Directly overwrite old values | No | Low | Data corrections, no historical traceability needed |
| Type 2 | Add new rows for changes; mark old rows as invalid | Yes (complete) | High | Dimensions requiring full history (customer addresses, product prices) |
| Type 3 | Add "old value" column to original row | Yes (previous version only) | Medium | Only need to compare current value with previous version |

This guide implements Type 1 and Type 2; Type 3 is outside the scope of this article.

### What You Need

* [Singdata Lakehouse](https://www.singdata.com/) account
* [GitHub repository for this guide](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/Slowly_Changing_Dimensions_In_Lakehouse_Using_Streams_and_Tasks)
* AK information for accessing Alibaba Cloud OSS

## Introduction to SCD Implementation on Lakehouse

A modern approach to implementing Slowly Changing Dimensions (SCD) in the Lakehouse, leveraging automated data pipelines and native Lakehouse features for efficient change tracking and historical data management.

^

:-: ![](.topwrite/assets/image_1736735808312.png =823)

^

### Pipeline Overview

An end-to-end data pipeline that automatically captures and processes data changes:

1. **Data Source** (Jupyter calling Faker to generate test data) **->** Use Python to create data simulating real-world events.
2. [Zettapark](zettapark-quick-start.md) **PUT** -> Use Zettapark to pull and load data onto the data lake Volume.
3. [Data Lake Volume](datalake_volume.md) -> Data lake storage based on Alibaba Cloud OSS.
4. [Lakehouse Pipe](pipe-summary.md) **Captures data lake file changes** -> Lakehouse Pipe efficiently streams data from the data lake Volume into the Lakehouse.
5. [Lakehouse Table Stream](table_stream.md) **Captures table data changes** -> Captures changed data in the base table for incremental consumption.
6. **SQL** [Tasks](ide.md) **For SCD Processing** -> Develop SQL tasks to implement SCD processing logic, with task scheduling through Singdata Lakehouse Studio.
7. **Lakehouse Data Management**: Lakehouse manages data through three tables:

   * `customer_raw`: Stores raw ingested data.
   * `customer`: Reflects the latest updates from the streaming pipeline.
   * `customer_history`: Retains records of all updates for analysis and auditing change history.

## Key Components

### Data Generation

* **Tools Used**: Python
* Python scripts dynamically generate simulated customer data to simulate real-time data sources.

### Data Ingestion Layer

* **Data Lake Volume**: Storage area for source files; Lakehouse's data lake storage. This case uses Alibaba Cloud OSS. Achieve unified management with tables by creating an External Volume.

* **Zettapark**: PUTs the generated simulated data onto the data lake Volume.

* **Pipe**: Lakehouse's built-in real-time data ingestion service. Use Pipe for real-time streaming:

  * Automatically detects new files in the data lake Volume
  * Loads data into the staging table `customer_raw` without manual intervention

### Change Detection Layer

* **Lakehouse Table Stream**:

  * Captures INSERT, UPDATE, DELETE operations
  * Maintains change tracking metadata
  * Capable of efficiently handling incremental changes
  * Stores change data detected from `customer` into `customer_table_changes`

### Processing Layer

* **Lakehouse SQL Tasks**:

  * Scheduled jobs for SCD processing
  * Handles Type 1 (overwrite) and Type 2 (history) changes
  * Maintains referential integrity
  * Tasks:
    * Insert new or updated records into the `customer` table (SCD Type 1)
    * Record updates to the `customer_history` table (SCD Type 2) to preserve audit trail

### Storage Layer

* **Staging Table**: Temporary storage area for raw data

* **Dimension Tables**: Final tables with historical tracking

  * Include effective dates
  * Maintain current and historical records
  * Support point-in-time analysis

### Application Scenarios

* Customer dimension management
* Product catalog versioning
* Employee data tracking
* Any dimension requiring historical change tracking

### Technology Stack

Required Components:

* Singdata Lakehouse
* Alibaba Cloud OSS (Data Lake Storage)
* [Jupyter Notebook](https://jupyter.org/install) (for test data generation and PUTing files to the data lake Volume), or another Python environment

## Implementation Steps

### Task Development

Navigate to **Development -> Tasks** in [Lakehouse Studio](studio_overview.md).

^

:-: ![](.topwrite/assets/image_1736424981726.png =537)

^

Click "+" to create the following directory:

* 01\_DEMO\_SCD\_In\_Lakehouse

Click "+" to create the following SQL tasks:

* 01\_setup\_env
* 10\_table\_creation\_for\_data\_storage
* 11\_stream\_creation\_for\_change\_detect
* 12\_volume\_creation\_for\_datalake
* 13\_pipe\_creation\_for\_data\_ingestion
* 14\_scd\_type\_1
* 15\_scd\_type\_2\_1
* 16\_scd\_type\_2\_2
* 20\_clean\_env

Copy the following code into the corresponding tasks. You can also download the files from [GitHub](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/Slowly_Changing_Dimensions_In_Lakehouse_Using_Streams_and_Tasks) and copy the content into the corresponding tasks.

^

#### Lakehouse Environment Setup

SQL Task: 01\_setup\_env

```SQL
-- Create required virtual cluster and schemas
-- SCD virtual cluster
CREATE VCLUSTER IF NOT EXISTS SCD_VC
   VCLUSTER_SIZE = XSMALL
   VCLUSTER_TYPE = ANALYTICS
   AUTO_SUSPEND_IN_SECOND = 60
   AUTO_RESUME = TRUE
   COMMENT  'SCD VCLUSTER for test';

-- Use our VCLUSTER
USE VCLUSTER SCD_VC;

-- Create and Use SCHEMA
CREATE SCHEMA IF NOT EXISTS  SCD_SCH;
USE SCHEMA SCD_SCH;
```

> Note: The vcluster_size parameter for compute clusters supports both T-shirt sizes (XSMALL, SMALL, Large, etc.) and numeric values (1, 2, 4, 16, etc.) to provide a richer range of compute cluster specifications for different scenarios. For more information, see: [VCluster Size Specification Change Description](vcluster_size_description.md)

#### Create Tables

SQL Task: 10\_table\_creation\_for\_data\_storage

```SQL
USE VCLUSTER SCD_VC;
USE SCHEMA SCD_SCH;

create  table if not exists customer (
     customer_id string,
     first_name varchar,
     last_name varchar,
     email varchar,
     street varchar,
     city varchar,
     state varchar,
     country varchar,
     update_timestamp timestamp_ntz default current_timestamp());

create  table if not exists customer_history (
     customer_id string,
     first_name varchar,
     last_name varchar,
     email varchar,
     street varchar,
     city varchar,
     state varchar,
     country varchar,
     start_time timestamp_ntz default current_timestamp(),
     end_time timestamp_ntz default current_timestamp(),
     is_current boolean
     );
     
create  table if not exists customer_raw (
     customer_id string,
     first_name varchar,
     last_name varchar,
     email varchar,
     street varchar,
     city varchar,
     state varchar,
     country varchar);
```

After execution: the three tables `customer`, `customer_history`, and `customer_raw` are created. Confirm with `SHOW TABLES`.

#### Create Stream

SQL Task: 11\_stream\_creation\_for\_change\_detect

```SQL
USE VCLUSTER SCD_VC;
USE SCHEMA SCD_SCH;
     
create table stream if not exists customer_table_changes 
on table customer 
WITH PROPERTIES('TABLE_STREAM_MODE' = 'STANDARD');
```

After execution: Stream `customer_table_changes` begins listening for INSERT / UPDATE / DELETE changes on the `customer` table.

#### Create Data Lake Volume

SQL Task: 12\_volume\_creation\_for\_datalake

Creating a Volume requires a Connection to Alibaba Cloud OSS. Refer to [Create Connection](connection-guide.md).

```SQL
--external data lake
--Create data lake Connection, connection to the data lake
CREATE STORAGE CONNECTION if not exists hz_ingestion_demo
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com'
    access_id = 'Please enter your access_id'
    access_key = 'Please enter your access_key'
    comments = 'hangzhou oss private endpoint for ingest demo'
```

```SQL
USE VCLUSTER SCD_VC;
USE SCHEMA SCD_SCH;

--Create Volume, the location for data lake file storage
CREATE EXTERNAL VOLUME  if not exists scd_demo
  LOCATION 'oss://yourbucketname/scd_demo' 
  USING connection hz_ingestion_demo  -- storage Connection
  DIRECTORY = (
    enable = TRUE
  ) 
  recursive = TRUE;

--Sync data lake Volume directory to Lakehouse
ALTER volume scd_demo refresh;

--View files on the Singdata Lakehouse data lake Volume
SELECT * from directory(volume scd_demo);
  
show volumes;
```

#### Create Pipe

SQL Task: 13\_pipe\_creation\_for\_data\_ingestion

```SQL
USE VCLUSTER SCD_VC;
USE SCHEMA SCD_SCH;

create pipe volume_pipe_cdc_demo
  VIRTUAL_CLUSTER = 'scd_vc'
  -- Use file scanning mode to fetch the latest files
  INGEST_MODE = 'LIST_PURGE'
  as
copy into customer_raw from volume scd_demo(customer_id string,
     first_name varchar,
     last_name varchar,
     email varchar,
     street varchar,
     city varchar,
     state varchar,
     country varchar) 
using csv OPTIONS(
  'header'='true'
)
-- Must add purge parameter to delete data after successful import 
purge=true
;

show pipes;
DESC PIPE volume_pipe_cdc_demo;
```

#### SCD Type 1

SQL Task: 14\_scd\_type\_1

```SQL
USE VCLUSTER SCD_VC;
USE SCHEMA SCD_SCH;

MERGE INTO customer AS c 
USING customer_raw AS cr
   ON c.customer_id = cr.customer_id
WHEN MATCHED AND (c.first_name  <> cr.first_name  OR
                  c.last_name   <> cr.last_name   OR
                  c.email       <> cr.email       OR
                  c.street      <> cr.street      OR
                  c.city        <> cr.city        OR
                  c.state       <> cr.state       OR
                  c.country     <> cr.country) THEN 
    UPDATE SET 
        c.first_name = cr.first_name,
        c.last_name = cr.last_name,
        c.email = cr.email,
        c.street = cr.street,
        c.city = cr.city,
        c.state = cr.state,
        c.country = cr.country,
        c.update_timestamp = current_timestamp()
WHEN NOT MATCHED THEN 
    INSERT (customer_id, first_name, last_name, email, street, city, state, country)
    VALUES (cr.customer_id, cr.first_name, cr.last_name, cr.email, cr.street, cr.city, cr.state, cr.country);

select count(*) from customer;
```

After execution: existing records in the `customer` table are overwritten with updates, new records are inserted; `select count(*)` returns the current total row count.

#### SCD Type 2-1

SQL Task: 15\_scd\_type\_2\_1

```SQL
USE VCLUSTER SCD_VC;
USE SCHEMA SCD_SCH;

-- Create view v_customer_change_data
CREATE VIEW IF NOT EXISTS v_customer_change_data AS
-- This subquery handles data being inserted into the customer table
-- Data inserted into the customer table generates a new insert record in the customer_HISTORY table
SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, STREET, CITY, STATE, COUNTRY,
       start_time, end_time, is_current, 'I' AS dml_type
FROM (
    SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, STREET, CITY, STATE, COUNTRY,
           update_timestamp AS start_time,
           LAG(update_timestamp) OVER (PARTITION BY customer_id ORDER BY update_timestamp DESC) AS end_time_raw,
           CASE WHEN end_time_raw IS NULL THEN '9999-12-31' ELSE end_time_raw END AS end_time,
           CASE WHEN end_time_raw IS NULL THEN TRUE ELSE FALSE END AS is_current
    FROM (
        SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, STREET, CITY, STATE, COUNTRY, UPDATE_TIMESTAMP
        FROM customer_table_changes
        WHERE __change_type = 'INSERT'
    )
)
UNION
-- This subquery handles data being updated in the customer table
-- Data updated in the customer table generates one update record and one insert record in the customer_HISTORY table
-- The subquery below generates two records, each with a different dml_type
SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, STREET, CITY, STATE, COUNTRY, start_time, end_time, is_current, dml_type
FROM (
    SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, STREET, CITY, STATE, COUNTRY,
           update_timestamp AS start_time,
           LAG(update_timestamp) OVER (PARTITION BY customer_id ORDER BY update_timestamp DESC) AS end_time_raw,
           CASE WHEN end_time_raw IS NULL THEN '9999-12-31' ELSE end_time_raw END AS end_time,
           CASE WHEN end_time_raw IS NULL THEN TRUE ELSE FALSE END AS is_current, 
           dml_type
    FROM (
        -- Identify data to be inserted into the customer_history table
        SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, STREET, CITY, STATE, COUNTRY, update_timestamp, 'I' AS dml_type
        FROM customer_table_changes
        WHERE __change_type = 'INSERT'
        UNION
        -- Identify data in the customer_HISTORY table that needs to be updated
        SELECT CUSTOMER_ID, null AS FIRST_NAME, null AS LAST_NAME, null AS EMAIL, null AS STREET, null AS CITY, null AS STATE, null AS COUNTRY, start_time, 'U' AS dml_type
        FROM customer_history
        WHERE customer_id IN (
            SELECT DISTINCT customer_id 
            FROM customer_table_changes
            WHERE __change_type = 'DELETE'
        )
        AND is_current = TRUE
    )
)
UNION
-- This subquery handles data being deleted from the customer table
-- Data deleted from the customer table generates an update record in the customer_HISTORY table
SELECT ctc.CUSTOMER_ID, null AS FIRST_NAME, null AS LAST_NAME, null AS EMAIL, null AS STREET, null AS CITY, null AS STATE, null AS COUNTRY, ch.start_time, current_timestamp() AS end_time, NULL AS is_current, 'D' AS dml_type
FROM customer_history ch
INNER JOIN customer_table_changes ctc
ON ch.customer_id = ctc.customer_id
WHERE ctc.__change_type = 'DELETE'
AND ch.is_current = TRUE;
```

#### SCD Type 2-2

SQL Task: 16\_scd\_type\_2\_2

```SQL
USE VCLUSTER SCD_VC;
USE SCHEMA SCD_SCH;

merge into customer_history ch -- Target table; merges changes from NATION into this table
using v_customer_change_data ccd -- v_customer_change_data is a view containing logic for inserts/updates into the customer_history table
   on ch.CUSTOMER_ID = ccd.CUSTOMER_ID -- CUSTOMER_ID and start_time determine whether a unique record exists in the customer_history table
   and ch.start_time = ccd.start_time
when matched and ccd.dml_type = 'U' then update -- Indicates the record has been updated and is no longer current; needs end_time marked
    set ch.end_time = ccd.end_time,
        ch.is_current = FALSE
when matched and ccd.dml_type = 'D' then update -- Deletion is effectively a logical delete. The record is marked and no new version is inserted
   set ch.end_time = ccd.end_time,
       ch.is_current = FALSE
when not matched and ccd.dml_type = 'I' then insert -- Inserting a new CUSTOMER_ID or updating an existing CUSTOMER_ID both produce an insert operation
          (CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, STREET, CITY, STATE, COUNTRY, start_time, end_time, is_current)
    values (ccd.CUSTOMER_ID, ccd.FIRST_NAME, ccd.LAST_NAME, ccd.EMAIL, ccd.STREET, ccd.CITY, ccd.STATE, ccd.COUNTRY, ccd.start_time, ccd.end_time, ccd.is_current);
```

After execution: new or updated historical records are added to the `customer_history` table; old version rows have `is_current` set to FALSE; new version rows have `end_time` as `9999-12-31` and `is_current` as TRUE.

### Building the Environment

Run the developed tasks to build the Lakehouse runtime environment.
Navigate to **Development -> Tasks**, open the following tasks, and run them one by one:

* 01\_setup\_env
* 10\_table\_creation\_for\_data\_storage
* 11\_stream\_creation\_for\_change\_detect
* 12\_volume\_creation\_for\_datalake
* 13\_pipe\_creation\_for\_data\_ingestion
* 15\_scd\_type\_2\_1

:-: ![](.topwrite/assets/image_1736480652293.png =594)

### Task Scheduling and Commit

Schedule the developed SCD tasks to execute once per minute.
Navigate to **Development -> Tasks**, open the following tasks, and configure scheduling for each:

* 14\_scd\_type\_1
* 16\_scd\_type\_2\_2

:-: ![](.topwrite/assets/image_1736480815329.png =623)

### Commit Tasks

After configuring the schedule, click "Commit." The tasks will run on a one-minute cycle, updating the data in the target tables.

^

:-: ![](.topwrite/assets/image_1736480973764.png =624)

### Generate Test Data

#### Generate Test Data and PUT to Data Lake Volume

```PYTHON
#!pip install faker
from faker import Faker
import csv
import uuid
import random
from decimal import Decimal
from datetime import datetime
from clickzetta.zettapark.session import Session
import json
RECORD_COUNT = 10000
fake = Faker()
```

```PYTHON
current_time = datetime.now().strftime("%Y%m%d%H%M%S")
print(current_time)
```

```PYTHON
file_path = f'FakeDataset/customer_{current_time}.csv'
```

```PYTHON
def create_csv_file():
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ["customer_id","first_name","last_name","email","street",
                      "city","state","country"
                     ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(RECORD_COUNT):
            #print(i)
            writer.writerow(
                {
                    "customer_id": str(uuid.uuid4()),
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'email': fake.email(),
                    'street': fake.street_address(),
                    'city': fake.city(),
                    'state': fake.state(),
                    'country': fake.country()
                }
            )
```

```PYTHON
def put_file_into_volume():
    # Read parameters from configuration file
    with open('security/config-uat.json', 'r') as config_file:
        config = json.load(config_file)
    
    # Create session
    session = Session.builder.configs(config).create()
    session.file.put(file_path,"volume://scd_demo/")
    session.sql("show volume directory scd_demo").show()
    session.close()
```

```PYTHON
if __name__ == '__main__':
    create_csv_file()
    put_file_into_volume()
```

* Executing the above code PUTs a new file to the Volume. The Pipe automatically detects the new file and writes its data into the `customer_raw` table.

:-: ![](.topwrite/assets/image_1736481547753.png =403)

* The 14\_scd\_type\_1 task, configured with periodic scheduling, performs SCD Type 1 computation every minute and merges the results into the `customer` table.

:-: ![](.topwrite/assets/image_1736481597919.png =419)

* Table Stream automatically detects changes in the `customer` table data and stores the changed data in `customer_table_changes`.

:-: ![](.topwrite/assets/image_1736481635363.png =416)

* The 16\_scd\_type\_2\_2 task, configured with periodic scheduling, performs SCD Type 2 computation every minute and merges the results into the `customer_history` table.

:-: ![](.topwrite/assets/image_1736481671328.png =425)

### Monitoring and Maintenance

#### Pipe Monitoring

* Use the SHOW PIPES command to view the list of PIPE objects

```SQL
SHOW PIPES;
```

* Use the DESC PIPE command to view detailed information for a specified PIPE object

```SQL
DESC PIPE volume_pipe_cdc_demo;
```

:-: ![](.topwrite/assets/image_1736483133453.png =562)

* View Pipe COPY job executions

Filter by query\_tag in the job history. All Pipe COPY job executions are tagged in query\_tag with the format: pipe.workspace\_name.schema\_name.pipe\_name

In this guide, workspace\_name is `ql_ws`, schema\_name is `SCD_SCH`, and pipe name is `volume_pipe_cdc_demo`, so the query\_tag is:

pipe.ql\_ws.scd\_sch.volume\_pipe\_cdc\_demo

Navigate to **Compute -> Job History**:

^

:-: ![](.topwrite/assets/image_1736482319263.png =553)

^

Click "More Filters" and enter "pipe.ql\_ws.scd\_sch.volume\_pipe\_cdc\_demo" in the QueryTag field to filter:

:-:
![](.topwrite/assets/image_1736482668378.png =617)

####

#### Scheduled Tasks

Navigate to **Operations Monitoring -> Task Operations -> Scheduled Tasks**:

:-:
![](.topwrite/assets/image_1736482942259.png =634)

^

View Task Instances:

^

:-: ![](.topwrite/assets/image_1736483055041.png =627)

^

## Resources

[Connection](connection-guide.md)

[External Volume](datalake_volume.md)

[Pipe](pipe-storage-object.md)

[Table Stream](table_stream.md)

[Merge Into](MERGE.md)
