# Lakehouse Studio

Lakehouse Studio is Singdata Lakehouse's **unified data development and governance platform**, providing a complete workflow from data ingestion, processing, and analysis to operations.

## What is Lakehouse Studio

Studio is a web-based graphical interface natively provided by Lakehouse. Users can perform all data operations through a browser without writing code or using command-line tools.

**Core Positioning**: A one-stop data platform entry point, covering the daily needs of data engineers, analysts, and operations personnel.

## Six Core Modules

| Module                    | Function                                                                                                             | Typical Users   |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------- |
| **Data Sync**             | Visually configure data sources, supporting offline batch sync and real-time CDC sync for 40+ data sources           | Data Engineers  |
| **Task Development**      | Visual IDE for writing SQL/Python/Shell tasks, supporting composite tasks, loops, branching, and other orchestration | Data Engineers  |
| **Task Scheduling**       | Cron scheduling + dependency management, automatically orchestrating upstream and downstream tasks                   | Data Engineers  |
| **Operations Monitoring** | View task run status, logs, duration, configure alert rules and backfill operations                                  | Data Operations |
| **Data Catalog**          | Manage table/view metadata, configure data quality rules, cross-instance data sharing                                | Data Governance |
| **Analysis**              | Interactive Notebook, supporting SQL query result visualization and data profiling                                   | Data Analysts   |

## Relationship Between Studio and CLI

| Dimension                | Studio                                                       | CLI / SQL                                      |
| ------------------------ | ------------------------------------------------------------ | ---------------------------------------------- |
| **Usage Mode**           | Browser graphical interface                                  | Command line / JDBC / SDK                      |
| **Applicable Scenarios** | Daily development, task orchestration, operations monitoring | Automation scripts, CI/CD, AI Agent            |
| **Learning Curve**       | Low (visual operations)                                      | Medium (requires SQL/command syntax knowledge) |
| **Recommended Users**    | Data engineers, analysts, operations personnel               | Developers, AI Agents, automation workflows    |

The two complement each other: Studio is suitable for daily development and visual operations, while CLI is suitable for automation and integration scenarios.

## Quick Start

* [Lakehouse Studio Quick Tour](LakehouseStudio-tour.md) — Understand interface layout and feature entry points
* [Lakehouse Studio Getting Started Guide](lakehouse-studio-101.md) — Start using Studio from scratch
* [Data Analytics Agent (DataGPT) Quick Tour](LakehouseDataGPT-tour.md) — AI-assisted data analysis

## Related Documentation

* [Studio Manual](studio_manual.md) — Complete feature descriptions
* [Task Development and Scheduling](task-develop.md) — Detailed guide for task development
* [Data Synchronization](data-integration.md) — Data source configuration and sync tasks
* [Operations Monitoring](data_ops.md) — Task operations and alert configuration

^
