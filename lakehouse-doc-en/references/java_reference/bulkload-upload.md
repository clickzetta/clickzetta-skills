# Lakehouse Bulkload Quick Start

## Introduction

Bulkload is a high-throughput batch data writing interface provided by Lakehouse, particularly suitable for handling large-scale continuous writing scenarios. Data written using Bulkload can be viewed immediately after submission.

## Principle of Bulk Import

The bulk upload SDK provides an efficient data import mechanism suitable for Singdata Lakehouse. Below is a simplified description and flowchart of its working principle:

1. **Data Upload**: Through the SDK, your data is first uploaded to the object storage service. The performance of this step is affected by local network speed and the number of concurrent connections.
2. **Trigger Import**: After the data upload is complete, when you call the `bulkloadStream.close()` method, the SDK will automatically trigger an SQL command to import the data from the object storage into the Lakehouse table. It is not recommended to frequently call `bulkloadStream.close()` in a single task; `bulkloadStream.close()` should only be called once at the end.
3. **Computing Resources**: It is recommended to choose [General Purpose Virtual Cluster](<../create_cluster.md>) for uploading data. General-purpose computing resources are more suitable for running batch jobs and loading data jobs. The speed of importing data from object storage to the Lakehouse table depends on the size of the computing resources you configure.
4. **Shard Upload Optimization**: When processing compressed data larger than 1GB, it is recommended to assign a unique shard ID to each concurrent thread or process in the `createRow` method. This approach can fully leverage the parallel processing advantages of multithreading or multiprocessing, significantly improving data import efficiency. The best practice is to determine the number of shard IDs based on the number of concurrent threads, ensuring that each concurrent thread corresponds to an independent shard ID. If multiple concurrent threads are assigned the same shard ID, the data written last may overwrite the previous data, resulting in data loss. To ensure that all shard data is correctly imported into the table, call the `bulkloadStream.close()` method to submit the entire import task after all concurrent operations are completed.

Below is the flowchart of the bulk import principle:
```
[SDK uploads data] ──> [Object Storage] ──> [Call bulkloadStream.close()]
                                ↓
                         [Trigger SQL command] ──> [Lakehouse Table]
```
## Applicable Scenarios

The SDK for bulk file uploads is particularly suitable for the following situations:

* **One-time large data import**: When you need to import a large amount of data, whether it is a one-time bulk task or a periodic operation with long intervals.
* **Low import frequency**: If your data import frequency is low (intervals greater than five minutes), even if the amount of data imported each time is not large, using the bulk import SDK is also appropriate.

## Inapplicable Scenarios

The SDK for bulk file uploads is not suitable for the following situations:

* **Real-time data import**: If you need to frequently import data within a very short time (such as within 5 minutes), it is recommended to use real-time data interfaces to meet the requirements for real-time performance.

## Write Restrictions

Please note that BulkloadStream does not support writing to primary key (pk) tables.

## Create BulkloadStream

To create a bulk write stream through the ClickZetta client, refer to the following sample code:

```python
bulkload_stream = client.create_bulkload_stream()
```java
RowStream stream = client.newBulkloadStreamBuilder()
        .schema(schema)
        .table(TABLE_NAME)
        .operate(RowStream.BulkLoadOperate.APPEND)
        .build();
```
### Operation Types

When creating a Bulkload, you can specify the following operation types using the `operate` method:

* `RowStream.BulkLoadOperate.APPEND`: Append mode, adds data to the table.
    ```
    bulkloadStream=client.newBulkloadStreamBuilder().schema(schema).table(table)
            .operate(RowStream.BulkLoadOperate.APPEND)
            .build();
    ```
* `RowStream.BulkLoadOperate.OVERWRITE`: Overwrite mode, deletes existing data in the table before writing new data.
    ```
    bulkloadStream=client.newBulkloadStreamBuilder().schema(schema).table(table)
            .operate(RowStream.BulkLoadOperate.OVERWRITE)
            .build();
    ```
## Writing Data

Use the Row object to represent the specific data to be written. Encapsulate the data into the Row object by calling the `row.setValue` method.
```java
Row row = stream.createRow(0);
row.setValue("id", t);
row.setValue("name", String.valueOf(t));
stream.apply(row, 0);
```
* The `createRow` method requires an integer as the shard ID when creating a Row object. This ID can be used with multithreading/process technology to write data using multiple complementary identical shard IDs, effectively increasing the speed of data writing.
* The first parameter of the `setValue` method is the field name, and the second parameter is the specific data. The data type must be consistent with the table type.
* The `apply` method is used to write data, and it requires specifying the Row object and the corresponding shard ID.

### Writing Complex Type Data
```java
// Write to array
row.setValue("col1", Arrays.asList("first", "b", "c"));

// Write to map
final HashMap<Integer, String> map = new HashMap<Integer, String>();
map.put(t, "first" + t);
row.setValue("col2", map);

// Write to struct
Map<String, Object> struct = new HashMap<>();
struct.put("first", "first-" + i);
struct.put("second", i);
row.setValue("col3", struct);
```
## Submit Data

The data written in batches is only visible after submission. Therefore, the submission process is very important.
```java
bulkloadStream.close();
```
* Use `bulkloadStream.getState()` to get the state of the BulkloadStream.
* If the submission fails, you can get the error message through `bulkloadStream.getErrorMessage()`.

## Usage Example

The following is an example of using Bulkload to write complex type data:
```java
// Create table complex_type(col1 array<string>,col2 map<int,string>, col3 struct<x:int,y:int>);
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.client.RowStream;
import com.clickzetta.platform.client.api.Options;
import com.clickzetta.platform.client.api.Row;
import com.clickzetta.platform.client.api.Stream;

public class BulkloadStreamDemo {
    public static void main(String[] args) throws Exception{
        if (args.length != 5) {
            System.out.println("input arguments: jdbcUrl, username, password");
            System.exit(1);
        }
        String jdbcUrl = args[0];
        String username = args[1];
        String password = args[2];
        String schema = args[3];
        String table = args[4];

        ClickZettaClient client = ClickZettaClient.newBuilder().url(jdbcUrl).username(username).password(password).build();


        BulkloadStream bulkloadStream = client.newBulkloadStreamBuilder()
                .schema(schema)
                .table(table)
                .operate(RowStream.BulkLoadOperate.APPEND)
                .build();

        for (int t = 0; t < 100; t++) {
            Row row = bulkloadStream.createRow(0);
            row.setValue("col1", Arrays.asList("first", "b", "c"));
            final HashMap<Integer, String> map = new HashMap<Integer, String>();
            map.put(t,"first"+t);
            row.setValue("col2", map);
            Map<String, Object> struct = new HashMap<>();
            struct.put("x", t);
            struct.put("y", t+1);
            row.setValue("col3", struct);
            bulkloadStream.apply(row, 0);
        }
        // Must call the stream close interface to trigger the commit action
        bulkloadStream.close();

        // Poll the commit status and wait for the commit to complete
        while(bulkloadStream.getState() == StreamState.RUNNING) {
            Thread.sleep(1000);
        }
        if (bulkloadStream.getState() == StreamState.FAILED) {
            throw new RuntimeException(bulkloadStream.getErrorMessage());
        }
        client.close();
    }
}
```
- Lakehouse url can be seen in the Lakehouse Studio management -> workspace to view the jdbc connection string![](../.topwrite/assets/20250219-114853.jpeg)