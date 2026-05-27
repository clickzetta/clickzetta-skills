# LAKEHOUSE INFORMATION\_SCHEMA Metadata View Service Introduction

LAKEHOUSE provides a workspace-level INFORMATION\_SCHEMA metadata view service. Through INFORMATION\_SCHEMA, you can view the metadata information and job history of the current space. INFORMATION\_SCHEMA is designed based on the ANSI SQL-92 standard and extends with fields and views unique to Singdata LAKEHOUSE. It is provided by default when the LAKEHOUSE space is created, allowing you to view the metadata views you are concerned with.

## Instructions

* The views currently have a delay of about 15 minutes, and the JOB\_HISTORY and MATERIALIZED\_VIEW refresh views retain records for 60 days.
* The latest online metadata information can be viewed through the SHOW command, for example: SHOW TABLES, SHOW JOBS, etc., will return real-time metadata information.
* The views under INFORMATION\_SCHEMA are read-only and cannot be modified or deleted.
* The fields of the views may change according to functional evolution. When using views in periodic tasks, avoid using SELECT \* to directly query all fields. It is strongly recommended to use SELECT COLUMN\_NAME to select the specific fields needed for the query to avoid errors in periodic tasks when the view fields change.

## Permission Requirements

* Possess the workspace\_admin role

## Usage Example

Get information about all tables in the current space:
```SQL
SELECT * FROM information_schema.tables;
```
Here is the translated content:

```
# Get all job information in the current space
```

I have followed all the rules you provided.
```SQL
SELECT * FROM information_schema.job_history;
```
Get all Materialized View information of the current space:
```SQL
SELECT * FROM information_schema.materialized_views;
```
## Authorization Operations

* Roles or users authorized by the workspace\_admin role

Authorize a role:
```SQL
GRANT ALL ON ALL VIEWS IN SCHEMA information_schema TO ROLE <role_name>;
```
Authorize a user:
```SQL
GRANT ALL ON ALL VIEWS IN SCHEMA information_schema TO USER <user_name>;
```
## Precautions

* Please ensure that you have the appropriate permissions, otherwise you will not be able to use the INFORMATION\_SCHEMA metadata view service.
* When using INFORMATION\_SCHEMA, please note its read-only nature; do not modify or delete the views.
* Use specific fields for queries in periodic tasks, and avoid using SELECT \* to query all fields, to prevent periodic task errors due to changes in view fields.