# Migrate Real-Time ETL Pipeline from Snowflake to Singdata Lakehouse

## Highlight

Based on Singdata Lakehouse, this article quickly implements the migration of the real-time ETL pipeline from Snowflake to Singdata Lakehouse and discovers the following unique advantages of the Singdata Lakehouse solution:

* Global multi-cloud support. In this solution, both Singdata Lakehouse and Snowflake are based on AWS, providing a consistent cloud experience. This solution is also suitable for migration on GCP. Additionally, Singdata Lakehouse supports Alibaba Cloud, Tencent Cloud, and Huawei Cloud, not just the mainstream overseas cloud service providers.
* Low migration cost.
  * Singdata Lakehouse offers product concepts very similar to Snowflake, making it very easy for users familiar with Snowflake to understand and get started.
  * The SQL syntax of Singdata Lakehouse is highly compatible with Snowflake, requiring only minimal tiny modifications to achieve code migration.
* Low operation and maintenance cost.
  * Singdata Lakehouse provides a built-in Python runtime environment and integrates scheduling, operation, and monitoring of SQL and other tasks. There is no need for additional Airflow services or Python runtime environments, greatly simplifying the system architecture and reducing operation and maintenance difficulty and cost.

## Real-Time Insurance Data ETL Pipeline with Snowflake Project Introduction

### Project Overview

