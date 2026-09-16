# CDC and Data Processing via Singdata Lakehouse Multi-Table Real-Time Sync and Dynamic Tables

## Overview

In this quickstart, we will explore how to use customer transaction data stored in a PostgreSQL database, ingest it into Singdata Lakehouse tables via Singdata Lakehouse's multi-table real-time sync, process it in real time using Dynamic Tables, and further perform visual data exploration and conversational data analysis through Singdata Lakehouse's built-in Data Analytics Agent (DataGPT). This creates a real-time end-to-end pipeline covering data ingestion, processing, and analysis to gain insights into customer transactions.

From an ELT perspective, Singdata Lakehouse's multi-table real-time sync handles CDC-based Data Extraction and Loading, including Schema Evolution — meaning the sync captures structural or schema changes in the source database. Dynamic Tables provide a new approach to Data Transformation.

### What is CDC and Why Use It

CDC (Change Data Capture) is a technique that syncs only the data that has changed, rather than copying an entire table each time. It works similarly to a database binlog — every insert, update, and delete is recorded, and downstream systems consume these change events to stay in sync with the source.

Full-table sync is fine at small scale, but as data volume grows, the time window for each full copy gets longer and resource consumption multiplies. CDC transmits only incremental changes, reducing latency to seconds while significantly lowering the load on the source database and network.

The data flow architecture for this tutorial is:

**PostgreSQL** (source database) → **Singdata Multi-Table Real-Time Sync** (CDC extraction + loading) → **Lakehouse Tables** (raw data landing) → **Dynamic Table** (incremental auto-transformation) → **Data Analytics Agent (DataGPT)** (conversational analysis)

^

:-: ![](.topwrite/assets/image_1735115515214.png)

^

After completing this tutorial, you will have:

* A real-time CDC sync pipeline from PostgreSQL to Lakehouse
* An automated incremental data processing workflow based on Dynamic Tables
* A real-time dataset you can query directly via the Data Analytics Agent (DataGPT)

Prerequisites:

