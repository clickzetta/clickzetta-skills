## Real-time Write Principle

The SDK for real-time writing to Lakehouse is an efficient data stream processing tool that allows users to upload and store data in Lakehouse in real-time. The following is the working principle of real-time writing:

1. **SDK Uploads Data**: Users upload data to Lakehouse's Ingestion Service in real-time through the SDK.
2. **Ingestion Service Processing**: After the Ingestion Service receives the data, it directly writes the data into the Lakehouse table. At this stage, the data is stored as temporary intermediate files, and this stage is called a **hybrid table**.
3. **Query Real-time Data**: Before the data is committed, users can query (select) the newly written real-time data, but this data is not visible to table stream, materialized view, and dynamic table.
4. **Data Commit**: The newly written data will be automatically committed after about one minute. After the commit, table stream, materialized view, and dynamic table can read this part of the data.
5. **Hybrid Table Becomes Regular Table**: After the data is committed, the background process will merge the hybrid table into a regular table. Once the merge is complete, users can perform update operations (update\merge\delete).

## Applicable Scenarios

The SDK for real-time writing to Lakehouse is suitable for the following scenarios:

* **Short Interval Data Import**: If your application scenario requires data to be imported at very short intervals (such as 5 minutes or less), the real-time write SDK can meet your needs.
* **Frequent Small Data Submissions**: For situations where data needs to be submitted frequently but the amount of data submitted each time is small, the real-time write SDK provides an efficient solution.
* **Real-time Data Analysis**: The real-time write SDK is suitable for applications that require immediate analysis and response to data, such as real-time monitoring, event tracking, and real-time reporting.

## Notes

* Real-time written data can be queried at the second level.
* Real-time written data can currently only achieve real-time table structure change perception through the sink operator (single concurrency) that supports schema change provided internally by the Flink Connector. In other scenarios, when changing the table structure, you need to stop the real-time write task first, and then restart the task after a period of time (about 90 minutes) after the table structure change.
* Table stream, materialized view, and dynamic table can only display committed data. Real-time task written data needs to wait 1 minute to be confirmed, so table stream also needs to wait 1 minute to see it.

## Create Real-time Data Stream via Client

To create a real-time data stream, you first need to use the ClickZetta client:
```SQL
RowStream stream = client.newRealtimeStreamBuilder()
.operate(RowStream.RealTimeOperate.APPEND_ONLY)
.options(options)
.schema(schema)
.table(table)
.build();
// Close the stream and release resources
stream.close();
operate: Pass in an enumeration value, the real-time interface supports RowStream.RealTimeOperate.APPEND_ONLY and RowStream.RealTimeOperate.CDC.
options: Used to pass parameters for the real-time write stream, see the options description below for details.
```
## Options

The following options can be passed into the real-time data stream to control the behavior of data writing. These parameters are all optional, and it is recommended to use the default parameters.
```SQL
Options options = Options.builder()
.withFlushMode(FlushMode.AUTO_FLUSH_BACKGROUND)
            .withMutationBufferLinesNum(50000)
            .withMutationBufferMaxNum(50)
            .withMutationBufferSpace(20 * 1024 * 1024)
            .withFlushInterval(10 * 1000)
            .withRequestFailedRetryEnable(true)
            .withRequestFailedRetryTimes(5)
            .withRequestFailedRetryInternalMs(5 * 1000)
            .withRequestFailedRetryLogDebugEnable(true)
            .withRequestFailedRetryStatus(
                    RegisterStatus.RetryStatus.THROTTLED,
                    RegisterStatus.RetryStatus.INTERNAL_ERROR,
                    RegisterStatus.RetryStatus.FAILED,
                    RegisterStatus.RetryStatus.PRECHECK_FAILED)
            .build();
```
**Parameter Description**

