# Multi-Table Batch Sync Task

## Overview

Multi-Table Batch Sync Task is a bulk data synchronization capability provided by Yunqi Lakehouse Studio, supporting scheduled synchronization of an entire database or multiple tables from source to Lakehouse. Unlike Multi-Table Real-time Sync Tasks, Multi-Table Batch Sync adopts periodic full synchronization, making it suitable for scenarios where data latency requirements are relatively relaxed and data updates follow periodic patterns.

## Use Cases

Multi-Table Batch Sync Tasks are suitable for the following scenarios:

* **Full Database Migration**: Batch synchronization of all tables from source database to Lakehouse, reducing table-by-table configuration effort
* **Periodic Data Updates**: Source data updates in fixed cycles (e.g., daily, hourly) without requiring real-time synchronization
* **Sharded Database and Table Consolidation**: Consolidating data from multiple sharded databases and tables into unified target tables
* **Periodic Data Reconciliation**: Ensuring target data consistency with source through periodic full synchronization
* **Resource Optimization**: Reducing resource consumption through batch sync when data latency requirements are not stringent

## Features

### Supported Data Sources

**Source**

* MySQL
* PostgreSQL
* SQL Server
* Aurora MySQL
* Aurora PostgreSQL
* PolarDB MySQL
* PolarDB PostgreSQL

**Target**

* Lakehouse

### Synchronization Modes

1. **Full Database Mirroring**: Synchronizes all tables from the source database to the target.
2. **Multi-Table Mirroring**: Selects multiple source tables for synchronization to the target, maintaining independent table structures.
3. **Multi-Table Merge**: Consolidates multiple source tables (e.g., sharded databases and tables) into one or more target tables.

### Core Capabilities

* **Automatic Table Creation**: Automatically creates tables on target when they don't exist, supporting both primary key and non-primary key tables. Supports flexible use of parameters to customize target table naming.
* **Schema Evolution**: Supports automatic synchronization of source schema changes to target (optional).
* **Flexible Write Modes**: Supports multiple write modes including overwrite, upsert, and more.
* **Concurrency Control**: Supports configuration of grouping strategies and concurrency levels to optimize sync performance and flexibly control pressure on source.
* **Scheduling Management**: Flexible scheduling configuration based on Cron expressions, can be orchestrated with other task nodes.

## Operation Steps

### Step 1: Create Task

1. In the Lakehouse Studio Development module, click the "New" button
2. Select "Multi-Table Batch Sync" from task types (located under "Data Synchronization" category)
3. Enter task name and select folder

### Step 2: Configure Source Data

#### Select Data Source Type

In the "Data Source Type" section, select source and target data source types:

* Source: Select the database type to be synchronized (e.g., PostgreSQL, MySQL, etc.)
* Target: Select Lakehouse

#### Select Source Data Source

1. Select a configured data source connection from the "Source Data Source" dropdown
2. The system will automatically load the database list under that data source

#### Configure Sync Objects

Select sync objects based on your requirements:

**Full Database Mirroring Mode**

* Select an entire database for synchronization
* The system will automatically synchronize all tables under that database

**Multi-Table Mirroring Mode**

* Expand database and schema structures
* Check the tables to be synchronized
* Supports batch selection at three levels: database, schema, and table

**Multi-Table Merge Mode**

* Additionally configure virtual tables to express merge relationships from multiple source tables to target tables
* Supports batch rule configuration at database, schema, and table levels to define source table scope and merge into the same target table

**Sync Object Filtering**

* Use search box for quick table location
* Supports filtering by selected/schema/table
* Upper right corner displays statistics of selected objects (e.g., "Selected: 3 Databases 45 Tables")

### Step 3: Configure Target Settings

#### Select Target Data Source

Select target Lakehouse data source in the "Data Source Type" section

#### Configure Target Data Source

1. Select target workspace
2. Configure target namespace (Schema)

#### Namespace Rules

The system provides three naming rules:

* **Mirror Source**: Maintains consistency with source schema name
* **Specify Selection**: Manually select an existing target schema
* **Custom**: Use rule expressions to customize target schema name

**Rule Expression Instructions**

* Supports using variables:

  * `{SOURCE_DATABASE}` represents source database name

* Supports using custom task parameters:

  * Such as `${bizdate}`, etc. For task parameter usage, see: [Task Parameters](task_param.md)

* Example: `{SOURCE_DATABASE}_${bizdate}`

#### Target Table Naming Rules

Configure target table naming rules:

