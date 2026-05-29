# Data Sharing

## 1. Overview

### What is Data Share

Data Share is a **zero-copy** data sharing feature provided by Singdata Lakehouse, enabling **cross-account or cross-service-instance** data authorization and usage within the same service region. Unlike traditional data replication or import solutions, Data Share does not require manually setting up data sync links between enterprises. Instead, it directly provides read-only access to source data through "authorization", with real-time updates.

### Application Scenarios

* **Real-time Sharing Scenario**: Enterprise A shares its own data (e.g., transaction logs, user behavior data) with Enterprise B in real time. Enterprise B can query updated data in real time without performing data sync.
* **Multi-party Collaborative Analysis**: Multiple partners analyze and mine data based on the same real-time dataset, reducing duplicate storage and transmission costs.
* **Data Provider and Data Consumer Model**: The data provider wants to open part of their data to partners. Partners can obtain read-only data without bearing storage costs for their own BI analysis or product integration.

### Use Case in This Document

This document takes **Enterprise A** (data provider) and **Enterprise B** (data consumer) as examples to introduce the following operations:

1. **Enterprise A creates a Data Share and shares data**: Enterprise A has e-commerce data for Brazil_Commercial in its own data warehouse and wants to include desensitized data in the Data Share, specifying Enterprise B as the recipient.
2. **Enterprise B receives and extracts data from the Data Share**: Enterprise B, in its own Singdata Lakehouse instance, receives the share from Enterprise A and creates the corresponding schema to extract the shared data.
3. **Enterprise B uses the extracted data with BI applications to create reports**: Enterprise B analyzes the read-only data extracted from the Data Share and creates reports in BI tools.
4. **Enterprise A writes data, and Enterprise B's reports reflect data changes in real time**: Since Data Share is zero-copy and real-time, updates made by Enterprise A to the data are immediately visible to Enterprise B.

***

## 2. Enterprise A Creates a Data Share and Specifies Enterprise B as the Recipient

In the following example, Enterprise A has a logistics table `rpt_brazil_ec`, which contains the logistics status of all products from all sellers. Enterprise B is one of the sellers under Enterprise A. Enterprise A needs to provide Enterprise B with the logistics status of its sold products so that Enterprise B can use this data for BI dashboards to analyze and track logistics status. To do this, Enterprise A will filter `rpt_brazil_ec`, create a view `sub_rpt_brazil_ec_05e107217c7266362fd44b75b2cd4cc4` containing only Enterprise B's data, and share this view with Enterprise B.

### 2.1 Creating a View

Since the logistics table `rpt_brazil_ec` contains data for all sellers, for data security reasons, not all data can be provided to Enterprise B. Therefore, a view needs to be created first that only contains Enterprise B's data, and only this view will be shared.

The table `rpt_brazil_ec` contains a seller ID field: `seller_id`. Use this field as a filter condition to create the following view:

```
-- Create an independent schema for the share, facilitating subsequent management and maintenance
CREATE SCHEMA seller_data_share;

-- Create a view. Assume Enterprise B's seller_id is 05e107217c7266362fd44b75b2cd4cc4
CREATE    VIEW seller_data_share.sub_rpt_brazil_ec_05e107217c7266362fd44b75b2cd4cc4 AS
SELECT    *
FROM      rpt_brazil_ec
WHERE     seller_id = '05e107217c7266362fd44b75b2cd4cc4';
```

### 2.2 Creating a Data Share and Sharing with Specified Enterprise B

#### Web Interface Operations

**1) Create a Data Share**

* Log into the Singdata Lakehouse console using an account with the "Instance Administrator" (`instance_admin`) role.
* In the left navigation, select "Data" → "Data Sharing", and click "+ New Share".

:-: ![](.topwrite/assets/image_1740388043727.png =742)

* In the dialog, fill in the share name (e.g., shipping_detail), and select the workspace where the data to be shared is located.
* Note: The data to be shared must be in the same workspace. If the data itself is distributed across multiple workspaces, you can create views of the data to be shared from other workspaces within one workspace to centralize all data to be shared into the same workspace.

:-: ![](.topwrite/assets/image_1740388342928.png =438)

**2) Add Data Objects to Share**

Continuing in the Create Share dialog, click "Add" and select the objects to share. As shown below, in the ql_ws workspace, find the schema created above: seller_data_share, and select the view within it: seller_data_share.sub_rpt_brazil_ec_05e107217c7266362fd44b75b2cd4cc4

After clicking "Done", the view will be included in the share list.

:-: ![](.topwrite/assets/image_1740388392799.png =537)

^

**3) Configure Recipient Instances**

In the same dialog, click the "Add" button below "Recipient Instances", enter Enterprise B's Singdata Lakehouse "Service Instance Name" (which Enterprise B needs to provide; it can be found in the upper right area of the homepage after logging into their service instance), and click Done.

:-: ![](.topwrite/assets/image_1740388438814.png =531)

^

**4) Complete Data Share Creation**

After completing all the above fields, click the "OK" button to finish creating the Data Share object and specify sharing it with Enterprise B's Lakehouse service instance.

Subsequently, you can edit this Data Share to add or remove data objects to share, or add or remove Lakehouse service instances receiving this data (e.g., if you need to share with other service instances of Enterprise B).

**5) View or Manage Share Objects**

After creation, you can see the newly created Data Share object in the "Data Sharing" → "Shared by Me" list.

:-: ![](.topwrite/assets/image_1740390203623.png =718)

^

#### SQL Operations

