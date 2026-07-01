# Batch Upload Data Using Java SDK

This document introduces how to use the Java SDK's BulkloadStream to batch load data into Lakehouse. It is suitable for one-time large data imports, supports custom data sources, and provides flexibility in data import. This example uses reading a local file. If your data source is within the range supported by object storage or Lakehouse Studio data integration, it is recommended to use the COPY command or data integration features.

# Reference Documentation

[Java SDK Bulk Data Upload](java_reference/realtime-upload.md)

## Application Scenarios

* Suitable for business scenarios that require bulk uploading of large amounts of data.
* Suitable for developers familiar with Java who need custom data import logic.

## Usage Restrictions

* BulkloadStream does not support writing to primary key (pk) tables.
* Not suitable for frequent data upload scenarios with intervals of less than five minutes.

# Usage Example

This example uses reading a local CSV file. The dataset used is the olist\_order\_items\_dataset data from the [Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_order_items_dataset.csv) public dataset. If the data source is within the range supported by object storage or Lakehouse Studio data integration, it is recommended to use the COPY command or data integration features.

## Prerequisites

* Create a table
  * ```SQL
    create    table bulk_order_items (
              order_id STRING,
              order_item_id INT,
              product_id STRING,
              seller_id STRING,
              shipping_limit_date STRING,
              price DOUBLE,
              freight_value DOUBLE
              );
    ```

* Have INSERT permission on the target table.

## Developing with Java Code

### Maven Dependency

Add the Lakehouse Maven dependency to the project's `pom.xml` file. The latest version of the Lakehouse Maven dependency can be found in the [Maven repository](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java).

```xml
<dependency>
    <groupId>com.clickzetta</groupId>
    <artifactId>clickzetta-java</artifactId>
    <version>1.3.1</version>
</dependency>
```

### Writing Java Code

1. **Initialize Lakehouse Client and BulkloadStream**: Create the `BulkloadFile` class, initialize the Lakehouse connection and BulkloadStream object.
2. **Read Local CSV File and Write to Lakehouse**: Use Java IO streams to read the local CSV file and write data to Lakehouse line by line.

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
        // Skip the header row
        reader.readLine(); // Skip the first line (header)
        // Insert data into the database
        String line;

        while ((line = reader.readLine()) != null) {
            String[] values = line.split(",");
            // Ensure type conversion is consistent with the server-side type
            String orderId = values[0];
            int orderItemId = Integer.parseInt(values[1]); // Convert order_item_id to int
            String productId = values[2];
            String sellerId = values[3];
            String shippingLimitDate = values[4];
            double price = Double.parseDouble(values[5]);
            double freightValue = Double.parseDouble(values[6]);
            Row row = bulkloadStream.createRow();
            // Set parameter values
            row.setValue(0, orderId);
            row.setValue(1, orderItemId);
            row.setValue(2, productId);
            row.setValue(3, sellerId);
            row.setValue(4, shippingLimitDate);
            row.setValue(5, price);
            row.setValue(6, freightValue);
         // This method must be called, otherwise data cannot be sent to the server
            bulkloadStream.apply(row);
        }
        // Close resources
        reader.close();
        bulkloadStream.close();
        waitForBulkloadCompletion();
        client.close();
        System.out.println("Data inserted successfully!");
    }
    private static void initialize() throws Exception {
        String url = MessageFormat.format("jdbc:clickzetta://demo_instance.cn-shanghai-alicloud.api.singdata.com/{0}?" +
                        "schema={1}&username={2}&password={3}&virtualcluster={4}&",
                workspace, schema, user, password, vc);
        client = ClickZettaClient.newBuilder().url(url).build();
        bulkloadStream = client.newBulkloadStreamBuilder().schema(schema).table(table)
                .operate(RowStream.BulkLoadOperate.APPEND)
                .build();
    }
    private static void waitForBulkloadCompletion() throws InterruptedException {
        while (bulkloadStream.getState() == StreamState.RUNNING) {
            Thread.sleep(1000);
        }
        if (bulkloadStream.getState() == StreamState.FAILED) {
            throw new ArithmeticException(bulkloadStream.getErrorMessage());
        }
    }

}
```

^
