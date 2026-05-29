# Introduction

The INFORMATION_SCHEMA of LAKEHOUSE provides detailed information about project INSTANCE and usage history data, helping you fully understand the information of all spaces. By querying INFORMATION_SCHEMA, you can view metadata information and usage history information of all spaces. INFORMATION_SCHEMA is based on the ANSI SQL-92 standard, with some additional fields and views specific to the LAKEHOUSE service. When you create a LAKEHOUSE instance, the system automatically creates an INFORMATION_SCHEMA in the system space named SYS. INFORMATION_SCHEMA not only records the currently existing metadata objects but also records the metadata objects that have been deleted. You can determine whether a metadata object has been deleted and the deletion time through the DELETE_TIME field. If the DELETE_TIME field is NULL, it means that the metadata object has not been deleted yet. It should be noted that there is currently a delay of about 15 minutes.

# Usage Restrictions

* Views under the instance-level SYS retain records of deleted objects for 60 days. There is currently a delay of about 15 minutes for views. JOB HISTORY and MATERIALIZED VIEW refresh views retain records for 60 days.
* Tables and views under each INFORMATION_SCHEMA are read-only (cannot be modified or deleted).
* Queries on INFORMATION_SCHEMA views do not guarantee consistency with concurrent DDL. For example, if a set of tables is created while executing a long-running INFORMATION_SCHEMA query, the query results may not include the created tables.

# Accessing INFORMATION_SCHEMA under SYS

To access INFORMATION_SCHEMA under SYS, you need INSTANCE ADMIN privileges. Here is an example of querying INFORMATION_SCHEMA:

```sql
SELECT * FROM SYS.information_schema.tables;
```
Here are some examples of querying INFORMATION_SCHEMA to help you better understand how to use these views and tables.

1. Query metadata information for all spaces:
```SQL
SELECT * FROM SYS.information_schema.columns;
```
2. Query table information of a specified space:
```SQL
SELECT * FROM SYS.information_schema.tables WHERE table_schema = 'your_schema_name';
```
3. Query deleted metadata objects:
```SQL
SELECT * FROM SYS.information_schema.columns WHERE delete_time IS NOT NULL;
```
4. Query the table creation time:
```SQL
SELECT table_name, create_time FROM SYS.information_schema.tables WHERE table_schema = 'your_schema_name';
```
5. Query JOB HISTORY Information:
```SQL
SELECT * FROM SYS.information_schema.job_history;
```
6. Query instance compute usage cost details:
```SQL
SELECT workspace_name, sku_name, measurements_consumption, amount
FROM SYS.information_schema.instance_usage
WHERE measurement_start >= '2026-05-01'
ORDER BY amount DESC;
```
7. Query object privilege grants:
```SQL
SELECT grantee, granted_to, object_name, object_type, privilege_type
FROM SYS.information_schema.object_privileges
WHERE object_type = 'TABLE';
```
By the above example, you can gain a deeper understanding of how to use INFORMATION_SCHEMA to query and manage metadata information and usage history information in the LAKEHOUSE instance.