If you are familiar with the practical operation and application of Snowflake, then the [Real-Time Insurance Data ETL Pipeline with Snowflake](https://github.com/ravishankar324/Real-Time-Insurance-claims-Data-ETL-Pipeline) on Github will be very familiar to you. This project involves creating a real-time ETL (Extract, Transform, Load) data pipeline in Snowflake to process insurance data from Kaggle and load it into Snowflake. The data pipeline is managed using Apache Airflow and involves several steps to clean, normalize, and transform the data before loading it into Snowflake for further processing. AWS S3 is used as a data lake to store raw and transformed data.

After developing the project, you can schedule the Airflow DAG to run as needed, ensuring that the ETL process executes at the desired frequency. The final cleaned, normalized, and transformed data will be available for real-time visualization in Tableau, providing up-to-date insights and reports. The project architecture diagram is as follows:

:-: ![](.topwrite/assets/image_1737353888502.png =814)

### Tools and Services Used

* **Python**: For scripting and data processing.
* **Pandas**: For data manipulation and analysis.
* **AWS S3**: As a data lake for storing raw and transformed data.
* **Snowflake**: For data modeling and storage.
* **Apache Airflow**: For orchestrating ETL workflows.
* **EC2**: For hosting the Airflow environment.
* **Kaggle API**: For extracting data from Kaggle.
* **Tableau**: For data visualization.

### ETL Workflow

1. **Data Extraction**

   * Create an Airflow DAG script to extract a random number of rows from the Kaggle insurance dataset using the Kaggle API.

   * Clean, normalize, and transform the data into four tables:

     * `policy_data`
     * `customers_data`
     * `vehicles_data`
     * `claims_data`

2. **Data Storage**

   * Store the transformed data in S3 buckets, organizing it into different folders for each type of normalized data (`policy_data`, `customers_data`, `vehicles_data`, `claims_data`).

3. **Data Processing in Snowflake**

   * Create Snowflake SQL worksheets to define the database schema.
   * Create staging tables in Snowflake for each type of normalized data.
   * Define Snowpipes to automatically extract data from S3 buckets into staging tables.
   * Create stream objects for each staging table to capture changes.
   * Create final tables to merge new data from stream objects, ensuring only distinct or new rows are inserted.

4. **Change Data Capture with Snowflake Streams and Tasks**

   * Create tasks in Snowflake to automatically capture change data.
   * Each task is triggered to load data into the final tables when new data is available in the stream objects.

5. **Airflow DAG Tasks**

   * **Task 1**: Check if the Kaggle API is available.
* **Task 2**: Upload the transformed data to the S3 bucket.

## Migration Plan

### Requirements

* [Singdata Lakehouse](https://www.yunqi.tech/) account
* [Github repository](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/Quickstarts_RealTime_Insurance_claims_Data_ETL_Pipeline) for this guide
* AK information to access AWS S3

### Singdata Lakehouse and Snowflake Object Concept Mapping

| [Singdata Lakehouse Concepts](key_concepts.md) | Snowflake Concepts    |
| ---------------------------------------------- | --------------------- |
| WORSPACE                                       | DATABASE              |
| SCHEMA                                         | SCHEMA                |
| VCLUSTER                                       | WAREHOUSE             |
| STORAGE CONNECTION                             | STORAGE INTEGRATION   |
| VOLUME                                         | STAGE                 |
| TABLE                                          | TABLE                 |
| PIPE                                           | SNOWPIPE              |
| TABLE STREAM                                   | STREAM                |
| STUDIO TASK                                    | TASK                  |
| Lakehouse SQL                                  | Snowflake SQL         |

### Architecture Based on Singdata Lakehouse

:-: ![](.topwrite/assets/image_1737358887540.png =812)

### Comparison of Tools and Services in Singdata Lakehouse and Snowflake Solutions

| Tools and Services in Singdata Lakehouse Solution | Purpose                | Tools and Services in Snowflake Solution | Purpose                |
| ------------------------------------------------- | ---------------------- | ---------------------------------------- | ---------------------- |
| Python                                            | For scripting and data processing | Python                                    | For scripting and data processing |
| Pandas                                            | For data manipulation and analysis | Pandas                                    | For data manipulation and analysis |
| AWS S3                                            | As a data lake for storing raw and transformed data | AWS S3                                    | As a data lake for storing raw and transformed data |
| **Singdata Lakehouse**                            | For data modeling and storage | Snowflake                                 | For data modeling and storage |
| **Singdata Lakehouse Studio IDE**                 | For orchestrating ETL workflows | Apache Airflow                            | For orchestrating ETL workflows |
| **Singdata Lakehouse Studio Python Task**         | For hosting Airflow environment | EC2                                       | For hosting Airflow environment |
| **Singdata Lakehouse JDBC Driver**                | For connecting to Tableau | Tableau Snowflake Connector               | For connecting to Tableau        |
| Kaggle API                      | Used to extract data from Kaggle    | Kaggle API            | Used to extract data from Kaggle    |
| Tableau                         | Used for data visualization         | Tableau               | Used for data visualization         |

### Syntax Differences Encountered During Migration

| Function        | Singdata Lakehouse                                             | Snowflake         |
| --------- | ------------------------------------------------------- | ----------------- |
| Code Comments      | —- or —                                                 | /// or //         |
| stream metadata | \_\_change\_type field                                      | METADATA$ACTION   |
| Create Object DDL   | Some objects do not support CREATE OR REPLACE, use CREATE IF NOT EXISTS and ALTER | CREATE OR REPLACE |

^

## Migration Steps

### Task Development

#### Task Tree

Navigate to [Lakehouse Studio](studio_overview.md) Development -> Tasks,

:-: ![](.topwrite/assets/image_1737359607866.png =766)

Click “+” to create the following directories:

* Quickstarts\_RealTime\_Insurance\_claims\_Data\_ETL\_Pipeline

Click “+” to create the following SQL tasks:

* 00\_Setup\_Env
* 02\_Stages\_or\_Volumes
* 03\_Tables
* 04\_Pipes
* 05\_Streams

After developing the above tasks, please click “Run” to complete the object creation.

^

Click “+” to create the following PYTHON tasks:

* 01\_Data\_Generate
* 06\_Tasks (directory)
  * claims\_cdc\_task
  * customers\_cdc\_task
  * policy\_cdc\_task
  * vehicles\_cdc\_task

After developing the above tasks, please click “Run” to test first (refer to the scheduling and publishing guide later in the document for subsequent steps).

^

Copy the following code into the corresponding tasks, or you can [download the files from GitHub](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/Quickstarts_RealTime_Insurance_claims_Data_ETL_Pipeline) and then copy the content into the corresponding tasks.

^

#### Parameter Settings in Tasks

^

For tasks (00\_Setup\_Env and 01\_Data\_Generate), there are parameters, for example:

^

:-: ![](.topwrite/assets/image_1737360457052.png =806)

^

Please click “Schedule”:

^

:-: ![](.topwrite/assets/image_1737360486722.png =797)

^

Then “Load Parameters from Code” and fill in the actual values:

^

:-: ![](.topwrite/assets/image_1737425374903.png =807)

####

#### Build Singdata Lakehouse Environment

00\_Setup\_Env:
```SQL
-- RealTime_Insurance_ETL_VC virtual cluster
CREATE VCLUSTER IF NOT EXISTS RealTime_Insurance_ETL_VC
   VCLUSTER_SIZE = XSMALL
   VCLUSTER_TYPE = GENERAL
   AUTO_SUSPEND_IN_SECOND = 60
   AUTO_RESUME = TRUE
   COMMENT  'RealTime_Insurance_ETL_VC VCLUSTER for test';

-- Use our VCLUSTER for data house
USE VCLUSTER RealTime_Insurance_ETL_VC;

-- Create and Use SCHEMA
CREATE SCHEMA IF NOT EXISTS  RealTime_Insurance_ETL_SCH;
USE SCHEMA RealTime_Insurance_ETL_SCH;

--external Connection for data lake
-- Create data lake Connection, connection to data lake
CREATE STORAGE CONNECTION if not exists aws_s3_connection_demo
    TYPE S3
    ENDPOINT = 's3.us-east-1.amazonaws.com'
    REGION = 'us-east-1'
    ACCESS_KEY = ${ACCESS_KEY}
    SECRET_KEY = ${SECRET_KEY}
    comments = 'us-east-1 storage connection for etl demo';
```
#### Migrate SNOWFLAKE\_ETL.py to Singdata Lakehouse's Built-in Python Task Data\_Generate

Singdata Lakehouse provides a managed Python runtime environment. Python tasks developed in Singdata Lakehouse Studio can run directly or be scheduled to run periodically by configuring scheduling information.

01\_Data\_Generate:
```PYTHON
import subprocess
import sys
import warnings
import contextlib
import os

# Suppress warnings
warnings.filterwarnings("ignore", message="A value is trying to be set on a copy of a slice from a DataFrame")

# Suppress stderr
@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

with suppress_stderr():
    # Install kaggle
    subprocess.run([sys.executable, "-m", "pip", "install", "kaggle", "--target", "/home/system_normal", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"], stderr=subprocess.DEVNULL)
    sys.path.append('/home/system_normal')

import pandas as pd
import boto3
import random
import os, json, io
import zipfile
from datetime import datetime

def load_random_sample(csv_file, sample_size):

    # Count total rows in the CSV file
    total_rows = sum(1 for line in open(csv_file, encoding='utf-8')) - 1  # Subtract header row

    # Calculate indices of rows to skip (non-selected)
    skip_indices = random.sample(range(1, total_rows + 1), total_rows - sample_size)

    # Load DataFrame with random sample of rows
    df = pd.read_csv(csv_file, skiprows=skip_indices)

    policy_table = df[['policy_id', 'subscription_length', 'region_code', 'segment']].copy()
    vehicles_table = df[['policy_id', 'vehicle_age', 'fuel_type', 'is_parking_sensors', 'is_parking_camera', 'rear_brakes_type', 'displacement', 'transmission_type', 'steering_type', 'turning_radius', 'gross_weight', 'is_front_fog_lights', 'is_rear_window_wiper', 'is_rear_window_washer', 'is_rear_window_defogger', 'is_brake_assist', 'is_central_locking', 'is_power_steering', 'is_day_night_rear_view_mirror', 'is_speed_alert', 'ncap_rating']].copy()
    customers_table = df[['policy_id', 'customer_age', 'region_density']].copy()
    claims_table = df[['policy_id', 'claim_status']].copy()

    vehicles_table.rename(columns={'policy_id': 'vehicle_id'}, inplace=True)
    customers_table.rename(columns={'policy_id': 'customer_id'}, inplace=True)
    claims_table.rename(columns={'policy_id': 'claim_id'}, inplace=True)

    return policy_table, vehicles_table, customers_table, claims_table

def upload_df_to_s3():
    try:
        with suppress_stderr():
            # Setup Kaggle API

            # Ensure the directory exists
            config_dir = '/home/system_normal/tempdata/.config/kaggle'
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            # Create the kaggle.json file with the given credentials
            kaggle_json = {
                "username": ${kaggle_username},
                "key": ${kaggel_key}
            }
            with open(os.path.join(config_dir, 'kaggle.json'), 'w') as f:
                json.dump(kaggle_json, f)

            # Set the environment variable to the directory containing kaggle.json
            os.environ['KAGGLE_CONFIG_DIR'] = config_dir
            from kaggle.api.kaggle_api_extended import KaggleApi
            # Authenticate the Kaggle API
            api = KaggleApi()
            api.authenticate()

            # Define the dataset
            dataset = 'litvinenko630/insurance-claims'

            # Define the CSV file name
            csv_file = 'Insurance claims data.csv'

            # Download the entire dataset as a zip file
            api.dataset_download_files(dataset, path='/home/system_normal/tempdata')

            # Extract the CSV file from the downloaded zip file
            with zipfile.ZipFile('/home/system_normal/tempdata/insurance-claims.zip', 'r') as zip_ref:
                zip_ref.extract(csv_file, path='/home/system_normal/tempdata')

            policy_data, vehicles_data, customers_data, claims_data = load_random_sample(f'/home/system_normal/tempdata/{csv_file}', 20)
            # Convert DataFrame to CSV string
            policy = policy_data.to_csv(index=False)
            vehicles = vehicles_data.to_csv(index=False)
            customers = customers_data.to_csv(index=False)
            claims = claims_data.to_csv(index=False)

            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Ensure you have set your AWS credentials in environment variables or replace the following with your credentials
            s3_client = boto3.client(
                's3',
                aws_access_key_id= ${aws_access_key_id},
                aws_secret_access_key= ${aws_secret_access_key},
                region_name= ${aws_region_name}
            )

            # Define S3 bucket and keys with current date and time
            s3_bucket = 'insurance-data-clickzetta-etl-project'
            s3_key_policy = f'policy/policy_{current_datetime}.csv'
            s3_key_vehicles = f'vehicles/vehicles_{current_datetime}.csv'
            s3_key_customers = f'customers/customers_{current_datetime}.csv'
            s3_key_claims = f'claims/claims_{current_datetime}.csv'

            # Upload to S3
            s3_client.put_object(Bucket=s3_bucket, Key=s3_key_policy, Body=policy)
            s3_client.put_object(Bucket=s3_bucket, Key=s3_key_vehicles, Body=vehicles)
            s3_client.put_object(Bucket=s3_bucket, Key=s3_key_customers, Body=customers)
            s3_client.put_object(Bucket=s3_bucket, Key=s3_key_claims, Body=claims)
            printf("upload_df_to_s3 down:{s3_key_policy},{s3_key_vehicles},{s3_key_customers},{s3_key_claims}")
    
    except Exception as e:
        pass  # Ignore errors

# Run the upload function
upload_df_to_s3()
```
#### Create Singdata Lakehouse Volumes (corresponding to Snowflake Stages)

02\_Stages\_or\_Volumes:

^

Please change the bucket name insurance-data-clickzetta-etl-project in LOCATION 's3://insurance-data-clickzetta-etl-project/policy' to your bucket name.
```SQL
-- Create Volume, the location of the data lake storage files
CREATE EXTERNAL VOLUME  if not exists policy_data_stage
  LOCATION 's3://insurance-data-clickzetta-etl-project/policy' 
  USING connection aws_s3_connection_demo  -- storage Connection
  DIRECTORY = (
    enable = TRUE
  ) 
  recursive = TRUE;

-- Synchronize the directory of the data lake Volume to the Lakehouse
ALTER volume policy_data_stage refresh;

-- View files on the Singdata Lakehouse data lake Volume
SELECT * from directory(volume policy_data_stage);

--********************************************************************--
-- Create Volume, the location of the data lake storage files
CREATE EXTERNAL VOLUME  if not exists vehicles_data_stage
  LOCATION 's3://insurance-data-clickzetta-etl-project/vehicles' 
  USING connection aws_s3_connection_demo  -- storage Connection
  DIRECTORY = (
    enable = TRUE
  ) 
  recursive = TRUE;

-- Synchronize the directory of the data lake Volume to the Lakehouse
ALTER volume vehicles_data_stage refresh;

-- View files on the Singdata Lakehouse data lake Volume
SELECT * from directory(volume vehicles_data_stage);

--********************************************************************--
-- Create Volume, the location of the data lake storage files
CREATE EXTERNAL VOLUME  if not exists customers_data_stage
  LOCATION 's3://insurance-data-clickzetta-etl-project/customers' 
  USING connection aws_s3_connection_demo  -- storage Connection
  DIRECTORY = (
    enable = TRUE
  ) 
  recursive = TRUE;

-- Synchronize the directory of the data lake Volume to the Lakehouse
ALTER volume customers_data_stage refresh;

-- View files on the Singdata Lakehouse data lake Volume
SELECT * from directory(volume customers_data_stage);

--********************************************************************--
-- Create Volume, the location of the data lake storage files
CREATE EXTERNAL VOLUME  if not exists claims_data_stage
  LOCATION 's3://insurance-data-clickzetta-etl-project/claims' 
  USING connection aws_s3_connection_demo  -- storage Connection
  DIRECTORY = (
    enable = TRUE
  ) 
  recursive = TRUE;

-- Synchronize the directory of the data lake Volume to the Lakehouse
ALTER volume claims_data_stage refresh;

-- View files on the Singdata Lakehouse data lake Volume
SELECT * from directory(volume claims_data_stage);
```
#### Create Singdata Lakehouse Tables

03\_Tables:
```SQL
--- STAGING TABLES ---
--creating staging tables for each normalized tables created by data pipeline
CREATE  TABLE IF NOT EXISTS staging_policy(
    policy_id VARCHAR(15) ,
    subscription_length FLOAT,
    region_code VARCHAR(5),
    segment VARCHAR(10));
    
CREATE  TABLE IF NOT EXISTS staging_vehicles (
    vehicle_id VARCHAR(15) ,
    vehicle_age FLOAT,
    fuel_type VARCHAR(10),
    parking_sensors VARCHAR(5),
    parking_camera VARCHAR(5),
    rear_brakes_type VARCHAR(10),
    displacement INT,
    trasmission_type VARCHAR(20),
    steering_type VARCHAR(15),
    turning_radius FLOAT,
    gross_weight INT,
    front_fog_lights VARCHAR(5),
    rear_window_wiper VARCHAR(5), 
    rear_window_washer VARCHAR(5),
    rear_window_defogger VARCHAR(5), 
    brake_assist VARCHAR(5), 
    central_locking VARCHAR(5),
    power_steering VARCHAR(5),      
    day_night_rear_view_mirror VARCHAR(5),  
    is_speed_alert VARCHAR(5),
    ncap_rating INT);

CREATE  TABLE IF NOT EXISTS staging_customers(
    customer_id VARCHAR(20) ,
    customer_age INT,
    region_density INT);

CREATE  TABLE IF NOT EXISTS staging_claims(
    claim_id VARCHAR(20) ,
    claim_status INT);




--- FINAL TABLES ---
--creating final table to store transformed data captured by stream objects 
CREATE  TABLE IF NOT EXISTS policy(
    policy_id VARCHAR(15) ,
    subscription_length FLOAT,
    region_code VARCHAR(5),
    segment VARCHAR(10));

SELECT * FROM policy;
TRUNCATE TABLE policy;

CREATE  TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(15) ,
    vehicle_age FLOAT,
    fuel_type VARCHAR(10),
    parking_sensors VARCHAR(5),
    parking_camera VARCHAR(5),
    rear_brakes_type VARCHAR(10),
    displacement INT,
    trasmission_type VARCHAR(20),
    steering_type VARCHAR(15),
    turning_radius FLOAT,
    gross_weight INT,
    front_fog_lights VARCHAR(5),
    rear_window_wiper VARCHAR(5), 
    rear_window_washer VARCHAR(5),
    rear_window_defogger VARCHAR(5), 
    brake_assist VARCHAR(5), 
    central_locking VARCHAR(5),
    power_steering VARCHAR(5),      
    day_night_rear_view_mirror VARCHAR(5),  
    is_speed_alert VARCHAR(5),
    ncap_rating INT);

CREATE  TABLE IF NOT EXISTS customers(
    customer_id VARCHAR(20) ,
    customer_age INT,
    region_density INT);

CREATE  TABLE IF NOT EXISTS claims(
    claim_id VARCHAR(20) ,
    claim_status INT);
```
#### Create Singdata Lakehouse Pipes

04\_Pipes:
```SQL
create pipe policy_pipe
  VIRTUAL_CLUSTER = 'RealTime_Insurance_ETL_VC'
  -- Execute to get the latest file using scan file mode
  INGEST_MODE = 'LIST_PURGE'
  as
copy into staging_policy from volume policy_data_stage(
    policy_id VARCHAR(15) ,
    subscription_length FLOAT,
    region_code VARCHAR(5),
    segment VARCHAR(10))
using csv OPTIONS(
  'header'='true'
)
-- Must add purge parameter to delete data after successful import
purge=true
;
--********************************************************************--
create pipe vehicles_pipe
  VIRTUAL_CLUSTER = 'RealTime_Insurance_ETL_VC'
  -- Execute to get the latest file using scan file mode
  INGEST_MODE = 'LIST_PURGE'
  as
copy into staging_vehicles from volume vehicles_data_stage(
    vehicle_id VARCHAR(15) ,
    vehicle_age FLOAT,
    fuel_type VARCHAR(10),
    parking_sensors VARCHAR(5),
    parking_camera VARCHAR(5),
    rear_brakes_type VARCHAR(10),
    displacement INT,
    trasmission_type VARCHAR(20),
    steering_type VARCHAR(15),
    turning_radius FLOAT,
    gross_weight INT,
    front_fog_lights VARCHAR(5),
    rear_window_wiper VARCHAR(5), 
    rear_window_washer VARCHAR(5),
    rear_window_defogger VARCHAR(5), 
    brake_assist VARCHAR(5), 
    central_locking VARCHAR(5),
    power_steering VARCHAR(5),      
    day_night_rear_view_mirror VARCHAR(5),  
    is_speed_alert VARCHAR(5),
    ncap_rating INT)
using csv OPTIONS(
  'header'='true'
)
-- Must add purge parameter to delete data after successful import
purge=true
;
--********************************************************************--
create pipe customers_pipe
  VIRTUAL_CLUSTER = 'RealTime_Insurance_ETL_VC'
  -- Execute to get the latest file using scan file mode
  INGEST_MODE = 'LIST_PURGE'
  as
copy into staging_customers from volume customers_data_stage(
    customer_id VARCHAR(20),
    customer_age INT,
    region_density INT)
using csv OPTIONS(
  'header'='true'
)
-- Must add purge parameter to delete data after successful import
purge=true
;
--********************************************************************--
create pipe claims_pipe
  VIRTUAL_CLUSTER = 'RealTime_Insurance_ETL_VC'
  -- Execute to get the latest file using scan file mode
  INGEST_MODE = 'LIST_PURGE'
  as
copy into staging_claims from volume claims_data_stage(
    claim_id VARCHAR(20) ,
    claim_status INT)
using csv OPTIONS(
  'header'='true'
)
-- Must add purge parameter to delete data after successful import
purge=true
;
```
#### Create Singdata Lakehouse Table Streams (corresponding to Snowflake's Streams)

05\_Streams:
```SQL
--********************************************************************--
--- CREATING TABLE STREAM OBJECTS FOR EACH STAGING TABLES TO CAPTURE NEW DATA
--  creating TABLE STREAM objects for staging tables
CREATE TABLE STREAM IF NOT EXISTS STREAM_policy ON TABLE staging_policy
WITH
  PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
--********************************************************************--
CREATE TABLE STREAM IF NOT EXISTS STREAM_vehicles ON TABLE staging_vehicles
WITH
  PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
--********************************************************************--
CREATE TABLE STREAM IF NOT EXISTS STREAM_customers ON TABLE staging_customers
WITH
  PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
--********************************************************************--
CREATE TABLE STREAM IF NOT EXISTS STREAM_claims ON TABLE staging_claims
WITH
  PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
--********************************************************************--
-- check total streams
SHOW TABLE STREAMS;
```
#### Check Newly Created Objects

Use the following command to check whether the objects created by the SQL command have been successfully created and the status of PIPES.
```SQL
--Lake Objects
SHOW CONNECTIONS;
SHOW VOLUMES;

--House Objects
SHOW TABLES;
SHOW PIPES;
SHOW TABLE STREAMS;
```

####

```SQL
SHOW CONNECTIONS;
```

:-: ![](.topwrite/assets/image_1737425940720.png =803)

```SQL
SHOW VOLUMES;
```

:-: ![](.topwrite/assets/image_1737425972728.png =794)

```SQL
SHOW TABLES;
```

:-: ![](.topwrite/assets/image_1737425995818.png =788)

```SQL
SHOW PIPES;
```

:-: ![](.topwrite/assets/image_1737425892542.png =776)

```SQL
SHOW TABLE STREAMS;
```
:-: ![](.topwrite/assets/image_1737426021254.png =766)

#### Create Transform Task

06\_Tasks\:claims\_cdc\_task
```SQL
MERGE INTO claims AS a
    USING stream_claims AS b
    ON a.claim_id = b.claim_id
    WHEN NOT MATCHED AND b.__change_type = 'INSERT' THEN
        INSERT (claim_id, claim_status)
        VALUES (b.claim_id, b.claim_status);
```

###

06\_Tasks\:customers\_cdc\_task

```SQL
MERGE INTO customers AS a
    USING stream_customers AS b
    ON a.customer_id = b.customer_id
    WHEN NOT MATCHED AND b.__change_type = 'INSERT' THEN
        INSERT (customer_id, customer_age, region_density)
        VALUES (b.customer_id, b.customer_age, b.region_density);
```

###

06\_Tasks\:policy\_cdc\_task

```SQL
MERGE INTO policy AS a
    USING stream_policy AS b
    ON a.policy_id = b.policy_id
    WHEN NOT MATCHED AND b.__change_type = 'INSERT' THEN
        INSERT (policy_id, subscription_length, region_code, segment)
        VALUES (b.policy_id, b.subscription_length, b.region_code, b.segment);
```

###

06\_Tasks\:vehicles\_cdc\_task

```SQL
MERGE INTO vehicles AS a
    USING stream_vehicles AS b
    ON a.vehicle_id = b.vehicle_id
    WHEN NOT MATCHED AND b.__change_type = 'INSERT' THEN
        INSERT (vehicle_id, vehicle_age, fuel_type, parking_sensors, parking_camera, rear_brakes_type, displacement, trasmission_type, steering_type, turning_radius, gross_weight, front_fog_lights, rear_window_wiper, rear_window_washer, rear_window_defogger, brake_assist, central_locking, power_steering, day_night_rear_view_mirror, is_speed_alert, ncap_rating)
        VALUES (b.vehicle_id, b.vehicle_age,b.fuel_type, b.parking_sensors, b.parking_camera, b.rear_brakes_type, b.displacement, b.trasmission_type, b.steering_type, b.turning_radius, b.gross_weight, b.front_fog_lights, b.rear_window_wiper, b.rear_window_washer, b.rear_window_defogger, b.brake_assist, b.central_locking, b.power_steering, b.day_night_rear_view_mirror, b.is_speed_alert, b.ncap_rating);
```
###

### Production Operation

### Job Scheduling

Navigate to [Lakehouse Studio](studio_overview.md) Development -> Tasks,

configure the scheduling parameters for the following tasks and submit them to the production environment for execution.

^

The tasks that need to be scheduled and submitted for deployment are as follows:

* 01\_Data\_Generate
* claims\_cdc\_task
* customers\_cdc\_task
* policy\_cdc\_task
* vehicles\_cdc\_task

^

:-: ![](.topwrite/assets/image_1737360326171.png =815)

^

The scheduling parameters are configured as follows:

^

:-: ![](.topwrite/assets/image_1737360361129.png =817)

^

Streams and Pipes will run automatically after creation, no scheduling is required.

^

### Analyzing Data in Singdata Lakehouse with Tableau

Refer to [this article](tableauconnecttolakehouse.md) to connect Tableau to Singdata Lakehouse via JDBC, explore and analyze the data in the Lakehouse, and create BI reports.

#### Periodic Task Maintenance

Navigate to [Lakehouse Studio](studio_overview.md) Operations Monitoring -> Task Maintenance -> Periodic Tasks, to view the running status of each periodic scheduling task:

^

:-: ![](.topwrite/assets/image_1737365542778.png =793)

#### Management of Task Instances for Periodic Tasks

:-: ![](.topwrite/assets/image_1737365603958.png =818)

#### Pipes Maintenance
```SQL
-- Pause and Start PIPE
-- Pause
ALTER pipe policy_pipe SET PIPE_EXECUTION_PAUSED = true;
-- Start
ALTER pipe policy_pipe SET PIPE_EXECUTION_PAUSED = false;

-- View the execution status of pipe copy jobs
-- Within seven days, delayed by half an hour
SELECT * FROM INFORMATION_SCHEMA.JOB_HISTORY WHERE QUERY_TAG="pipe.qiliang_ws.realtime_insurance_etl_sch.policy_pipe";
-- Real-time
SHOW JOBS IN VCLUSTER SCD_VC WHERE QUERY_TAG="pipe.qiliang_ws.realtime_insurance_etl_sch.policy_pipe";

SHOW JOBS where length(QUERY_TAG)>10;

-- View the historical files imported by copy jobs
select * from load_history('RealTime_Insurance_ETL_SCH.staging_policy');
select * from load_history('RealTime_Insurance_ETL_SCH.staging_vehicles');
select * from load_history('RealTime_Insurance_ETL_SCH.staging_customers');
select * from load_history('RealTime_Insurance_ETL_SCH.staging_claims');
```
#### View data in staging table, table stream, and final table
```SQL
SELECT '01staging' AS table_type, 'staging_policy' AS table_name, COUNT(*) AS row_count FROM staging_policy
UNION ALL
SELECT '01staging' AS table_type, 'staging_vehicles' AS table_name, COUNT(*) AS row_count FROM staging_vehicles
UNION ALL
SELECT '01staging' AS table_type, 'staging_customers' AS table_name, COUNT(*) AS row_count FROM staging_customers
UNION ALL
SELECT '01staging' AS table_type, 'staging_claims' AS table_name, COUNT(*) AS row_count FROM staging_claims
UNION ALL
SELECT '02stream' AS table_type, 'STREAM_policy' AS table_name, COUNT(*) AS row_count FROM STREAM_policy
UNION ALL
SELECT '02stream' AS table_type, 'STREAM_vehicles' AS table_name, COUNT(*) AS row_count FROM STREAM_vehicles
UNION ALL
SELECT '02stream' AS table_type, 'STREAM_customers' AS table_name, COUNT(*) AS row_count FROM STREAM_customers
UNION ALL
SELECT '02stream' AS table_type, 'STREAM_claims' AS table_name, COUNT(*) AS row_count FROM STREAM_claims
UNION ALL
SELECT '03final' AS table_type, 'policy' AS table_name, COUNT(*) AS row_count FROM policy
UNION ALL
SELECT '03final' AS table_type, 'vehicles' AS table_name, COUNT(*) AS row_count FROM vehicles
UNION ALL
SELECT '03final' AS table_type, 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT '03final' AS table_type, 'claims' AS table_name, COUNT(*) AS row_count FROM claims
ORDER BY table_type;
```
:-: ![](.topwrite/assets/image_1737429058137.png =810)

## Documentation

[Singdata Lakehouse Basic Concepts](key_concepts.md)

[Singdata Lakehouse JDBC Driver](jdbc-driver.md)

[Singdata Lakehouse Python Tasks](python_task.md)

[Singdata Lakehouse Scheduling and Operations](taskdevelop.md)

^
^
^
^
^
^
^