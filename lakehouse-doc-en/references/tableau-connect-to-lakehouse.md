# Connecting Tableau to Lakehouse

Tableau is a Business Intelligence (BI) product. Lakehouse supports connecting data to Tableau for visual analysis. You can leverage Tableau's simple drag-and-drop interface to customize views, layouts, shapes, colors, and more to present your own data perspective. This article explains how to connect Tableau using the Lakehouse JDBC driver and perform visual data analysis.

# Background Information

Tableau Desktop is a software application developed by Tableau based on breakthrough technology from Stanford University. It helps you vividly analyze virtually any structured data and generate beautiful charts, graphs, dashboards, and reports within minutes. For more information about Tableau Desktop, see [Tableau Desktop](https://www.tableau.com/products/desktop).

# Prerequisites
Before starting, ensure you meet the following conditions:
- Lakehouse service is activated.
- [Lakehouse JDBC Driver](https://www.singdata.com/documents/version-update) has been downloaded.
- [Tableau](https://www.tableau.com/products/desktop/download) has been downloaded and installed. This article uses Professional Edition 2024.3.1 as an example.
- The Lakehouse-provided [Tableau Plugin](<https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/tableau-plugin/clickzetta_jdbc-v0.0.1.taco>)
# Connecting to Lakehouse
## Step 1: Place the Lakehouse JDBC Driver
Place the downloaded Lakehouse [JDBC Driver JAR file](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions) in the corresponding directory for Tableau Desktop based on your operating system:
- Windows: C:\\Program Files\\Tableau\\Drivers
- macOS: ~/Library/Tableau/Drivers
- Linux: /opt/tableau/tableau_driver/jdbc
## Step 2: Place the Lakehouse Tableau Plugin
Download the Lakehouse-provided [Tableau Plugin](<https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/tableau-plugin/clickzetta_jdbc-v0.0.1.taco>). This plugin is developed based on the Tableau official [plugin documentation](https://tableau.github.io/connector-plugin-sdk/docs/package-sign).

Place the downloaded plugin in the corresponding directory for Tableau Desktop:
- Windows: C:\\Users\\[Windows User]\\Documents\\My Tableau Repository\\Connectors
- macOS: /Users/[user]/Documents/My Tableau Repository/Connectors
- Linux: /opt/tableau/connectors
The example in this article uses macOS, with the location: /Users/xxx/Documents/My Tableau Repository/Connectors
## Step 3: Launch Tableau
1. Launch Tableau Desktop. Since the plugin above has not been digitally signed, signature verification must be disabled on startup.
 ```
-- Run on macOS command line
/Applications/Tableau\ Desktop\[version].app/Contents/MacOS/Tableau -DDisableVerifyConnectorPluginSignature=true
-- Run on Windows command line
tableau.exe -DDisableVerifyConnectorPluginSignature=true
```
2. In the left navigation bar under **To Server**, select **More... > Lakehouse by Singdata**.
 ![](.topwrite/assets/af1a476424/45fa8a07085269be5490f751bbe23dcecdb1335f.png)
3. In Lakehouse by Singdata, configure the parameter information:
![](.topwrite/assets/af1a476424/3a4b0c7e6667057f56190550395cf6a845282aa3.png)

| Parameter | Required | Description                                       |
| --- | ---- | ---------------------------------------- |
| Server | Y    | You can find the JDBC connection string in Lakehouse Studio Administration -> Workspaces |
| Username | Y    | Username                                      |
| Password | Y    | Password                                       |
4. Click **Sign In** to enter the Tableau Desktop workspace.
5. In the Schema dropdown list on the left, select the target Lakehouse Schema.
 ![](.topwrite/assets/af1a476424/a10eb44867352ca69377affd79c8faa77f7f3bf4.png)

## Step 4: Query and Analyze Data Using Tableau
This example uses the `clickzetta_sample_data.tpch_100g.orders` table from the public dataset to analyze data.

Double-click New Custom SQL:
 ![](.topwrite/assets/af1a476424/ccf42506d4d03632469570fc042ff8d9c84dcc03.png)

Enter the following and click OK:
```SQL
select *  from    clickzetta_sample_data.tpch_100g.orders
```
 ![](.topwrite/assets/af1a476424/cd06ef3dd0b040769d666cafd8278199f2e1f4b3.png)

Click Sheet to analyze the dataset from the `clickzetta_sample_data.tpch_100g.lineitem` table:
![](.topwrite/assets/af1a476424/6c856c2e85e70c074ba137c43ef4bf35f82ce3ec.png)
