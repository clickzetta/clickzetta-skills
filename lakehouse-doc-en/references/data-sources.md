# Data Source Support Scope

Before using the data synchronization service, to ensure your synchronization needs are met, first confirm whether the data synchronization service covers your required data sources and select the appropriate task type. Currently, the data synchronization service supports the following three sync task types:

1. Single-table offline sync: Applicable to supported data sources, providing offline sync for single-table reads and writes.
2. Single-table real-time sync: For supported data sources, implementing real-time sync for single-table reads and writes.
3. Multi-table real-time sync: For supported data sources, providing multi-table functionality with one-time full sync and real-time incremental sync.

The data source types and versions currently supported by each task type are as follows (including but not limited to the following types; please refer to the actual support within the product):

### Offline Sync

| Data Source | Release Level | Offline Single-Table Read | Offline Single-Table Write | Supported Versions |
| --------------------- | ------- | ---- | ---- | --------------------- |
| Singdata Lakehouse | GA | Y | Y | - |
| ADB MySQL              | GA (Beta) | Y     | Y     | 3.x                    |
| ADB PostgreSQL         | GA (Beta) | Y     | Y     | 6.x                    |
| AMQP                   | GA (Beta) | Y     | N     | -                      |
| AutoMQ                 | GA       | Y     | Y     | -                      |
| ClickHouse | GA | Y | Y | 19.x and above |
| COS                    | GA       | Y     | Y     | -                      |
| Databricks             | GA       | Y     | Y     | -                      |
| DB2                    | GA (Beta) | Y     | Y     | 11.x                   |
| DM                     | GA (Beta) | Y     | Y     | 8.x                    |
| Doris                  | GA (Beta) | Y     | Y     | 1.x                    |
| DynamoDB               | GA       | Y     | Y     | -                      |
| Elasticsearch          | GA       | Y     | Y     | 7.x                    |
| Greenplum | GA (Beta) | Y | Y | 5.x and above |
| HBase | GA | N | Y | 1.4+ |
| Hive                   | GA       | Y     | Y     | 2.x                    |
| Hologres               | GA (Beta) | Y     | Y     | -                      |
| Kafka | GA | Y | Y | 0.8.x, 0.9.x, 0.10.x, 2.x |
| MaxCompute             | GA       | Y     | N     | -                      |
| MariaDB                | GA (Beta) | Y     | Y     | -                      |
| MongoDB | GA | Y | N | 3.4 and above |
| MySQL                  | GA       | Y     | Y     | 5.x, 8.x                |
| Oracle                 | GA (Beta) | Y     | Y     | -                      |
| OSS                    | GA       | Y     | Y     | -                      |
| PolarDB for MySQL      | GA       | Y     | Y     | -                      |
| PolarDB for PostgreSQL | GA       | Y     | Y     | -                      |
| PostgreSQL | GA | Y | Y | 9.4 and above |
| Redis                  | GA       | N     | Y     | -                      |
| Redshift               | GA (Beta) | Y     | Y     | -                      |
| RestApi                | GA       | Y     | N     | -                      |
| SLS (LogHub)            | GA       | Y     | N     | -                      |
| SQL Server | GA | Y | Y | 2012 and above |
| StarRocks              | GA (Beta) | Y     | Y     | 2.5                    |
| TiDB                   | GA (Beta) | Y     | Y     | -                      |

### Real-Time Sync

| Data Source | Release Level | Real-Time Single-Table Read | Real-Time Multi-Table Read | Real-Time Write | Supported Versions |
| --------------- | --- | ---- | ---- | ---- | ---- |
| Singdata Lakehouse | GA | N | N | Y | - |
| AutoMQ                 | GA   | Y     | N     | N   | -             |
| Kafka | GA | Y | N | Y | 0.8.x, 0.9.x, 0.10.x, 2.x |
| MySQL | GA | Y | Y | N | 5.x, 8.x |
| PolarDB for MySQL      | GA   | Y     | Y     | N   | -         |
| PolarDB for PostgreSQL | GA   | Y     | Y     | N   | -       |
| SQL Server | GA | Y | Y | N | SQL Server 2016 Service Pack 1 (SP1) and above |

^
