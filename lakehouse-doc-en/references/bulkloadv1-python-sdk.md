# Using Python to Upload Data in Batch (BulkLoadV1)



Singdata Lakehouse provides APIs for batch data upload (Bulkload) using Python through the `clickzetta-connector` package. This API allows data to be sent directly from the client to the storage system. The transmission process consumes no compute resources, and data becomes visible after an explicit commit (the commit process consumes a small amount of compute resources). It is suitable for high-throughput scenarios with relatively relaxed data freshness requirements.

Through Bulkload-related APIs, single-threaded data upload can be achieved.

## Installation

If you have an older version of the SDK installed, uninstall it first to avoid conflicts:

```shell
pip uninstall clickzetta-connector clickzetta-connector-python clickzetta-sqlalchemy clickzetta-ingestion-python clickzetta-ingestion-python-v2 -y
```

> Before uninstalling, keep a record of the old package versions in case you need to roll back. Command to view installed package versions:

```shell
pip show clickzetta-connector clickzetta-sqlalchemy clickzetta-ingestion-python clickzetta-ingestion-python-v2 clickzetta-connector-python
```

Install the latest version (requires Python >= 3.7):

```bash
pip install clickzetta-connector -U -i https://pypi.org/simple/
```


## Bulk Import Principles

The Bulkload SDK provides an efficient data import mechanism suitable for Singdata Lakehouse. The following is a simplified description and flow diagram of how it works:

1. **Data Upload**: Through the SDK, your data is first uploaded to the object storage service. The performance of this step is affected by local network speed and the number of concurrent connections.
2. **Trigger Import**: After the data upload is complete, when you call the `bulkloadStream.commit()` method, the SDK automatically triggers an SQL command to import the data from object storage into the Lakehouse table. It is not recommended to call `bulkloadStream.commit()` frequently within a single task; this method should ultimately only be called once.
3. **Compute Resources**: For uploading data, it is recommended to use a [General Purpose Virtual Cluster](virtual-cluster.md). General purpose compute resources are better suited for running batch jobs and data loading jobs. The speed of importing data from object storage to the Lakehouse table depends on the size of your configured compute resources.
4. **Shard Upload Optimization**: When processing compressed data larger than 1GB, it is recommended to assign a unique shard ID to each concurrent thread or process in the `createRow` method. This approach can fully leverage the parallel processing advantages of multi-threading or multi-processing, significantly improving data import efficiency. The best practice is to determine the number of shard IDs based on the number of concurrent workers, ensuring each concurrent worker corresponds to an independent shard ID. If multiple concurrent workers are assigned the same shard ID, the final written data may be overwritten, causing previously written data to be lost. To ensure that data from all shards is correctly imported into the table, call the `bulkloadStream.commit()` method after all concurrent operations are complete to commit the entire import task.

The following is a flow diagram of the bulk import principle:

```
[SDK Upload Data] ──> [Object Storage] ──> [Call bulkloadStream.close()]
                                ↓
                         [Trigger SQL Command] ──> [Lakehouse Table]
```

## Single-threaded Writing

Assume the target table for uploading data is `public.bulkload_test`, with the following DDL:

```sql
CREATE TABLE public.bulkload_test (
    i BIGINT,
    s STRING,
    d DOUBLE
);
```

Complete sample code for single-threaded mode:

```python
from clickzetta import connect

conn = connect(
    username='your_username',
    password='your_password',
    service='<region\_id>.api.singdata.com',
    instance='your_instance',
    workspace='your_workspace',
    schema='public',
    vcluster='default'
)

bulkload_stream = conn.create_bulkload_stream(schema='public', table='bulkload_test')

writer = bulkload_stream.open_writer(0)
for index in range(1000000):
    row = writer.create_row()
    row.set_value('i', index)
    row.set_value('s', 'Hello')
    row.set_value('d', 123.456)
    writer.write(row)
writer.close()

bulkload_stream.commit()
```

## API Step-by-Step Explanation

