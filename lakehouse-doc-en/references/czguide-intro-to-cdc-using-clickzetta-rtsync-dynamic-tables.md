# Real-time Multi-table Synchronization and Dynamic Table Implementation for Change Data Capture (CDC) and Data Processing through Singdata Lakehouse

## Overview

In this quick start guide, we will explore how to use customer transaction data stored in a PostgreSQL database, import the data into Singdata Lakehouse tables through real-time multi-table synchronization, process the data in real-time using dynamic tables, and further perform visual data exploration and conversational data analysis using Singdata Lakehouse's built-in DataGPT. This will achieve real-time end-to-end data ingestion, data processing, and data analysis to gain insights into customer transactions.

From an ELT perspective, Singdata Lakehouse's real-time multi-table synchronization achieves data extraction (Data Extraction) and loading (Load) based on CDC, and during this process, schema evolution is realized, meaning the synchronization content will include changes in the structure or schema of the source database. Dynamic Table implements data transformation (Data Transform) in a brand-new way.

^

:-: ![](.topwrite/assets/image_1735115515214.png)

^

Environment Preparation:

* [Docker](https://www.docker.com/products/docker-desktop/) installed on the local machine

* Tools available to connect to the PostgreSQL database

  * For example, Visual Studio Code or DBV/DBGrid, and Python code, etc.

* Familiarity with basic Python and SQL

* Familiarity with using data science Notebooks

* An existing Singdata account, or go to the [Singdata Technology](https://accounts.clickzetta.com/register) registration page and register for a free account. After registration, you can directly [log in](https://accounts.clickzetta.com/login) to the Singdata Lakehouse Web console.

## Singdata Lakehouse Environment

Overview

You will use [Singdata Lakehouse Studio](https://accounts.clickzetta.com/) (the web interface of Singdata Lakehouse) to create Singdata Lakehouse objects (virtual compute clusters, spaces/databases, schemas, database schemas, users, etc.).

### Create Objects and Load Data

1. Navigate to Development -> Tasks, click `+` to create a new workspace and worksheet task, then select SQL Worksheet

:-: ![](.topwrite/assets/image_1735115534331.png =600)

2. Workspace Name: 01\_Demo\_Real\_Time\_Financial\_Insights\_Using\_Change\_Data\_Capture\_CDC
3. Task Name: 01\_Setup Environment

:-: ![](.topwrite/assets/image_1735115562368.png =600)

2. Copy and paste the following [SQL script](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/scripts/clickzetta-lakehouse-setup.sql) to create Singdata Lakehouse objects (virtual compute clusters, database schemas), then click "Run" at the top of the worksheet

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

### Start Database Instance

Before starting this step, make sure you have installed Docker Desktop for [Mac](https://docs.docker.com/desktop/install/mac-install/), [Windows](https://docs.docker.com/desktop/install/windows-install/), or [Linux](https://docs.docker.com/desktop/install/linux/). Ensure that Docker Compose is installed on your machine. [Docker Compose.](https://docs.docker.com/compose/install/)

1. To start a PostgreSQL database using Docker, you need to create a file named docker-compose.yaml. This file will contain the configuration for the PostgreSQL database. If you have another container client, start the container and use the PostgreSQL image below.
2. Open your preferred IDE (such as VS Code), and copy and paste the following content by copying and pasting this file:

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

3. Open the terminal and navigate to the directory where the docker-compose.yaml file is located. Run the following command to start the PostgreSQL database:

```Shell
docker-compose up -d
```

### Connect to the Database

To connect to the pre-configured database using Visual Studio Code or DBV/DBGrid/PyCharm or any IDE of your choice for database connection, follow these steps using the provided credentials:

1. Open your chosen tool to connect to the PostgreSQL database

   1. For VSCode, you can use the [PostgreSQL extension](https://marketplace.visualstudio.com/items?itemName=cweijan.vscode-postgresql-client2)
   2. For PyCharm, you can use the [Database tools and SQL plugin](https://www.jetbrains.com/help/pycharm/database-tool-window.html)

2. Click the `+` symbol or similar to add a data source

3. Use these connection parameters:

   1. User: `postgres`
   2. Password: `postgres`
   3. URL: `jdbc:postgresql://localhost:5432/`

4. Test the connection and save

5. To allow Singdata Lakehouse Studio to access the Postgres database via the public network, be sure to set up public NAT mapping for the Postgres database.

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

2. Download these csv files and save them to a directory on your local computer:

   1. [customers.csv](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/postgres_csv/customers.csv)
   2. [merchants.csv](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/postgres_csv/merchants.csv)
   3. [products.csv](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/postgres_csv/products.csv)
   4. [transactions.csv](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/postgres_csv/transactions.csv)

3. Postgres Data Loading Method 1, Load via PG's Copy Command

   1. Before loading the data into the PostgreSQL database, we need to move the files from the local computer to the Docker container.
   2. Navigate to your terminal and use the following command to get the Docker container ID:
   3. ```Shell
      docker ps
      ```

4. To copy the CSV file to the container, run the following command in the terminal, replacing the file path with the actual file path, and replacing `container_id` with the actual container ID from the previous command:
   5\. \`\`\`Shell
   docker cp /Users/your\_username/Downloads/customers.csv container\_id:/tmp/customers.csv
   docker cp /Users/your\_username/Downloads/merchants.csv container\_id:/tmp/merchants.csv
   docker cp /Users/your\_username/Downloads/products.csv container\_id:/tmp/products.csv
   docker cp /Users/your\_username/Downloads/transactions.csv container\_id:/tmp/transactions.csv
   ```
   ```

5. Return to the PostgreSQL console and run the following SQL command to load the file from the container into the PostgreSQL table:

```SQL
COPY postgres.raw_cdc.customers FROM '/tmp/customers.csv' DELIMITER ',' CSV HEADER;
COPY postgres.raw_cdc.merchants FROM '/tmp/merchants.csv' DELIMITER ',' CSV HEADER;
COPY postgres.raw_cdc.products FROM '/tmp/products.csv' DELIMITER ',' CSV HEADER;
COPY postgres.raw_cdc.transactions FROM '/tmp/transactions.csv' DELIMITER ',' CSV HEADER;
```

```markdown
4. Postgres Data Loading Method 2, Loading via Python Script

Copy the following code into a Python file or Notebook and then run it. You can also directly download [this Python file](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/scripts/load-data-into-pg-by-python.py).
```

```Python
import psycopg2

# Database connection information
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
# Set search_path
cur.execute("SET search_path TO raw_cdc;")
import os
# Set CSV file directory
csv_directory = "csv/"

def load_csv_to_postgres(csv_file, table_name):
    with open(csv_file, 'r') as f:
        cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER DELIMITER ','", f)
    conn.commit()

# Iterate through all CSV files in the directory and load them into the corresponding tables
for filename in os.listdir(csv_directory):
    if filename.endswith(".csv"):
        csv_file = os.path.join(csv_directory, filename)
        table_name = os.path.splitext(filename)[0]  # Use the filename without extension as the table name
        print(f"Loading {csv_file} into table {table_name}...")
        load_csv_to_postgres(csv_file, table_name)
        print(f"Loaded {csv_file} into table {table_name} successfully!")
# Close cursor and connection
cur.close()
conn.close()
```

### 5. Next, ensure to run the `CREATE PUBLICATION` command to enable logical replication of the tables in the schema `raw_cdc`. This will allow the real-time synchronization task below to capture changes made to the tables in the PostgreSQL database:

```SQL
CREATE PUBLICATION agent_postgres_publication FOR ALL TABLES;
```

```markdown
Publication is part of PostgreSQL logical replication, which allows users to define a set of table changes (inserts, updates, deletes) that will be transmitted to one or more subscribers. Logical replication is a way to implement CDC, capturing and propagating data changes in database tables. In other words, after executing this statement, PostgreSQL will capture data changes in all tables in the database, and these changes can be received and processed by subscribers. This achieves the data change recording in CDC.

6. Finally, check if the table has been loaded correctly by running the following SQL command:
```

```SQL
SELECT * FROM postgres.raw_cdc.customers;
SELECT * FROM postgres.raw_cdc.merchants;
SELECT * FROM postgres.raw_cdc.products;
SELECT * FROM postgres.raw_cdc.transactions;
```

## Create and Start Singdata Lakehouse CDC Multi-Table Real-Time Sync Task

### Overview

You will use [Singdata Lakehouse Studio](https://accounts.clickzetta.com/) to create a multi-table real-time sync task in a no-code manner through interface operations, loading data from Postgres tables to Singdata Lakehouse tables.

### Create Postgres Data Source

Navigate to Management -> Data Source, click "New Data Source" and select Postgres to create a Postgres data source, making Postgres accessible to Singdata Lakehouse.

:-: ![](.topwrite/assets/image_1735115653296.png =600)

^

:-: ![](.topwrite/assets/image_1735115660694.png =600)

* Data Source Name: PG\_CDC\_DEMO
* Connection Parameters: Same as the connection parameters in the previous Postgres environment section.
* Please ensure to configure the correct timezone of the database to avoid data sync failure.

### Create Multi-Table Real-Time Sync Task

Navigate to Development -> Tasks, click `+` to create a new workspace and worksheet task, then select "Multi-Table Real-Time Sync".

* Select "Multi-Table Real-Time Sync":

:-: ![](.topwrite/assets/image_1735115675871.png =600)

Create a multi-table real-time sync task and store it in the same directory as the previously built environment:

* Task Name: 02\_Ingestion\_CDC
* Source Data: Select Postgres

:-: ![](.topwrite/assets/image_1735115689339.png =600)

  Select the Postgres data source created in the previous step: PG\_CDC\_DEMO. After selection, the accessible databases, Schema, and tables of the data source will be automatically displayed, and all tables will be selected (all tables need to be synced):

:-: ![](.topwrite/assets/image_1735115698983.png =624)

  Select or create a new SlotName for CDC sync. Please note that the same Slot should not be shared by two tasks to avoid data loss:

:-: ![](.topwrite/assets/image_1735115710124.png =600)

  Target Table Configuration:

  Select the existing Schema under the target data source as the storage location for the target table.

:-: ![](.topwrite/assets/image_1735115718468.png =663)

  Configure and check the table and field mapping relationships:

  Singdata Lakehouse will automatically form the mapping of tables and fields, including data type mapping. If there is no corresponding table in the selected Singdata Lakehouse namespace, the multi-table real-time sync task will automatically check and create the table when the task starts, without the need for manual pre-creation.
CDC sync requires primary keys in the source tables, and the multi-table real-time sync will automatically create corresponding [primary keys](primary-key.md) in the Lakehouse target tables.

:-: ![](.topwrite/assets/image_1735115731100.png =641)

  

Configure Sync Rules:

  Schema Evolution refers to the process of modifying and adapting the structure or schema of a database over time and as needs change in a database management system. Schema evolution typically involves changes to the structure of database tables, fields, data types, relationships, and constraints, without interrupting the operation of existing systems or causing data loss.

  In the sync rules of real-time sync tasks, you can configure automatic handling strategies for changes to source tables and fields:

* Set the behavior after deleting fields from the source table.
* Set the behavior after adding fields to the source table. Renaming fields is considered as field deletion, and the renamed fields are recognized as new fields.
* Set the behavior after adding fields to the source table.
* Set the behavior when the data source sync object is deleted. Renaming tables is considered as deletion, and the renamed tables are considered as new tables.

  Additionally, the sync rules also support setting the types of source change messages that need to be processed. Please set as needed. For example, in some scenarios, it is expected that the data on the target side will always accumulate, without processing the "delete" changes from the source side. In this configuration, simply remove the "delete" option.

:-: ![](.topwrite/assets/image_1735115747197.png =652)

### Submit and Start Multi-Table Real-Time Sync Task

* **Submit** the multi-table real-time sync task:

:-: ![](.topwrite/assets/image_1735115761930.png =600)

* **Operate and Maintain** the multi-table real-time task:

:-: ![](.topwrite/assets/image_1735115774424.png =600)

* **Start** the multi-table real-time task:

:-: ![](.topwrite/assets/image_1735115784817.png =600)

* And select "Full Data Sync":

Whether to perform a full data sync before incremental sync. Please note that this configuration can only be selected the first time the task is started after going live.
\:-: ![](.topwrite/assets/image_1735115795219.png =474)

### View Full Sync Status

In the previous "Postgres Environment" step, data was loaded into the four Postgres tables using either the Copy method or a Python script. The "Full Data Sync" selected in the previous step achieves full data synchronization before the incremental data synchronization begins.

:-: ![](.topwrite/assets/image_1735115806467.png =613)

The full sync status and incremental sync status of all 4 tables are normal, with no Failover occurring.

:-: ![](.topwrite/assets/image_1735115814661.png =789)

You can see that the full sync has been completed. After that, the incremental sync status will automatically switch to "Syncing" without manual intervention.

##

## Incremental Sync Process of Multi-Table Real-Time Sync

### Insert New Data into the Data Source

Insert data into the source table in Postgres to achieve incremental data synchronization through the already started real-time multi-table sync task, and check the sync status of the real-time multi-table sync task.

During the incremental sync process of multi-table real-time sync, the [Java Real-Time Programming Interface](java_reference/realtime-upload.md) of Lakehouse is used to write data in real-time into the primary key table of Lakehouse.

Copy the following code into the Notebook and run it, or [download it directly](https://github.com/yunqiqiliang/czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables/blob/main/scripts/pg-insert-transaction.ipynb):

* Create a database connection

```Python
import psycopg2
import random
import time
from datetime import datetime
from pytz import timezone
import uuid # Import uuid module

# Database connection information
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
# Set search_path 
cur.execute("SET search_path TO raw_cdc;")
```

* Set parameters for incremental data generation

```Python
# Set parameters
loop_interval = 0  # Loop interval (seconds)
loop_count = 1000  # Number of loops
batch_size = 100  # Number of records inserted each time
```

* Data Loading Functions

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


                # Generate new transaction ID (unique)
                v_new_transaction_id = f"TX{int(datetime.now().timestamp())}{j}"
                # Generate new transaction ID (UUID format) 
                v_new_transaction_id = str(uuid.uuid4())

                # Generate current date and time in New York timezone
                nyc_time = datetime.now(timezone('America/New_York'))
                v_transaction_date = nyc_time.date()
                v_transaction_time = nyc_time.strftime('%H:%M:%S')

                # Generate random quantity (between 1 and 7)
                v_quantity = random.randint(1, 7)

                # Get product price and calculate total price
                v_product_price = v_existing_product[3]  # Price is in the 4th column
                # if not is_number(v_product_price):
                #     continue  # Skip non-numeric records
                v_total_price = float(v_product_price) * v_quantity

                # Randomly select transaction card type
                v_transaction_card = random.choice(['American Express', 'Visa', 'Mastercard', 'Discover'])

                # Randomly select transaction category
                v_transaction_category = 'Purchase' if random.random() < 0.8 else 'Refund'

                # Insert new transaction into transactions table
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
            conn.rollback()  # Rollback current transaction
```

* Call function to insert transaction data

```Python
# Call the function to insert transaction data
insert_transactions(loop_interval, loop_count, batch_size)
```

* Closing cursors and connections

```Python
# Close the cursor and connection
cur.close()
conn.close()
```

### View Incremental Sync Status

:-: ![](.topwrite/assets/image_1735115833155.png =600)

## Process Multiple Tables' Real-Time Synced Data via Dynamic Table

Overview

You will use [Singdata Lakehouse Studio](https://accounts.clickzetta.com/) to create a Dynamic Table, which will process data in real-time that is synced from Postgres tables to Singdata Lakehouse via multiple tables.

### Create Dynamic Table

Navigate to Development -> Tasks, and click "+ Select Dynamic Table".

:-: ![](.topwrite/assets/image_1735115842636.png =600)

* Task Name: 03\_customer\_purchase\_summary
* Schema Selection: real\_time\_financial\_insights\_using\_change\_data\_capture\_cdc
* Enter Table Name: customer\_purchase\_summary
* Enter the following in the SQL code:

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

This SQL query specifically functions to retrieve detailed transaction records from the `transactions` table by joining multiple tables and obtaining related information from the `customers`, `products`, and `merchants` tables. Here is a detailed explanation:

* **Extract transaction records from the** `` **table**:

  * `t.transaction_id`: Retrieve the unique identifier for each transaction.
  * `t.customer_id`: Retrieve the identifier of the customer associated with the transaction.
  * `t.product_id`: Retrieve the identifier of the product involved in the transaction.
  * `t.merchant_id`: Retrieve the identifier of the merchant providing the product or service.
  * `t.transaction_date` and `t.transaction_time`: Retrieve the date and time when the transaction occurred.
  * `t.quantity`: Retrieve the quantity of products purchased in the transaction.
  * `t.transaction_card`: Retrieve the type of card used for the transaction (e.g., credit card or debit card).
  * `t.transaction_category`: Retrieve the category of the transaction (e.g., purchase or refund).

* **Extract customer information from the** `` **table**:

  * Use `JOIN customers c ON t.customer_id = c.customer_id` to join the `transactions` table with the `customers` table and retrieve customer information associated with the transaction.
  * `c.age AS customer_age`: Retrieve the customer's age and name it `customer_age`.

* **Extract product information from the** `` **table**:

  * Use `JOIN products p ON t.product_id = p.product_id` to join the `transactions` table with the `products` table and retrieve product information involved in the transaction.
  * `p.product_name`: Retrieve the name of the product.
  * `p.product_category`: Retrieve the category of the product.
  * `t.quantity * p.price AS total_price`: Calculate the total price of each transaction (quantity multiplied by product unit price) and name it `total_price`.

* **Extract merchant information from the** `` **table**:

  * Use `JOIN merchants m ON t.merchant_id = m.merchant_id AND m.merchant_category = p.product_category` to join the `transactions` table with the `merchants` table and ensure the merchant's category matches the product category.
  * `m.merchant_name`: Retrieve the name of the merchant.
  * `m.merchant_category`: Retrieve the category of the merchant.

Through these joins and data extractions, this query generates a detailed result set where each record contains detailed transaction information, customer information, product information, and merchant information, and calculates the total price of each transaction, thus providing a more comprehensive and in-depth transaction analysis.

Dynamic tables will directly refresh data periodically according to the life syntax, achieving the purpose of dynamic data changes.

:-: ![](.topwrite/assets/image_1735115966112.png =600)

* Validate and save, select "Complete SQL Development":

:-: ![](.topwrite/assets/image_1735115978198.png =600)

* Select the virtual cluster for dynamic table refresh before submission

  Select the virtual compute cluster "CDC\_DS\_VS" created in the "Singdata Lakehouse Environment" step.

* Select "Auto Refresh" before submission

:-: ![](.topwrite/assets/image_1735115986827.png =379)

### Submit and complete the development of the dynamic table

:-: ![](.topwrite/assets/image_1735116000834.png =691)

### Dynamic Table Operations

After successful submission, you can go to the Operations Center to view the task details and refresh history of the current table, and support starting or stopping the current table.

* Task details:

:-: ![](.topwrite/assets/image_1735116009194.png =600)

* Refresh history:

  You can see the number of rows added and deleted in each refresh cycle, thus understanding how the data in the dynamic table "dynamically" changes.

:-: ![](.topwrite/assets/image_1735116016064.png =781)

##

## Conduct Q\&A Data Analysis through Singdata DataGPT

Overview
You will use Singdata Lakehouse DataGPT to synchronize tables from Postgres to Singdata Lakehouse in real-time and analyze them through Q\&A.

### Access Singdata DataGPT

Navigate to the account homepage -> DataGPT to enter Singdata DataGPT.

:-: ![](.topwrite/assets/image_1735116025067.png =600)

### Create a New Analysis Domain

Build data analysis based on multiple data tables, metrics, answer builders, knowledge, and documents, and support adding users for permission isolation.

:-: ![](.topwrite/assets/image_1735116034928.png =600)

* Analysis Domain Name: CDC Transaction Data Analysis.
* After successfully creating, select "Add Data," then choose "Add Table" -> "Import Table" to add the dynamic table created in the previous section to DataGPT.

:-: ![](.topwrite/assets/image_1735116042469.png =600)

^

:-: ![](.topwrite/assets/image_1735116049605.png =600)

* Click the icon next to "Description," and the system will use a large model to add appropriate descriptions for each field, facilitating alignment with Chinese semantics.

:-: ![](.topwrite/assets/image_1735116058010.png =600)

* Adopt the metrics automatically generated by the large model, complete and start the analysis:

:-: ![](.topwrite/assets/image_1735116067960.png =600)

Enter the following analysis domain page to start data exploration and conversational analysis.

:-: ![](.topwrite/assets/image_1735116077565.png =641)

### Data Exploration

Navigate to the analysis domain (select "CDC Transaction Data Analysis") -> Explore to explore data based on the automatically created metrics.

:-: ![](.topwrite/assets/image_1735116085712.png =638)

### Conversational Data Analysis

Enter the question "Number of transactions for Mastercard, distributed by merchant category," and get the following analysis result:

:-: ![](.topwrite/assets/image_1735116092619.png =630)

^

It understands that Mastercard needs to match the transaction card (transaction\_card = Mastercard), thanks to DataGPT's automatic indexing of the transaction\_card field values.

The number of transactions is an automatically created metric, achieving metric caliber alignment.

The merchant category corresponds to the field merchant\_category, benefiting from the automatic generation of field descriptions, quickly achieving semantic alignment.

Enter the question: What is the total number of transactions for 'Disinfectant Wipes' products purchased through each channel? Get the following analysis result:

:-: ![](.topwrite/assets/image_1735279174589.png =631)

In the Lakehouse table, the product 'Disinfectant Wipes' is stored in English as 'Disinfectant Wipes.' When the user asks about 'disinfectant wipes,' DataGPT will automatically translate it to achieve precise matching, without requiring the user to input 'Disinfectant Wipes,' fully leveraging the advantages of the large model, making data analysis simpler.

## Cleanup

After completing this quick start, you can clean up the objects created in Singdata Lakehouse.

## Summary

Congratulations! You have completed this quick start!

### Key Learnings

After completing this quick start, you now have a deep understanding of:

* How to use Singdata Lakehouse multi-table real-time synchronization to sync PostgreSQL data to Singdata Lakehouse tables, corresponding to the data extraction (E) and loading (L) in the ELT process.
* Using dynamic tables to process data, corresponding to the data transformation (T) in the ELT process.
* Visualizing and analyzing data conversationally through Singdata Lakehouse's built-in DataGPT.

### Resources

[Singdata Lakehouse Multi-table Real-time Synchronization](https://www.yunqi.tech/documents/realtime_sync)

[Singdata Lakehouse Dynamic Table](https://www.yunqi.tech/documents/dynamictable)

Singdata Lakehouse Q\&A Data Analysis DataGPT

[Singdata Lakehouse Studio: Web Development and Management Tools](https://www.yunqi.tech/documents/Studio)

[Primary Key Definition](primary-key.md)

[Java Real-time Programming Interface](java_reference/realtime-upload.md)

[Using Java SDK to Read Kafka Data for Real-time Upload](use-java-sdk-realtime-uploaddata.md)
