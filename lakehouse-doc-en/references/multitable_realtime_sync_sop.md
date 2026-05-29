# Multi-Table Real-Time Sync Complete Guide

## Overview

The multi-table real-time sync task enables full sync and incremental sync of source database tables. Incremental sync is primarily achieved by processing database change messages. This is a long-running resident task that can achieve second-level end-to-end data freshness. It supports two sync types and two sync modes:

### Two Sync Types: Full Sync and Incremental Sync

* Full sync is optional — you can choose whether to run it when starting the real-time sync task.
* If you choose full sync, the system runs it concurrently with incremental sync at startup. Full sync data is written to a temporary table and then merged. After full sync completes, incremental sync continues automatically without manual intervention.
* Full sync uses the JDBC protocol to connect to the source and extract data, which places a heavier read load on the source database.
* Incremental sync is based on database change messages (such as MySQL binlog) and parses them to write changes to the target. The load on the source database is primarily connection overhead, which is much lighter than full sync.

### Two Sync Modes: Multi-Table Mirror and Multi-Table Merge

These modes differ in how source tables are written to the target.

* **Multi-table mirror**: each target table has a one-to-one correspondence with its source table.
* **Multi-table merge**: multiple source tables are merged into a single target table. This mode is suited for sharded database scenarios. It requires that the source tables have identical or nearly identical field structures.

## How It Works

### Workflow

The main steps are:

1. Start incremental sync — source change data is continuously written to the target table.
2. Run full sync — historical data is synced to a temporary table while incremental sync continues uninterrupted.
3. After full sync completes, merge the temporary table into the target table. Incremental sync is paused briefly during this merge step.
4. Resume incremental sync after the merge is complete.

## Usage and Operations Guide

### General: What source database parameters and permissions do I need to configure before starting real-time sync?

The source database requires certain parameter settings and permission grants to ensure change logs work correctly and the sync task has the access it needs.

#### Database Parameter Configuration

**PostgreSQL**

Note: Modifying the following parameters requires restarting the PostgreSQL server to take effect.

|                            |                                                                                                                                                                                                                                                                                                 |                      |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Configuration              | Description                                                                                                                                                                                                                                                                                     | Default Value (Unit) |
| wal\_level                 | WAL level. `logical` is required for real-time sync. `replica` supports WAL archiving and replication. `minimal` keeps only what is needed to recover from a crash.                                                                                                                             | replica              |
| max\_replication\_slots    | Maximum number of replication slots allowed on the server.                                                                                                                                                                                                                                      | 10                   |
| max\_wal\_senders          | Maximum number of WAL sender processes that can run simultaneously, corresponding to the number of concurrent real-time sync tasks.                                                                                                                                                              | 10                   |
| max\_slot\_wal\_keep\_size | Size of WAL retained per slot. `-1` means unlimited.                                                                                                                                                                                                                                           | -1 (MB)              |
| wal\_sender\_timeout       | Replication connections idle longer than this value will be terminated.                                                                                                                                                                                                                         | 60000 (ms)           |

**MySQL**

|                               |                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                           |                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- | ------------------------------------------------ |
| Attribute                     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                | Required Setting                                                          | Query Method                                     |
| log\_bin                      | Whether binlog is enabled.                                                                                                                                                                                                                                                                                                                                                                                                                 | ON                                                                        | SHOW GLOBAL VARIABLES LIKE 'log\_bin'            |
| binlog\_format                | Binlog format. `statement` records SQL (compact but can cause sync errors with non-deterministic functions). `row` records full before/after row images (accurate but higher volume). `mixed` lets MySQL choose automatically.                                                                                                                                                                                                              | ROW                                                                       | SHOW GLOBAL VARIABLES LIKE 'binlog\_format'      |
| binlog\_row\_image            | Whether full before/after row images are recorded.                                                                                                                                                                                                                                                                                                                                                                                         | FULL (record all fields in both images)                                   | SHOW GLOBAL VARIABLES LIKE 'binlog\_row\_image'  |
| binlog\_expire\_logs\_seconds | Binlog automatic cleanup interval.                                                                                                                                                                                                                                                                                                                                                                                                         | Configure based on business needs; 86400 seconds (1 day) or more recommended. |                                              |

#### Database Permission Configuration

Appropriate permissions must be configured on each source database to ensure change events can be synced normally. Granting admin or superuser permissions is sufficient, but it is best practice to grant only the minimum required permissions. The specific permissions for each scenario are described below.

