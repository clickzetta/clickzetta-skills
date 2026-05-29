# Full Incremental Integrated Synchronization Function

The full incremental integrated synchronization function is a powerful data synchronization tool that can completely synchronize data from the database to the Lakehouse. This feature includes full synchronization of historical data and incremental synchronization of real-time change data. Please note that this feature is currently in Beta version, and some known limitations will be improved and optimized in subsequent versions.

## Task Creation Process

### Operation Entry

In the task development interface, click the new operation button and select the "Full Incremental Integrated Synchronization" task type from the drop-down menu.

![Create a new full incremental integrated synchronization task](.topwrite/assets/image_1710210458365.png)

### Configure Source Data Type

When creating a task, you first need to select a source data type to be synchronized. The currently supported source data types and their corresponding incremental reading modes and database versions are as follows:

| **Type**     | **Incremental Reading Mode** | **Database Version** |
| ---------- | ---------- | --------- |
| MySQL      | Binlog     | 5.x, 8.x   |
| PostgreSQL | WALs log     | 14 and above     |

### Select Synchronization Type

The full incremental integrated synchronization task supports two types of synchronization. Please choose according to actual needs:

1. Real-time synchronization - multi-table mirroring: Suitable for scenarios where source data is completely mirrored to the target.
2. Real-time synchronization - multi-table merging: Suitable for scenarios where data from multiple databases and tables are merged and written into the same target table.

#### Multi-table Mirroring

##### Source Configuration
* Select Data Source: Choose an existing data source. If no data source is available, please refer to the [Data Source Configuration](config-datasource.md) document to create a new data source.
* Configure Reading Mode: Select the appropriate reading mode based on the selected data source type. For example, MySQL data sources currently only support BINLOG mode, while PostgreSQL data sources only support WALs mode.
* Select Synchronization Objects: Select the databases and tables to be synchronized. You can quickly select multiple synchronization objects by uploading a configuration file through the batch configuration function. Please note that comments in the configuration file need to be deleted.
* Configure Slot
  * Only PostgreSQL needs to configure the slot, which refers to PostgreSQL's replication slot. For details, see [Documentation](https://www.postgresql.org/docs/9.4/catalog-pg-replication-slots.html).
  * Each database needs to configure a slot. Currently, decoderbufs and pgoutput plugin types are supported.
  * You can choose to use an existing slot; or create a new one on the page. In the creation window's lower area, you can modify the creation statement as needed. Click OK to create. The username configured in the data source must have the permission to create a slot, otherwise, the creation will fail. See the permission description below for details.
  * Special attention, do not reuse the same slot for different tasks. When the task starts, if the slot is occupied by other running tasks, it will fail to start. If other tasks are in a stopped state, because the data in the slot will be shared and consumed, the point is shared. The incremental data consumed by the new task may not be fully synchronized to the target table.

##### **Target Configuration**
* Target Data Source: By default, select the Lakehouse data source corresponding to the current workspace.
* Namespace Rules: Currently, only specific namespaces can be selected. Future versions will support mirroring naming or custom naming rules based on the source.
* Target Table Naming Rules: Currently, only the source table name can be mirrored. Future versions will support adding prefixes or custom naming rules.
* Compute Cluster: Select the available compute cluster in the workspace. It is recommended to use an AP type cluster.

##### Preview Configuration
After completing the source and target configuration, you can preview the mapping relationship between the synchronization tables and fields. If modifications are needed, you can go back to the previous step to adjust.

##### Synchronization Rules
In the synchronization rules, you can configure rules such as Schema Evolution to define the handling behavior after changes in source tables and fields.

#### Multi-table Merging

##### **Source Configuration**

* Select Data Source
  * Same as above, similar to multi-table mirroring synchronization
* Configure Reading Mode
  * Same as above, similar to multi-table mirroring synchronization
