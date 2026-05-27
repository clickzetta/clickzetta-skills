#### WORKSPACES View

Records detailed information of WORKSPACE

| COLUMN NAME            | DATA TYPE           | DESCRIPTION                         |
| ---------------------- | ------------------- | ----------------------------------- |
| WORKSPACE\_ID          | STRING              | Workspace ID                        |
| WORKSPACE\_NAME        | STRING              | Name of the workspace               |
| WORKSPACE\_CREATOR     | STRING              | Owner of the workspace              |
| WORKSPACE\_CREATOR\_ID | STRING              | Account ID of the workspace owner   |
| WORKSPACE\_STORAGE     | BIGINT              | Workspace storage status, excluding external tables and external data lakes, only internal data lakes and table storage are counted |
| CREATE\_TIME           | TIMESTAMP           | Workspace creation time             |
| LAST\_MODIFY\_TIME     | TIMESTAMP           | Workspace modification time         |
| COMMENT                | STRING              | Workspace comment information       |
| DELETE\_TIME           | TIMESTAMP           | Workspace deletion time             |
| PROPERTIES             | MAP\<STRING,STRING> | All set PROPERTIES are recorded in this parameter |

#### SCHEMAS View

Records detailed information of SCHEMA
**Field Details**

| COLUMN NAME         | DATA TYPE           | DESCRIPTION            |
| ------------------- | ------------------- | ---------------------- |
| CATALOG\_NAME       | STRING              | Name of the current WORKSPACE |
| SCHEMA\_ID          | STRING              | SCHEMA ID              |
| SCHEMA\_NAME        | STRING              | Name of the SCHEMA     |
| TYPE                | STRING              | Enum values EXTERNAL, MANAGED |
| SCHEMA\_CREATOR     | STRING              | Account name of the database owner |
| SCHEMA\_CREATOR\_ID | STRING              | Account ID of the database owner   |
| CREATE\_TIME        | TIMESTAMP           | Database creation time  |
| LAST\_MODIFY\_TIME  | TIMESTAMP           | Database modification time |
| COMMENT             | STRING              | Comment information when creating the database |
| DELETE\_TIME        | TIMESTAMP           | Database deletion time  |
| PROPERTIES          | MAP\<STRING,STRING> | All set PROPERTIES will be recorded in this parameter |


#### TABLES View


Each table in the current WORKSPACE is displayed in one row


