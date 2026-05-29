# BulkloadStream Detailed Reference

> Best for: scheduled ETL, local file imports, and database migration.
> Not for: primary-key tables or high-frequency writes under 5 minutes.

## Maven Dependency

```xml
<!-- See https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java for the latest version. -->
<dependency>
    <groupId>com.clickzetta</groupId>
    <artifactId>clickzetta-java</artifactId>
    <version>2.0.0</version>
</dependency>
```

See [Maven Central](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java) for the latest version.

## Usage Limits

- **Primary-key table writes are not supported.**
- **High-frequency writes at intervals shorter than 5 minutes are not recommended.**
- Data becomes visible only after writing is complete and `close()` has been called.

## Complete Example: Read a Local CSV and Write to Lakehouse

### Create the Table

```sql
CREATE TABLE bulk_order_items (
    order_id            STRING,
    order_item_id       INT,
    product_id          STRING,
    seller_id           STRING,
    shipping_limit_date STRING,
    price               DOUBLE,
    freight_value       DOUBLE
);
```

### Java Code: BulkloadFile Class

```java
import com.clickzetta.client.BulkloadStream;
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.client.RowStream;
import com.clickzetta.client.StreamState;
import com.clickzetta.platform.client.api.Row;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.text.MessageFormat;

public class BulkloadFile {
    private static ClickZettaClient client;
    private static final String password = "";
    private static final String table = "bulk_order_items";
    private static final String workspace = "";
    private static final String schema = "public";
    private static final String vc = "default";
    private static final String user = "";
    static BulkloadStream bulkloadStream;

    public static void main(String[] args) throws Exception {
        initialize();
        File csvFile = new File("olist_order_items_dataset.csv");
        BufferedReader reader = new BufferedReader(new FileReader(csvFile));
        reader.readLine(); // Skip the header row.

        String line;
        while ((line = reader.readLine()) != null) {
            String[] values = line.split(",");
            // Type conversion must match the table DDL.
            String orderId = values[0];
            int orderItemId = Integer.parseInt(values[1]);
            String productId = values[2];
            String sellerId = values[3];
            String shippingLimitDate = values[4];
            double price = Double.parseDouble(values[5]);
            double freightValue = Double.parseDouble(values[6]);

            Row row = bulkloadStream.createRow();
            // BulkloadStream uses column indexes starting at 0. The order must match the table DDL.
            row.setValue(0, orderId);
            row.setValue(1, orderItemId);
            row.setValue(2, productId);
            row.setValue(3, sellerId);
            row.setValue(4, shippingLimitDate);
            row.setValue(5, price);
            row.setValue(6, freightValue);
            // apply() is required. Otherwise the row is not sent to the server.
            bulkloadStream.apply(row);
        }

        reader.close();
        bulkloadStream.close();
        waitForBulkloadCompletion();
        client.close();
        System.out.println("Data inserted successfully!");
    }

    private static void initialize() throws Exception {
        // Recommended: explicit parameters. Supported in 2.0.0+.
        client = ClickZettaClient.newBuilder()
            .service("cn-shanghai-alicloud.api.clickzetta.com")
            .instance("your_instance")
            .workspace(workspace)
            .schema(schema)
            .username(user)
            .password(password)
            .vcluster(vc)
            .build();
        bulkloadStream = client.newBulkloadStreamBuilder()
            .schema(schema)
            .table(table)
            .operate(RowStream.BulkLoadOperate.APPEND)
            .build();
    }

    private static void waitForBulkloadCompletion() throws InterruptedException {
        while (bulkloadStream.getState() == StreamState.RUNNING) {
            Thread.sleep(1000);
        }
        if (bulkloadStream.getState() == StreamState.FAILED) {
            throw new RuntimeException(bulkloadStream.getErrorMessage());
        }
    }
}
```

## Key APIs

| API | Description |
|---|---|
| `bulkloadStream.createRow()` | Create a row object without arguments. |
| `row.setValue(int index, Object value)` | Set a value by column index, starting at 0. |
| `bulkloadStream.apply(row)` | Send the row to the server. This call is required. |
| `bulkloadStream.close()` | Close the stream and trigger the commit. |
| `bulkloadStream.getState()` | Get the state: RUNNING, SUCCEEDED, or FAILED. |
| `bulkloadStream.getErrorMessage()` | Get the failure reason. |

## Type Mapping

| Java type | Lakehouse type |
|---|---|
| `Long` / `long` | BIGINT |
| `Integer` / `int` | INT |
| `Double` / `double` | DOUBLE |
| `String` | STRING / VARCHAR |
| `Boolean` | BOOLEAN |
| `java.sql.Timestamp` | TIMESTAMP |
| `java.sql.Date` | DATE |
| `BigDecimal` | DECIMAL |

## FAQ

| Issue | Cause | Solution |
|---|---|---|
| Data cannot be queried after writing | `apply()` was not called or the RUNNING state has not finished | Call `apply()` for every row and wait until the state becomes SUCCEEDED. |
| Primary-key table write fails | BulkloadStream does not support primary-key tables | Use JDBC with MERGE or Flink `igs-dynamic-table` instead. |
| Column value type mismatch | Java types do not match the table DDL | Convert values before writing, for example with `parseInt` or `parseDouble`. |
| Connection fails | Wrong URL parameter name | BulkloadStream uses `virtualcluster=`, not `vcluster=`. |
