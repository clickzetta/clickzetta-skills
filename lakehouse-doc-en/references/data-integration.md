# Data Integration

Singdata Lakehouse Studio includes a full-featured data integration capability that supports 40+ data sources with visual configuration — no coding required. It covers real-time CDC sync, offline batch sync, full-database migration, and more.

## Choosing a Sync Approach

| My scenario                                                 | Recommended approach       | Documentation                                                                |
| ----------------------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------- |
| MySQL / PG / Oracle or similar — single-table real-time CDC | Real-time sync task        | [Real-time Sync Task](realtime_sync.md)                                      |
| Full-database migration, syncing multiple tables together   | Multi-table real-time sync | [Multi-table Real-time Sync Complete Guide](multitable_realtime_sync_sop.md) |
| Scheduled batch sync (T+1 or hourly)                        | Offline sync task          | [Offline Sync Task](batch_sync.md)                                           |
| Full-database offline migration, multiple tables at once    | Multi-table offline sync   | [Multi-table Offline Sync Task](multitable_batch_sync.md)                    |
| Not sure which to use                                       | Check supported sources    | [Data Source Support](data-sources.md)                                       |

## Quick Start

**Step 1** — [Configure a data source](config-datasource.md): add the connection details for your source database

**Step 2** — Create a sync task based on your scenario (see the table above)

**Step 3** — Configure a scheduling policy and publish the task

**Step 4** — Monitor run status and configure alerting

> 💡 **Tip**: Configuring a data source for the first time? Check the [Data Source Configuration Guide](datasource-config-guide.md) to find your database type and follow the step-by-step setup.

## Scheduling, Deployment, and Operations

| Scenario                                                | Documentation                                                                                         |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Configure scheduled runs and task dependencies          | [Task Scheduling](task_scheduling.md) · [Task Scheduling Dependencies](task_scheduling_dependency.md) |
| Publish / unpublish a task                              | [Task and Instance Operations](task-instance-maintenance.md)                                          |
| View run history, logs, and failure details             | [Task and Instance Operations](task-instance-maintenance.md)                                          |
| Configure alert notifications (DingTalk / Lark / email) | [Monitoring and Alerting](monitoring_and_alerting.md)                                                 |
| Understand monitoring metric definitions                | [Monitoring Metric Specifications](monitoring_item_specification.md)                                  |
| Backfill historical data                                | [Data Backfill Tasks](backfilling_data.md)                                                            |

## Contents of This Section

| Page                                                                         | Description                                                  |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------ |
| [Overview](data-integration-intro.md)                                        | Basic concepts, task types, and core components of data sync |
| [Data Source Management](config-datasource.md)                               | Add and manage data source connections                       |
| [Supported Data Sources](data-sources.md)                                    | List of 40+ supported data sources                           |
| [Data Source Configuration Guide](datasource-config-guide.md)                | Detailed setup steps for each database type                  |
| [Offline Sync Task](batch_sync.md)                                           | Scheduled batch sync with full and incremental modes         |
| [Multi-table Offline Sync Task](multitable_batch_sync.md)                    | Full-database offline migration                              |
| [Real-time Sync Task](realtime_sync.md)                                      | Single-table real-time CDC sync                              |
| [Multi-table Real-time Sync Task](multitable_realtime_sync.md)               | Full-database real-time CDC sync                             |
| [Multi-table Real-time Sync Complete Guide](multitable_realtime_sync_sop.md) | End-to-end SOP for full-database migration                   |
| [Offline Sync FAQ](batch_sync_sop.md)                                        | Common questions and usage guide                             |

^
