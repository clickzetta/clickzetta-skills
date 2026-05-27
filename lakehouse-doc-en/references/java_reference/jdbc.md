# JDBC Usage Instructions

## Installation

You can introduce the `clickzetta-java` SDK through Maven dependency:

```xml
<dependency>
  <groupId>com.clickzetta</groupId>
  <artifactId>clickzetta-java</artifactId>
  <version>${version}</version>
</dependency>
```

Directly click the Maven repository to search within the library
`clickzetta-java` to get the latest update version records

* [Download Link One](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions)
* [Download Link Two](https://mvnrepository.com/artifact/com.clickzetta/clickzetta-java)

### JDBC Connection String

When using the JDBC driver to connect to Clickzetta Lakehouse, the syntax format of the JDBC connection string is as follows:

```
jdbc:clickzetta://<service_instance_name>.api.singdata.com/<workspace_name>?<connection_params>
```

* Connection Parameter Description:

  * `<service_instance_name>`: Lakehouse service instance name. When a Lakehouse service instance is activated in a specified Region, the system will automatically assign an instance name. You can find the Lakehouse instance name on the product console page.

  * `<workspace_name>`: Workspace name.

  * `<connection_params>`: Supports defining parameters using the `=` format, with multiple parameters separated by the `&` symbol. Common parameters are listed in the table below:

| Parameter      | Value                                                                                                                                                                            |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| username       | Clickzetta login username                                                                                                                                                        |
| password       | Login user password                                                                                                                                                              |
| schema         | Specifies the default schema to connect to, optional                                                                                                                             |
| virtualCluster | Configures the default virtual cluster for JDBC connections, optional. If not specified, you need to use the SQL command `use vcluster <vc_name>` after connecting to specify it |
| use\_http=true | Whether to use the HTTP protocol, default is HTTPS. This parameter needs to be specified when using a private link connection                                                    |
| use_oss_internal_endpoint=true | Whether to use the HTTP protocol. The default is false. If the service you are using is supported by Alibaba Cloud, it enforces the use of the OSS internal network Endpoint during queries. |

## Driver Class Name

`com.clickzetta.client.jdbc.ClickZettaDriver`

## Initialize JDBC Connection

The JDBC driver provided by `clickzetta-java` supports two ways to create a Connection:

1. Create a Connection through JDBC URL:
   ```java
   try {
       Class.forName("com.clickzetta.client.jdbc.ClickZettaDriver");
   } catch (ClassNotFoundException e) {
       e.printStackTrace();
       System.exit(1);
   }
   Connection conn = DriverManager.getConnection("jdbc:clickzetta://instance.api.singdata.com/workspace?schema=schema&vcluster=cluster", username, password);
   ```

* The Lakehouse URL can be seen in the Lakehouse Studio management -> workspace to view the JDBC connection string![](../.topwrite/assets/20250219-114853.jpeg)

2. Create a Connection through `ClickZettaClient`:
   ```java
   ClickZettaClient client = ClickZettaClient.newBuilder()
    .instance("instanceName")
    .service("service")
    .username("username")
    .password("password")
    .vcluster("cluster")
    .schema("schema")
    .build();
   Connection conn = client.getJdbcConnection();
   ```

## Performing Queries

`clickzetta-java` provides a complete JDBC standard interface, allowing you to use familiar JDBC APIs for data queries. Here are some examples:

### Example 1: Query and Print Results

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.Statement;

public class SimpleJdbcDemo {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            System.out.println("Input parameters: jdbcUrl, username, password");
            System.exit(1);
        }
        String jdbcUrl = args[0];
        String username = args[1];
        String password = args[2];

        Connection conn = DriverManager.getConnection(jdbcUrl, username, password);
        Statement stmt = conn.createStatement();
        ResultSet resultSet = stmt.executeQuery("SELECT * FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live LIMIT 10");
        ResultSetMetaData rsmd = resultSet.getMetaData();
        int count = rsmd.getColumnCount();
        while (resultSet.next()) {
            for (int i = 1; i <= count; i++) {
                System.out.print(rsmd.getColumnName(i) + ":" + resultSet.getObject(i) + " ");
            }
            System.out.println();
        }
        stmt.close();
        conn.close();
    }
}
```

* The Lakehouse URL can be seen in the Lakehouse Studio management -> workspace to view the JDBC connection string![](../.topwrite/assets/20250219-114853.jpeg)

### Example 2: Insert Data

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;

public class InsertDataDemo {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            System.out.println("Input parameters: jdbcUrl, username, password");
            System.exit(1);
        }
        String jdbcUrl = args[0];
        String username = args[1];
        String password = args[2];

        Connection conn = DriverManager.getConnection(jdbcUrl, username, password);
    String sql = "INSERT INTO public.test_event (event_id, event_date, user_id) VALUES ('event_001', date'2025-02-10', 10001)";
    stmt.execute(sql);
    stmt.close();
    conn.close();
    }
}
```

### Example 3: Update Data

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;

public class UpdateDataDemo {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            System.out.println("Input parameters: jdbcUrl, username, password");
            System.exit(1);
        }
        String jdbcUrl = args[0];
        String username = args[1];
        String password = args[2];

        Connection conn = DriverManager.getConnection(jdbcUrl, username, password);
        Statement stmt = conn.createStatement();
        String sql = "UPDATE   public.test_event SET  event_date = date'2025-02-11' WHERE event_id = 'event_001'";
        stmt.execute(sql);
        stmt.close();
        conn.close();
      

    }
}
```

^