| COLUMN NAME        | DATA TYPE           | DESCRIPTION                                                                                                                                                                                                                                                                                                                        |
| ------ | --- | ------------ |
| TABLE\_CATALOG     | STRING              | Name of the current WORKSPACE                                                                                                                                                                                                                                                                                                                     |
| TABLE\_CATALOG\_ID | STRING              | ID of the WORKSPACE                                                                                                                                                                                                                                                                                                                       |
| TABLE\_SCHEMA      | STRING              | SCHEMA to which the current TABLE belongs                                                                                                                                                                                                                                                                                                                   |
| TABLE\_SCHEMA\_ID  | STRING              | ID of the database corresponding to the table                                                                                                                                                                                                                                                                                                                          |
| TABLE\_NAME        | STRING              | Table name                                                                                                                                                                                                                                                                                                                                |
| TABLE\_ID          | STRING              | Table ID                                                                                                                                                                                                                                                                                                                                |
| TABLE\_CREATOR     | STRING              | Table owner                                                                                                                                                                                                                                                                                                                              |
| TABLE\_CREATOR\_ID | STRING              | Table creator ID                                                                                                                                                                                                                                                                                                                             |
| TABLE\_TYPE        | STRING              | EXTERNAL TABLE: External table VIRTUAL\_VIEW: View MATERIALIIZED VIEW: Materialized view MANAGED\_TABLE: Standard table                                                                                                                                                                                                                                                     |
| ROW\_COUNT         | BIGINT              | Number of rows, MATERIALIZED VIEW shows the corresponding number of rows. When the TABLE's ROW COUNT is NULL, it means it cannot be counted. The situations where it cannot be counted include:&#XA;1. Data written in real-time includes PRIMARY KEY tables. Since the data is constantly changing, the data in the MEMORY TABLE cannot be counted.&#XA;2. Most UPDATE and DELETE operations can usually be counted, but real-time written partition tables may not be counted after performing UPDATE/DELETE because the request does not carry information on how many rows were deleted at the time of deletion submission.&#XA;3. Deleting partitions with INSERT OVERWRITE PARTITION and TRUNCATE PARTITION, the request does not carry information on how many rows were deleted, so it cannot be recorded temporarily.&#XA;&#XA; |
| BYTES              | BIGINT              | Space occupied, VIEW shows NULL, MATERIALIZED VIEW shows the corresponding size                                                                                                                                                                                                                                                                                       |
| CREATE\_TIME       | TIMESTAMP           | Table creation time                                                                                                                                                                                                                                                                                                                              |
| LAST\_MODIFY\_TIME | TIMESTAMP           | Table modification time                                                                                                                                                                                                                                                                                                                              |
| DATA\_LIFECYCLE    | BIGINT              | Lifecycle                                                                                                                                                                                                                                                                                                                               |
| IS\_PARTITIONED    | BOOLEAN             | Whether it is a partitioned table                                                                                                                                                                                                                                                                                                                             |
| IS\_CLUSTERED      | BOOLEAN             | Whether it is a clustered table                                                                                                                                                                                                                                                                                                                             |
| COMMENT            | STRING              | Table comment information                                                                                                                                                                                                                                                                                                                              |
| DELETE\_TIME       | TIMESTAMP           | Deletion time, NULL if not deleted                                                                                                                                                                                                                                                                                                                     |
| DATA\_LIFECYCLE    | INT                 | Set lifecycle, if not set it shows NULL representing permanent, if set it will show the corresponding time                                                                                                                                                                                                                                                                                                |
| PROPERTIES         | MAP\<STRING,STRING> | All set PROPERTIES will be recorded in this parameter                                                                                                                                                                                                                                                                                                             |


#### COLUMNS View


The query result contains each field in the table as a row


| COLUMN NAME              | DATA TYPE | DESCRIPTION      |
| ------------------------ | --------- | ---------------- |
| TABLE\_CATALOG           | STRING    | Name of the current WORKSPACE   |
| TABLE\_CATALOG\_ID       | STRING    | ID of the WORKSPACE     |
| TABLE\_SCHEMA            | STRING    | SCHEMA to which the current TABLE belongs |
| TABLE\_SCHEMA\_ID        | STRING    | ID of the database corresponding to the table        |
| TABLE\_NAME              | STRING    | Table name              |
| TABLE\_ID                | STRING    | Table ID              |
| COLUMN\_NAME             | STRING    | Field name            |
| COLUMN\_ID               | STRING    | Field ID             |
| COLUMN\_DEFAULT          | STRING    | Field default value, currently reserved value      |
| IS\_NULLABLE             | BOOLEAN   | Whether it can be NULL        |
| DATA\_TYPE               | STRING    | Field type             |
| IS\_PARTITIONING\_COLUMN | BOOLEAN  | Whether it is a partition field          |
| IS\_CLUSTERING\_COLUMN   | BOOLEAN  | Whether it is a CLUSTER table      |
| IS\_PRIMARY\_KEY         | BOOLEAN  | Whether it is a primary key            |
| COMMENT                  | STRING    | Field comment information          |
| DELETE\_TIME             | TIMESTAMP | Deletion time, NULL if not deleted   |


​


#### VIEWS View


Each view displays a row, containing all views under the current INSTANCE


| COLUMN NAME        | DATA TYPE | DESCRIPTION     |
| ------------------ | --------- | --------------- |
| TABLE\_CATALOG     | STRING    | Name of the current WORKSPACE  |
| TABLE\_CATALOG\_ID | STRING    | ID of the WORKSPACE    |
| TABLE\_SCHEMA      | STRING    | SCHEMA to which the current VIEW belongs |
| TABLE\_SCHEMA\_ID  | STRING    | ID of the database corresponding to the view      |
| TABLE\_NAME        | STRING    | View name            |
| TABLE\_ID          | STRING    | View ID            |
| TABLE\_CREATOR     | STRING    | Account name of the view owner      |
| TABLE\_CREATOR\_ID | STRING    | Account ID of the view owner      |
| VIEW\_DEFINITION   | STRING    | Statement to create the view         |
| CREATE\_TIME       | TIMESTAMP | View creation time          |
| LAST\_MODIFY\_TIME | TIMESTAMP | View modification time          |
| COMMENT            | STRING    | View comment information         |
| DELETE\_TIME       | TIMESTAMP | Deletion time, NULL if not deleted  |

