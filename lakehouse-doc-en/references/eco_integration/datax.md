# DataX ClickZettaWriter Plugin

> 💡 **If your goal with DataX is to batch-sync data into Singdata Lakehouse**, Singdata Studio provides a visual offline sync solution that requires no JSON configuration files:
>
> | Scenario | Recommended Solution | Description |
> |------|---------|------|
> | Batch sync from relational databases (MySQL / PG / Oracle, etc.) | [Studio Offline Sync Task](../batch_sync.md) | Wizard-based configuration, supports scheduled dispatch, supports 40+ data sources |
> | Full database migration, syncing multiple tables at once | [Multi-table Offline Sync](../multitable_batch_sync.md) | Sync an entire database in one task, with automatic table creation and field mapping |
> | Real-time CDC sync | [Studio Real-time Sync Task](../realtime_sync.md) | If you need real-time rather than batch, DataX does not support CDC — use a real-time sync task instead |
>
> If you already have DataX jobs or need DataX-specific transformation capabilities, continue reading the integration guide below.

---

## DataX Introduction

DataX is an open-source data synchronization tool by Alibaba, supporting multiple data sources including relational databases, HDFS, Hive, MaxCompute, HBase, FTP, and local files. This document will introduce how to use the DataX ClickZettaWriter plugin to synchronize DataX data to Singdata Lakehouse.

## Usage Restrictions

- vector and json types are not supported

## Preparations

1. Please ensure that DataX is installed. For specific installation methods, please refer to the [DataX User Guide](https://github.com/alibaba/DataX/blob/master/userGuid.md).
2. Download the DataX ClickZettaWriter plugin from the following address: [DataX ClickzettaWriter Plugin](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/dataxwriter/datax.tar.gz). Unzip the plugin into the `plugin/writer` directory under the DataX installation directory.
3. Before using the DataX ClickZettaWriter plugin, please ensure that the corresponding table has been created in Singdata Lakehouse.

## Using the DataX ClickZettaWriter Plugin

### 1. Create Configuration File

The following example demonstrates how to use the DataX ClickZettaWriter plugin to synchronize MySQL data to Singdata Lakehouse.
```json
{
  "job": {
    "content": [
      {
        "reader": {
            "name": "mysqlreader",
            "parameter": {
                "column": ["*"],
                "connection": [
                    {
                        "jdbcUrl": ["jdbc:mysql://mysql_host:mysql_port/database?useSSL=false"],
                        "table": ["test_table"]
                    }
                ],
                "password": "example",
                "username": "example",
                "where": ""
            }
        },
        "writer": {
          "name": "clickzettawriter",
          "parameter": {
              "column": ["*"],
              "connection": [
                  {
                      "jdbcUrl": "jdbc:clickzetta://instance.service/workspace?schema=example&username=example&password=example&vcluster=example",
                      "table": ["test_table"]
                  }
              ],
              "password": "example",
              "username": "example",
              "preSql": [],
              "postSql": [],
              "writeMode": "overwrite",
              "tableNumber": "1",
              "partitionColumns": {
                  "region" : "example"
              }
          }
        }
      }
    ],
    "setting": {
      "speed": {
        "channel": 1
      }
    }
  }
}
```
Configuration Instructions:

* `mysqlreader`: The built-in mysqlreader plugin in DataX, used for reading MySQL data. For specific usage, please refer to the [mysqlreader plugin documentation](https://github.com/alibaba/DataX/blob/master/mysqlreader/doc/mysqlreader.md).
* `clickzettawriter` parameter instructions:
  * `jdbcUrl`: LakeHouse JDBC connection information.
  * `table`: The name of the table to write to (only supports writing to one table).
  * `column`: The names of the columns to write to (`*` asterisk indicates all columns).
  * `partitionColumns`: The names of the partition columns, used for partitioned table writing (the columns specified in `column` plus the partition columns must be all columns of the table).
  * `writeMode`: The write mode, optional values are `append`, `overwrite`, and `upsert`, default is `append`.
  * `username`: LakeHouse username.
  * `password`: LakeHouse password.
  * `preSql`: SQL statements to be executed before writing.
  * `postSql`: SQL statements to be executed after writing.

### 2. Execute the Synchronization Task

Run the following command to execute the synchronization task:
```shell
python bin/datax.py job.json
```
## Usage Example

### Example 1: Sync MySQL Data to Singdata Lakehouse

The following configuration file example synchronizes the `test_table` data in MySQL to the `example_table` in Singdata Lakehouse.
```json
{
    "job": {
        "content": [
            {
                "reader": {
                    "name": "mysqlreader",
                    "parameter": {
			"column": ["*"],
               		"connection": [
                  	  {
                        	"jdbcUrl": ["jdbc:mysql://mysql_host:mysql_port/database?useSSL=false"],
                      		"table": ["test_table"]
                    }
                ],
                "password": "example",
                "username": "example",
                "where": ""
                    }
                },
                "writer": {
                	          "name": "clickzettawriter",
          "parameter": {
              "column": ["*"],
              "connection": [
                  {
                      "jdbcUrl": "jdbc:clickzetta://your_instance_name.api.singdata.com/your_workspace_name?schema=sample&username=your_user_name&password=your_password&vcluster=your_vcluster_name",
                      "table": ["example_table"]
                  }
              ],
                      "partitionColumns": {
                        "region" : "example"
                      },
              "password": "your_password",
              "preSql": [],
              "session": [],
              "username": "your_user_name",
              "writeMode": "append",
              "tableNumber": "1"
          }
        }
      }
    ],
    "setting": {
      "speed": {
        "channel": 1
       }
    }
  }
}
        
```

^
