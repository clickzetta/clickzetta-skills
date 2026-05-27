# Building an Analytics-Oriented Modern Data Stack with Singdata Lakehouse

This document describes how to build an analytics-oriented Modern Data Stack based on Singdata Lakehouse, Metabase, and MindsDB.

## Solution Architecture

Features of the Modern Data Stack solution based on Singdata Lakehouse:

* Evolve from AWS data warehouse to data lake, achieving optimization and improvement of lake-house unification through Singdata Lakehouse, significantly reducing data storage, compute, and operations costs.
* Unlimited Storage and Efficient Migration: The full-link data pipeline uses cloud object storage to achieve a compute-storage separation architecture, avoiding bandwidth and storage capacity bottlenecks of server nodes in traditional solutions.
* Singdata Lakehouse + Metabase: Achieve ultra-simple BI data analysis, requiring just two mouse clicks to complete visual data exploration and analysis, greatly lowering the barrier for business personnel to analyze data and being very user-friendly for business users.
* Singdata Lakehouse + MindsDB: Achieve 100% SQL-based AI and LLM enhanced analysis. Without needing to master other complex languages, data engineers and BI analysts can implement AI and LLM enhanced analysis based on SQL.
* Lower the requirements for technical personnel across the full data stack (cloud infrastructure, data lake, data warehouse, BI, AI), reducing enterprise hiring thresholds and improving talent availability.

This solution emphasizes simplicity and ease of use, aiming to help enterprises shift their focus from data infrastructure to data analysis, achieving modernization of data analysis.

![](.topwrite/assets/image_1734577522644.png)

The above diagram illustrates the architecture for migrating to and building a Modern Data Stack based on Singdata Lakehouse, summarized as follows:

* Use the Redshift UNLOAD command to unload data to Parquet files in an S3 bucket.
* Through Singdata Lakehouse's `SELECT * FROM VOLUME` statement, directly load data from Parquet files in the AWS S3 bucket into Singdata Lakehouse tables, achieving rapid data ingestion (in this example, loading a table with over 20 million rows into the Lakehouse took only 30 seconds).
* BI Application: Explore and analyze data through Metabase (from table to dashboard in just two mouse clicks -- yes, just two).
* AI Application: Predict house prices through MindsDB (100% implemented using SQL for model prediction).

## Solution Components

* AWS:

  * Redshift
  * S3

* Singdata

  * Singdata Lakehouse, a multi-cloud and unified data platform. Adopts a SaaS fully managed service model, providing enterprises with an ultra-simple data architecture.
  * Singdata Lakehouse Driver for Metabase
  * Singdata Lakehouse Connector for MindsDB

