# Database Metadata Views

In this section, we will introduce various database metadata views to help you better understand and query your data. These views provide detailed information about databases, tables, columns, views, users, roles, and job history. Through these views, you can easily manage and monitor your data.

## SCHEMAS View

The SCHEMAS view provides detailed information about the database, including the WORKSPACE name, SCHEMA name, creator, type, etc.

**Field Details**

| COLUMN NAME | DATA TYPE | Description |
| --- | --- | --- |
| CATALOG\_NAME | STRING | The name of the current WORKSPACE |
| SCHEMA\_NAME | STRING | The name of the database |
| SCHEMA\_CREATOR | STRING | The account name of the database owner |
| TYPE | STRING | Enum values: EXTERNAL (external), INTERNAL (internal) |
| COMMENT | STRING | Comment information when creating the database |
| CREATE\_TIME | TIMESTAMP | Database creation time |
| LAST\_MODIFY\_TIME | TIMESTAMP | Database modification time |
| PROPERTIES | MAP | PROPERTIES specified at creation, reserved field |

## TABLES View

The TABLES view shows detailed information about each table under the current WORKSPACE.

**Field Details**

| COLUMN NAME | DATA TYPE | Description |
| --- | --- | --- |
| TABLE\_CATALOG | STRING | The name of the current WORKSPACE |
| TABLE\_SCHEMA | STRING | The SCHEMA to which the current TABLE belongs |
| TABLE\_NAME | STRING | The name of the table |
| TABLE\_TYPE | STRING | Enum values: EXTERNAL (external table), VIEW (view), MATERIALIZED VIEW (materialized view), BASE TABLE (standard table), SNAPSHOT (snapshot table) |
| ROW\_COUNT | BIGINT | Number of rows in the table (NULL for VIEW, corresponding number for MATERIALIZED VIEW) |
| BYTES | BIGINT | Size of the table (NULL for VIEW, corresponding size for MATERIALIZED VIEW) |
| CREATE\_TIME | TIMESTAMP | Table creation time |
| LAST\_MODIFY\_TIME | TIMESTAMP | Table modification time |
| TABLE\_CREATOR | STRING | The account name of the table owner |
| IS\_PARTITIONED | BOOLEAN | Whether it is a partitioned table (NULL for VIEW) |
| IS\_CLUSTERED | BOOLEAN | Whether it is a clustered table (NULL for VIEW) |
| COMMENT | STRING | Table comment information |
| DATA\_LIFECYCLE | BIGINT | Lifecycle (in days) |
| PROPERTIES | MAP | PROPERTIES specified at creation, reserved field |

## COLUMNS View

The COLUMNS view shows detailed information about each field in the table.

**Field Details**

| COLUMN NAME | DATA TYPE | Description |
| --- | --- | --- |
| TABLE\_CATALOG | STRING | The name of the current WORKSPACE |
| TABLE\_SCHEMA | STRING | The SCHEMA to which the current TABLE belongs |
| TABLE\_NAME | STRING | The name of the table |
| COLUMN\_NAME | STRING | The name of the field |
| COLUMN\_DEFAULT | STRING | Default value of the field |
| IS\_NULLABLE | BOOLEAN | Whether it can be NULL |
| DATA\_TYPE | STRING | Field type |
| CREATE\_TIME | TIMESTAMP\_LTZ | Table creation time |
| IS\_CLUSTERING\_COLUMN | BOOLEAN | Whether it is a CLUSTER field |
| IS\_PRIMARY\_KEY | BOOLEAN | Whether it is a primary key |
| COMMENT | STRING | Field comment information |

## VIEWS View

The VIEWS view shows all views and their detailed information under the current WORKSPACE.

**Field Details**
| COLUMN NAME        | DATA TYPE | DESCRIPTION     |
| ------------------ | --------- | --------------- |
| TABLE\_CATALOG     | STRING    | Name of the current WORKSPACE  |
| TABLE\_SCHEMA      | STRING    | SCHEMA to which the current VIEW belongs |
| TABLE\_NAME        | STRING    | Name of the view            |
| TABLE\_CREATOR     | STRING    | Account name of the view owner      |
| VIEW\_DEFINITION   | STRING    | Statement to create the view         |
| CREATE\_TIME       | TIMESTAMP | View creation time          |
| LAST\_MODIFY\_TIME | TIMESTAMP | View modification time          |
| COMMENT            | STRING    | View comment information         |