#### USERS View

Each user and workspace displays one row, containing all users of the current ACCOUNT

| COLUMN NAME          | DATA TYPE           | DESCRIPTION                        |
| -------------------- | ------------------- | ---------------------------------- |
| WORKSPACE\_NAME       | STRING              | Workspace of the user                          |
| WORKSPACE\_ID         | STRING              | Workspace ID of the user                          |
| USER\_ID             | STRING              | User ID generated by the system                     |
| USER\_NAME           | STRING              | User name, concatenated with WORKSPACE NAME and USER NAME |
| ROLE\_NAME           | STRING              | Roles owned by the current user, multiple roles separated by commas               |
| ADD\_TIME            | TIEMSTAMP           | User creation time                             |
| EMAIL                | STRING              | User email                               |
| TELEPHONE             | STRING              | User phone                               |
| LAST\_SUCCESS\_LOGIN | TIMESTAMP           | Last login time                             |
| COMMENT              | STRING              | Description of user information                             |
| DELETE\_TIME         | TIMESTAMP           | Deletion time, NULL if not deleted                     |
| PROPERTIES           | MAP\<STRING,STRING> | All set PROPERTIES will be recorded in this parameter             |

#### ROLES View

Each role and workspace displays one row, containing all roles of the current ACCOUNT

| COLUMN NAME    | DATA TYPE | DESCRIPTION                         |
| -------------- | --------- | ----------------------------------- |
| WORKSPACE\_NAME | STRING    | Name of the current workspace                             |
| WORKSPACE\_ID   | STRING    | Workspace ID of the role                           |
| ROLE\_NAME     | STRING    | Role name                               |
| ROLE\_ID       | STRING    | ROLE ID                             |
| USER\_NAME     | STRING    | The name of the user granted this role, multiple users are separated by commas. Corresponding users for the ROLE |
| USER\_ID       | STRING    | The ID of the user granted this role                         |
| COMMENT        | STRING    | Description of user information                              |
| DELETE\_TIME   | TIMESTAMP | Deletion time, NULL if not deleted                      |

#### JOB_HISTORY View

Run information under all spaces