**PostgreSQL**

When executing grant SQL statements, ensure the executing account itself has the ability to grant those permissions — using an administrator account is recommended. Execute the grants for all scenarios listed below to ensure the task runs smoothly.

**Scenario: Task configuration (fetching metadata: schema list, table list, field list)**

Required permissions:

> SELECT (on information_schema and the tables to be inspected)

Grant statements:

* Grant a role permission to read `information_schema`:

  ```SQL
    GRANT SELECT ON TABLE information_schema.tables TO role_name; 
  ```

* Grant a role permission to read a specific table:

  ```SQL
    GRANT SELECT ON TABLE your_schema.your_table TO role_name;
  ```

**Scenario: Sync WAL logs**

* Required permissions:

> REPLICATION LOGIN

* Grant statement:

```SQL
CREATE ROLE <name> REPLICATION LOGIN;
```

**Scenario: Sync historical full data (optional)**

* Required permissions:

> SELECT (on the tables to be synced)

* Grant statements:

  * Grant a role permission to read a specific table:

    ```SQL
      GRANT SELECT ON TABLE table_name TO role_name; 
    ```

  * Grant a role permission to read all tables in a schema:

    ```SQL
      GRANT SELECT ON ALL TABLES IN SCHEMA schema_name TO role_name;
    ```

**Scenario: Change data sync — create publication**

Required permissions:

> CREATE (on the database where the publication will be created) SELECT (on the tables to be added to the publication)

Grant statement:

* Grant CREATE permission:

  ```SQL
   GRANT CREATE ON DATABASE your_database TO role_name;
  ```

**MySQL**

When executing grant SQL statements, ensure the executing account has the GRANT OPTION privilege — using a superuser such as root is recommended. Execute the grants for all scenarios listed below.

**Scenario: Task configuration (fetching metadata: database list, table list, field list)**

Required permissions:

> SHOW DATABASES SHOW TABLES (or grant the more general SELECT permission instead) SELECT

Grant statements:

* Grant permission to query the database list:

  ```SQL
    GRANT SHOW DATABASES ON *.* TO 'username'@'host'; 
  ```

* Grant permission to query the table list and table details (SELECT includes SHOW TABLES):

  ```SQL
    GRANT SELECT ON database_name.table_name TO 'username'@'host';
  ```

**Scenario: Sync change data from binlog**

Required permissions:

> RELOAD REPLICATION SLAVE REPLICATION CLIENT

Grant statement:

```SQL
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'username'@'host';
```

**Scenario: Sync historical full data**

Required permissions:

> SELECT

Grant statement:

* Grant permission to query a table:

  ```SQL
    GRANT SELECT ON database_name.table_name TO 'username'@'host';
  ```

### General: How do I configure and run a real-time sync task?

Follow these steps in order:

1. In task development, configure the sync task — choose the appropriate mirror or merge mode, select the sync objects, and set the correct target schema.
2. Save the task configuration.
3. In the scheduling configuration, select an appropriate sync-type cluster as the task resource and save.
4. Submit the task to the operations center.
5. In the operations center, start the task. Note that the option to perform a full sync is only available the first time you start the task after submitting it online.

### General: How do I select source data objects when configuring a sync task?

* **Mirror mode**: selecting source tables is straightforward — follow the page guidance to check the databases and tables you want to sync.

* **Merge mode**: this mode is more complex and involves the concept of a "virtual table."

  * A virtual table defines which source tables will be merged into a single target table.
  * When creating a virtual table, specify selection criteria based on data source, schema, and table names to define which source tables belong to this virtual table.
  * The system automatically creates the corresponding target table in the Lakehouse based on the virtual table name.

### General: How do I add extra fields to record source information in the target table?

* Enable the extended fields feature in the task configuration.

* Extended fields currently support: source server name, database name, schema name, and table name.

  ![](.topwrite/assets/image_1740314767939.png =680)

### General: If the same primary key exists in different sharded source tables, how do I avoid write conflicts in the target table?

* Enable the extended fields feature in the task configuration, and include those extended fields in the composite primary key of the target table.

  ![](.topwrite/assets/image_1740314789823.png =680)

### General: If the sharded source tables have mostly — but not exactly — the same field structure, how do I configure the sync task?