* Select Synchronization Objects
  Multi-table merging synchronization will use a "virtual table" as an intermediate transition to receive data from specified objects. There are two ways to configure:
  * Method 1: Based on rule configuration, filter through regular expressions, such as selecting all tables starting with abc, fill in ^abc in the regular expression.
  * Method 2: Based on file batch configuration, fill in the configuration file according to the template format requirements, upload it, and the page will select the objects to be synchronized according to the content given in the file. After selection, you can fine-tune as needed. Please note to delete the comments in the template file.

##### **Target Configuration**
* Same as above, similar to multi-table mirroring synchronization

##### **Preview Configuration**
* Same as above, similar to multi-table mirroring synchronization

##### **Synchronization Rules**
* Same as above, similar to multi-table mirroring synchronization

### Configure Advanced Parameters
After completing the regular task configuration, click the "Configure" button to complete the advanced parameter settings.
* Cluster: Specify the cluster used to run the synchronization task. It is recommended to use an AP type cluster.
* Update Frequency: Set the frequency interval for data writing.

### Submit Task
Click the submit button to submit the task to the production environment for execution. Note that the task does not start automatically after submission and needs to be started manually.

## Task Operations

### Start Task

On the task details page, you can start the task. Here are three ways to start:
1. Stateless start (only applicable for the first start of the task): Fully synchronize all data, first perform full synchronization, and then start incremental synchronization.
2. Resume from the last saved state (applicable for restarting tasks after stopping): Resume from the breakpoint where it was stopped.
3. Custom starting position: Synchronize from the given position, which can be used for data backfill. It applies uniformly to all tables configured in the task.

* MySQL: Choose to start from a specified file or a specified time. You can get the last file position in the page monitoring area.
* PostgreSQL: Specify the LSN value, and you can view the latest LSN value in the instance monitoring below.

### Instance Monitoring

After the task starts, it will go through three stages: initialization, full synchronization, and incremental synchronization. In the instance monitoring area, you can view the running status of these three stages.
![Instance Monitoring](.topwrite/assets/image_1705386710920.png)

### Metrics Monitoring

In the metrics monitoring area, you can view the key monitoring metrics for full synchronization and incremental synchronization.
![Metrics Monitoring](.topwrite/assets/image_1705386727702.png)

| **Metric Name**   | **Description**                                               |
| ---------- | ------------------------------------------------------ |
| Data Read       | The number of records read from the data source by the data synchronization task during the statistical period.                                |
| Data Written       | The number of records written to the target data source by the data synchronization task during the statistical period.                              |
| Average Read Rate     | The average read rate of the data synchronization task during the statistical period. (Total records read during the period / period time)                     |
| Average Write Rate     | The average write rate of the data synchronization task during the statistical period. (Total records written during the period / period time)                     |
| Failover Count | The number of failovers that occurred during the statistical period of the data synchronization task. The number of failovers represents the stability of the data synchronization service itself. |

### Synchronization Objects

In the synchronization objects area, you can view the final state of single table synchronization and perform corresponding operations.
![](.topwrite/assets/image_1710214491047.png)

| **Metric** | **Description**                                    |
| ------ | ------------------------------------------- |
| Latest Read Position | The synchronization task reads data from the source object in real-time and writes it to the target table, using the write time of the latest record in the target table as the read position. |
| Latest Update Time | The last time data was written to the target table.                               |
| Data Delay   | The time interval from when the data is committed at the data source end to when it is visible at the target end.                  |

| **Operation** | **Behavior Definition**                                     |
| ------ | -------------------------------------------- |
| Full Synchronization Details |                                              |
| Pause     | For tables that are being synchronized, you can pause the synchronization of the table and save the synchronization position.                  |
| Resume     | Continue synchronization from the last paused synchronization position.                            |
| Resynchronize   | Perform full and incremental synchronization for the table again.                              |
| View Exceptions   | Click to view the exception information of the incremental synchronization task of the table, such as Schema Evolution exceptions. |

### Stop Task

Stopping a task will stop the ongoing full synchronization and incremental synchronization in the task. The incremental synchronization position will be automatically saved when stopping.

* If the table is in the full synchronization stage when stopping, it will perform a new full synchronization for the table that has not been fully synchronized after restarting.
* If the table is in the incremental synchronization stage when stopping, it will continue synchronization from the position where it stopped by default after restarting.

