# Data Export Overview

The Lakehouse big data computing engine provides flexible data export functionality, allowing users to export data in CSV file format for use locally or on other data analysis platforms. It also supports the use of data integration tools, which support a variety of data sources such as MySQL, PostgreSQL, HIVE, TIDB, StarRocks.

## Overview of Data Export Methods

:-: ![](.topwrite/assets/image_1739954699659.png =518)

## Classification by Export Method

| Export Method                                                                   | Use Case                                                                                                                                                                                           | Limitations                                                                                          |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| [Using the visual download interface of Lakehouse Studio](unload-data-local.md) | 1. User-friendly interface, simplifies the export process 2. Supports custom SQL to download the result set of SQL                                                                                 | 1. Currently only supports CSV files 2. Does not support complex types like map, struct, array, json |
| [Using Jdbc client](unload-data-local.md)                                       | 1. Suitable for technical users, especially those familiar with command line operations and need to export small amounts of data in bulk. 2. Supports custom SQL to download the result set of SQL | 1. Currently only supports CSV files 2. Does not support complex types like map, struct, array, json |
| [Using Lakehouse Studio's data integration](data-integration-intro.md)          | 1. Supports a variety of data sources and multiple export methods. 2. Supports periodic scheduling, task monitoring, and visual operations and maintenance                                         |                                                                                                      |

^