* Use the heterogeneous field merge feature.
* When configuring the virtual table, the system will automatically check whether the field structures of the source tables are identical. If not, the system will flag the differences — follow the prompts to choose the appropriate configuration.

### General: If I did not choose full sync when first starting the task, how can I run a full sync later?

There are several options:

* **Option 1**: Resync a single table.

  * This syncs the source table to a temporary table, then writes it to the target using `INSERT OVERWRITE`.
  * This does not interrupt queries on the target table.

* **Option 2**: Run a backfill sync for a single table with a filter condition that retrieves all records (e.g., `WHERE 1=1`).

  * In addition to the `WHERE` clause, you can also filter by data source name or table name as needed.

* **Option 3**: Stop the task, unpublish it, then republish and start it again — this time choosing to perform a full sync.

  * Stopping and unpublishing the task does not delete the target table.
  * While the task is stopped, the target table will not be updated and its data will be stale.
  * Unpublishing the task clears checkpoint information, so the task cannot resume from where it left off. After republishing and starting, you must run a fresh full sync followed by incremental sync.

### General: How do I add more tables to sync after the task has started?

* Edit the task to add the new tables, then save.

* Submit and publish the task.

* In the operations center, stop the task and then restart it.

  * After restarting, the task will automatically sync data from the newly added tables. If full sync is enabled, the new tables will also undergo full sync.

### General: How do I add or remove data sources, schemas, or tables from a sharded setup?

* Edit the task directly in the task development interface.
* After making changes, save and submit, then restart the task for the changes to take effect.
* After restarting, the task will start syncing the newly added objects. If full sync is enabled, new objects will also be fully synced.
* Existing tables are not affected.

### General: Full sync is taking a long time for all tables — how can I prioritize important tables?

* Use the **Prioritize** action on an important table that is currently undergoing full sync. This bumps it to the front of the resource queue so it is processed first.

### General: How do I check the full sync status and details for each table?

* In the operations center, on the real-time sync task page, you can see the full sync status for each table in the sync objects area.
* In the **Operations** menu for a table, click **Full Sync Details** to view the full sync instance details, including task configuration and logs.

### General: How do I resync a specific table in the task after it has started?

* **To fix data issues in a specific table**: use **Resync**.

  * Resync re-syncs the source table to a temporary table, then overwrites the target table using `INSERT OVERWRITE`. This does not interrupt queries on the target table.

* **To pull full or partial data from the source**: use **Backfill Sync**.

  * Backfill sync retrieves data from the source based on a filter condition, deletes the matching rows from the target table, then writes the data back using `MERGE INTO`.

### General: How do I temporarily pause incremental sync?

* In the operations center, on the real-time sync task details page, click **Stop** to pause incremental message consumption for all tables.

  * Note: there is no need to unpublish the task.

* To resume sync, click **Start**.

* When clicking Start, the default option is **Resume from last saved state** — the system will resume from where it stopped. If you need to replay data, select **Custom Start Position** and provide a specific checkpoint or file. For MySQL, make sure the binlog checkpoint you specify has not expired.

### General: How do I pause and resume incremental sync for a single table?

* In the per-table operations menu, select **Pause Incremental Sync** to stop consuming change data for that table.

* To resume, select **Resume Incremental Sync**. The task will restart incremental sync for that table.

  * Note: to ensure data continuity, the system will re-fetch a full copy of the table's data from the source when resuming.

### General: What are the implications of unpublishing a real-time sync task, and when should I do it?

* Unpublishing is a relatively high-risk operation — use it with caution and only when necessary.
* Unpublishing a task does not delete the target table or its data, but it does clear intermediate cache data and checkpoint information.
* Unpublish the task if it is no longer needed.
* If the task encounters an intermittent issue and you want to reset it, try unpublishing and then republishing.
* After republishing and starting the task, it will begin syncing from scratch. Full sync will overwrite existing target table data; incremental sync will apply updates using `MERGE INTO`.

### General: How do I tune performance for tasks with very large tables or high data volumes?

* The default parameter values are generally sufficient.

* If the full sync data volume is very large and you want to speed it up, you can increase the following parameters in the task configuration:

  * `step1.taskmanager.memory.process.size` — for example, set to `4000m` (default: `1728m`)

  * `step1.taskmanager.memory.task.off-heap.size` — for example, set to `500M` (default: `256M`)

    ![](.topwrite/assets/image_1740314863947.png =680)

