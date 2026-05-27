# Analysis of Structured and Semi-Structured Data in VOLUME

### Syntax:

```
SELECT { <column_name>,... | * } 
FROM VOLUME <volume_name>(
    <column_name> <column_type>,
    ...

) USING CSV|PARQUET|ORC|BSON
OPTIONS(
  FileFormatParams
) 
FILES|SUBDIRECTORY|REGEXP <pattern>;
```

### Parameter Description:

**column\_name** and **column\_type**: Optional, Singdata supports automatic file schema recognition. It is recommended not to fill in, as the column names and types in the specified file need to match the predefined column types in the file.

* Automatic file schema recognition for CSV files will automatically generate fields, with field numbers starting from f0. Currently, the automatically recognized types are int, double, string, and bool.
* For Parquet and ORC formats, the field names and types stored in the file will be automatically recognized. If the number of columns in the specified file is inconsistent, Singdata will attempt to merge them, and if it cannot merge, an error will be reported.

**FileFormatParams**:

CSV format:

* sep: Column separator, default is ",". Supports a maximum length of 1 character, for example: `'sep'=','`
* compression: Configures the file compression format. Supported compression formats are: gzip/zstd/zlib. For example: `'compression'='gzip'`
* lineSep: Line separator, default value is "\n". Supports a maximum length of 2 characters, for example: `'lineSep'='$'`
* quote: Sets a single character used to escape quote values. The default value is a double quote `"`, for example: `'quote'='"'`
* header: Whether to parse the header, default is false. Boolean type, for example: `'header'='true'`
* timeZone: Configures the time zone, no default value. Used to specify the time zone for the time format in the file. For example: `'timeZone' = 'Asia/Shanghai'`
* escape: Used to escape quotes within quoted values, default value is `\`, for example: `'escape'='\'`

Parquet, ORC, BSON formats:

* None

**FILES**: Specify files. For example: `files('part-00002.snappy.parquet','part-00003.snappy.parquet')`

**SUBDIRECTORY**: Specify subdirectory. For example: `subdirectory 'month=02'`

**REGEXP** \<pattern>: Supports using regular expressions to match files. Note that the target of the regular expression match is the **complete object storage path** of the file (e.g., 's3://cz-udf-user/volume-data/1234321.csv.gz'), not the relative path of the file in the Volume object.

![](.topwrite/assets/20250124-160418.jpeg)

**Matching rules**:

* `.` - Matches any single character except newline
* `*` - Matches the preceding element zero or more times, often used with `.`. For example, `.*` combination means matching any character any number of times
* `+` - Matches the preceding element one or more times, often used with `.`. For example, `.+` means matching any character one or more times
* `?` - Matches the preceding element zero or one time
* `[abc]`: Matches any one of the characters a, b, or c
* `[^abc]`: Matches any character except a, b, or c
* `[a-z]`: Matches lowercase letters a to z
* `[A-Z]`: Matches uppercase letters A to Z
* `[0-9]`: Matches digits 0 to 9

**For example**:

1. `REGEXP '.*.parquet'` matches files with the suffix `parquet`
2. `REGEXP '.*yellow_tripdata_202[0-4]-0[23].parquet'` matches files containing `yellow_tripdata_`, with the year from `2020` to `2024`, the month being `02` or `03`, and ending with `.parquet`

^

## Example:

### Query CSV format file:

#### Data Preparation:

Create a volume object: `hz_csv_volume`, bind to Alibaba Cloud OSS path: `oss://hz-datalake/csv_files/`, the file structure under this path is the CSV files of the Brazilian e-commerce dataset:

```
-------------oss://hz-datalake/csv_files/ Object Storage Directory Structure ------------------
-- brazil-ecommerce/olist_customers_dataset.csv
-- brazil-ecommerce/olist_geolocation_dataset.csv
-- brazil-ecommerce/olist_order_items_dataset.csv
-- brazil-ecommerce/olist_order_payments_dataset.csv
-- brazil-ecommerce/olist_order_reviews_dataset.csv
-- brazil-ecommerce/olist_orders_dataset.csv
-- brazil-ecommerce/olist_products_dataset.csv
-- brazil-ecommerce/olist_sellers_dataset.csv
-- brazil-ecommerce/product_category_name_translation.csv
```

#### Query Example:

```
-- Query file: olist_customers_dataset.csv
SELECT * FROM VOLUME hz_csv_volume 
USING CSV 
OPTIONS(
  'header'='true',
  'sep'=','
) 
FILES('brazil-ecommerce/olist_customers_dataset.csv');

-- Query file: olist_geolocation_dataset.csv
SELECT * FROM VOLUME hz_csv_volume USING csv 
OPTIONS(
    'header'='true',
    'sep'=','
 ) 
FILES('brazil-ecommerce/olist_geolocation_dataset.csv');
```

#### Data Import into Lakehouse:

You can import data into Singdata Lakehouse internal tables using the create table as select method:

```
CREATE TABLE olist_customers_dataset as
SELECT * FROM VOLUME hz_csv_volume
USING CSV
OPTIONS(
    'header'='true',
    'sep'=','
 ) 
FILES('brazil-ecommerce/olist_customers_dataset.csv');
```

### Query Parquet Format Files:

#### Data Preparation:

Create a volume object: `hz_parquet_volume`, bind the Alibaba Cloud OSS path: `oss://hz-datalake/yellowtrip-partitioned/`. The file structure under this path includes the New York taxi dataset and some other scattered Parquet format files. The purpose is to demonstrate how to use the `FILES | SUBDIRECTORY | REGEXP` options to query the target data files. The organization of the files is as follows:

```
--------- oss://hz-datalake/yellowtrip-partitioned/ Object Storage Directory Structure ----
-- month=01/yellow_tripdata_2023-01.parquet
-- month=02/yellow_tripdata_2023-02.parquet
-- month=03/yellow_tripdata_2023-03.parquet
-- month=04/yellow_tripdata_2023-04.parquet
-- month=05/yellow_tripdata_2023-05.parquet
-- part-00000-d87581e8-afdb-49ba-abd4-d8f9f5a37a6e-c000.snappy.parquet
-- part-00002-d87581e8-afdb-49ba-abd4-d8f9f5a37a6e-c000.snappy.parquet
-- part-00005-d87581e8-afdb-49ba-abd4-d8f9f5a37a6e-c000.snappy.parquet
-- part-00007-d87581e8-afdb-49ba-abd4-d8f9f5a37a6e-c000.snappy.parquet
```

#### Query Example:

Query 1: Query the parquet files of month partitions 1-5

```
SELECT * FROM VOLUME hz_parquet_volume 
USING parquet 
REGEXP '.*month=0[1-5].*.parquet' ;
```

Query 2: Query files with the parquet suffix starting with part-, which contain complex types:

```
SELECT * FROM VOLUME hz_parquet_volume 
USING parquet 
REGEXP '.*part-.*.parquet';
```

Query 3: Use the files parameter to include specific files, complex type query:

```
SELECT id, array_col[0],map_col['Key2'],struct_col.field2, FROM volume hz_parquet_volume( 
    id INT,
    string_col STRING,
    int_col INT,
    float_col FLOAT,
    boolean_col BOOLEAN,
    date_col STRING,
    timestamp_col STRING,
    array_col ARRAY<STRING>,
    struct_col STRUCT<field1: STRING, field2: INT>,
    map_col MAP<STRING, INT>
  ) 
USING parquet 
FILES(
    'part-00002-d87581e8-afdb-49ba-abd4-d8f9f5a37a6e-c000.snappy.parquet',
    'part-00005-d87581e8-afdb-49ba-abd4-d8f9f5a37a6e-c000.snappy.parquet'
);
```

### Query ORC Format Files:

#### Data Preparation:

Create a volume object: `hz_orc_volume`, bind the Alibaba Cloud OSS path: `oss://hz-datalake/orcfiles/`, the file structure under this path is:

```
--------- oss://hz-datalake/orcfiles/ ----------
-- t_search_log/dt=20230401/hours=06/part-00000-7342ed8826c5.c000
-- t_search_log/dt=20230401/hours=07/part-00002-7342ed8826c5.c000
```

#### Query Example:

```
SELECT * FROM VOLUME hz_orc_volume (
    dpt_city_code STRING,
    dpt_city_name STRING,
    month_year STRING
  ) 
USING orc 
SUBDIRECTORY 't_search_log/dt=20230401/hours=06/'
limit 10;
```

### Query BSON Format File:

```SQL
--Query bson files
SELECT * FROM VOLUME my_external_vol (
    name string, 
    age bigint, 
    city string, 
    interests array<string>
)
USING bson
FILES( 'data.bson');
```

^