* **Mirror Source**: Maintains consistency with source table name
* **Custom**: Use rule expressions to customize target table name

**Rule Expression Instructions**

* Supports using variables:

  * `{SOURCE_DATABASE}` represents source database name, `{SOURCE_SCHEMA}` represents source schema name, `{SOURCE_TABLE}` represents source table name

* Supports using custom task parameters:

  * Such as `${bizdate}`, etc. For task parameter usage, see: [Task Parameters](task_param.md)

* Example: `{SOURCE_DATABASE}_{SOURCE_TABLE}_${bizdate}`

#### Partition Configuration (Optional)

If creating partitioned tables, configure:

* Whether to create as partitioned table
* Partition field selection
* Partition value expression

### Step 4: Configure Mapping Relationships

#### View Sync Objects

The system displays all configured sync objects and their mapping relationships:

* Left side shows source table list
* Middle shows field-level mapping details
* Right side shows complete target table path

#### Field Mapping

* System automatically identifies primary keys (marked as PK)
* Displays field type mapping relationships
* Supports viewing detailed field mappings for each table

Statistics display:

* Number of successfully mapped objects
* Number of failed mappings (if any)

### Step 5: Configure Sync Rules

#### Source Data Rules

**Source Data Field Deletion**

* Continue sync, write Null values for deleted fields

**Source Data Field Addition**

* Auto-adapt, add new fields in target table

**Source Data Table Deletion**

* Auto-adapt, continue sync, ignore deleted tables

#### Grouping Strategy

Controls grouping and concurrent execution of sync tasks:

**Smart Grouping**

* System automatically groups based on table size and other characteristics

**Static Grouping**

* Groups based on fixed number of tables
* Configurable number of tables per group

#### Concurrency Control

**Number of Tables per Group**

* Manually specified in static grouping mode
* Controls the number of tables in a single group
* Default: 4

**Maximum Source Connections per Group**

* Limits maximum concurrent connections to source per group
* Default: 4

**Number of Concurrent Groups**

* Number of groups that can execute simultaneously
* Default: 2

> **Performance Tuning Recommendation**: Excessive concurrency may impose pressure on source database. Configure appropriately based on source database performance.

#### Data Write Mode

Configure write strategies for different table types:

**Non-Primary Key Table Write Mode**

* **Overwrite**: Clears target table and writes new data with each sync

**Primary Key Table Write Mode**

* **Overwrite**: Clears target table and writes new data with each sync
* **Upsert**: Performs insert or update operations based on primary key

### Step 6: Task Debugging (Optional)

After completing task configuration and saving, you will enter the task overview page. The "Run" button in the upper right corner provides functionality to debug and verify if data sources and task configuration are correct. After triggering the run, you can view run details in "Run History" at the lower right corner of the page.

> Please note: To control validation sync duration, the system automatically adds a limit of extracting only 1,000 rows per source table by default during runtime (can be manually adjusted, maximum 10,000 rows). For full synchronization of all data, please refer to subsequent steps to configure scheduled execution.

### Step 7: Configure Scheduling Properties

Click the "Schedule" button to configure periodic scheduling rules for the task:

1. **Scheduling Frequency**: Select scheduling frequency as needed, such as daily or hourly scheduling

2. **Scheduling Cycle**:

   1. Supports multiple cycles including hourly, daily, weekly, monthly
   2. Can use visual configuration (system automatically converts to Cron expression)

3. **Effective Date and Expiration Date**: Set start and end dates for task scheduling

4. **Dependency Configuration**: Set upstream and downstream dependencies for the task (optional)

5. **Other Configuration**: Instance information and other configurations, same as periodic scheduling configuration for regular tasks

### Step 8: Submit Task

1. Click "Submit" button after completing configuration
2. System performs configuration validation
3. After successful submission, task enters scheduling system and executes automatically according to set cycle

## Task Operations

In "Task Operations", Multi-Table Batch Sync Tasks are categorized under "Scheduled Tasks". Click task name to drill down into detailed task information.

### Task Details

In the task details page, you can view:

**Task Details Tab**

* Displays DAG diagram of task upstream and downstream dependencies
* Task configuration information
* Scheduling configuration
* Owner information

**Task Instances Tab**

* Displays complete instance list of the task, including manually triggered temporary runs and scheduled periodic instances
* Click on specific instance for details

**Node Code Tab**

* Code representation of task configuration information

**Sync Objects Tab**

* View all source and target tables configured in the task
* View field mapping relationships
* Reflects current configuration status in real-time