| COLUMN NAME          | DATA TYPE     | DESCRIPTION                                                                                                                                                                                                           |
| ------ | --- | ------------ |
| WORKSPACE\_NAME       | STRING        | The space where the JOB is running                                                                                                                                                                                                            |
| WORKSPACE\_ID        | STRING        |                                                                                                                                                                                                                       |
| JOB\_ID              | STRING        | Job ID                                                                                                                                                                                                                  |
| JOB\_NAME            | STRING        | Job name                                                                                                                                                                                                                  |
| JOB\_CREATOR\_ID     | STRING        | User ID running the job                                                                                                                                                                                                             |
| JOB\_CREATOR         | STRING        | User running the job                                                                                                                                                                                                               |
| STATUS               | STRING        | SETUP RESUMING\_CLUSTER QUEUED RUNNING SUCCESS FAILED CANCELED                                                                                                                                                        |
| CRU                  | DECIMAL(38,5) | Computing resources consumed by the user                                                                                                                                                                                                   |
| ERROR\_MESSAGE       | STRING        | This information will be available if there is an error during execution                                                                                                                                                                                                           |
| JOB\_TYPE            | STRING        | Job type  SQL                                                                                                                                                                                                             |
| JOB\_TEXT            | STRING        | Statement executed by the JOB                                                                                                                                                                                                              |
| START\_TIME          | TIMESTAMP     | JOB start time                                                                                                                                                                                                             |
| END\_TIME            | TIMESTAMP     | JOB end time                                                                                                                                                                                                             |
| EXECUTION\_TIME      | DOUBLE        | Execution time, in seconds                                                                                                                                                                                                             |
| INPUT\_BYTES         | BIGINT        | Actual scanned data volume.                                                                                                                                                                                                             |
| CACHE\_HIT           | BIGINT        | Data read from cache                                                                                                                                                                                                             |
| OUTPUT\_BYTES        | BIGINT        | Output bytes.                                                                                                                                                                                                                |
| INPUT\_OBJECTS       | STRING        | Input table names in the format \[SCHEMA].\[TABLE], multiple tables separated by commas                                                                                                                                                                                      |
| OUTPUT\_OBJECTS      | STRING        | Output table names in the format \[SCHEMA].\[TABLE]                                                                                                                                                                                            |
| CLIENT\_INFO         | STRING        | Client information, from JDBC, client, web page, JAVA SDK                                                                                                                                                                                      |
| VIRTUAL\_CLUSTER     | STRING        | Computing resources used                                                                                                                                                                                                               |
| VIRTUAL\_CLUSTER\_ID | BIGINT        |                                                                                                                                                                                                                       |
| ROWS\_PRODUCED       | BIGINT        | Total number of records processed, input data                                                                                                                                                                                                         |
| ROWS\_INSERTED       | BIGINT        | Should have a value if it is an insert action                                                                                                                                                                                                           |
| ROWS\_UPDATED        | BIGINT        | Should have a value if it is an update action                                                                                                                                                                                                           |
| ROWS\_DELETED        | BIGINT        | Should have a value if it is a delete action                                                                                                                                                                                                           |
| JOB\_CONFIG          | STRING        | Parameter information set when submitting the job                                                                                                                                                                                                          |
| JOB\_PRIORITY        | STRING        | Job priority                                                                                                                                                                                                                 |
| INPUT\_TABLES        | STRING        | JSON format array INPUT\_TABLES:{\[{TABLE:WORKSAPCE\_NAME.SCHEMA.TABLENAME1, SIZE:0,RECORD:0,CACHESIZE:0,PARTITIONS:\[]},{TABLE:WORKSAPCE\_NAME.SCHEMA.TABLENAME2 SIZE:0,RECORD:0,CACHESIZE:0,PARTITIONS:\[]}......]}         |
| OUTPUT\_TABLES       | STRING        | Name of the output object |
| QUERY\_TAG          | STRING        | Users can tag the JOB in the client                                                                                                                                                                                                        |
| ERROR\_MESSAGE       | STRING        | Error message                                                                                                                                                                                                                  |


#### MATERIALIZED VIEW Refresh View (MATERIALIZED\_VIEW\_REFRESH\_HISTORY) {#materialized-view-refresh-history}

| COLUMN\_NAME             | DATA\_TYPE   | DESCRIPTION                          |
| ------------------------ | ------------ | ------------------------------------ |
| WORKSPACE\_ID            | BIGINT       | Project space ID                               |
| WORKSPACE\_NAME          | STRING       | Project space name                               |
| SCHEMA\_ID               | BIGINT       | SCHEMA ID                            |
| SCHEMA\_NAME             | STRING       | SCHEMA name                             |
| MATERIALIZED\_VIEW\_ID   | BIGINT       | Materialized view ID                               |
| MATERIALIZED\_VIEW\_NAME | STRING       | Materialized view name                               |
| CREDITS\_USED            | DECIMAL      | Credits used for refreshing the materialized view    |
| VIRTUAL\_CLUSER\_ID      | BIGINT       | Materialized view ID                                 |
| VIRTUAL\_CLUSTER         | STRING       | Materialized view name, this information is available for automatic refresh |
| STATUS                   | STRING       | PENDING\RUNNING\FINISHED\FAILED                      |
| REFRESH\_MODE            | STRING       | Enum values INCREMENTAL FULL\_REFRESH NO\_DATA       |
| STATISTICS               | STRING       | Records the number of incremental rows               |
| SCHEDULE\_START\_TIME    | TIMESTAMP_LTZ | Scheduled refresh time                               |
| START\_TIME              | TIMESTAMP_LTZ | Materialized view start time                         |
| END\_TIME                | TIMESTAMP_LTZ | Materialized view end time                           |
| ERROR\_MESSAGE           | STRING       | Error message if the refresh fails, it will be here  |