1. Create the `connection` object by replacing the parameters according to your actual situation:
   ```python
   conn = connect(
       username='your_username',
       password='your_password',
       service='<region\_id>.api.singdata.com',
       instance='your_instance',
       workspace='your_workspace',
       schema='public',
       vcluster='default'
   )
   ```

| **Parameter** | **Required** | **Description**                                                                                                                          |
| --------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| username  | Y        | Username                                                                                                                             |
| password  | Y        | Password                                                                                                                              |
| service   | Y        | The address to connect to Lakehouse, e.g., <region\_id>.api.singdata.com. You can find the JDBC connection string in Lakehouse Studio under **Management** -> **Workspace**![](../.topwrite/assets/image_1728887857029.png) |
| instance  | Y        | You can find the JDBC connection string in Lakehouse Studio under **Management** -> **Workspace**![](../.topwrite/assets/image_1729051500396.png)                                        |
| workspace | Y        | Workspace to use                                                                                                                         |
| vcluster  | Y        | VC to use                                                                                                                           |
| schema    | Y        | Schema name to access                                                                                                                      |

2. Create the `BulkLoad Stream` object, specifying the target table for upload and the upload method:
   **Required Parameters**
   * `table`: Table name
   **Optional Parameters**
   * `schema`: If not specified, uses the `schema` specified in the `connection` object
    * `operation`
        * `BulkLoadOperation.APPEND`: Append mode (all written data is treated as new data, with no impact on existing data)
        * `BulkLoadOperation.OVERWRITE`: Overwrite mode (clears existing table data and writes new data to the table)

* `partition_spec`: Used to specify partition information for the target table, controlling the partition behavior for data writes.
    * Non-partitioned table: Ignore this parameter or set it to empty.
    * Partitioned table:
        * Static partition write: Writes all data to a designated fixed partition. Regardless of the actual values in the partition column of the source data, the `partition_spec` value is used when writing to the target table, and all data is written to the same specified partition. The parameter format is 'partition_col1=value1,partition_col2=value2'.
        * Dynamic partition write: Automatically writes to the corresponding partition based on the actual values of the partition column in the data. By ignoring this parameter, the system automatically creates or writes to the appropriate partition based on the values of the partition column in the data.

  ```python

  from clickzetta.bulkload.bulkload_enums import BulkLoadOperation

  # Build in APPEND mode (APPEND is the default operation)
  bulkload_stream = conn.create_bulkload_stream(schema='public', table='bulkload_append_test')



  # Build in OVERWRITE mode
  bulkload_stream = conn.create_bulkload_stream(
      schema='public',
      table='bulkload_overwrite_test',
      partition_spec='pt=2023-07-01',
      operation=BulkLoadOperation.OVERWRITE
  )
  ```

3. Create a `writer` and write data:
   Each `bulkload stream` can create multiple `writer`s, and different `writer`s must be identified by different IDs. Using multiple `writer`s enables multi-threaded concurrent writing within a single commit.
   ```python
   # Use the open_writer method to create a writer, with the parameter being the writer ID. In single-machine mode, only one writer ID is needed; pass 0 directly.
   writer = bulkload_stream.open_writer(0)
   ```
4. Write data:
   ```python
   # Each row of data must be created using the create_row() method to create a Row object, then write specific data using the set_value() method.
   # The first parameter of set_value() is the column name, and the second parameter is the value
   row = writer.create_row()
   row.set_value('i', 1)
   row.set_value('s', 'January')
   row.set_value('d', 123.456)
   writer.write(row)
   ```
   Data written through the writer will directly form corresponding parquet files in the storage system. The writer will automatically split files based on the amount of data written. After the writer finishes writing data, you must explicitly call writer.close() to ensure data integrity.
   ```python
   writer.close()
   ```
5. Commit the stream. Before committing, ensure all writers have completed writing and are closed. After a successful commit, data becomes visible in the table.
   ```python
   bulkload_stream.commit()
   ```