#### USERS View

Each user is displayed in a row, containing all users of the current WORKSPACE

| COLUMN NAME    | DATA TYPE | DESCRIPTION           |
| -------------- | --------- | --------------------- |
| WORKSPACE\_NAME | STRING    | Name of the current space               |
| USER\_NAME     | STRING    | User name                  |
| ROLE\_NAME     | STRING    | Roles owned by the current user, multiple roles separated by commas  |
| CREATE\_TIME   | TIMESTAMP | User join time                |
| EMAIL          | STRING    | User email                  |
| TELEPHONE       | STRING    | User phone number                  |
| COMMENT        | STRING    | Description of user information                |
| PROPERTIES     | MAP       | PROPERTIES specified at creation, reserved field |

#### ROLES View

| COLUMN NAME    | DATA TYPE | DESCRIPTION            |
| -------------- | --------- | ---------------------- |
| WORKSPACE\_NAME | STRING    | Name of the current space                |
| ROLE\_NAME     | STRING    | All roles in the space               |
| USER\_NAMES    | STRING    | User names granted this role, multiple users separated by commas |
| CREATE\_TIME   | TIMESTAMP | View creation time                 |
| COMMENT        | STRING    | Description of role information                 |
| PROPERTIES     | MAP       | PROPERTIES specified at creation, reserved field  |

#### JOB\_HISTORY View
| COLUMN NAME      | DATA TYPE | DESCRIPTION                                     |
| ---------------- | --------- | ----------------------------------------------- |
| WORKSPACE\_NAME  | STRING    | Space where the JOB is run                                      |
| JOB\_ID          | STRING    | Job ID                                            |
| JOB\_NAME        | STRING    | Job name                                            |
| JOB\_CREATOR     | STRING    | User running the job                                         |
| STATUS           | STRING    | SCHEDULE, PROCESS, SUCCEEDED, FAILED, CANCELLED |
| CRU              | DECIMAL   | Computing resources consumed by the task                                       |
| ERROR\_MESSAGE   | STRING    | This information is available if an error occurs                                     |
| JOB\_TYPE        | STRING    | Job type COPY SQL DATALAKE (file operation commands)                  |
| JOB\_TEXT        | STRING    | Statement executing the JOB                                        |
| QUERY\_TAG       | STRING    | User-set TAG for identifying the QUERY                              |
| START\_TIME      | TIMESTAMP | JOB start time                                       |
| END\_TIME        | TIMESTAMP | JOB end time                                       |
| EXECUTION\_TIME  | DOUBLE    | Execution time in seconds, accurate to milliseconds                                 |
| INPUT\_BYTES     | BIGINT    | Actual scanned data volume.                                       |
| OUTPUT\_BYTES    | BIGINT    | Output bytes.                                          |
| INPUT\_OBJECTS   | STRING    | Input table names                                           |
| OUTPUT\_OBJECTS  | STRING    | Output table names                                           |
| CLIENT\_INFO     | STRING    | Client information, from JDBC, client, web page                         |
| VIRTUAL\_CLUSTER | STRING    | Computing resources used                                         |
| ROW\_PRODUCED    | BIGINT    | Total records processed, input data                                   |
| ROW\_INSERTED    | BIGINT    | Should have a value if it is an insert action                                     |
| ROW\_UPDATED     | BIGINT    | Should have a value if it is an update action                                     |
| ROW\_DELETED     | BIGINT    | Should have a value if it is a delete action                                     |
| JOB\_CONFIG      | STRING    | Parameter information set when submitting the job                                    |
| CACHE\_HIT       | BIGINT    | Data read from cache                                       |
| JOB\_PRIORITY    | STRING    | Job priority                                           |
| INPUT\_TABLES    | STRING    | Input table names                                           |
| OUTPUT\_TABLES   | STRING    | Output table name                                           |

#### Materialized View Refresh History

