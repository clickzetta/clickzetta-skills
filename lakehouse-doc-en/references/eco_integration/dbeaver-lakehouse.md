# DBeaver Connect to Singdata Lakehouse

This document will guide you on how to connect and manage data in Singdata Lakehouse using the database management tool DBeaver. DBeaver is a powerful multi-platform database tool suitable for developers, database administrators, analysts, and anyone who needs to use databases. This document will detail how to configure DBeaver to connect to Lakehouse and provide some practical usage examples.

## Background Information

DBeaver is a free database management tool that supports various databases such as MySQL, PostgreSQL, Oracle, etc. For more information about DBeaver, please refer to the [DBeaver official website](https://dbeaver.io/).

## Prerequisites

Before starting, please ensure you meet the following conditions:

1. Successfully activated the Lakehouse service.
2. Downloaded the JDBC driver suitable for Lakehouse. For information on how to download and install the driver, please refer to the [Java SDK documentation](<../version-update.md>).
3. Downloaded and installed DBeaver. For information on how to download and install DBeaver, please refer to the [DBeaver download page](https://dbeaver.io/download/).
4. Installed the DBeaver version suitable for your operating system. The DBeaver example in this document is `dbeaver-ce-23.1.4-macos-x86_64`.

## Step 1: Configure DBeaver to Connect to Lakehouse Driver

1. Launch DBeaver and enter the main interface. In the top menu bar, click "Database" -> "Driver Manager".

![Driver Manager Interface](.topwrite/assets/image_1693482257812.png)

2. In the Driver Manager interface, click the "New Driver" button in the lower left corner.

![New Driver Button](.topwrite/assets/image_1693482268306.png)

3. In the pop-up dialog, click the "Settings" button and fill in the following information:
   - Driver Name: `Clickzetta`
   - Class Name: `com.clickzetta.client.jdbc.ClickZettaDriver`
   - URL Template: `jdbc:clickzetta://{instanceName}.{service}/{workspaceName}?virtualCluster={Your Virtual Cluster Name}`

![Configure Driver Information](.topwrite/assets/image_1693482279541.png)

4. Click "Add File" to add the downloaded Lakehouse JDBC driver (`*.jar-with-dependencies.jar`) to the driver, and click "OK".

![Add JDBC Driver](.topwrite/assets/image_1693482290529.png)

5. In the top menu bar, click "New Connection", select "All", enter the newly created driver name `Clickzetta` in the search box, and then click "Next".

![New Connection](.topwrite/assets/image_1693482299012.png)

6. In the "Connection Configuration" interface, select "URL", copy the JDBC connection string from the Lakehouse homepage and paste it into the corresponding input box. Also, fill in your username and password.

![Connection Configuration](.topwrite/assets/image_1693482307635.png)

For information on how to obtain the JDBC connection string from the Lakehouse homepage, please refer to the [Lakehouse documentation](<../version-update.md>).

## Step 2: Use DBeaver to Query and Analyze Lakehouse Data

After successfully connecting DBeaver and Lakehouse, you can find the newly created Lakehouse connection in the "Connections" panel on the left side of DBeaver. Next, you can manage the data in Lakehouse through SQL.

1. Right-click the newly created Lakehouse connection and select "New SQL Editor".

![New SQL Editor](.topwrite/assets/image_1693482322444.png)

2. In the SQL editor, write the query statement you need to execute. For example, query the first 10 records of a table:
```sql
SELECT * FROM your_table_name LIMIT 10;
```
![Writing Query Statements](.topwrite/assets/image_1693482333626.png)

3. Execute the query and view the results. You can also sort, filter, and perform other operations on the query results.

By following the above steps, you can easily use DBeaver to connect to and manage data in the Lakehouse. For more advanced features and usage tips of DBeaver, please refer to the [DBeaver Official Documentation](https://dbeaver.io/docs/).