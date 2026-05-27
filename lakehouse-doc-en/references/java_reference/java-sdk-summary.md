# Lakehouse Java SDK Introduction

Lakehouse provides you with a Java SDK named `clickzetta-java`. Through this unified SDK, we offer users the following features:

* Standard type 4 JDBC driver, allowing you to access ClickZetta Lakehouse via JDBC
* Real-time data writing SDK, supporting you to quickly write real-time data into ClickZetta Lakehouse
* Batch data writing SDK, supporting you to efficiently write large amounts of data into ClickZetta Lakehouse

## How to Obtain

You can introduce the `clickzetta-java` SDK through Maven dependency:

```xml
<dependency>
  <groupId>com.clickzetta</groupId>
  <artifactId>clickzetta-java</artifactId>
  <version>${version}</version>
</dependency>
```

Directly click on the Maven repository to search for `clickzetta-java` to get the latest update records

* [Download Link 1](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions)
* [Download Link 2](https://mvnrepository.com/artifact/com.clickzetta/clickzetta-java)

## Notes

* `clickzetta-java` supports Java 8 and above.
* When using Java 9 and above, you need to add the JVM startup parameter `--add-opens=java.base/java.nio=ALL-UNNAMED` to ensure normal operation.

## Common Issues and Solutions

1. Issue Description: `javax.net.ssl.SSLHandshakeException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target`

   Solution: You may be using an earlier version of Java (e.g., 11.0.1+13), which is affected by the JDK issue with TLSv1.3 implementation [JDK-8211806](https://bugs.openjdk.org/browse/JDK-8211806). We recommend upgrading to a newer stable production version. If you cannot change the Java version, you can add the following Java startup parameter to work around the issue: `-Djdk.tls.client.protocols=TLSv1.2`

## Usage Example

### 1. Use JDBC Driver to Connect to ClickZetta Lakehouse

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class ClickZettaJDBCExample {
  public static void main(String[] args) {
    String url = "jdbc:clickzetta://your-lakehouse-url";
    String user = "your-username";
    String password = "your-password";

    try {
      Class.forName("com.clickzetta.client.jdbc.ClickZettaDriver");
      Connection connection = DriverManager.getConnection(url, user, password);
      Statement statement = connection.createStatement();
      ResultSet resultSet = statement.executeQuery("SELECT * FROM schema.your_table");

      while (resultSet.next()) {
        System.out.println( resultSet.getString(1));

      }

      resultSet.close();
      statement.close();
      connection.close();
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}
```

* The Lakehouse URL can be seen in the Lakehouse Studio **Management** -> **Workspace** to view the JDBC connection string![](../.topwrite/assets/20250219-114853.jpeg)

### 2. Use the real-time data writing SDK to send data to ClickZetta Lakehouse

```java
//  create table ingest_stream(id int,name string);
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.client.RowStream;
import com.clickzetta.platform.client.api.Options;
import com.clickzetta.platform.client.api.Row;
import com.clickzetta.platform.client.api.Stream;
import com.clickzetta.client.RealtimeStream;

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

        Options options = Options.builder().build();

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
        // After calling flush, the data will be submitted to the server. If not called, it will be written according to the parameters specified by the above refresh method, such as withFlushInterval.
        ((RealtimeStream)stream).flush();
        // The stream close interface must be called, and flush will be implicitly executed when closing.
        stream.close();
        client.close();
    }
}
```

### 3. Use the Batch Data Write SDK to Send Data to ClickZetta Lakehouse

```
// Create table create table complex_type(col1 array<string>,col2 map<int,string>, col3 struct<x:int,y:int>);
import com.clickzetta.client.BulkloadStream;
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.client.RowStream;
import com.clickzetta.client.StreamState;
import com.clickzetta.platform.client.api.Options;
import com.clickzetta.platform.client.api.Row;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

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

        Options options = Options.builder().build();

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
        // Must call stream close interface to trigger commit action
        bulkloadStream.close();

        // Polling submission status, waiting for submission to end
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

^