* Data Analysis

  * Metabase with Lakehouse Driver on Docker: Metabase is a comprehensive BI platform, but its design philosophy is very different from Superset. Metabase places great emphasis on the user experience for business personnel (such as product managers, marketing operations staff), allowing them to freely explore data and answer their own questions.
  * MindsDB with Lakehouse Connector on Docker: MindsDB can model directly in Singdata Lakehouse, eliminating professional steps such as data processing and model building. Data analysts and BI analysts can use it out of the box without needing to be familiar with data engineering and modeling knowledge, lowering the modeling barrier so that everyone can be a data analyst and everyone can apply algorithms.
  * Zeppelin with Lakehouse JDBC Interpreter on Docker
  * Zeppelin with MySQL JDBC Interpreter on Docker (connecting to MindsDB's MySQL interface)

## Why Choose Singdata Lakehouse?

* **Fully Managed**: Singdata Lakehouse provides a fully managed, cloud-based Lakehouse service that is easy to use and scale. This means you don't have to worry about managing and maintaining your own hardware and infrastructure, avoiding time-consuming and costly investments, achieving peace of mind.
* **Cost Savings**: Compared to Redshift, Singdata Lakehouse's total cost of ownership (TCO) is typically lower because it charges based on usage without requiring upfront commitments. Singdata Lakehouse's highly flexible pricing model means you only pay for the resources you actually use, without being locked into a fixed cost model.
* **Scalability**: Singdata Lakehouse is designed to handle large amounts of data and can scale up or down as needed, making it a great choice for enterprises with fluctuating compute loads. Singdata Lakehouse stores data on cloud object storage services, achieving "unlimited scaling" in data scale.
* **Performance**: Singdata Lakehouse adopts a Single Engine All Data architecture, achieving compute-storage separation, enabling it to process queries faster than Redshift.
* **Ease of Use**: Singdata Lakehouse provides a unified data integration, development, operations, and governance platform, making development and management much easier without complex solution integration.
* **Data Source Support**: Singdata Lakehouse supports a variety of data sources and formats, including structured and semi-structured data. In most cases, BI and AI applications can be developed using only SQL.
* **Data Integration**: Singdata Lakehouse's built-in data integration features support a wide range of data sources, making data loading and preparation easier for analysis.
  Overall, migrating to Singdata Lakehouse can help you save time and money, and enable you to process and analyze data more easily and effectively.

## Implementation Steps

### Data Extraction (E)

#### Unload House Price Sales Data from Redshift to S3

Redshift UNLOAD command: Use Amazon S3 server-side encryption (SSE-S3) to unload query results to one or more text, JSON, or Apache Parquet files on Amazon S3.

```SQL
UNLOAD ('select-statement')
TO 's3://object-path/name-prefix'
authorization
[ option, ...] 

where authorization is
IAM_ROLE { default | 'arn:aws:iam::<AWS account-id-1>:role/<role-name>[,arn:aws:iam::<AWS account-id-2>:role/<role-name>][,...]' }
            
where option is
| [ FORMAT [ AS ] ] CSV | PARQUET | JSON
| PARTITION BY ( column_name [, ... ] ) [ INCLUDE ]
| MANIFEST [ VERBOSE ]
| HEADER
| DELIMITER [ AS ] 'delimiter-char'
| FIXEDWIDTH [ AS ] 'fixedwidth-spec'
| ENCRYPTED [ AUTO ]
| BZIP2
| GZIP
| ZSTD
| ADDQUOTES
| NULL [ AS ] 'null-string'
| ESCAPE
| ALLOWOVERWRITE
| CLEANPATH
| PARALLEL [ { ON | TRUE } | { OFF | FALSE } ]
| MAXFILESIZE [AS] max-size [ MB | GB ]
| ROWGROUPSIZE [AS] size [ MB | GB ]
| REGION [AS] 'aws-region' }
| EXTENSION 'extension-name'
```

#### Data Lake Data Exploration: Explore Parquet Data on AWS S3 through Singdata Lakehouse

View the total number of rows (requires creating Singdata Lakehouse's `STORAGE CONNECTION` and `EXTERNAL VOLUME` in advance):

![](.topwrite/assets/image_1718933981338.png)

Preview data

```SQL
select 
        *
    from volume hz_qiliang_csv_volume(
    price  int,
    date  int,
    postcode1  binary,
    postcode2  binary,
    type  binary,
    is_new  int,
    duration  binary,
    addr1  binary,
    addr2  binary,
    street  binary,
    locality  binary,
    town  binary,
    district  binary,
    county  binary
) USING parquet
regexp '/house_prices_iceberg/data/000.*.parquet'
limit 10;
```

Execute the above query in Singdata Lakehouse, with the following results:

![](.topwrite/assets/image_1718933998640.png)

### Data Loading: Load (L) Data from S3 into Singdata Lakehouse and Perform Data Transformation (T)

```SQL
use schema public_datasets;
create table if not exists house_prices_paid_from_oss_parquet as
select price,
        cast(date*24*3600 as timestamp) as date,
        cast(postcode1 as string) as postcode1,
        cast(postcode2 as string) as postcode2,
        cast(type as string) as type,
        is_new,
        cast(duration as string) as duration,
        cast(addr1 as string) as addr1,
        cast(addr2 as string) as addr2,
        cast(street as string) as street,
        cast(locality as string) as locality,
        cast(town as string) as town,
        cast(district as string) as district,
        cast(county as string) as county
    from volume public.hz_qiliang_csv_volume(
    price  int,
    date  int,
    postcode1  binary,
    postcode2  binary,
    type  binary,
    is_new  int,
    duration  binary,
    addr1  binary,
    addr2  binary,
    street  binary,
    locality  binary,
    town  binary,
    district  binary,
    county  binary
) USING parquet
regexp '/house_prices_iceberg/data/000.*.parquet'
order by date,county,price;
```

Verify the number of rows loaded:

![](.topwrite/assets/image_1718934039921.png)

Explore data in the Lakehouse using SQL:

![](.topwrite/assets/image_1718934046872.png)

### BI Application: Explore and Analyze Data in Singdata Lakehouse through Metabase

#### Create a Database Connection to Singdata Lakehouse in Metabase

![](.topwrite/assets/image_1718934063007.png)

#### Explore and Analyze Data through Metabase (Just Two Clicks -- Yes, Just Two!)

##### Select Database and Table:

![](.topwrite/assets/image_1718934072740.png)

![](.topwrite/assets/image_1718934080762.png)

##### Browse and Analyze Data through Metabase

![](.topwrite/assets/image_1718934087952.png)

#### Explore and Analyze Data through Metabase:

![](.topwrite/assets/image_1718934094905.png)

### AI Application: Predict House Prices through MindsDB (Only SQL)

This section's data flow: Zeppelin -> MindsDB -> Singdata Lakehouse.

* Zeppelin creates a new Interpreter via MySQL JDBC Driver to connect to MindsDB
* MindsDB connects to Singdata Lakehouse via clickzetta handler (based on Python SQLAlchemy)

### Build Model Training Data in Singdata Lakehouse

```SQL
drop table if exists house_prices_paid_grouped_by_features;
create table if not exists house_prices_paid_grouped_by_features as 
SELECT
  postcode1,
  postcode2,
  TYPE,
  is_new,
  duration,
  street,
  town,
  district,
  county,
  round(max(price)) as max_price,
  round(min(price)) as min_price,
  round(avg(price)) as avg_price,
  count(*) as paid_times,
FROM
  house_prices_paid_from_oss_parquet
WHERE  postcode1 !='' and  postcode2 !=''
GROUP BY 1,2,3,4,5,6,7,8,9
ORDER BY 9,1,2,3,4,5,6,7,8
LIMIT 10000;
```

### Create Zeppelin Interpreter, Connect to MindsDB via MySQL JDBC

![](.topwrite/assets/image_1718934120805.png)

#### Create a New Notebook in Zeppelin

MindsDB connects to Singdata Lakehouse, using Singdata Lakehouse as a data source

![](.topwrite/assets/image_1718934127523.png)

```SQL
-- Connect MindsDB to Singdata Lakehouse
CREATE DATABASE if not exists clickzetta_uat_public_datasets    --- display name for database.
WITH ENGINE = 'clickzetta',                                     --- name of the mindsdb handler
PARAMETERS = {
    "service": "<region_id>.api.clickzetta.com",                        --- Singdata Lakehouse service address.
    "workspace": "********",                                       --- Singdata workspace.
    "instance": "********",                                     --- account instance id.
    "vcluster": "default",                                      --- vcluster
    "username": "********",                                      --- your username.
    "password": "********",                                    --- Your password.
    "schema": "public_datasets"                                 --- common schema PUBLIC.
};
```

### Create Model

Create a prediction model to predict `paid_times`, i.e., the number of times a house has been sold.

![](.topwrite/assets/image_1718934140448.png)

```SQL
-- Create prediction model
CREATE MODEL IF NOT EXISTS
  clickzetta.uk_house_prices_grouped_by_features_model_avg_price
FROM clickzetta_uat_public_datasets  (SELECT * FROM house_prices_paid_grouped_by_features)
PREDICT avg_price;
-- Check model status
DESCRIBE clickzetta.uk_house_prices_grouped_by_features_model_avg_price;
```

#### House Price Prediction

![](.topwrite/assets/image_1718934147927.png)

```SQL
-- MAKE A PREDICTION
SELECT avg_price, 
       avg_price_explain 
FROM clickzetta.uk_house_prices_grouped_by_features_model_avg_price
WHERE postcode1 = 'BS32'
AND postcode2= '9DF'
AND type= 'terraced'
AND is_new =1
AND duration= 'freehold'
AND street= 'FERNDENE'
AND town= 'BRISTOL'
AND district= 'NORTHAVON'
AND county= 'AVON';
```

Prediction result:

```SQL
avg_price        avg_price_explain
1306        {"predicted_value": 1306, "confidence": 0.97, "anomaly": null, "truth": null, "confidence_lower_bound": 0, "confidence_upper_bound": 7654}
```

#### Batch House Price Prediction

![](.topwrite/assets/image_1718934160811.png)

```SQL
-- Bulk predictions by joining a table with your model:
SELECT t.*, m.avg_price as predicted_avg_price,m.avg_price_explain
FROM clickzetta_uat_public_datasets.house_prices_paid_grouped_by_features as t 
JOIN clickzetta.uk_house_prices_grouped_by_features_model_avg_price as m
LIMIT 100;
```

## Appendix

### Metabase, MindsDB, Zeppelin Environment Installation and Deployment Guide

* [Metabase](metabase.md) with Lakehouse Driver on Docker
* [MindsDB](mindsdb.md) with Lakehouse Connector on Docker
* [Zeppelin](eco_integration/Zeppelin.md) with Lakehouse JDBC Driver

### Preview Parquet File Schema and Data via Python Code, and Generate SQL Code for Singdata Lakehouse

```Python
import os
import pyarrow.parquet as pq

def print_parquet_file_head(file_path, num_rows=10):
    # Open the Parquet file
    parquet_file = pq.ParquetFile(file_path)
    
    # Read the first few rows of the Parquet file into a pandas DataFrame
    table = parquet_file.read_row_group(0, columns=None, use_threads=True)
    df = table.to_pandas()

    # Truncate the DataFrame to the desired number of rows
    if len(df) > num_rows:
        df = df.head(num_rows)

    # Print DataFrame with headers
    print(df)

def print_parquet_schema(file_path):
    # Open the Parquet file
    parquet_file = pq.ParquetFile(file_path)
    
    # Get schema information and build SQL fragment
    schema = parquet_file.schema.to_arrow_schema()
    sql_parts = []
    for field in schema:
        field_name = field.name
        field_type = str(field.type)
        sql_parts.append(f"    {field_name}  {field_type}")

    # Combine the list of fields into an SQL string
    sql_fields = ",\n".join(sql_parts)
    file_name = os.path.basename(file_path)

    # Print the final SQL statement format
    print(f"""-- Schema for {file_name}
select * from volume hz_qiliang_csv_volume(
{sql_fields}
) USING parquet
files('/amazon_reviews/{file_name}');
""")

# Update the directory path as needed
local_directory = "/Users/liangmo/Documents/yqgithub/qiliang_py"

# List all relevant Parquet files in the given directory
parquet_files = [f for f in os.listdir(local_directory) if f.endswith('.parquet') and f.startswith('000')]

# Print the schema and head for each Parquet file
for file_name in parquet_files:
    file_path = os.path.join(local_directory, file_name)
    try:
        print_parquet_schema(file_path)
        print_parquet_file_head(file_path)  # Function call to print the top rows
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
```

Sample input:

![](.topwrite/assets/image_1718934180299.png)