### Emergency Maintenance: The task has failed and I cannot resolve it on my own — how do I get help from Singdata?

* Contact Singdata technical support via the agreed communication channel (such as Lark or phone). The support team will respond quickly and initiate the troubleshooting process.
* Because the deployment environment may be network-isolated, you may need to collect and share task execution logs and other information to help diagnose the issue quickly.

### Emergency Maintenance: High traffic from multiple tables is affecting important table sync throughput — what should I do?

* For less important tables, use **Pause Incremental Sync** to stop consuming their change messages and free up processing resources for the important tables.
* Once the important tables have caught up, resume incremental sync for the paused tables.

## Task Monitoring and Alerting

### Understanding the Monitoring Metrics on the Task Details Page

#### Phase Monitoring

After a task starts, it goes through three phases: initialization, full sync, and incremental sync. You can view the status of these phases in the instance monitoring area.

![](.topwrite/assets/image_1740314893402.png =600)

#### Metric Monitoring

|                    |                                                                                                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Metric             | Description                                                                                                                                                              |
| Data read          | Number of records read from the source during the measurement period.                                                                                                    |
| Data written       | Number of records written to the target during the measurement period.                                                                                                   |
| Avg. read rate     | Average read rate during the measurement period (total records read / period duration).                                                                                  |
| Avg. write rate    | Average write rate during the measurement period (total records written / period duration).                                                                              |
| Failover count     | Number of failovers during the measurement period. This reflects the operational stability of the sync service itself.                                                   |

![](.topwrite/assets/image_1740314904374.png =600)

#### Per-Table Sync Progress

|                      |                                                                                                                                           |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Metric               | Description                                                                                                                               |
| Latest read position | The write time of the most recent record written to the target table, used as a proxy for the current read position.                      |
| Latest update time   | The last time a record was written to the target table.                                                                                   |
| Data latency         | The time between a transaction committing on the source and the data becoming visible on the target.                                      |

![](.topwrite/assets/image_1740314933658.png =600)

### Configuring Task Monitoring and Alerts

In the monitoring and alerting module, you can configure monitoring rules to track the run status and latency of real-time sync tasks. For comprehensive health monitoring, it is recommended to configure at least the following alerts (add more as needed):

* Multi-table real-time sync task run failure
* Multi-table real-time sync job failover
* Multi-table real-time sync target table change failure
* Multi-table real-time sync latency
* Multi-table real-time sync read checkpoint latency

#### Initial Setup: IM Alert Bot Configuration

