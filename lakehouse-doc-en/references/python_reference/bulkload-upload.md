# Using Python for Bulk Data Upload (BulkLoad)

Clickzetta Lakehouse provides a Python API for bulk data upload (Bulkload) through the `clickzetta-connector` package. This API allows data to be sent directly from the client to the storage system without consuming computational resources during the transfer process. The data becomes visible after an explicit commit (the commit process consumes a small amount of computational resources). It is suitable for scenarios with high throughput and relatively loose requirements for data freshness.

With the Bulkload-related API, both single-threaded and distributed data upload scenarios can be achieved.

Installation

If you have previously installed an older version of the SDK, uninstall it first to avoid conflicts:

```shell
pip uninstall clickzetta-connector clickzetta-sqlalchemy clickzetta-ingestion-python clickzetta-ingestion-python-v2 -y
```

Install the latest version (requires Python >=3.7):

```bash
pip install clickzetta-connector -U -i https://pypi.org/simple/
```

## Batch Import Principle

The batch upload SDK provides an efficient data import mechanism suitable for Singdata Lakehouse. Below is a simplified description and flowchart of its working principle:

1. **Data Upload**: Through the SDK, your data is first uploaded to the object storage service. The performance of this step is affected by local network speed and the number of concurrent connections.
2. **Trigger Import**: After the data upload is complete, when you call the `bulkloadStream.commit()` method, the SDK automatically triggers an SQL command to import the data from the object storage into the Lakehouse table. It is not recommended to frequently call `bulkloadStream.commit()` in one task; `bulkloadStream.commit()` should only be called once at the end.
3. **Computing Resources**: It is recommended to choose [General Purpose Virtual Cluster](../create_cluster.md) for uploading data. General-purpose computing resources are more suitable for running batch jobs and loading data jobs. The speed of importing data from object storage to the Lakehouse table depends on the size of the computing resources you configure.
4. **Shard Upload Optimization**: When processing compressed data larger than 1GB, it is recommended to assign a unique shard ID to each concurrent thread or process in the `createRow` method. This approach can fully utilize the parallel processing advantages of multithreading or multiprocessing, significantly improving data import efficiency. The best practice is to determine the number of shard IDs based on the number of concurrents, ensuring each concurrent corresponds to an independent shard ID. If multiple concurrents are assigned the same shard ID, the final written data may be overwritten, resulting in the loss of previous data. To ensure that all shard data is correctly imported into the table, call the `bulkloadStream.commit()` method to submit the entire import task after all concurrent operations are completed.

Below is the flowchart of the batch import principle:
```
[SDK uploads data] ──> [Object Storage] ──> [Call bulkloadStream.close()]
                                ↓
                         [Trigger SQL command] ──> [Lakehouse Table]
```
## Single-threaded Write

Assuming the target table for uploading data is `public.bulkload_test`, the DDL is as follows:
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
    service='api.singdata.com',
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

1. Create a `connection` object, replacing the parameters according to your actual situation:
   ```python
   conn = connect(
       username='your_username',
       password='your_password',
       service='api.singdata.com',
       instance='your_instance',
       workspace='your_workspace',
       schema='public',
       vcluster='default'
   )
   ```
| **Parameter**   | **Required** | **Description**                                                                                                                                                                                                                                                                                                                                                                                           |
| -------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| username       | Y        | Username                                                                                                                                                                                                                                                                                                                                                                                              |
| password       | Y        | Password                                                                                                                                                                                                                                                                                                                                                                                               |
| service        | Y        | Address to connect to the lakehouse, region.api.singdata.com. You can see the JDBC connection string in Lakehouse Studio management -> workspace![](../.topwrite/assets/image_1740559132862.png)|
| instance      | Y        | Can be seen in Lakehouse Studio management -> workspace to view the jdbc connection string ![](../.topwrite/assets/image_1740559198094.png)                                                                                                                                                                                                                                                                                                              |
| workspace      | Y        | Workspace in use                                                                                                                                                                                                                                                                                                                                                                                          |
| vcluster | Y        | VC in use                                                                                                                                                                                                                                                                                                                                                                                            |
| schema         | Y        | Name of the schema being accessed                                                                                                                                                                                                                                                                                                                                                                                       |
2. Create a `BulkLoad Stream` object, specifying the target table for upload, upload method, etc.:
   **Required Parameters**
   `table` Table name
   **Optional Parameters**
   - `schema`, if not specified, the `schema` specified by `connection` will be used
   - `operation`
        * `BulkLoadOperation.APPEND`: Incremental mode (all written data is treated as new data, without affecting old data)
         * `BulkLoadOperation.OVERWRITE`: Overwrite mode (clears old table data and writes new data into the table)
   - `partition_spec`
* If there are no partition columns, ignore this parameter. If there are partition columns, fill in according to the corresponding format, for example: `'pt=xx,item=xx'`, separated by commas. Note that if partition column values are specified, regardless of the values of the partition columns in the data source, the values of the partition columns in the table being written to will be the values defined by this parameter.
```python

from clickzetta.bulkload.bulkload_enums import BulkLoadOperation

# Construct in APPEND mode, the default operation is APPEND
bulkload_stream = conn.create_bulkload_stream(schema='public', table='bulkload_append_test')
# Construct in OVERWRITE mode
bulkload_stream = conn.create_bulkload_stream(
    schema='public',
    table='bulkload_overwrite_test',
    partition_spec='pt=2023-07-01',
    operation=BulkLoadOperation.OVERWRITE
)
```
3. Create `writer` and write data:
   Each `bulkload stream` can create multiple `writers`, and different `writers` need to be identified with different ids. Using multiple `writers` can achieve multi-threaded concurrent writing or distributed concurrent writing in a single commit.
```python
# Use the `open_writer` method to create a `writer`, with the parameter being the `writer` id. In single-machine mode, only one `writer` id is needed, so just pass in 0.
writer = bulkload_stream.open_writer(0)
```
4. Writing Data:
```python
# Each row of data needs to be created using the create_row() method to create a Row object, and then the set_value() method is used to write specific data.
# The first parameter of set_value() is the column name, and the second parameter is the value.
row = writer.create_row()
row.set_value('i', 1)
row.set_value('s', 'January')
row.set_value('d', 123.456)
writer.write(row)
```
The data written by the writer will directly form the corresponding parquet files in the storage system. The writer will automatically split the files based on the amount of data written. When the writer finishes writing data, you need to explicitly call writer.close() to ensure data integrity.
   ```python
   writer.close()
   ```
5. Submit stream. Before committing, ensure that all writers have completed writing and closed. After a successful commit, the data will be visible in the table.
   ```python
   bulkload_stream.commit()
   ```