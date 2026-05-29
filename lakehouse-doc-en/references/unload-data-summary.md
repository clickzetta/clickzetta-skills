# Data Export Overview

The Lakehouse big data compute engine provides flexible data export functionality, allowing users to export data in CSV file format for local use or in other data analysis platforms. It also supports data integration tools that cover a wide range of data sources such as MySQL, PostgreSQL, HIVE, TIDB, and StarRocks.

## Data Export Methods Overview

:-: ![](.topwrite/assets/image_1714295263012.png =543)

## By Export Method

| Export Method                                                 | Use Case                                                     | Limitations                                         |
| ---------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------ |
| [Using Lakehouse Studio's Visual Download Interface](unload-data-local.md)  | 1. User-friendly interface that simplifies the export workflow. 2. Supports custom SQL to download SQL result sets.                     | 1. Currently only supports CSV files. 2. Does not support complex types: map, struct, array, json |
| [Using JDBC Client](unload-data-local.md)               | 1. Suitable for technical users, especially those familiar with command-line operations and needing to export small data volumes in batches. 2. Supports custom SQL to download SQL result sets. | 1. Currently only supports CSV files. 2. Does not support complex types: map, struct, array, json |
| [Using Lakehouse Studio Data Integration](data-integration-intro.md) | 1. Supports a wide range of data sources and multiple export methods. 2. Supports scheduled execution, task monitoring, and visual operations management.                    |                                            |

^