|          | Parameter                             | Default Value                        | Description                                                                                                                                                                                                                       |
| -------- | ------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Write Performance Parameters | withFlushMode                        | FlushMode.AUTO\_FLUSH\_BACKGROUND    | Data flush mode, currently supports FlushMode.AUTO\_FLUSH\_SYNC: Wait for the previous flush to complete before proceeding with the next write FlushMode.AUTO\_FLUSH\_BACKGROUND: Asynchronous flush allows multiple writes to proceed simultaneously without waiting for the previous write to complete                                                                                                       |
|          | withMutationBufferLinesNum           | 100                                  | The limit on the number of data entries accumulated in each buffer. Once this limit is reached, the data will be sent to the server. When this limit is reached, the data will be actually flushed and submitted to the server. If the amount of data imported at one time reaches the MB level, this parameter can be increased to speed up the import. The conditions for data submission to the server are that either MutationBufferLinesNum or FlushInterval is reached first.                                                                                                                                                                                                                               |
|          | withMutationBufferMaxNum             | 5                                    | During data submission, `withMutationBufferLinesNum` specifies the threshold for sending data entries after reaching a certain number. `withMutationBufferMaxNum` defines the maximum number of buffers that can exist simultaneously. Even if the data in the previous buffer has not been completely written, as long as the number of buffers does not exceed the limit specified by `withMutationBufferMaxNum`, new data can continue to be written to new buffers. This allows the system to achieve higher concurrency in processing and sending data, as it does not have to wait for all buffers to be cleared before continuing to write new data. In short, `withMutationBufferMaxNum` is equivalent to a JDBC connection pool.
|          | withMutationBufferSpace              | 5 \* 1024 \* 1024 (5MB)              | When this limit is reached, the data will be actually flushed and submitted to the server. If the amount of data imported at one time reaches the MB level, this parameter can be increased to speed up the import. The condition for data submission to the server is that either MutationBufferSpace or MutationBufferLinesNum is reached first.                                                                                               |
|          | withFlushInterval                    | 10 \* 1000 (10 seconds)              | When this time limit is reached, the data will be actually flushed and submitted to the server. The condition for data submission to the server is that either MutationBufferSpace or withMutationBufferLinesNum is reached first.                                                                                                                                       |
| Retry Mechanism Parameters | withRequestFailedRetryEnable         | FALSE                                | Whether to enable the retry mechanism for failed mutations. TRUE                                                                                                                                                                                                         |
|          | withRequestFailedRetryTimes          | 5                                    | The maximum number of retries for failed mutations.                                                                                                                                                                                                               |
|          | withRequestFailedRetryInternalMs     | 5000 (5 seconds)                      | Unit: ms, the interval time for retrying after a failure.                                                                                                                                                                                                                  |
|          | withRequestFailedRetryLogDebugEnable | FALSE                                | Whether to enable debug logging                                                                                                                                                                                                                     |
|          | withRequestFailedRetryStatus         | RegisterStatus.RetryStatus.THROTTLED | Retry based on which error reason, the default is RegisterStatus.RetryStatus.THROTTLED. Multiple values are separated by commas. Values: RegisterStatus.RetryStatus.THROTTLED RegisterStatus.RetryStatus.INTERNAL\_ERROR RegisterStatus.RetryStatus.FAILED RegisterStatus.RetryStatus.PRECHECK\_FAILED |

## Write Data (Row)

Create a specific data object (Row) through the `stream.createRow` method, and encapsulate the data into the Row object through the `row.setValue` method.

**Row** **row** = stream.createRow(Stream.Operator.INSERT);

row\.setValue("id", t);

row\.setValue("name", String.valueOf(t));

stream.apply(row);

* When the Stream is created as `RowStream.RealTimeOperate.APPEND_ONLY`, only `Stream.Operator.INSERT` type Rows can be created.

* When the Stream is created as `RowStream.RealTimeOperate.CDC`, all the following Row types can be used:

  * `Stream.Operator.INSERT`: Insert row, an error is reported if the target row already exists.
  * `Stream.Operator.DELETE`: Delete row, an error is reported if the target row does not exist.
  * `Stream.Operator.UPDATE`: Update row, an error is reported if the target row does not exist.
  * `Stream.Operator.UPSERT`: Insert row, if the target row already exists, update that row.
  * `Stream.Operator.INSERT_IGNORE`: Insert row, if the target row already exists, it is automatically ignored.

## Data Submission to Server
By calling the ((RealtimeStream)stream).flush() method, the data will be submitted to the server. If not called, the data will be sent to the server when any one of MutationBufferSpace, withMutationBufferLinesNum, or withFlushInterval is reached first.

# Specific Cases
## Append Write to Ordinary Table
```Java
// Create table ingest_stream(id int,name string);
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.client.RowStream;
import com.clickzetta.platform.client.api.Options;
import com.clickzetta.platform.client.api.Row;
import com.clickzetta.platform.client.api.Stream;

public class RealtimeStreamDemo {
    public static void main(String[] args) throws Exception {
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
        Options options = Options.builder()
            // Specify the refresh mode, optional, the default is asynchronous refresh
            .withFlushMode(FlushMode.AUTO_FLUSH_BACKGROUND)
           // Number of lines in each buffer
            .withMutationBufferLinesNum(50000)
            .withMutationBufferMaxNum(50)
            // Maximum size in the buffer, when this value is reached, it will be submitted to the server.
            .withMutationBufferSpace(20 * 1024 * 1024)
            // Interval for submitting data to the server, when this value is reached, it will be submitted to the server.
            .withFlushInterval(10 * 1000)
            // Whether to enable retry on error, the default value is false
            .withRequestFailedRetryEnable(true)
            // Number of retry attempts on error
            .withRequestFailedRetryTimes(5)
            // Retry interval on error
            .withRequestFailedRetryInternalMs(5 * 1000)
            // Whether to enable debug logs, default is false
            .withRequestFailedRetryLogDebugEnable(false)
            .build();

        RowStream stream = client.newRealtimeStreamBuilder()
                .operate(RowStream.RealTimeOperate.APPEND_ONLY)
                .options(options)
                .schema(schema)
                .table(table)
                .build();

        for (int t = 0; t < 1000; t++) {
            Row row = stream.createRow(Stream.Operator.INSERT);
            row.setValue("id",t);
            row.setValue("name", String.valueOf(t));
            stream.apply(row);
        }
        // After calling flush, the data will be submitted to the server. If not called, it will be written according to the parameters specified by the refresh mode above, such as withFlushInterval
        ((RealtimeStream)stream).flush();
        // Call the stream close interface, close will implicitly execute flush
        stream.close();
        client.close();
    }
}
```
## Writing Vector Types