**Operation Log Tab**

* Displays audit information for operations such as pause/start, publish/update, etc.

### Task Operations

**Edit**:

* Quick jump to task development interface to modify task configuration

**Pause/Resume**: Pause or resume scheduled execution

**Offline**:

* Stops task and removes from scheduling system, task reverts to unsubmitted scheduling state
* Offline (including downstream): Use this function to offline current task and its downstream together. If task has downstream, individual offline is not allowed

**Backfill**:

* Performs data backfill for historical cycles

### Instance Management

#### Instance List

Each task execution generates an instance. Under "Task Operations" -> "Instance Operations" tab, you can view task instances of Multi-Table Batch Sync Tasks.

#### Instance Details

Click instance ID to view detailed instance information.

**Instance Details Tab**

* Upstream and downstream DAG task lineage relationships for this instance
* Instance status, start time, end time
* Runtime statistics

**Sync Objects Tab**

* View all tables synchronized in this execution
* Display read rows, written rows, sync rate for each table
* Show execution status for each table

**Script Content Tab**

* Code representation of task configuration information for this instance

**Execution Log Tab**

* View detailed execution logs
* Includes logs for initialization, table synchronization, completion, and other stages

**Operation Log Tab**

* Displays audit logs for operations such as rerun, set success/set failure, etc.

#### Instance Operations

**Rerun**

* Re-execute this instance

* Supports selecting rerun scope:

  * All Objects: Re-synchronize all tables
  * Failed Objects Only: Rerun only failed synchronizations

**Set Success/Set Failure**

* Manually set final status of instance

**Cancel Run**

* Forcibly terminate running instance

**Single Table Operations** (in Sync Objects Tab)

* View Sync Details: View synchronization details for a single table
* Re-sync: Re-synchronize only this table
* Force Stop: Terminate synchronization of this table

### Monitoring and Alerting

#### Configure Alert Rules

Multi-Table Batch Sync as a whole can have the same monitoring alerts configured as other scheduled tasks. Additionally, alerts can be configured for individual tables within sync tasks:

**Alert Item: Task Instance Failure**

* Alert Type: Event alert
* Trigger Condition: Entire task instance execution fails
* Supports configuring alert filter conditions

**Alert Item: Multi-Table Batch Sync Single Table Sync Failure**

* Alert Type: Event alert
* Trigger Condition: Any target table synchronization failure in the task
* Alert Granularity: Based on target table unit, each failed table independently triggers alert
* Supports configuring alert recipients and notification methods

## Important Notes

### Permission Requirements

* **Source Permissions**: The account configured in the data source needs to have permissions to read source database metadata and table data (SELECT privilege)
* **Target Permissions**: The task owner needs to have permissions to create tables and insert data in target Lakehouse (CREATE, INSERT privileges)

### Performance Considerations

1. **Source Pressure**: Configure concurrency appropriately to avoid excessive pressure on source database.
2. **Initialization Time**: First execution requires initialization of all sync objects, which may take considerable time.
3. **Table Quantity Limit**: It's recommended to control the number of tables synchronized in a single task within a reasonable range; too many tables may affect task execution efficiency.

### Data Consistency

1. **Overwrite Mode**: With overwrite mode, each execution completely refreshes target table data.
2. **Upsert Mode**: With upsert mode, incremental updates are performed based on primary key.
3. **Source Data Changes**: Batch sync adopts periodic full synchronization; data changes between two sync intervals will be reflected in the next synchronization.

### Schema Evolution Limitations

When enabling Schema Evolution functionality, note:

* Does not support modifying primary key fields (Lakehouse primary key table limitation)
* Field type modifications only support same-type extensions (e.g., int8→int16→int32→int64)
* Cross-type conversions (e.g., int→double) are not supported
* Recommended to use this feature when source schema is relatively stable

### Best Practices

1. **Task Granularity**: Reasonably divide task granularity based on business relevance and synchronization requirements
2. **Scheduling Time**: Choose time windows with lower source database pressure for execution
3. **Testing and Validation**: Use "Run" function for small-batch data testing before formal scheduling
4. **Monitoring Configuration**: Configure alert rules promptly to ensure quick awareness of synchronization anomalies
5. **Regular Checks**: Regularly review "Table Auto-change Records" to understand schema changes

## Related Documentation

* [Task Development](ide.md)
* [Data Source Connection Configuration](config-datasource.md)
* [Task and Instance Operations](task-instance-maintenance.md)

For other questions, please contact technical support or consult the complete product documentation.
