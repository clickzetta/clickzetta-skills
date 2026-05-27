# Using Java to Upload Data in Batch (BulkLoadV1)
>The original BulkLoadV1 API will be deprecated and phased out. Please migrate to the BulkloadV2 API as soon as possible. clickzetta-java version 3.0.21 or higher is required. BulkloadV2 API launch: The new V2 API is released, supporting more efficient data processing capabilities and more stable service guarantees. Benefits of the V2 new version:
>i. 30% Performance Improvement: Significantly improves the efficiency of data integration sync tasks and custom batch import tasks.
>ii. Process Optimization: Introduces a Table Volume-based data staging and loading mechanism, enhancing task auditability and data traceability, making your data management more standardized and secure.
## Maven Dependencies
You can include the `clickzetta-java` SDK via Maven dependency:

```xml
<dependency>
  <groupId>com.clickzetta</groupId>
  <artifactId>clickzetta-java</artifactId>
  <version>${version}</version>
</dependency>
```

Search for `clickzetta-java` on the Maven repository to get the latest version record.

* [Download Location 1](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions)
* [Download Location 2](https://mvnrepository.com/artifact/com.clickzetta/clickzetta-java)


## Creating a BulkloadStream

To create a bulk write stream through the Singdata client, refer to the following example code:

```java
RowStream stream = client.newBulkloadStreamBuilder()
        .schema(schema)
        .table(TABLE_NAME)
        .operate(RowStream.BulkLoadOperate.APPEND)
        .build();
```

### Options

Starting from clickzetta-java version 3.0.18, options are provided. Options are used to specify upload options including partition specification.

```
bulkloadStream=client.newBulkloadStreamBuilder().schema(schema).table(table)
                .options(BulkLoadOptions.newBuilder().withPartitionSpecs(Optional.of("your_partition_spec")).build())

                .operate(RowStream.BulkLoadOperate.APPEND)
                .build();
```

* withPartitionSpecs is used to specify partition information for the target table, controlling the partition behavior for data writes.

  * Non-partitioned table: Ignore this parameter or set it to empty.
  * Partitioned table:
    * Static partition write: Writes all data to a designated fixed partition. Regardless of the actual values in the partition column of the source data, the `partition_spec` value is used when writing to the target table, and all data is written to the same specified partition. The parameter format is 'partition_col1=value1,partition_col2=value2'.
    * Dynamic partition write: Automatically writes to the corresponding partition based on the actual values of the partition column in the data. By ignoring this parameter, the system automatically creates or writes to the appropriate partition based on the values of the partition column in the data.

### Operation Types

When creating a Bulkload, you can specify the following operation types via the `operate` method:

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

Use the Row object to represent the specific data to be written. Encapsulate data into the Row object by calling the `row.setValue` method.

```java
Row row = stream.createRow(0);
row.setValue("id", t);
row.setValue("name", String.valueOf(t));
stream.apply(row, 0);
```

* The `createRow` method creates a Row object and requires an integer as a shard ID. This ID can be used with multi-threading/multi-processing techniques, where multiple mutually distinct shard IDs are used to write data, effectively improving data write speed.
* The first parameter of the `setValue` method is the field name, and the second parameter is the specific data. The data type must match the table column type.
* The `apply` method is used to write data, requiring the Row object and the corresponding shard ID.

### Writing Complex Type Data

```java
// Write array
row.setValue("col1", Arrays.asList("first", "b", "c"));

// Write map
final HashMap<Integer, String> map = new HashMap<Integer, String>();
map.put(t, "first" + t);
row.setValue("col2", map);

// Write struct
Map<String, Object> struct = new HashMap<>();
struct.put("first", "first-" + i);
struct.put("second", i);
row.setValue("col3", struct);
```

## Committing Data

Batch-written data is only visible after being committed. Therefore, the commit process is very important.

```java
bulkloadStream.close();
```

* Use `bulkloadStream.getState()` to get the status of the BulkloadStream.
* If the commit fails, use `bulkloadStream.getErrorMessage()` to get the error message.

## Usage Example

The following is an example of using Bulkload to write complex type data:

```java
// Create table: create table complex_type(col1 array<string>,col2 map<int,string>, col3 struct<x:int,y:int>);
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
        // Must call the stream close API to trigger the commit action
        bulkloadStream.close();

        // Poll the commit status, wait for commit to complete
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

* The Lakehouse URL can be found in Lakehouse Studio under **Management** -> **Workspace** by checking the JDBC connection string.![](../.topwrite/assets/image_1739177196184.png)


