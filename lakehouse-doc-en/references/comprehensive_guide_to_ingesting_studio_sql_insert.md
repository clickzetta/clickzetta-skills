# Complete Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Importing Data via SQL INSERT in Singdata Lakehouse Studio

#### Overview

In the Singdata Lakehouse platform, users can import data into the target table using the `INSERT` statement. `INSERT` supports various import methods, including direct value insertion, importing data from other tables, and importing data from external files. The following documentation will detail how to use the `INSERT` statement to import data, its use cases, operation examples, and precautions.

#### Method 1: Importing Data Using `INSERT INTO VALUES` Statement

##### Use Case

Suitable for manually importing small amounts of data, user debugging, and testing. For large-scale data processing, it is generally recommended to use batch insertion, streaming data import, and other more efficient methods to ensure the stability and efficiency of the data import process.

##### Implementation Steps

Navigate to Development -> Tasks, and click "+" to create a new SQL task (both methods below are implemented in the same task).

:-: ![](.topwrite/assets/image_1736148597217.png =470)

You can use the `INSERT INTO VALUES` statement to directly insert data. Multiple records are separated by commas.
```SQL
--Method 1: Use the INSERT INTO SELECT FROM TABLE statement to insert
DROP TABLE IF EXISTS ingest.lift_tuckets_import_by_insert_into_values;
CREATE TABLE IF NOT EXISTS ingest.lift_tuckets_import_by_insert_into_values(
  `txid` string,
  `rfid` string,
  `resort` string,
  `purchase_time` timestamp_ltz,
  `expiration_time` date,
  `days` int,
  `name` string,
  `address_street` string,
  `address_city` string,
  `address_state` string,
  `address_postalcode` string,
  `phone` string,
  `email` string,
  `emergency_contact_name` string,
  `emergency_contact_phone` string);

INSERT INTO ingest.lift_tuckets_import_by_insert_into_values (
  txid, rfid, resort, purchase_time, expiration_time, days, name, address_street, 
  address_city, address_state, address_postalcode, phone, email, emergency_contact_name, emergency_contact_phone
) VALUES
('0056b1f3-79b0-455c-80e9-3b80c45ac61e', '0x39eb22cbb32e9e115917b6', 'Singdata One',
  timestamp_ltz '2023-08-30 12:00:00', TO_DATE('2025-03-12', 'yyyy-MM-dd'), 2, 'She Xuemei', 'Guangzhou Road S Block', 
  'Yan City', 'Hebei Province', 853592, 13912709719, 'pchen@example.net', 'Lin Nan', 18041629236),
('52016065-1399-48cc-aed2-d4a525d90452', '0x121a00c15e41d8c3410c7490', 'Haidilao',
  timestamp_ltz '2023-08-30 12:00:00', TO_DATE('2025-10-16', 'yyyy-MM-dd'), 3, 'Wei Chao', 'Shanghai Road R Block', 
  'Wei County', 'Hong Kong Special Administrative Region', 123342, 18259131600, 'panyan@example.net', 'Wei Yulan', 14795983190);
```
#### Method Two: Import Data Using `INSERT INTO SELECT` Statement

##### Usage Scenario

If you need to import data from another table, you can use the `INSERT INTO SELECT` statement. You can choose to import the entire table's data, or perform ETL operations such as selecting specific columns or performing data transformations.

##### Implementation Steps

Navigate to Development -> Tasks, and click "+" to create a new SQL task.
```SQL
-- Method Two: Use the INSERT INTO SELECT FROM TABLE statement to insert
DROP TABLE IF EXISTS ingest.lift_tuckets_import_by_insert_into_select;
CREATE TABLE IF NOT EXISTS ingest.lift_tuckets_import_by_insert_into_select(
  `txid` string,
  `rfid` string,
  `resort` string,
  `purchase_time` timestamp_ltz,
  `expiration_time` date,
  `days` int,
  `name` string,
  `address_street` string,
  `address_city` string,
  `address_state` string,
  `address_postalcode` string,
  `phone` string,
  `email` string,
  `emergency_contact_name` string,
  `emergency_contact_phone` string);
  
INSERT INTO ingest.lift_tuckets_import_by_insert_into_select
SELECT * FROM ingest.lift_tuckets_import_by_studio_web;
```
#### Method Three: Query Data from Volume Files and Import

##### Use Case

Singdata Lakehouse supports using `INSERT INTO` in combination with `SELECT FROM VOLUME` to directly import data from external files (such as CSV or Parquet files in cloud storage).

Note: In the case of uploading data files using ZettaPark, CSV and JSON format data files have already been uploaded to the Singdata Lakehouse data lake object ingest\_demo.

##### Implementation Steps

Navigate to Development -> Tasks, and click "+" to create a new SQL task.
```SQL
DROP TABLE IF EXISTS ingest.lift_tuckets_import_by_insert_into_select_from_volume;
CREATE TABLE IF NOT EXISTS ingest.lift_tuckets_import_by_insert_into_select_from_volume(
  `txid` string,
  `rfid` string,
  `resort` string,
  `purchase_time` timestamp_ltz,
  `expiration_time` date,
  `days` int,
  `name` string,
  `address_street` string,
  `address_city` string,
  `address_state` string,
  `address_postalcode` string,
  `phone` string,
  `email` string,
  `emergency_contact_name` string,
  `emergency_contact_phone` string);


-- Import data using the results of the SELECT file
-- View the data files uploaded to Volume
SHOW VOLUME  DIRECTORY ingest.ingest_demo;

-- Import using CSV format data files
INSERT INTO ingest.lift_tuckets_import_by_insert_into_select_from_volume 
select * from volume ingest_demo(
  `txid` string,
  `rfid` string,
  `resort` string,
  `purchase_time` timestamp_ltz,
  `expiration_time` date,
  `days` int,
  `name` string,
  `address_street` string,
  `address_city` string,
  `address_state` string,
  `address_postalcode` string,
  `phone` string,
  `email` string,
  `emergency_contact_name` string,
  `emergency_contact_phone` string
) using csv
 options(
    'header'='true',
    'sep'=',',
    'compression' = 'gzip'
 ) files('gz/lift_tickets_data.csv.gz');
 
-- Import using JSON format data files
INSERT INTO ingest.lift_tuckets_import_by_insert_into_select_from_volume  
select * from volume ingest_demo(
        `txid` string,
        `rfid` string,
        `resort` string,
        `purchase_time` timestamp_ltz,
        `expiration_time` date,
        `days` int,
        `name` string,
        `address_street` string,
        `address_city` string,
        `address_state` string,
        `address_postalcode` string,
        `phone` string,
        `email` string,
        `emergency_contact_name` string,
        `emergency_contact_phone` string
        ) using json
options(
'compression' = 'gzip'
) files('gz/lift_tickets_data.json.gz');
```
Besides CSV and JSON formats, Singdata Lakehouse also supports querying open format data such as Parquet, ORC, BSON, etc., through the SELECT FROM VOLUME method and importing it.

#### Documentation

[SQL Insert Into](insert.md)

[Create Table As](create-table-ddl.md)