### Offline Task

Taking a task offline is a high-risk operation. After the task is taken offline, the current synchronization position will not be saved. If the task is brought online and started again, it will start synchronizing data from scratch.

* Taking offline will not clean the data that has been synchronized to the target end, but it will clean the cached data and position information of the intermediate process.
* Resynchronization will not recreate the table. Full data synchronization will overwrite the old table, and incremental synchronization will update the target table with a merge into.

## Permission Description

When synchronizing change events from different types of data sources, appropriate permissions need to be configured on the corresponding data source server to ensure normal data synchronization. Although directly assigning an administrator or superuser permission is sufficient to ensure the task runs normally, it is usually desirable to minimize the permissions that need to be assigned to the user synchronizing the data. The specific permission configurations required for each operation step are as follows.

### PostgreSQL

| Requirement                             | Permission                                                             | Example                                                                                                                                                                               |
| -------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Configure task (retrieve metadata: schema list, table list, table field list) | SELECT (on information\_schema and the tables that need details)       | Grant a role permission to read information\_schema: GRANT SELECT ON TABLE information\_schema.tables TO role\_name;&#xA;&#xA;Grant a role permission to read a specific table: GRANT SELECT ON TABLE your\_schema.your\_table TO role\_name; |
| Synchronize wal logs                    | REPLICATION&#xA;LOGIN                                                 | CREATE ROLE \<name> REPLICATION LOGIN;                                                                                                                                               |
| Synchronize historical full data (optional) | SELECT (on the tables that need to be synchronized)                    | Grant a role permission to read a specific table: GRANT SELECT ON TABLE table\_name TO role\_name;&#xA;&#xA;Grant a role permission to read all tables in a schema: GRANT SELECT ON ALL TABLES IN SCHEMA schema\_name TO role\_name;                      |
| Create publication (optional)           | CREATE (on the database where the publication needs to be created)&#xA;SELECT (on the tables that need to be added to the publication) | Grant CREATE permission: GRANT CREATE ON DATABASE your\_database TO role\_name;                                                                                                                    |

### MySQL
| Requirement                                | Permission                                                    | Example                                                                                                                                                                                              |
| ---------------------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Configure tasks (fetch metadata: database list, table list, table field list) | SHOW DATABASES&#xA;SHOW TABLES (directly granting the more general SELECT permission is also possible)&#xA;SELECT | Grant the user permission to query the database list: GRANT SHOW DATABASES ON . TO 'username'@'host';&#xA;&#xA;Grant the user permission to query the table list and table details (SELECT includes the SHOW TABLES permission): GRANT SELECT ON database\_name.table\_name TO 'username'@'host'; |
| Sync binlog logs                               | RELOAD&#xA;REPLICATION SLAVE&#xA;REPLICATION CLIENT           | GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON . TO 'username'@'host';                                                                                          |
| Sync historical full data                                 | SELECT                                                        | Grant the user permission to query the table:&#xA;  GRANT SELECT ON database\_name.table\_name TO 'username'@'host';                                                                                                          |

## Known Limitations

* The current solution requires setting the data refresh frequency, with a minimum support of 1 minute. This means that the end-to-end data freshness delay will be at least over 1 minute, and second-level delay is not yet achieved (will be provided in future versions).
* Schema Evolution, currently does not support changing field types, and does not support automatic table addition.
* In multi-table real-time sync tasks, if there are data with the same primary key in different source tables, the sync result will be abnormal.
* MySQL sync, unsupported field types:

| Field Type | Behavior after Sync |
| ---- | ----- |
| year | Value does not correspond |

* PostgreSQL sync, unsupported field types:

| Field Type     | Behavior after Sync          |
| -------- | -------------- |
| varbit   | Value does not correspond          |
| bytea    | Value does not correspond          |
| TIMETZ   | Value does not correspond          |
| interval | Value does not correspond          |
| NAME     | Value does not correspond          |
| NUMERIC  | Precision does not correspond, target end precision will be higher |
| decimal  | Precision does not match, the target end precision will be higher |

^