### Creating a Table

```sql
CREATE TABLE test_vector (
    vec1 vector(float, 512), -- Specify element type as float, with dimension 512
    vec2 vector(512), -- Default element type is float, with dimension 512
    vec3 vector(tinyint, 128) -- Specify element type as tinyint, with dimension 128
);
```

### Writing with Java

```java
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.client.RowStream;
import com.clickzetta.platform.client.api.Options;
import com.clickzetta.platform.client.api.Row;
import com.clickzetta.platform.client.api.Stream;

public class RealtimeStreamDemo {
    public static void main(String[] args) throws Exception {
        if (args.length != 5) {
            System.out.println("input arguments: jdbcUrl, username, password, schema, table");
            System.exit(1);
        }
        String jdbcUrl = args[0];
        String username = args[1];
        String password = args[2];
        String schema = args[3];
        String table = args[4];

        // Initialize the ClickZetta client
        ClickZettaClient client = ClickZettaClient.newBuilder()
                .url(jdbcUrl)
                .username(username)
                .password(password)
                .build();

        // Set options for the stream
        Options options = Options.builder().withMutationBufferLinesNum(10).build();

        // Build the real-time stream
        RowStream realtimeStream = client.newRealtimeStreamBuilder()
                .operate(RowStream.RealTimeOperate.APPEND_ONLY)
                .options(options)
                .schema(schema)
                .table(table)
                .build();

        // Prepare data
        float[] vec1 = new float[512];
        float[] vec2 = new float[512];
        byte[] vec3 = new byte[128]; // tinyint can be represented by byte in Java

        // Initialize data (this is just an example; actual data should be filled according to requirements)
        for (int i = 0; i < 512; i++) {
            vec1[i] = (float) Math.random();
            vec2[i] = (float) Math.random();
        }
        for (int i = 0; i < 128; i++) {
            vec3[i] = (byte) (Math.random() * 256);
        }

        // Create a row and set values
        Row row = realtimeStream.createRow(Stream.Operator.INSERT);
        row.setValue("vec1", vec1);
        row.setValue("vec2", vec2);
        row.setValue("vec3", vec3);

        // Apply the row to the stream
        realtimeStream.apply(row);
        realtimeStream.flush();

        // Close the stream (flush is implicitly executed when closing)
        realtimeStream.close();
        client.close();
    }
}
```
## CDC Real-time Writing

Lakehouse supports the CDC (Change Data Capture) function of databases, writing data into Lakehouse tables in a streaming manner and updating table data in real-time. The synchronization process is achieved by RealtimeStream updating insert and delete row operations in real-time. Additionally, it supports data writing using Flink connector and IGS SDK. When creating a table, a primary key needs to be set to ensure the uniqueness and consistency of the data.
### Creating a Table

When creating a Lakehouse table, a primary key needs to be specified. CDC writing will deduplicate data based on the primary key to ensure data accuracy. The created primary key table does not support SQL operations and can only write data through real-time writing streams. The created primary key table also does not support adding or modifying columns using SQL. Below is an example of creating a table:
```sql
CREATE TABLE igs_test_upsert (
    id INT PRIMARY KEY,
    event VARCHAR(100),
    event_time STRING
);
```
### IGS SDK Real-time Write Stream

#### Create Real-time Write Stream

To create a real-time write stream using the IGS SDK, you need to specify the operation type (CDC) and related options. Below is an example of creating a real-time write stream:
```java
RowStream stream = client.newRealtimeStreamBuilder()
    .operate(RowStream.RealTimeOperate.CDC)
    .options(options)
    .schema(schema)
    .table(table)
    .build(); // Close the stream, release stream resources, must be called
stream.close();
```
#### Specify Operation Type

According to the requirements, different operation types can be specified:

* `Stream.Operator.UPSERT`: Insert or update a row. If the target row does not exist, insert it; if it already exists, update it.
* `Stream.Operator.DELETE_IGNORE`: Delete a row. If the target row does not exist, it is automatically ignored.

#### Use Native Java SDK to Write
```java
Row row = stream.createRow(Stream.Operator.UPSERT); // Insert or update row
Row rowToDelete = stream.createRow(Stream.Operator.DELETE_IGNORE); // Delete row
```
### Using Lakehouse Real-time Sync Function to Write
Refer to the documentation [Multi-table Real-time Sync](<../realtime_sync.md>)
### Using FLINK CONNECTOR to Write

Flink connector is encapsulated based on RealtimeStream SDK, used for real-time data synchronization. See [Flink Connector](<../flink-write-connector.md>)