* [Docker](https://www.docker.com/products/docker-desktop/) installed on your local machine

* A tool for connecting to a PostgreSQL database

  * For example, Visual Studio Code, DBV/DBGrid, or Python scripts

* Basic familiarity with Python and SQL

* Familiarity with data science Notebooks

* An existing Singdata account, or go to the [Singdata](https://accounts.singdata.com/register) registration page to sign up for a free account. After registration, you can [log in](https://accounts.singdata.com/login) to the Singdata Lakehouse Web console.

## Singdata Lakehouse Environment

Overview

You will use [Singdata Lakehouse Studio](https://accounts.singdata.com/) (the Singdata Lakehouse web interface) to create Singdata Lakehouse objects (virtual compute clusters, spaces/databases, schemas, users, etc.).

### Create Objects and Load Data

1. Navigate to Development -> Tasks, click `+` to create a new working directory and worksheet task, then select SQL Worksheet

:-: ![](.topwrite/assets/image_1735115534331.png =600)

2. Working directory name: 01\_Demo\_Real\_Time\_Financial\_Insights\_Using\_Change\_Data\_Capture\_CDC
3. Task name: 01\_Setup\_Environment

:-: ![](.topwrite/assets/image_1735115562368.png =600)

2. Copy and paste the following [SQL script](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/scripts/clickzetta-lakehouse-setup.sql) to create Singdata Lakehouse objects (virtual compute cluster, database schema), then click "Run" at the top of the worksheet

```SQL
CREATE SCHEMA IF NOT EXISTS  Real_Time_Financial_Insights_Using_Change_Data_Capture_CDC;
USE SCHEMA Real_Time_Financial_Insights_Using_Change_Data_Capture_CDC;

/*---------------------------*/
-- Create our Virtual Cluster
/*---------------------------*/

-- data science virtual cluster
CREATE VCLUSTER IF NOT EXISTS cdc_ds_vc
   VCLUSTER_SIZE = XSMALL
   VCLUSTER_TYPE = ANALYTICS
   AUTO_SUSPEND_IN_SECOND = 60
   AUTO_RESUME = TRUE
   COMMENT  'data science VCLUSTER for cdc';

-- Use our VCLUSTER
USE VCLUSTER cdc_ds_wh;
/*---------------------------*/
-- sql completion note
/*---------------------------*/
SELECT 'cdc sql is now complete' AS note;
```

## Postgres Environment

### Overview

In this section, we will set up a PostgreSQL database and create tables to simulate customer transaction data for a financial company.

### Start the Database Instance

Before starting this step, make sure Docker Desktop is installed for [Mac](https://docs.docker.com/desktop/install/mac-install/), [Windows](https://docs.docker.com/desktop/install/windows-install/), or [Linux](https://docs.docker.com/desktop/install/linux/). Ensure [Docker Compose](https://docs.docker.com/compose/install/) is also installed on your machine.

1. To start a PostgreSQL database using Docker, you need to create a file named docker-compose.yaml. This file will contain the configuration for the PostgreSQL database. If you have another container client, start the container using the PostgreSQL image below.
2. Open your IDE of choice (e.g., VS Code) and copy-paste the following content into the file:

```YAML
services:
  postgres:
    image: "postgres:17"
    container_name: "postgres17"
    environment:
      POSTGRES_DB: 'postgres'
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
    ports:
      - "5432:5432"
    command:
      - "postgres"
      - "-c"
      - "wal_level=logical"
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
```

3. Open a terminal and navigate to the directory containing the docker-compose.yaml file. Run the following command to start the PostgreSQL database:

```Shell
docker-compose up -d
```

### Connect to the Database

To connect to the pre-configured database using Visual Studio Code, DBV/DBGrid/PyCharm, or any IDE of your choice, follow these steps using the provided credentials:

1. Open your chosen tool to connect to the PostgreSQL database

   1. For VSCode, you can use the [PostgreSQL extension](https://marketplace.visualstudio.com/items?itemName=cweijan.vscode-postgresql-client2)
   2. For PyCharm, you can use the [Database Tools and SQL plugin](https://www.jetbrains.com/help/pycharm/database-tool-window.html)

2. Click the `+` symbol or similar to add a data source

3. Use these connection parameters:

   1. User: `postgres`
   2. Password: `postgres`
   3. URL: `jdbc:postgresql://localhost:5432/`

4. Test the connection and save

5. To allow Singdata Lakehouse Studio to access the Postgres database over the public internet, be sure to configure public NAT mapping for the Postgres database.

### Load Data

1. Run the following [postgres script](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/scripts/postgresql_setup.sql) in PostgreSQL to create the database, schema, and tables:

```SQL
CREATE SCHEMA raw_cdc;
SET search_path TO raw_cdc;

DROP TABLE IF EXISTS postgres.raw_cdc.customers;
DROP TABLE IF EXISTS postgres.raw_cdc.merchants;
DROP TABLE IF EXISTS postgres.raw_cdc.products;
DROP TABLE IF EXISTS postgres.raw_cdc.transactions;

CREATE TABLE postgres.raw_cdc.customers (
   customer_id INTEGER PRIMARY KEY,
   firstname VARCHAR,
   lastname VARCHAR,
   age INTEGER,
   email VARCHAR,
   phone_number VARCHAR
);

CREATE TABLE postgres.raw_cdc.merchants (
   merchant_id integer PRIMARY KEY,
   merchant_name VARCHAR,
   merchant_category VARCHAR
);

CREATE TABLE postgres.raw_cdc.products (
   product_id INTEGER PRIMARY KEY,
   product_name VARCHAR,
   product_category VARCHAR,
   price DOUBLE PRECISION
);

CREATE TABLE postgres.raw_cdc.transactions (
   transaction_id VARCHAR PRIMARY KEY,
   customer_id INTEGER,
   product_id INTEGER,
   merchant_id INTEGER,
   transaction_date DATE,
   transaction_time VARCHAR,
   quantity INTEGER,
   total_price DOUBLE PRECISION,
   transaction_card VARCHAR,
   transaction_category VARCHAR
);
```

2. Download these CSV files and save them to a directory on your local machine:

   1. [customers.csv](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/postgres_csv/customers.csv)
   2. [merchants.csv](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/postgres_csv/merchants.csv)
   3. [products.csv](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/postgres_csv/products.csv)
   4. [transactions.csv](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/postgres_csv/transactions.csv)

3. Postgres data loading method 1: load via PostgreSQL COPY command

   1. Before loading data into the PostgreSQL database, we need to move the files from the local machine to the Docker container.
   2. Open your terminal and use the following command to get the Docker container ID:
   3. ```Shell
      docker ps
      ```
   4. To copy the CSV files to the container, run the following commands in the terminal, replacing the file paths with your actual file paths and replacing `container_id` with the actual container ID from the previous command:
   5. ```Shell
      docker cp /Users/your_username/Downloads/customers.csv container_id:/tmp/customers.csv
      docker cp /Users/your_username/Downloads/merchants.csv container_id:/tmp/merchants.csv
      docker cp /Users/your_username/Downloads/products.csv container_id:/tmp/products.csv
      docker cp /Users/your_username/Downloads/transactions.csv container_id:/tmp/transactions.csv
      ```
   6. Return to the PostgreSQL console and run the following SQL commands to load the files from the container into the PostgreSQL tables:

```SQL
COPY postgres.raw_cdc.customers FROM '/tmp/customers.csv' DELIMITER ',' CSV HEADER;
COPY postgres.raw_cdc.merchants FROM '/tmp/merchants.csv' DELIMITER ',' CSV HEADER;
COPY postgres.raw_cdc.products FROM '/tmp/products.csv' DELIMITER ',' CSV HEADER;
COPY postgres.raw_cdc.transactions FROM '/tmp/transactions.csv' DELIMITER ',' CSV HEADER;
```

4. Postgres data loading method 2: load via Python script

Copy the following code into a Python file or Notebook and run it. You can also directly download [this Python file](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/scripts/load-data-into-pg-by-python.py).

```Python
import psycopg2

```

Database connection info:

```Python
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
```

Set search_path:

```Python
cur.execute("SET search_path TO raw_cdc;")
import os
```

Set the CSV file directory:

```Python
csv_directory = "csv/"

def load_csv_to_postgres(csv_file, table_name):
    with open(csv_file, 'r') as f:
        cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER DELIMITER ','", f)
    conn.commit()

```

Iterate over all CSV files in the directory and load them into the corresponding tables:

```Python
for filename in os.listdir(csv_directory):
    if filename.endswith(".csv"):
        csv_file = os.path.join(csv_directory, filename)
        table_name = os.path.splitext(filename)[0]  # Use filename without extension as table name
        print(f"Loading {csv_file} into table {table_name}...")
        load_csv_to_postgres(csv_file, table_name)
        print(f"Loaded {csv_file} into table {table_name} successfully!")
```

Close the cursor and connection:

```Python
cur.close()
conn.close()
```

5. Next, make sure to run the `CREATE PUBLICATION` command to enable logical replication for tables in the `raw_cdc` schema. This allows the real-time sync task below to capture changes made to tables in the PostgreSQL database:

```SQL
CREATE PUBLICATION agent_postgres_publication FOR ALL TABLES;
```

A Publication is part of PostgreSQL logical replication. It lets users define a set of table changes (inserts, updates, deletes) that will be delivered to one or more subscribers. Logical replication is one implementation of CDC — it captures and propagates data changes in database tables. In short, after running this statement, PostgreSQL will capture data changes across all tables in the database, and those changes can be received and processed by subscribers, enabling CDC-based change tracking.

6. Finally, verify the tables are correctly loaded by running the following SQL commands:

```SQL
SELECT * FROM postgres.raw_cdc.customers;
SELECT * FROM postgres.raw_cdc.merchants;
SELECT * FROM postgres.raw_cdc.products;
SELECT * FROM postgres.raw_cdc.transactions;
```

## Create and Start the Singdata Lakehouse CDC Multi-Table Real-Time Sync Task

### Overview

You will use [Singdata Lakehouse Studio](https://accounts.singdata.com/) to create a multi-table real-time sync task through the UI in a no-code manner, loading data from Postgres tables into Singdata Lakehouse tables.

### Create a Postgres Data Source

Navigate to Administration -> Data Sources, click "New Data Source" and select Postgres to create a Postgres data source, making Postgres accessible to Singdata Lakehouse.

:-: ![](.topwrite/assets/image_1735115653296.png =600)

^

:-: ![](.topwrite/assets/image_1735115660694.png =600)

* Data source name: PG\_CDC\_DEMO
* Connection parameters: same as the Postgres environment connection parameters above.
* Make sure to configure the correct timezone for the database to avoid sync failures.

### Create the Multi-Table Real-Time Sync Task

Navigate to Development -> Tasks, click `+` to create a new working directory and task, then select "Multi-Table Real-Time Sync".

* Select "Multi-Table Real-Time Sync":

:-: ![](.topwrite/assets/image_1735115675871.png =600)

Create the multi-table real-time sync task and store it in the same directory created during environment setup:

* Task name: 02\_Ingestion\_CDC
* Source data: select Postgres

:-: ![](.topwrite/assets/image_1735115689339.png =600)

  For the source data, select the Postgres data source created in the previous step: PG\_CDC\_DEMO. After selecting it, the accessible databases, schemas, and tables for that data source will be shown automatically. Select all tables (all tables need to be synced):

:-: ![](.topwrite/assets/image_1735115698983.png =624)

  Select or create a SlotName for CDC sync. Note that the same slot should not be shared by two tasks, as this can cause data loss:

:-: ![](.topwrite/assets/image_1735115710124.png =600)

  Target table configuration:

  Select an existing schema under the target data source as the storage location for target tables.

:-: ![](.topwrite/assets/image_1735115718468.png =663)

  Configure and review the table and field mapping:

  Singdata Lakehouse automatically generates table and field mappings, including data type mappings. If no corresponding table exists in the selected Singdata Lakehouse namespace, the multi-table real-time sync task will automatically check and create the table when the task starts — no need to create it manually in advance.
CDC sync requires primary keys on source tables. The multi-table real-time sync will automatically create the corresponding [primary keys](primary-key.md) in the Lakehouse target tables.

:-: ![](.topwrite/assets/image_1735115731100.png =641)

  

Configure sync rules:

  Schema Evolution refers to the process of modifying and adapting a database's structure or schema (Schema) over time as requirements change, without interrupting existing system operations or causing data loss. It typically involves changes to table structures, fields, data types, relationships, and constraints.

  In the sync rules of a real-time sync task, you can configure automatic handling policies for changes to source tables and fields:

* Set the behavior when a field is deleted from the source table.
* Set the behavior when a new field is added to the source table. Renaming a field is treated as a deletion of the old field; the renamed field is recognized as a new field addition.
* Set the behavior when a new field is added to the source table.
* Set the behavior when a synced object in the data source is deleted. Renaming a table is treated as a deletion, and the renamed table is treated as a new table.

  In addition, the sync rules also support specifying which types of source change messages to process. Configure as needed. For example, in some scenarios where you want target data to only accumulate and not process source "delete" changes, simply remove the "Delete" option from this configuration.

:-: ![](.topwrite/assets/image_1735115747197.png =652)

### Submit and Start the Multi-Table Real-Time Sync Task

* **Submit** the multi-table real-time sync task:

:-: ![](.topwrite/assets/image_1735115761930.png =600)

* **Operations** for the multi-table real-time task:

:-: ![](.topwrite/assets/image_1735115774424.png =600)

* **Start** the multi-table real-time task:

:-: ![](.topwrite/assets/image_1735115784817.png =600)

* Select "Full Data Sync":

Whether to perform a full data sync before starting incremental sync. Note that this option can only be selected the first time the task is started after going live.

:-: ![](.topwrite/assets/image_1735115795219.png =474)

### View Full Sync Status

In the "Postgres Environment" section above, data was already loaded into the four Postgres tables via COPY or Python script. The "Full Data Sync" option selected in the previous step syncs all data before incremental sync begins.

:-: ![](.topwrite/assets/image_1735115806467.png =613)

All 4 tables have normal full sync and incremental sync status with no failovers.

:-: ![](.topwrite/assets/image_1735115814661.png =789)

You can see that the full sync has completed. After this, the incremental sync status will automatically switch to "Syncing" without any manual intervention.

## Incremental Sync Process for Multi-Table Real-Time Sync

### Insert New Data into the Source

Insert data into the Postgres source tables, verify incremental data sync through the already-started real-time multi-table sync task, and check the sync task status.

During incremental sync, the multi-table real-time sync uses the Lakehouse [Java Real-Time Programming Interface](java_reference/realtime-upload.md) to write data in real time into Lakehouse primary key tables.

Copy the following code into a Notebook and run it, or [download it directly](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/scripts/pg-insert-transaction.ipynb):

* Create a database connection

```Python
import psycopg2
import random
import time
from datetime import datetime
from pytz import timezone
import uuid # Import uuid module

```

Database connection info:

```Python
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
```

Set search_path:

```Python
cur.execute("SET search_path TO raw_cdc;")
```

* Set parameters for incremental data generation

```Python
```

Set parameters:

```Python
loop_interval = 0  # Loop interval (seconds)
loop_count = 1000  # Number of loop iterations
batch_size = 100  # Number of records to insert per batch
```

* Data loading function

```Python
def insert_transactions(loop_interval,loop_count,batch_size):
    # Loop loop_count times
    for i in range(loop_count):
        try:
            for j in range(1, batch_size + 1):
                # Randomly select valid customers, products, and merchants from existing tables
                cur.execute("SELECT * FROM customers ORDER BY RANDOM() LIMIT 1;")
                v_existing_customer = cur.fetchone()


                cur.execute("SELECT * FROM products ORDER BY RANDOM() LIMIT 1;")
                v_existing_product = cur.fetchone()


                cur.execute("SELECT * FROM merchants ORDER BY RANDOM() LIMIT 1;")
                v_existing_merchant = cur.fetchone()


                # Generate a new transaction ID (unique)
                v_new_transaction_id = f"TX{int(datetime.now().timestamp())}{j}"
                # Generate a new transaction ID (UUID format)
                v_new_transaction_id = str(uuid.uuid4())

                # Generate current date and time in New York timezone
                nyc_time = datetime.now(timezone('America/New_York'))
                v_transaction_date = nyc_time.date()
                v_transaction_time = nyc_time.strftime('%H:%M:%S')

                # Generate a random quantity (between 1 and 7)
                v_quantity = random.randint(1, 7)

                # Get product price and calculate total price
                v_product_price = v_existing_product[3]  # Price is in the 4th column
                # if not is_number(v_product_price):
                #     continue  # Skip non-numeric records
                v_total_price = float(v_product_price) * v_quantity

                # Randomly select a transaction card type
                v_transaction_card = random.choice(['American Express', 'Visa', 'Mastercard', 'Discover'])

                # Randomly select a transaction category
                v_transaction_category = 'Purchase' if random.random() < 0.8 else 'Refund'

                # Insert the new transaction into the transactions table
                cur.execute("""
                    INSERT INTO transactions (
                        transaction_id, customer_id, product_id, merchant_id, transaction_date, transaction_time, quantity, total_price, transaction_card, transaction_category
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    v_new_transaction_id, v_existing_customer[0], v_existing_product[0],
                    v_existing_merchant[0], v_transaction_date, v_transaction_time,
                    v_quantity, v_total_price, v_transaction_card, v_transaction_category
                ))

            # Commit after each batch of batch_size rows
            conn.commit()

            # Wait loop_interval seconds before inserting the next batch
            time.sleep(loop_interval)
        
        except Exception as e:
            print(f"Error occurred: {e}")
            conn.rollback()  # Roll back the current transaction
```

* Call the function to insert transaction data

```Python
```

Call the function to insert transaction data:

```Python
insert_transactions(loop_interval,loop_count,batch_size)
```

* Close the cursor and connection

```Python
```

Close the cursor and connection:

```Python
cur.close()
conn.close()
```

### View Incremental Sync Status

:-: ![](.topwrite/assets/image_1735115833155.png =600)

## Process Data from Multi-Table Real-Time Sync Using Dynamic Tables

Overview

You will use [Singdata Lakehouse Studio](https://accounts.singdata.com/) to create Dynamic Tables, processing in real time the data synced from Postgres tables to Singdata Lakehouse via multi-table real-time sync.

### Create a Dynamic Table

Navigate to Development -> Tasks, click "+" and select "Dynamic Table".

:-: ![](.topwrite/assets/image_1735115842636.png =600)

* Task name: 03\_customer\_purchase\_summary
* Schema: real\_time\_financial\_insights\_using\_change\_data\_capture\_cdc
* Table name: customer\_purchase\_summary
* Enter in the SQL code field:

```Python
SELECT
    t.transaction_id
    , t.customer_id
    , c.age AS customer_age
    , t.product_id
    , p.product_name
    , p.product_category
    , t.merchant_id
    , m.merchant_name
    , m.merchant_category
    , t.transaction_date
    , t.transaction_time
    , t.quantity
    , t.quantity * p.price AS total_price
    , t.transaction_card
    , t.transaction_category
FROM
    transactions t
JOIN
    customers c ON t.customer_id = c.customer_id
JOIN
    products p ON t.product_id = p.product_id
JOIN
    merchants m ON t.merchant_id = m.merchant_id
AND
    m.merchant_category = p.product_category;
```

  This SQL query retrieves detailed transaction records from the `transactions` table and joins related information from the `customers`, `products`, and `merchants` tables. Here is a detailed explanation:

  

* **Extract transaction records from the** `transactions` **table**:

  * `t.transaction_id`: Retrieves the unique identifier for each transaction.
  * `t.customer_id`: Retrieves the identifier of the customer associated with the transaction.
  * `t.product_id`: Retrieves the identifier of the product involved in the transaction.
  * `t.merchant_id`: Retrieves the identifier of the merchant providing the product or service.
  * `t.transaction_date` and `t.transaction_time`: Retrieve the date and time the transaction occurred.
  * `t.quantity`: Retrieves the quantity of products purchased in the transaction.
  * `t.transaction_card`: Retrieves the card type used for the transaction (e.g., credit or debit card).
  * `t.transaction_category`: Retrieves the category of the transaction (e.g., purchase or refund).

  

* **Extract customer information from the** `customers` **table**:

  * Uses `JOIN customers c ON t.customer_id = c.customer_id` to join the `transactions` table with the `customers` table to retrieve customer information associated with the transaction.
  * `c.age AS customer_age`: Retrieves the customer's age and aliases it as `customer_age`.

  

* **Extract product information from the** `products` **table**:

  * Uses `JOIN products p ON t.product_id = p.product_id` to join the `transactions` table with the `products` table to retrieve product information for the transaction.
  * `p.product_name`: Retrieves the product name.
  * `p.product_category`: Retrieves the product category.
  * `t.quantity * p.price AS total_price`: Calculates the total price for each transaction (quantity multiplied by unit price) and aliases it as `total_price`.

  

* **Extract merchant information from the** `merchants` **table**:

  * Uses `JOIN merchants m ON t.merchant_id = m.merchant_id AND m.merchant_category = p.product_category` to join the `transactions` table with the `merchants` table, ensuring the merchant category matches the product category.
  * `m.merchant_name`: Retrieves the merchant name.
  * `m.merchant_category`: Retrieves the merchant category.

Through these joins and data extractions, this query produces a detailed result set where each record contains full transaction details, customer information, product information, and merchant information, while also calculating the total price for each transaction — enabling more comprehensive and in-depth transaction analysis.

The Dynamic Table uses declarative syntax to refresh data on a scheduled basis, achieving the goal of dynamically updating data.

:-: ![](.topwrite/assets/image_1735115966112.png =600)

* Validate and save, then select "Complete SQL Development":

:-: ![](.topwrite/assets/image_1735115978198.png =600)

* Before submitting, select the virtual cluster for running the Dynamic Table refresh

  Select the virtual compute cluster "CDC\_DS\_VS" created in the "Singdata Lakehouse Environment" step.

* Before submitting, select "Auto Refresh"

:-: ![](.topwrite/assets/image_1735115986827.png =379)

### Submit and Complete Dynamic Table Development

:-: ![](.topwrite/assets/image_1735116000834.png =691)

### Dynamic Table Operations

After a successful submission, you can go to the Operations Center to view the current table's task details and refresh history, with options to start or stop the current table.

* Task details:

:-: ![](.topwrite/assets/image_1735116009194.png =600)

* Refresh history:

&#x20;      You can see the number of rows added and deleted in each refresh cycle, giving you visibility into how the Dynamic Table data changes "dynamically".

:-: ![](.topwrite/assets/image_1735116016064.png =781)

## Conversational Data Analysis via Singdata Data Analytics Agent (DataGPT)

Overview

You will use the Singdata Lakehouse Data Analytics Agent (DataGPT) to analyze the data synced from Postgres tables to Singdata Lakehouse via multi-table real-time sync through a question-and-answer interface.

### Access the Singdata Data Analytics Agent (DataGPT)

Navigate to Account Home -> Data Analytics Agent (DataGPT) to enter the Singdata Data Analytics Agent (DataGPT).

:-: ![](.topwrite/assets/image_1735116025067.png =600)

### Create a New Analysis Domain

Build data analysis on top of multiple data tables, metrics, Answer Builders, knowledge, and files — with support for adding users for permission isolation.

:-: ![](.topwrite/assets/image_1735116034928.png =600)

* Analysis domain name: CDC Transaction Data Analysis.
* After creation, select "Add Data", then select "Add Table" -> "Import Table" to add the Dynamic Table created in the previous section to the Data Analytics Agent (DataGPT).

:-: ![](.topwrite/assets/image_1735116042469.png =600)

^

:-: ![](.topwrite/assets/image_1735116049605.png =600)

* Click the icon to the right of "Description" — the system will use a large language model to add appropriate descriptions to each field, making it easier to align natural language semantics.

:-: ![](.topwrite/assets/image_1735116058010.png =600)

* Accept the automatically generated metrics from the LLM and complete the setup to begin analysis:

:-: ![](.topwrite/assets/image_1735116067960.png =600)

Once you enter the analysis domain page below, you can start data exploration and conversational analysis.

:-: ![](.topwrite/assets/image_1735116077565.png =641)

### Data Exploration

Navigate to the Analysis Domain (select "CDC Transaction Data Analysis") -> Explore to start exploring data based on the auto-created metrics.

:-: ![](.topwrite/assets/image_1735116085712.png =638)

### Conversational Data Analysis

Enter the question "Number of Mastercard transactions, distributed by merchant category" to get the following analysis result:

:-: ![](.topwrite/assets/image_1735116092619.png =630)

^

The system understood that "Mastercard" should match the transaction card (transaction\_card = Mastercard). This is thanks to the Data Analytics Agent (DataGPT) automatically indexing the values of the transaction\_card field.

Transaction count is a metric that was automatically created, achieving alignment of the metric's calculation definition.

Merchant category corresponds to the field merchant\_category, thanks to the automatic field description generation which quickly enabled semantic alignment.

Enter the question: What is the total number of transactions for purchasing 'Disinfectant Wipes' across each channel? The following analysis result is returned:

:-: ![](.topwrite/assets/image_1735279174589.png =631)

In the Lakehouse table, the product 'Disinfectant Wipes' is stored in English. When a user asks about 'Disinfectant Wipes' in Chinese, the Data Analytics Agent (DataGPT) automatically translates the query for a precise match, so users don't have to input the exact English term. This fully leverages the power of large language models to make data analysis simpler.

## Cleanup

After completing this quickstart, you can clean up the objects created in Singdata Lakehouse.

## Summary

Congratulations! You have completed this quickstart!

### Key Takeaways

  After completing this quickstart, you now have a deeper understanding of:

* How to use Singdata Lakehouse multi-table real-time sync to sync PostgreSQL data into Singdata Lakehouse tables — corresponding to the Extract (E) and Load (L) steps of the ELT process.
* Using Dynamic Tables to process data — corresponding to the Transform (T) step of the ELT process.
* Visually exploring data and performing conversational data analysis using the built-in Data Analytics Agent (DataGPT) in Singdata Lakehouse.

### Resources

  [Singdata Lakehouse Multi-Table Real-Time Sync](https://www.singdata.com/documents/realtime_sync)

  [Singdata Lakehouse Dynamic Tables](https://www.singdata.com/documents/dynamictable)

  Singdata Lakehouse Conversational Data Analysis — Data Analytics Agent (DataGPT)

  [Singdata Lakehouse Studio: Web Development and Management Tool](https://www.singdata.com/documents/Studio)

  [Table Primary Key Definition](primary-key.md)

  [Java Real-Time Programming Interface](java_reference/realtime-upload.md)

  [Using Java SDK to Read Kafka Data and Upload in Real Time](use-java-sdk-realtime-uploaddata.md)
