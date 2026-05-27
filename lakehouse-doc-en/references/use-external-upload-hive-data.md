# Data Import via EXTERNAL SCHEMA

With EXTERNAL SCHEMA, you can directly federate query data from other databases, and then directly import the target data into Singdata Lakehouse.

## EXTERNAL SCHEMA

[Introduction to EXTERNAL SCHEMA](EXTERNALSCHMEA.md)

## Usage Restrictions

* Supports hive and the hive database is stored on object storage

## Application Scenarios

* Data is already stored in an external data source
* For Extract, Transform, and Load (ELT) workloads, you can load and clean data in one go, and use INSERT INTO ..SELECT to write the query results into Singdata Lakehouse

^