1. Configure a bot:

   1. Configure a group bot in Lark. Reference: [Using bots in groups](https://www.feishu.cn/hc/zh-CN/articles/360024984973-%E5%9C%A8%E7%BE%A4%E7%BB%84%E4%B8%AD%E4%BD%BF%E7%94%A8%E6%9C%BA%E5%99%A8%E4%BA%BA#tabs0|lineguid-TINL0)
   2. Configure a group bot in WeCom. Reference: <https://open.work.weixin.qq.com/help2/pc/14931>

2. Get the webhook URL of the group bot.

3. Add a new webhook configuration in the product — select Lark or WeCom as the channel and enter the bot's webhook URL.

   ![](.topwrite/assets/image_1740315003712.png =680)

4. Enable the webhook in the notification policy.

   ![](.topwrite/assets/image_1740315034077.png =680)

5. In the monitoring rule, select the notification policy with the webhook enabled, then choose the webhook configuration you just created.

   ![](.topwrite/assets/image_1740315043022.png =680)

#### Configuring Exception Monitoring for Real-Time Data Integration Tasks

1. **Task failover alert**: create a new monitoring rule and select "Multi-table real-time sync job failover" as the monitoring event. You can add filter attributes such as workspace or task name. If no filter is added, all multi-table real-time sync tasks in the instance are monitored by default.

   ![](.topwrite/assets/image_1740315064690.png =680)

2. **Task stop alert**: create a new monitoring rule and select "Multi-table real-time sync task run failure" as the monitoring event. You can add filter attributes such as workspace or task name. If no filter is added, all multi-table real-time sync tasks in the instance are monitored by default.

   ![](.topwrite/assets/image_1740315072098.png =460)

#### Configuring In-Task Exception Monitoring

1. Full sync exception alert for a single table.

2. Incremental sync exception alert for a single table.

   * You can configure an alert for when a table is added to the blacklist, covering two scenarios: Schema Evolution failure and a single field value exceeding the 10 MB size limit.

     ![](.topwrite/assets/image_1740315081002.png =460)

   * Schema Evolution failure alert: create a new monitoring rule and select "Multi-table real-time sync target table change failure."

     ![](.topwrite/assets/image_1740315087204.png =460)

#### Configuring Maximum Latency Monitoring for Real-Time Data Integration Tasks

1. **End-to-end sync latency**: create a new monitoring rule and select "Multi-table real-time sync latency." You can add filter attributes such as workspace or task name. If no filter is added, all multi-table real-time sync tasks in the instance are monitored by default.

   ![](.topwrite/assets/image_1740315096380.png =680)

2. **Read checkpoint latency**: create a new monitoring rule and select "Multi-table real-time sync read checkpoint latency." You can add filter attributes such as workspace or task name. If no filter is added, all multi-table real-time sync tasks in the instance are monitored by default.

   ![](.topwrite/assets/image_1740315103745.png =680)

## Common Error Troubleshooting

### Incremental Sync Failure

#### Binlog Checkpoint Expired

* Problem

  * The task is started with a specific file and position, or it was stopped for some time and then resumed from a saved state — and now it fails. The execution log contains: `Caused by: java.lang.IllegalStateException: The connector is trying to read binlog starting at Struct{version=1.9.7.Final,connector=mysql,name=mysql_binlog_source,ts_ms=1734071479878,db=,server_id=0,file=mysql-bin.010937,pos=432041283,row=0}, but this is no longer available on the server. Reconfigure the connector to use a snapshot when needed.`

* Cause

  * MySQL binlogs are not kept indefinitely — they are purged periodically. If the specified binlog file or position has already been cleaned up, or if the task was stopped long enough that the auto-resumed position no longer exists, this error occurs.

* Resolution

  * Query the current binlog file and position with `SHOW MASTER STATUS`:

    ![](.topwrite/assets/image_1740315126085.png =460)

  * Restart the sync task using the file and position from the result.

    ![](.topwrite/assets/image_1740315139248.png =460)

  * If you need to recover the data that was missed, resync the affected tables.

#### Server-ID Conflict

* Problem

  * The task fails to start. The execution log contains: `A slave with the same server_uuid/server_id as this slave has connected to the master; the first event '' at 4, the last event read from '/home/mysql/log/mysql/mysql-bin.011268' at 90995258, the last byte read from '/home/mysql/log/mysql/mysql-bin.011268' at 90995258. Error code: 1236; SQLSTATE: HY000. The 'server-id' in the mysql cdc connector should be globally unique, but conflicts happen now.`

* Cause

  * The real-time sync task assigns a unique server-id (in the range 5400–6400) to each MySQL data source connection. If this error occurs, the assigned server-id conflicts with another sync tool or task connected to the same database.

* Resolution

  * Check whether another sync task or tool is connected to the same database instance and consuming binlog with a conflicting server-id.
  * Restart the sync task.

#### Data Source Timezone Misconfiguration

* Problem

  * The task fails to start. The execution log contains: `Caused by: org.apache.flink.table.api.ValidationException: The MySQL server has a timezone offset (28800 seconds ahead of UTC) which does not match the configured timezone Etc/GMT+12. Specify the right server-time-zone to avoid inconsistencies for time-related fields.`

* Cause

  * The timezone configured in the data source connection (default: Asia/Shanghai) does not match the actual timezone configured in the database.

* Resolution

  * Confirm the database's timezone setting, then update the timezone in the data source configuration to match.

#### Binlog Event Size Exceeds Limit

* Problem

  * The task fails. The execution log contains: `Caused by: io.debezium.DebeziumException: log event entry exceeded max_allowed_packet; Increase max_allowed_packet on master; the first event '' at 58722808, the last event read from '/rdsdbdata/log/binlog/mysql-bin-changelog.004054' at 109251835, the last byte read from '/rdsdbdata/log/binlog/mysql-bin-changelog.004054' at 109251854. Error code: 1236; SQLSTATE: HY000.`

* Cause

  * The database's `max_allowed_packet` setting is smaller than the size of a binlog event.
  * The binlog file may be corrupted.

* Resolution

  * Contact your DBA to increase the database's `max_allowed_packet` parameter (maximum: 1 GB). Restart the sync task after the change takes effect.
  * If the task still fails after adjusting `max_allowed_packet`, the binlog file may be corrupted. Restart the task and choose a more recent checkpoint to skip the problematic event and continue incremental sync. If you need to recover any missing data, resync the affected tables from scratch.

### Full Sync Failure

#### Primary Key Length Exceeds Limit

* Problem

  * Full sync fails. The execution log contains: `BulkLoad stream error com.dtstack.flinkx.throwable.FlinkxRuntimeException: BulkLoad failed, stream id: bulkload_stream_xxx final status:COMMIT_FAILED, error msg:Task lost connection, message: container stopped by AM. Detail CZLH-71006:Encoded key size 191 exceeds max size 128`

* Cause

  * The total encoded length of the primary key fields in the source table exceeds the default limit of 128 bytes.
  * In a merge scenario, multiple extended fields (e.g., server_id, database, schema, table) are included in the composite primary key to prevent conflicts across sharded tables — and the total encoded key length exceeds 128 bytes.

* Resolution

  * Modify the sync task configuration to add the following parameters:

  ```Bash
    step1.containerized.taskmanager.env.pk_encoded_key_override_size 256step2.containerized.taskmanager.env.pk_encoded_key_override_size 256
  ```

### Sync Task Failover

#### Disconnected from Lakehouse Ingestion Service

* Problem

  * The task fails over. The failover details contain: `java.util.concurrent.ExecutionException: java.lang.RuntimeException: java.lang.RuntimeException: java.io.IOException: Async commit for instance [270076] workspace [xsy_ent] failed. Error detail is:rpcProxy call hit final failed after max retry reached. at com.dtstack.flinkx.connector.lakehouse.sink.LakeHouseRedisMetaHybridIgsMultiWriter.flushInternal`

* Cause

  * This typically occurs during a Lakehouse service upgrade, which causes the sync task to lose its connection to the Lakehouse Ingestion Service.

* Resolution

  * This generally resolves itself after the upgrade completes.
  * If the task continues to fail over after the upgrade is done, try restarting it manually.
  * If the task still does not recover after a manual restart, check the health status of the Lakehouse Ingestion Service.

#### Binlog Event Deserialization Failure

* Problem

  * The task fails over. The failover details contain: `com.github.shyiko.mysql.binlog.event.deserialization.EventDataDeserializationException: Failed to deserialize data of EventHeaderV4`

* Cause

  * This typically occurs when the source database's binlog suddenly receives a large volume of events — for example, a mass data update or bulk historical data deletion. The write side of the sync task cannot process all the data in time, causing backpressure that halts the read side. The binlog client's connection to the database server is then terminated due to timeout or idle thread recycling, resulting in incomplete binlog event messages and deserialization failure.

* Resolution

  * If the traffic spike is short-lived, the sync task should recover on its own within a limited number of failovers.
  * If the problem persists, try increasing the MySQL `slave_net_timeout` and `thread_pool_idle_timeout` values.
  * Temporary adjustment (resets on MySQL restart):

  ```SQL
    set global slave_net_timeout = 120; -- default 60 secondsset global thread_pool_idle_timeout = 120; -- default 60 seconds
  ```

  * Permanent adjustment — edit the MySQL configuration file:

  ```Bash
    [mysqld]slave_net_timeout = 120thread_pool_idle_timeout = 120
  ```

### Table Added to Blacklist

#### Schema Evolution Failure

* Problem

  *   A table's status automatically changes to "sync stopped." The tooltip on the table object shows errors such as `pk column different`, `pk column type mismatch`, or `invalid modify column`.

* Cause

  * The source table structure has been changed in a way that Lakehouse does not support, including:
  * The primary key (PK) column list changed — for example, a PK column was renamed, or a single-column PK was changed to a composite PK.
  * The PK column type changed — for example, from `bigint` to `varchar`.
  * A field type was modified in an incompatible way — for example, from `int` to `double`.

* Resolution

  * Review the source table structure and revert it to the correct state.
  * Resync the table that stopped incremental sync from scratch. After full sync completes, incremental sync will resume automatically.

## Known Limitations and Important Notes

* To prevent write conflicts on the target, only source tables with primary key (PK) fields are supported. Tables without a primary key cannot be synced.
* The sync task will automatically create target tables. To ensure stable task execution and data correctness, avoid manually creating, modifying, or deleting target tables unless absolutely necessary.
* Schema Evolution supports adding and removing columns on the source. Changing column types and automatically adding new tables are not currently supported.
