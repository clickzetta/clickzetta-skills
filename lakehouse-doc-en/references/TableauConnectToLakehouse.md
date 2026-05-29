# Tableau Connects to Lakehouse

Tableau is a Business Intelligence (BI) product. Lakehouse supports data access to Tableau for visualization analysis. You can use Tableau's simple drag-and-drop interface to customize views, layouts, shapes, colors, etc., to help you present your data perspective. This article introduces how to connect Tableau through the Lakehouse JDBC driver and perform visual data analysis.

# Background Information

Tableau Desktop is a software application developed by Tableau based on breakthrough technology from Stanford University. It can help you vividly analyze any structured data that actually exists and generate beautiful charts, coordinate graphs, dashboards, and reports within minutes. For more information on Tableau Desktop, please refer to [Tableau Desktop](https://www.tableau.com/products/desktop).

# Prerequisites

Before starting, please ensure you meet the following conditions:
- Lakehouse service has been activated.
- [Lakehouse JDBC driver](https://www.yunqi.tech/documents/version-update) has been downloaded.
- [Tableau](https://www.tableau.com/products/desktop/download) has been downloaded and installed. This article uses Professional Edition 2024.3.1 as an example.
- Lakehouse provides the [Tableau plugin](<https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/tableau-plugin/clickzetta_jdbc-v0.0.1.taco>).

# Connect to Lakehouse

## Step 1: Place the Lakehouse JDBC Driver

Place the downloaded Lakehouse [JDBC driver JAR package](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions) in the corresponding directory of Tableau Desktop according to the operating system type:
- Windows: C:\\Program Files\\Tableau\\Drivers
- macOS: ~/Library/Tableau/Drivers
- Linux: /opt/tableau/tableau_driver/jdbc

## Step 2: Place the Lakehouse Tableau Plugin

Download the Lakehouse provided [Tableau plugin](<https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/tableau-plugin/clickzetta_jdbc-v0.0.1.taco>). This plugin is written according to the official Tableau [plugin documentation](https://tableau.github.io/connector-plugin-sdk/docs/package-sign).

Place the downloaded plugin in the corresponding directory of Tableau Desktop:
- Windows: C:\\Users\\\[Windows User\]\\Documents\\My Tableau Repository\\Connectors
- macOS: /Users/\[user\]/Documents/My Tableau Repository/Connectors
- Linux: /opt/tableau/connectors

In this article, macOS is used, so the location is: /Users/xxx/Documents/My Tableau Repository/Connectors

## Step 3: Start Tableau

1. Start Tableau Desktop. Since the above plugin is not digitally signed, you need to disable signature verification when starting.
```
--mac open command line and run  
/Applications/Tableau\ Desktop\[version].app/Contents/MacOS/Tableau -DDisableVerifyConnectorPluginSignature=true
-- Windows command line run  
tableau.exe -DDisableVerifyConnectorPluginSignature=true 
```
2. In the **To Server** section of the left navigation bar, select **More... &gt; Lakehouse x Singdata**.
 ![](.topwrite/assets/af1a476424/45fa8a07085269be5490f751bbe23dcecdb1335f.png)
3. In Lakehouse x Singdata, configure the parameter information
![](.topwrite/assets/af1a476424/3a4b0c7e6667057f56190550395cf6a845282aa3.png)

| Parameter | Required | Description                                       |
| --- | ---- | ---------------------------------------- |
| Server | Y    | You can see the jdbc connection string in Lakehouse Studio Management -》Workspace |
| Username | Y    | Username                                      |
| Password  | Y    | Password                                       |
4. Click **Login** to enter the Tableau Desktop interface.
5. Select the target Lakehouse Schema from the schema dropdown list on the left.
 ![](.topwrite/assets/af1a476424/a10eb44867352ca69377affd79c8faa77f7f3bf4.png)

## Step 4: Use Tableau to Query and Analyze Data
In this case, we use the clickzetta\_sample\_data.tpch\_100g.orders table from the public dataset to analyze data

Double-click New Custom SQL
 ![](.topwrite/assets/af1a476424/ccf42506d4d03632469570fc042ff8d9c84dcc03.png)

Enter, click OK
```SQL
select *  from    clickzetta_sample_data.tpch_100g.orders
```
![](.topwrite/assets/af1a476424/cd06ef3dd0b040769d666cafd8278199f2e1f4b3.png)

Click on the worksheet to analyze the dataset in the clickzetta\_sample\_data.tpch\_100g.lineitem table
![](.topwrite/assets/af1a476424/6c856c2e85e70c074ba137c43ef4bf35f82ce3ec.png)