If you prefer SQL operations, use an account with the "Instance Administrator" (`instance_admin`) role to execute the following operations in Enterprise A's workspace (e.g., `ql_ws`):

**1) Create Share**

```
CREATE SHARE shipping_detail;
```

**2) Add View to Share**

```
-- Note: SELECT grants the recipient the ability to query data, READ METADATA grants the recipient the ability to see this view object. Both permissions need to be granted.
GRANT SELECT, READ METADATA ON VIEW seller_data_share.sub_rpt_brazil_ec_05e107217c7266362fd44b75b2cd4cc4 TO SHARE shipping_detail;
```

**3) Configure Target Instance for Share**

```
ALTER SHARE shipping_detail ADD INSTANCE '<Replace with Enterprise B instance_name>';
```

Enterprise B needs to provide the name of their Lakehouse service instance. After this operation, Enterprise B will immediately obtain the right to use share shipping_detail and can extract read-only access to the view: seller_data_share.sub_rpt_brazil_ec_05e107217c7266362fd44b75b2cd4cc4 from it.

> After completing the above steps, Enterprise A has successfully shared filtered data with Enterprise B via the Data Share feature.

##

### 2.3 Enterprise B Receives and Extracts Data from the Data Share

After Enterprise A completes the sharing, Enterprise B needs to "receive and extract" the shared data in their own Singdata Lakehouse instance to use the view object in queries.

#### Web Interface Operations

**View Objects Shared with Me**

Log into Enterprise B's Singdata Lakehouse console using an account with the "Instance Administrator" or "Workspace Administrator" role.

In the left navigation, select "Data Management" → "Data Sharing", switch to the "Shared with Me" tab, and you will see the shipping_detail shared by Enterprise A.

^

**Extract Data**

Click the "Extract" button below the shipping_detail card.

In the dialog, select the "Source Schema" (a Data Share may contain multiple schemas; you need to specify the schema for data extraction), as well as the workspace and corresponding schema in Enterprise B's service instance where you want the shared data to land.

Note: A new schema will be created based on the filled-in schema name. This schema is read-only, and you cannot create other data objects such as tables or views within this schema.

After completing the fields, click the "OK" button. The system will create a read-only schema in Enterprise B's specified workspace and map it to the objects shared by Enterprise A.

^

**After Extraction is Complete**

Enterprise B can see the corresponding new schema and the view: sub_rpt_brazil_ec_05e107217c7266362fd44b75b2cd4cc4 in "Data Catalog" or on the "Data" tab of the "Development" feature.

You can query the data in the view just like using local data objects.

^

### 2.4 SQL Operations

If using SQL to extract data from a share, execute the following commands in Enterprise B's workspace:

**View Share Objects**

```SQL
SHOW SHARES;
```

You can see the `INBOUND` type Data Share named shipping_detail from Enterprise A's service instance.

**View Data in shipping_detail**

```
DESC SHARE shipping_detail;
```

^

**Create Local Schema**

```
CREATE SCHEMA b_workspace_share_schema FROM SHARE A_instance_name.shipping_detail.share_demo;
```

Where `A_instance_name`, `share_demo`, and the source schema name can be found through `SHOW SHARES;` and `DESC SHARE share_demo;`.

`b_workspace_share_schema` is the name of the read-only schema created in Enterprise B's workspace, which can be customized.

^

***

## 4. Enterprise B Uses the Extracted Data with BI Applications to Create Reports

After Enterprise B extracts and successfully creates a read-only schema, they can query or perform join analysis on `orders_view` in any BI tool or SQL workbench compatible with Singdata Lakehouse. For example:

```
SELECT 
    order_id,
    customer_id,
    order_amount,
    order_status
FROM b_workspace_share_schema.orders_view
WHERE order_status = 'COMPLETED';
```

* **Joining External Data**: You can join `orders_view` with Enterprise B's internal data tables (`JOIN`) for analysis.
* **Data Modeling**: You can use `orders_view` as a data source in BI tools for data visualization and report creation.

At this point, Enterprise B no longer needs to worry about whether the data is synced in real time — Data Share ensures that when Enterprise A's source data is updated, Enterprise B queries the latest data.

***

## 5. Enterprise A Writes Data to the Data Share, and Enterprise B's Reports Reflect Changes in Real Time

When Enterprise A inserts new data into the underlying table `orders` corresponding to `orders_view`, or updates existing order data, the Data Share automatically exposes the changed data to Enterprise B in real time. Enterprise B does not need any additional operations and can see the latest results in SQL queries or BI reports.

Example: Enterprise A executes the following statement to update the order status, and Enterprise B can immediately see the updated status records in their existing reports.

```
-- Enterprise A executes in workspace_a
UPDATE orders
SET order_status = 'SHIPPED'
WHERE order_id = 10001;
```

Enterprise B obtains the latest status in real time through the previous BI report or the following SQL query:

```
-- Enterprise B executes
SELECT 
    order_id,
    order_status
FROM b_workspace_share_schema.orders_view
WHERE order_id = 10001;
```

***

## Summary

Through the above 5 steps, you can achieve real-time data sharing similar to Snowflake Data Sharing on the Singdata Lakehouse platform. The biggest features of Data Share are:

* **Zero-copy, Low Latency**: No need for duplicate storage or periodic sync between enterprises. Data changes can be propagated to consumers in real time.
* **Secure and Controllable Data**: Data is only shared in a "read-only" form, and share objects can be removed at any time through permission control.
* **Easy to Scale**: Data columns or rows can be flexibly filtered through Views to achieve fine-grained sharing control.

^