#### VOLUMES View


| column\_name        | data\_type          | description                                           |
| ------------------- | ------------------- | ----------------------------------------------------- |
| VOLUME\_CATALOG     | STRING              | Name of the associated Workspace                      |
| VOLUME\_CATALOG\_ID | STRING              | ID of the associated Workspace                        |
| VOLUME\_SCHEMA      | STRING              | Name of the associated Schema                         |
| VOLUME\_SCHEMA\_ID  | STRING              | ID of the schema corresponding to the Volume          |
| VOLUME\_NAME        | STRING              | Volume name                                           |
| VOLUME\_ID          | STRING              | Volume ID                                             |
| VOLUME\_URL         | STRING              | URL bound to the Volume                               |
| VOLUME\_REGION      | STRING              | Region to which the Volume belongs                    |
| VOLUME\_TYPE        | STRING              | Volume type (internal means no need to specify third-party cloud provider address when creating volume, or external) |
| VOLUME\_CREATOR     | STRING              | Volume owner                                        |
| CONNECTION\_NAME    | STRING              | Referenced connection name                                       |
| CONNECTION\_ID      | STRING              | Referenced connection ID                                      |
| PROPERTIES          | map\<string,string> |                                                       |
| COMMENT             | STRING              | Comment                                                    |
| CREATE\_TIME        | TIMESTAMP           | Creation time                                                  |
| LAST\_MODIFY\_TIME  | TIMESTAMP           | Modification time                                                  |

#### CONNECTIONS View


| column_name     | data type           | description                                                                   |
| ---------------- | ------------------- | ----------------------------------------------------------------------------- |
| WORKSPACE\_NAME  | STRING              | The workspace where the object is located                                                                       |
| WORKSPACE\_ID    | STRING              |                                                                               |
| CONNECTION\_NAME | STRING              | Connection object name                                                                   |
| CONNECTION\_ID   | STRING              |                                                                               |
| CONNECTION\_KIND | STRING              | Enum values supporting connection types, STORAGE CONNECTION, API CONNECTION                         |
| TYPE             | STRING              | Specifies the type of data source connection, storage connection supports FILE\_SYSTEM, API connection supports CLOUD\_FUNCTION |
| PROVIDER         | STRING              | When TYPE is FILE\_SYSTEM, it is OSS / COS; when TYPE is CLOUD\_FUNCTION, it is aliyun / tencent   |
| REGION           | STRING              | The region connected to, such as ap-shanghai / cn-beijing                              |
| SOURCE\_CREATOR  | STRING              | Creator                                                                           |
| CREATED\_TIME    | TIMESTAMP           | Creation time                                                                          |
| COMMENT          | STRING              | Comment information                                                                          |
| PROPERTIES       | map\<string,string> |                                                                               |


### OBJECT_PRIVILEGES View

| Column Name         | Data Type      | Description                                                                 |
|---------------------|----------------|-----------------------------------------------------------------------------|
| GRANTOR             | TEXT           | The USER who grants the privilege.                                  |
| GRANTEE             | TEXT           | The user\_name or role\_name that is granted the privilege.               |
| GRANTED\_TO         | TEXT           | Whether the privilege is granted to a USER or ROLE.                     |
| OBJECT\_CATALOG     | TEXT           | The workspace or catalog name where the granted object resides.           |
| OBJECT\_SCHEMA      | TEXT           | The schema where the granted object resides, or null if the object is not schema-bound. |
| OBJECT\_NAME        | TEXT           | The name of the object that the privilege is granted on. Displayed directly without using workspace.schema.name format. |
| OBJECT\_TYPE        | TEXT           | The type of the object that the privilege is granted on.                 |
| SUB\_OBJECT\_TYPE   | TEXT           | Sub-object type (details not provided).                                  |
| PRIVILEGE\_TYPE     | TEXT           | The specific type of privilege granted.                                  |
| IS\_GRANTABLE       | TEXT           | Whether the privilege was granted with the WITH GRANT OPTION.            |
| AUTHORIZATION\_TIME | TIMESTAMP\_LTZ | The time when the privilege was granted.                                 |