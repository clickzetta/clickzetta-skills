# Data Lifecycle

The data lifecycle (TTL) measures the length of time from the last update of tables and table partitions in the Singdata Lakehouse. If the data does not change within the specified period, the system will automatically reclaim the data. The lifecycle unit is days, and the value is an integer.

## How the Data Lifecycle Works

The expiration of the data lifecycle relies on the last modification time (last\_modified\_time). You can view the last\_modified\_time using the `desc extended` command. The last\_modified\_time changes when DDL (Data Definition Language) and DML (Data Manipulation Language) operations occur.

It is important to note that expired data is not immediately reclaimed. You can still query this data until the background process performs the deletion operation. Typically, the background process will delete this data within 24 hours. Additionally, reclaimed tables still adhere to the [data retention period](TIMETRAVEL.md), and you can still query using the [time travel](TIMETRAVEL.md) feature. If you need to restore deleted objects, you can use the [undrop table](UNDROP-TABLE.md) command.

## Setting the Data Lifecycle

The lifecycle unit is days, and the value is a positive integer. Setting it to '-1' means the lifecycle is not enabled, and the data will be retained permanently. You can specify the lifecycle when creating a table or modify it after the table is created.

### Specific SQL Operations

**Setting the lifecycle when creating a table**
```SQL
-- Create a table and set the lifecycle to 7 days
CREATE TABLE tname (col1 datatype1, col2 datatype2) PROPERTIES('data_lifecycle'='7');
-- Create a table and set the lifecycle to 7 days, and delete the table structure when the lifecycle expires
CREATE TABLE tname (col1 datatype1, col2 datatype2) PROPERTIES('data_lifecycle'='7', 'data_lifecycle_delete_meta'='true');
```
**Modify the Lifecycle of an Existing Table**
```SQL
-- Modify the table's lifecycle to 10 days
ALTER TABLE tname SET PROPERTIES ('data_lifecycle'='10');
-- Modify the table's lifecycle to 10 days and delete the table structure when the lifecycle expires
ALTER TABLE tname SET PROPERTIES ('data_lifecycle'='10', 'data_lifecycle_delete_meta'='true');
```
## Precautions

1. Lifecycle recycling is initiated daily at a scheduled time and will scan all partitions. Data will only be recycled when the `last_modified_time` exceeds the time specified by the lifecycle.
2. Lifecycle recycling mainly targets tables or partitions and is performed daily based on the service's busyness. It cannot ensure immediate recycling upon expiration.
3. Upon lifecycle expiration, the default behavior is not to delete the table structure but to clear the data. If you wish to delete the table structure, please add the parameter `ALTER TABLE tname SET PROPERTIES ('data_lifecycle_delete_meta'='true')` when setting the lifecycle.
4. When modifying the lifecycle, for example when you change the lifecycle policy from 15 days to 30 days, the new policy takes effect immediately. However, since the lifecycle recycling task starts at an unscheduled time each day and typically polls every 12 hours, in rare cases, if the recycling task happens to start and reads the old policy at the moment of the policy change, it may recycle some data according to the old policy (15 days). This behavior is a normal mechanism of the system design and does not affect the safety of data that has not yet expired.

By setting a reasonable data lifecycle, you can effectively manage storage space, ensuring timely data updates and cleaning.