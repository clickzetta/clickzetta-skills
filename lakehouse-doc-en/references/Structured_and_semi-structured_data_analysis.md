# Analyzing Structured and Semi-Structured Data in VOLUME

### Syntax:

```SQL
SELECT { <column_name>,... | * } 
FROM VOLUME <volume_name>(
    <column_name> <column_type>,
    ...
) USING CSV|PARQUET|ORC 
OPTIONS(
  FileFormatParams
) 
FILES|SUBDIRECTORY|REGEXP <pattern>;
```

### Parameter Description:

- **column_name**: The name of the column contained in the file. Currently, it does not support automatic recognition of the schema in the file, and must be filled in manually. Required field.
- **column_type**: The type of the column in the file, which must match the predefined column type in the file. Required field.
- **FileFormatParams**:
  - CSV format:
    - sep: Column separator, default is ",", supports up to 1 character in length, e.g., `'sep'=','`.
    - compression: Configure file compression format. Supported compression formats include gzip/zstd/zlib. For example: `'compression'='gzip'`.
    - lineSep: Line separator, default is "\n", supports up to 2 characters in length, e.g., `'lineSep'='$'`.
    - quote: Set a single character used to escape quote values. Default is double quote "", e.g., `'quote'='"'`.
    - header: Whether to parse the header, default is false. Boolean type, e.g., `'header'='true'`.
    - timeZone: Configure the time zone, no default value. Used to specify the time zone of the time format in the file. For example: `'timeZone' = 'Asia/Shanghai'`.
    - escape: Used to escape quotes in quoted values, default is "\", e.g., `'escape'='\'`.
  - Parquet, ORC, BSON formats:
    - None

- **FILES**: Specify files. For example: `files('part-00002.snappy.parquet','part-00003.snappy.parquet')`.
- **SUBDIRECTORY**: Specify sub-path. For example: `subdirectory 'month=02'`.
- **REGEXP** <pattern>: Regular expression matching. For example: `regexp 'part-.*.parquet'` matches files with parquet suffix starting with part-. Another example: `regexp 'NYC/YellowTaxiTripRecords/parquet/yellow_tripdata_2022.*.parquet'` matches all parquet suffix files starting with *yellow_tripdata_2022* in the sub-path *NYC/YellowTaxiTripRecords/parquet*.

## Examples:

### Query CSV format files:

#### Data Preparation:

Create a volume object: `hz_csv_volume`, bind to Alibaba Cloud OSS path: `oss://hz-datalake/csv_files/`, the file structure under this path is the CSV files of the Brazilian e-commerce dataset:

```
-------------oss://hz-datalake/csv_files/ Object storage directory structure ------------------
-- brazil-ecommerce/olist_customers_dataset.csv
-- brazil-ecommerce/olist_geolocation_dataset.csv
...
```

#### Query Examples:

```
-- Query file: olist_customers_dataset.csv
SELECT * FROM VOLUME hz_csv_volume (
  customer_id STRING,
  customer_unique_id STRING,
  customer_zip_code_prefix INT,
  customer_city STRING,
  customer_state STRING
) USING CSV 
OPTIONS(
  'header'='true',
  'sep'=','
) FILES('brazil-ecommerce/olist_customers_dataset.csv');

-- Query file olist_geolocation_dataset.csv
SELECT * FROM VOLUME hz_csv_volume (
  geolocation_zip_code_prefix INT,
  geolocation_lat DECIMAL(10,8),
  geolocation_lng DECIMAL(11,8),
  geolocation_city STRING,
  geolocation_state STRING
)USING csv 
 OPTIONS(
    'header'='true',
    'sep'=','
 ) files('brazil-ecommerce/olist_geolocation_dataset.csv');
```

#### Import Data into Lakehouse:

You can import data into the cloud appliance Lakehouse internal table through the create table as select method:

```
create Table olist_customers_dataset as
select * from volume hz_csv_volume (
  customer_id STRING,
  customer_unique_id STRING,
  customer_zip_code_prefix INT,
  customer_city STRING,
  customer_state STRING
)using csv 
 options(
    'header'='true',
    'sep'=','
 ) files('brazil-ecommerce/olist_customers_dataset.csv');
```

### Query Parquet format files:

#### Data Preparation:

Create a volume object: `hz_parquet_volume`, bind to Alibaba Cloud OSS path: `oss://hz-datalake/yellowtrip-partitioned/`, the file structure under this path is the New York taxi dataset and some other miscellaneous parquet format files, the purpose is to show how to use `FILES | SUBDIRECTORY | REGEXP` these file matching options to query the target data files. The organization of the files is:

```
--------- oss://hz-datalake/yellowtrip-partitioned/ Object storage directory structure ----
-- month=01/yellow_tripdata_2023-01.parquet
...
```

#### Query Examples:

Query 1: Query parquet files of month partition 1-5

```
select * from volume hz_parquet_volume(
    ...
) USING parquet regexp 'month=0[1-5].*.parquet' ;
```

Query 2: Query files with parquet suffix starting with part-, including complex types:

```
SELECT * FROM volume hz_parquet_volume( 
    ...
) USING parquet regexp 'part-.*.parquet';
```

Query 3: Use files parameter to include specific files, complex type query:

```
SELECT id, array_col[0],map_col['Key2'],struct_col.field2 FROM volume hz_parquet_volume( 
    ...
) USING parquet files(
    'part-00002-d87581e8-afdb-49ba-abd4-d8f9f5a37a6e-c000.snappy.parquet',
    'part-00005-d87581e8-afdb-49ba-abd4-d8f9f5a37a6e-c000.snappy.parquet'
);
```

### Query ORC format files:

#### Data Preparation:

Create a volume object: `hz_orc_volume`, bind to Alibaba Cloud OSS path: `oss://hz-datalake/orcfiles/`, the file structure under this path is:

```
--------- oss://hz-datalake/orcfiles/ Object storage directory structure ----------
-- t_search_log/dt=20230401/hours=06/part-00000-7342ed8826c5.c000
...
```

#### Query Example:

```
SELECT * FROM volume hz_orc_volume (
    ...
) USING orc subdirectory 't_search_log/dt=20230401/hours=06/'
limit 10;
```

### Query BSON format files:

```SQL
-- Query bson files
SELECT * FROM VOLUME my_external_vol
(name string, age bigint, city string, interests array<string>)
using bson
FILES( 'data.bson');
```