| COLUMN\_NAME             | DATA\_TYPE   | DESCRIPTION                    |
| ------------------------ | ------------ | ------------------------------ |
| WORKSPACE\_NAME          | STRING       | Project workspace name                         |
| SCHEMA\_NAME             | STRING       | SCHEMA name                       |
| MATERIALIZED\_VIEW\_NAME | STRING       | Materialized view name                         |
| CRU                    | DECIMAL      | Cost for refreshing the materialized view                    |
| VIRTUAL\_CLUSTER\_NAME   | STRING       | Materialized view name, this information is available for automatic refresh               |
| STATUS                   | STRING       | PENDING\RUNNING\FINISHED\FAILED |
| SCHEDULED\_START\_TIME   | TIMESTAMP_LTZ | Scheduled refresh time                         |
| START\_TIME              | TIMESTAMP_LTZ | Materialized view start time                       |
| END\_TIME                | TIMESTAMP_LTZ | Materialized view end time                       |
| ERROR\_CODE              | STRING       |                                |
| ERROR\_MESSAGE           | STRING       | Refresh failure information, if failed it will be here             |

#### AUTOMV\_REFRESH\_HISTORY Refresh View
| COLUMN\_NAME               | DATA\_TYPE   | DESCRIPTION                                                             |
| -------------------------- | ------------ | ----------------------------------------------------------------------- |
| WORKSPACE_NAME            | STRING       | Project workspace name SYS                                                               |
| SCHEMA_NAME               | STRING       | SCHEMA name, SCHEMA where AUTOMV is located                                                |
| MATERIALIZED_VIEW\_NAME   | STRING       | Materialized view name                                                                  |
| CRU                        | DECIMAL      | Cost for refreshing the materialized view                                                             |
| STATUS                     | STRING       |  PROCESS: Refreshing. SUCCEEDED: Refresh completed successfully. FAILED: Refresh failed during execution. CANCELLED: Refresh was cancelled before execution.  |
| MV\_PROCESS\_TYPE          | STRING       | BUILD: Build MV. REFRESH: Refresh                                                   |
| START\_TIME                | TIMESTAMP_LTZ | Start time of the materialized view                                                                |
| END\_TIME                  | TIMESTAMP_LTZ | End time of the materialized view                                                                |
| BUILD\_FROM\_WORKSPACE     | STRING       | Source workspace for building MV                                                             |
| JOB_ID | SRING       | Job ID for building MV                                                           |
| ERROR\_MESSAGE             | STRING       | Error message if the refresh fails                                                      |

#### VOLUMES View


| column_name       | data\_type          | description                                           |
| ------------------ | ------------------- | ----------------------------------------------------- |
| VOLUME\_CATALOG    | STRING              | Name of the associated Workspace                                       |
| VOLUME\_SCHEMA     | STRING              | Name of the associated Schema                                          |
| VOLUME\_NAME       | STRING              | Name of the Volume                                             |
| VOLUME\_URL        | STRING              | URL bound to the Volume                                         |
| VOLUME\_REGION     | STRING              | Region to which the Volume belongs                                           |
| VOLUME\_TYPE       | STRING              | Type of Volume (internal means no need to specify a third-party cloud provider address when creating the volume, or external) |
| VOLUME\_CREATOR    | STRING              | Owner of the Volume                                        |
| CONNECTION\_NAME   | STRING              | Name of the referenced connection                                       |
| COMMENT            | STRING              | Comment                                                    |
| PROPERTIES         | map\<string,string> |                                                       |
| CREATE\_TIME       | TIMESTAMP           | Creation time                                                  |
| LAST\_MODIFY\_TIME | TIMESTAMP           | Modification time                                              |

#### CONNECTIONS View


| column\_name       | data type           | description                                                                   |
| ------------------ | ------------------- | ----------------------------------------------------------------------------- |
| WORKSPACE\_NAME    | STRING              | The workspace where the object is located                                      |
| CONNECTION\_NAME   | STRING              | Connection object name                                                        |
| CONNECTION\_KIND   | STRING              | Enum value supporting connection types, STORAGE CONNECTION, API CONNECTION     |
| TYPE               | STRING              | Specifies the type of data source connection. storage connection supports FILE\_SYSTEM, api connection supports CLOUD\_FUNCTION |
| PROVIDER           | STRING              | When TYPE is FILE\_SYSTEM, it is OSS / COS. When TYPE is CLOUD\_FUNCTION, it is aliyun / tencent |
| REGION             | STRING              | The region of the connection, such as ap-shanghai / cn-beijing                 |
| SOURCE\_CREATOR    | STRING              | Creator                                                                        |
| CREATE\_TIME       | TIMESTAMP           | Creation time                                                                  |
| LAST\_MODIFY\_TIME | TIMESTAMP           | Last modification time                                                         |
| COMMENT            | STRING              | Comment information                                                            |
| PROPERTIES         | map\<string,string> |                                                                               |