# Multi-Table Real-Time Sync Task SOP

## Overview of Functionality

The multi-table real-time synchronization task enables full and incremental synchronization of source database tables. Incremental synchronization is primarily achieved by processing database change messages. This task is a persistent, always-on task that can achieve second-level end-to-end data timeliness. Multi-table real-time synchronization supports two types of synchronization and two modes:

### Two Types of Synchronization: Full and Incremental

* **Full Synchronization**: An optional step that can be selected when starting the real-time synchronization task. If chosen, the system will perform full synchronization concurrently with incremental synchronization. Data from full synchronization is written to a temporary table and then merged. After full synchronization completes, incremental synchronization continues automatically without manual intervention.
* **Incremental Synchronization**: Based on database change messages (e.g., MySQL's binlog), it parses and writes changes to the target database. Compared to full synchronization, it exerts less pressure on the database, primarily due to connection overhead.

### Two Modes of Synchronization: Mirror and Merge

* **Mirror Mode**: Each table in the target database corresponds one-to-one with the source tables.
* **Merge Mode**: Multiple source tables can be merged into a single target table. This mode is suitable for sharded databases and tables, requiring consistent or nearly consistent field structures across source tables.

## Principle of Operation

### Workflow Principle

The main steps are as follows:

1\. **Incremental Synchronization**: Synchronize changes from the source database to the target table.

2\. **Full Synchronization**: Synchronize existing data to a temporary table while incremental synchronization continues.

3\. **Merge Data**: After full synchronization completes, merge data from the temporary table into the target table. This process temporarily halts incremental synchronization and pauses consumption of source database changes.

4\. **Resume Incremental Synchronization**: After merging completes, resume incremental synchronization.

## Usage and Maintenance Guide

### General Usage: Preparing Source Database for Real-Time Synchronization

Before starting real-time synchronization, necessary configurations and permissions must be set up for the source database to ensure that database change logs work properly and the synchronization task has sufficient permissions to access data.

#### Database Configuration

**PostgreSQL**

Note: Modifying the following parameters requires restarting the PostgreSQL server to take effect.

|                            |                                                                                                           |                      |
| -------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------- |
| Configuration              | Description                                                                                               | Default Value (Unit) |
| wal\_level                 | Determines the amount of information written to WAL. `logical` is required for real-time synchronization. | replica              |
| max\_replication\_slots    | Maximum number of slots allowed on the server.                                                            | 10                   |
| max\_wal\_senders          | Maximum number of WAL sender processes that can run simultaneously.                                       | 10                   |
| max\_slot\_wal\_keep\_size | Size of WAL kept per slot. `-1` means unlimited.                                                          | -1 (MB)              |
| wal\_sender\_timeout       | Time after which idle replication connections are terminated.                                             | 60000 (ms)           |

**MySQL**

|                               |                                                                               |                                                                            |                                                  |
| ----------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------ |
| Configuration                 | Description                                                                   | Required Setting                                                           | Query Method                                     |
| log\_bin                      | Enables binary logging.                                                       | ON                                                                         | `SHOW GLOBAL VARIABLES LIKE 'log_bin';`          |
| binlog\_format                | Format of binlog entries. `ROW` is recommended for accurate data.             | ROW                                                                        | `SHOW GLOBAL VARIABLES LIKE 'binlog_format';`    |
| binlog\_row\_image            | Determines the information recorded in binlog entries. `FULL` is recommended. | FULL                                                                       | `SHOW GLOBAL VARIABLES LIKE 'binlog_row_image';` |
| binlog\_expire\_logs\_seconds | Time after which binlogs are automatically purged.                            | Configure based on business requirements, suggest 86400 (seconds) or more. | N/A                                              |

#### Database Permission Configuration

When synchronizing change events from different data sources, appropriate permissions must be configured on the source database to ensure data can be accessed and synchronized correctly. While granting administrative or superuser permissions is sufficient, it is generally recommended to minimize the permissions required for the synchronization user. Specific permission requirements are as follows:

**PostgreSQL**

**Scenario: Task Configuration (Obtaining Metadata: Schema List, Table List, Field List**)

\- **Required**\*\* Permissions\*\*: SELECT on `information_schema` and target tables.

\- **Granting Permissions**:

* Grant SELECT permission on `information_schema.tables`:

  * ```SQL
    GRANT SELECT ON TABLE information_schema.tables TO role_name;
    ```

* Grant SELECT permission on a specific table:

  * ```SQL
    GRANT SELECT ON TABLE your_schema.your_table TO role_name;
    ```

**Scenario: Synchronizing** **WAL** **Logs**

\- **Required Permissions**: REPLICATION LOGIN

\- **Granting Permissions**:

```SQL
CREATE ROLE <name> REPLICATION LOGIN;
```

**Scenario: Full Data Synchronization (Optional**)

\- **Required**\*\* Permissions\*\*: SELECT on target tables.

\- **Granting Permissions**:

* Grant SELECT permission on a specific table:

  * ```SQL
    GRANT SELECT ON TABLE table_name TO role_name;
    ```

* Grant SELECT permission on all tables in a schema:

  * ```SQL
    GRANT SELECT ON ALL TABLES IN SCHEMA schema_name TO role_name;
    ```

**Scenario: Change Data Synchronization, Creating Publication**

\- **Required**\*\* Permissions\*\*: CREATE on the database and SELECT on target tables.

\- **Granting Permissions**:

```SQL
GRANT CREATE ON DATABASE your_database TO role_name;
```

**MySQL**

**Scenario: Task Configuration (Obtaining Metadata: Database List, Table List, Field List**)

\- **Required Permissions**: SHOW DATABASES, SHOW TABLES, SELECT

\- **Granting Permissions**:

* Grant permission to view database lists:

  * ```SQL
    GRANT SHOW DATABASES ON *.* TO 'username'@'host';
    ```

* Grant permission to view table lists and details:

  * ```SQL
    GRANT SELECT ON database_name.table_name TO 'username'@'host';
    ```

**Scenario: Synchronizing Change Data Based on Binlog**

\- **Required Permissions**: RELOAD, REPLICATION SLAVE, REPLICATION CLIENT

\- **Granting Permissions**:

```SQL
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'username'@'host';
```

**Scenario: Full Data Synchronization**

\- **Required Permissions**: SELECT

\- **Granting Permissions**:

```SQL
GRANT SELECT ON database_name.table_name TO 'username'@'host';
```

### General Usage: Configuring and Running Real-Time Synchronization Tasks

Follow these steps in sequence:

1. Configure the synchronization task in the task development section, selecting the appropriate mirror or merge mode, target schema, and synchronization objects.
2. Save the task configuration.
3. In the scheduling configuration, select an appropriate synchronization cluster as the task's resource and save.
4. Submit the task to the operations center.
5. In the operations center, start the task. Note that the option to perform a full synchronization is only available during the first start after task submission.

### General Usage: How to Select Source Data Objects When Configuring Synchronization Tasks

\- **Mirror Mode**: Selecting source tables is straightforward; simply follow the page guidance to choose the required tables.

\- **Merge Mode**: This mode is more complex and involves the concept of a "virtual table."

* The "virtual table" defines which source tables will be synchronized into a single target table.
* When creating a "virtual table," you can specify selection criteria based on data source, schema, and table names to select the source tables to be synchronized into the same "virtual table."
* The system will automatically create the target table in the Lakehouse based on the "virtual table" name.

### General Usage: How to Configure Additional Fields to Record Source Information During Synchronization

* Enable the use of extended fields during task configuration.
* Extended fields currently support setting the source server name, database name, schema name, and table name.

### General Usage: How to Configure Synchronization Tasks to Avoid Data Write Conflicts When Source Tables Have Identical Primary Keys

* Enable the use of extended fields during task configuration and set these extended fields as the composite primary key of the target table.

### General Usage: How to Configure Synchronization Tasks When Source Tables Have Slightly Different Field Structures

* Use the heterogeneous field merging feature.
* When configuring the virtual table, the system will automatically check if the field structures of the source tables are consistent. If not, follow the system prompts to select the appropriate configuration.

### General Usage: How to Perform a Full Synchronization After the Task Has Started Without Initially Choosing It

**Option 1**: Re-synchronize a single table.

* Data from the source table will be synchronized to a temporary table and then written to the target table using `INSERT OVERWRITE`. This will not affect queries on the target table.

**Option 2**: Perform a data catch-up synchronization for a single table with a filter condition that retrieves all data (e.g., `WHERE 1=1`).

* In addition to the `WHERE` condition, you can also filter by data source name or table name as needed.

**Option 3**: Stop, take offline, and then bring the synchronization task back online. Choose to perform a full synchronization when restarting the task.

* Stopping and taking the task offline will not delete the target table.
* Stopping the task will prevent the target table from being updated, resulting in stale data.
* Taking the task offline will clear intermediate information such as synchronization checkpoints, preventing the task from resuming from where it left off. After re-launching, the task will start a new full and incremental synchronization.

### General Usage: How to Add More Tables for Synchronization After the Task Has Started

* Edit the task to add the new tables and save the task.

* Submit the task for publication.

* In the operations center, stop and then restart the task.

  * After restarting, the task will automatically synchronize data from the newly added tables. If the task is configured for full synchronization, it will perform a full synchronization; otherwise, it will only perform incremental synchronization.

### General Usage: How to Add or Remove Data Sources, Schemas, or Tables After the Task Has Started

* Directly edit the task in the task development interface.
* After adding objects, save, submit, and then restart the task to take effect.
* Restarting the task will start synchronizing data from the newly added objects. If the task is configured for full synchronization, the new objects will also undergo a full synchronization.
* This will not affect the synchronization progress of existing tables.

### General Usage: How to Prioritize Synchronization of Important Tables When Full Synchronization Takes a Long Time

* Use the "Prioritize Execution" feature on important tables undergoing full synchronization. This will allow them to jump the queue in the resource pool and synchronize data first.

### General Usage: How to View the Status and Details of Full Synchronization for Tables After the Task Has Started

* In the operations center, on the real-time synchronization task page, you can view the full synchronization status of tables in the synchronization object area.
* In the "Operations" section of a table, click "Full Synchronization Details" to view detailed information about the full synchronization instance, including task instance configuration and detailed logs.

### General Usage: How to Re-synchronize Specific Tables in a Task After It Has Started

\- **To Fix Data Issues in Specific Tables**: Choose "Re-synchronize."

* This operation will first synchronize data from the source table to a temporary table and then overwrite existing data in the target table using `INSERT OVERWRITE`. This will not affect queries on the target table.

\- **To Retrieve Full or Partial Data from the Source**: Choose "Catch-up Synchronization."

* This operation will retrieve data from the source table based on the given filter conditions, delete related data from the target table, and then write the data to the target table using `MERGE INTO`.

### General Usage: How to Temporarily Pause Incremental Data Synchronization

* In the operations center, on the real-time synchronization task page, click the "Stop" button to pause incremental message consumption and stop synchronization for all tables.

  * Note: There is no need to take the task offline.

* To resume synchronization, click the "Start" button.

* When clicking "Start," the system will automatically resume synchronization from the last saved state by default. If you need to backtrack, you can choose "Custom Start Position" and provide a specific checkpoint or file to retrieve data. For example, with MySQL, ensure that the provided binlog checkpoint has not expired.

### General Usage: How to Pause and Resume Incremental Synchronization for a Single Table After the Task Has Started

* In the operations menu for a specific table, select "Pause Incremental Synchronization" to stop the incremental synchronization of change data for that table and prevent it from being written to the target table.

* To resume incremental synchronization for a paused table, select "Resume Incremental Synchronization." This will restart the incremental synchronization of change data and write it to the target table.

  * Note: To ensure data continuity, the system will re-fetch full data from the source when resuming incremental synchronization.

### General Usage: What Are the Implications of Taking a Real-Time Synchronization Task Offline and When Should It Be Done?

* Taking a task offline is a relatively high-risk operation and should be used with caution, only when necessary.
* Stopping and taking a real-time synchronization task offline will not delete the target table or its data but will clear intermediate cache data and checkpoint information.
* If a task is no longer needed, it can be taken offline.
* If a task encounters intermittent issues and you wish to troubleshoot and repair it, you can try taking the task offline and then bringing it back online.
* After taking a task offline and bringing it back online and starting it again, the task will restart data synchronization. Full synchronization will overwrite existing data in the target table, while incremental synchronization will update the target table using `MERGE INTO`.

### General Usage: How to Optimize Performance for Large-Scale Data Synchronization Tasks

* The default values for task configuration parameters are usually sufficient.

* If the full synchronization data volume is particularly large and you wish to accelerate the synchronization speed, you can increase the following parameters in the task configuration:

  * `step1.taskmanager.memory.process.size`: For example, set it to `4000m` (default: `1728m`).
  * `step1.taskmanager.memory.task.off-heap.size`: For example, set it to `500M` (default: `256M`).

### Emergency Maintenance: How to Troubleshoot Issues When a Task Fails

* Contact the technical support team via Feishu or phone as soon as possible. The support team will respond quickly and initiate the troubleshooting process.
* Since the deployment environment is network-isolated, you may need to assist by providing task execution logs and other information to facilitate rapid problem resolution.

### Emergency Maintenance: How to Handle High Traffic from Multiple Tables Affecting Important Table Synchronization

* For tables that are less critical, use the "Pause Incremental Synchronization" feature to stop consuming change messages for those tables, freeing up resources for important tables.
* After the important tables have finished synchronizing their changes, resume incremental synchronization for the paused tables.

## Task Monitoring and Alerting

### Meaning of Monitoring Indicators on the Task Details Operations Page

#### Phase Monitoring

After a task starts, it goes through three phases: initialization, full synchronization, and incremental synchronization. You can view the status of these phases in the instance monitoring area.

#### **Metric Monitoring**

|                    |                                                                                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Metric Name        | Description                                                                                                                                  |
| Data Read          | The number of records read from the source data during the statistical cycle.                                                                |
| Data Written       | The number of records written to the target data source during the statistical cycle.                                                        |
| Average Read Rate  | The average read rate of the data synchronization task during the statistical cycle (total read records / cycle time).                       |
| Average Write Rate | The average write rate of the data synchronization task during the statistical cycle (total written records / cycle time).                   |
| Failover Count     | The number of Failover occurrences during the statistical cycle. Failover count indicates the stability of the data synchronization service. |

#### **Single Table Synchronization Progress**

|                      |                                                                                                                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Metric               | Description                                                                                                                                                                                      |
| Latest Read Position | The synchronization task reads data from the source object in real-time and writes it to the target table. The write time of the latest record in the target table is used as the read position. |
| Latest Update Time   | The time of the most recent write to the target table.                                                                                                                                           |
| Data Latency         | The time interval from when data is committed in the source database to when it becomes visible in the target database.                                                                          |

### Configuration of Task Monitoring and Alerting

In the monitoring and alerting module, users can configure monitoring rules to track operational status and latency metrics of real-time data synchronization tasks. To ensure comprehensive monitoring of task health for real-time synchronization operations, it is recommended to implement the following essential alerts according to the operational guidelines below (with optional additional configurations as needed):

1. Multi-Table Real-Time Synchronization Task Failure
2. Multi-Table Real-Time Synchronization Job Failover
3. Destination Table Modification Failure in Multi-Table Real-Time Synchronization
4. Multi-Table Real-Time Synchronization Latency
5. Checkpoint Read Latency in Multi-Table Real-Time Synchronization

#### **Initial Preparation: IM Alert Bot Configuration**

1\. **Bot Configuration**:

* Configure a group bot in Feishu. Reference: [Using Bots in Groups](https://www.feishu.cn/hc/zh-CN/articles/360024984973-%E5%9C%A8%E7%BE%A4%E7%BB%84%E4%B8%AD%E4%BD%BF%E7%94%A8%E6%9C%BA%E5%99%A8%E4%BA%BA#tabs0%7Clineguid-TINL0)
* Configure a group bot in WeChat Work. Reference: <<https://open.work.weixin.qq.com/help2/pc/14931>>

2\. **Obtain the webhook address of the group bot**.

3\. **Add a new webhook configuration** **in** **the product**:

* Channel: Select Feishu/WeChat Work.
* Webhook address: Fill in the address of the bot.

4\. **Enable webhook in the notification strategy**.

5\. **Select the configured webhook in the monitoring rule**.

#### **Configuration of Real-Time Data Integration Task Exception Monitoring**

1\. **Task Failover Alert**:

* Create a new monitoring rule and select "Multi-Table Real-Time Synchronization Job Failover" in the monitoring item. You can add additional filtering attributes, such as workspace or task name. If no filtering is added, all multi-table real-time tasks under the instance will be monitored by default.

2\. **Task Stop Alert**:

* Create a new monitoring rule and select "Multi-Table Real-Time Synchronization Task Failure" in the monitoring item. You can add additional filtering attributes, such as workspace or task name. If no filtering is added, all multi-table real-time tasks under the instance will be monitored by default.

#### **Configuration of Real-Time Data Integration Task Exception Monitoring**

1\. **Full Synchronization Exception Alert for Single Table**:

* Configure alerts for tables being added to the blacklist due to schema evolution failures or fields exceeding the 10M size limit.

2\. **Incremental Synchronization Exception Alert for Single Table**:

* Schema Evolution Failure Alert: Create a new monitoring rule and select "Multi-Table Real-Time Synchronization Target Table Change Failure."

#### **Configuration of Maximum Latency Monitoring for Real-Time Data Integration Tasks**

1\. **End-to-End Synchronization Latency**:

* Create a new monitoring rule and select "Multi-Table Real-Time Synchronization Latency" in the monitoring item. You can add additional filtering attributes, such as workspace or task name. If no filtering is added, all multi-table real-time tasks under the instance will be monitored by default.

2\. **Read Checkpoint Latency**:

* Create a new monitoring rule and select "Multi-Table Real-Time Synchronization Read Checkpoint Latency" in the monitoring item. You can add additional filtering attributes, such as workspace or task name. If no filtering is added, all multi-table real-time tasks under the instance will be monitored by default.

## Common Error Troubleshooting

### Incremental Synchronization Failure

#### Binlog Checkpoint Expired

\- **Problem Phenomenon**:

* The task fails to start, and the execution log reports an error: `Caused by: java.lang.IllegalStateException: The connector is trying to read binlog starting at Struct{version=1.9.7.Final,connector=mysql,name=mysql_binlog_source,ts_ms=1734071479878,db=,server_id=0,file=mysql-bin.010937,pos=432041283,row=0}, but this is no longer available on the server. Reconfigure the connector to use a snapshot when needed.`

\- **Possible Cause**:

* MySQL binlogs are not permanently stored and are periodically purged. If the specified binlog file or checkpoint has been cleaned up, or if the task has been stopped for a long time and resumes from a purged checkpoint, the above error will occur because the corresponding binlog data has been deleted.

\- **Solution**:

* Query the latest binlog file and checkpoint of the database using `SHOW MASTER STATUS`:

  * ```Plain
    +------------------+----------+--------------+------------------+| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB |+------------------+----------+--------------+------------------+| mysql-bin.010937 | 432041283|              |                  |+------------------+----------+--------------+------------------+
    ```

* Restart the synchronization task using the file and position from the result.

* If you need to recover lost data, you can choose to re-synchronize the corresponding tables.

#### Server-ID Conflict

**Problem Phenomenon**:

* Task startup fails, and the execution log reports an error: `A slave with the same server_uuid/server_id as this slave has connected to the master; the first event '' at 4, the last event read from '/home/mysql/log/mysql/mysql-bin.011268' at 90995258, the last byte read from '/home/mysql/log/mysql/mysql-bin.011268' at 90995258. Error code: 1236; SQLSTATE: HY000. The 'server-id' in the mysql cdc connector should be globally unique, but conflicts happen now.`

**Possible Cause**:

* The real-time synchronization task assigns a server-id for each MySQL data source connection to synchronize binlog data. The assigned server-id range is between 5400 and 6400. If this error occurs, it indicates a conflict with other synchronization tasks or tools using the same server-id.

**Solution**:

* Check if there are other synchronization tasks or tools connected to the same database instance that may be using the same server-id.
* Restart the synchronization task.

#### Data Source Time Zone Configuration Error

**Problem Phenomenon**:

* Task startup fails, and the execution log reports an error: `Caused by: org.apache.flink.table.api.ValidationException: The MySQL server has a timezone offset (28800 seconds ahead of UTC) which does not match the configured timezone Etc/GMT+12. Specify the right server-time-zone to avoid inconsistencies for time-related fields.`

**Possible Cause**:

* The configured time zone in the data source (default Asia/Shanghai) does not match the time zone configured in the database.

**Solution**:

* Confirm the time zone configured in the database and update the time zone configuration in the data source accordingly.

#### Binlog Event Size Exceeds Limit

**Problem Phenomenon**:

* Task execution fails, and the execution log reports an error: `Caused by: io.debezium.DebeziumException: log event entry exceeded max_allowed_packet; Increase max_allowed_packet on master; the first event '' at 58722808, the last event read from '/rdsdbdata/log/binlog/mysql-bin-changelog.004054' at 109251835, the last byte read from '/rdsdbdata/log/binlog/mysql-bin-changelog.004054' at 109251854. Error code: 1236; SQLSTATE: HY000.`

**Possible Cause**:

* The `max_allowed_packet` parameter in the database is smaller than the size of a binlog event.
* The binlog file may be corrupted.

**Solution**:

* Contact your DBA to adjust the `max_allowed_packet` parameter in the database. The upper limit is 1G. After the adjustment, restart the synchronization.
* If the task still fails after adjusting `max_allowed_packet`, the binlog file may be corrupted. Restart the task and choose a newer checkpoint to skip the problematic event and continue incremental synchronization. If you need to recover missing data, re-synchronize the full data for the affected tables.

### Full Synchronization Failure

#### Primary Key Length Exceeds Limit

**Problem Phenomenon**:

* Full synchronization status fails, and the execution log reports an error: `BulkLoad stream error com.dtstack.flinkx.throwable.FlinkxRuntimeException: BulkLoad failed, stream id: bulkload_stream_xxx final status: COMMIT_FAILED, error msg: Task lost connection, message: container stopped by AM. Detail CZLH-71006: Encoded key size 191 exceeds max size 128.`

**Possible Cause**:

* The total length of the primary key fields in the source table exceeds the default configuration of 128 bytes.
* In the synchronization task configuration, multiple extended fields are chosen as composite primary keys (e.g., in a merge scenario where server\_id, database, schema, and table are used to avoid primary key conflicts across tables), and the total length of the composite primary key exceeds the default configuration of 128 bytes.

**Solution**:

* Modify the synchronization task to increase the configuration:

  * ```Bash
    step1.containerized.taskmanager.env.pk_encoded_key_override_size 256step2.containerized.taskmanager.env.pk_encoded_key_override_size 256
    ```

### Synchronization Task Failover

#### Disconnection from Lakehouse Ingestion Service

**Problem Phenomenon**:

* The task experiences a failover, and the failover details contain the following information: `java.util.concurrent.ExecutionException: java.lang.RuntimeException: java.lang.RuntimeException: java.io.IOException: Async commit for instance [270076] workspace [xsy_ent] failed. Error detail is: rpcProxy call hit final failed after max retry reached.`

**Possible Cause**:

* This usually occurs during upgrades to the Lakehouse service, causing the data synchronization task to lose connection with the Lakehouse Ingestion Service.

**Solution**:

* This typically happens during service upgrades and usually resolves automatically after the upgrade is completed.
* If the task continues to failover after the upgrade is complete, try restarting the task manually.
* If the task still does not return to normal after manual restart, check the health status of the Lakehouse Ingestion Service.

#### Binlog Event Deserialization Failure

**Problem Phenomenon**:

* The task experiences a failover, and the failover details contain the following information: `com.github.shyiko.mysql.binlog.event.deserialization.EventDataDeserializationException: Failed to deserialize data of EventHeaderV4`.

**Possible Cause**:

* This issue typically arises when the source database's binlog suddenly generates a large number of events (e.g., due to massive business data updates or bulk historical data deletions). This can overwhelm the synchronization task's write end, causing backpressure and halting the read end from consuming binlog data. The connection between the synchronization task's binlog client and the database server may be terminated due to task timeout or the server's processing thread being idle for too long, potentially resulting in incomplete binlog event messages and deserialization failures.

**Solution**:

* If the traffic spike is short-lived, the synchronization task should recover within a limited number of failovers.

* If the issue persists for an extended period, consider adjusting MySQL configurations to increase the values of `slave_net_timeout` and `thread_pool_idle_timeout`.

* Temporary adjustments (will be lost after MySQL instance restart):

  * ```SQL
    SET GLOBAL slave_net_timeout = 120; -- default 60 secondsSET GLOBAL thread_pool_idle_timeout = 120; -- default 60 seconds
    ```

* Permanent adjustments (modify MySQL configuration file):

  * ```Bash
    [mysqld]slave_net_timeout = 120thread_pool_idle_timeout = 120
    ```

### Table Added to Blacklist

#### Schema Evolution Failure

**Problem Phenomenon**:

* A table's status automatically changes to "stopped synchronization," and the table object tooltip displays errors such as `pk column different`, `pk column type mismatch`, or `invalid modify column`.

**Possible Cause**:

* The source table structure has undergone changes unsupported by Lakehouse, including:

  * Changes to the primary key (PK) field list, such as renaming a PK field or changing it from one field to two fields.
  * Changes to the PK field type, such as changing the type from `bigint` to `varchar`.
  * Incompatible modifications to field types, such as changing from `int` to `double`.

**Solution**:

* Check the source table structure and revert it to the correct structure.
* Re-synchronize the full data for the stopped table. After full synchronization completes, incremental data will also resume synchronization.

## Known Limitations and Precautions

* To ensure no conflicts in target data writes, synchronization is only supported for source tables with primary key (PK) fields. Non-PK tables are not supported.
* The synchronization task will automatically create target tables. To ensure smooth task execution, avoid manually creating, modifying, or deleting tables unless necessary.
* Schema Evolution supports adding or removing fields in the source table but does not support changing field types or automatically adding new tables.

^
