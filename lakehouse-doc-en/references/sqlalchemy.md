# Using SQLAlchemy to Connect to Singdata Lakehouse

## Introduction

SQLAlchemy is an SQL toolkit and Object-Relational Mapping (ORM) system for the Python programming language. It provides comprehensive and flexible SQL functionality for Python application development, making database operations more convenient. Singdata Lakehouse, as a high-performance data warehouse service, now supports SQLAlchemy, making it easier for users to perform data operations and analysis.

## Installation

To use SQLAlchemy to connect to Singdata Lakehouse, you first need to install the clickzetta-sqlalchemy package in your Python environment. Use the following command to install (ensure the current environment does not have clickzetta-sqlalchemy and clickzetta-connector installed; uninstall them first if needed to avoid dependency conflicts):
```
pip uninstall -y clickzetta-sqlalchemy clickzetta-connector && pip install clickzetta-connector -U
```
## Configure Connection Parameters

When using SQLAlchemy to connect to Singdata Lakehouse, you need to provide the correct connection parameters. The format of the connection parameters is as follows:
```
clickzetta://<user_login_name>:<password>@<instance_name>.<region_id>.api.singdata.com/<workspace_name>?schema=<target_schema>&virtualcluster=<your_vcluster_name>
```
The meanings of each parameter are as follows:

* `<user_login_name>`: Your Singdata Lakehouse login username.
* `<password>`: Your Singdata Lakehouse login password.
* `<instance_name>`: Your Singdata Lakehouse instance name.
* `<region_id>`: The cloud provider and region code for the service instance, e.g. `cn-shanghai-alicloud`. See [Supported Cloud Platforms](Supported-Cloud-Platforms.md) for all region IDs.
* `<workspace_name>`: Your Singdata Lakehouse workspace name.
* `<target_schema>`: The name of the target schema you wish to access.
* `<your_vcluster_name>`: The name of your virtual cluster.

**Connection Example**:
```
clickzetta://Alice:xxxx@1a2b3c4d.cn-shanghai-alicloud.api.singdata.com/myworkspace?schema=public&virtualcluster=default_vc
```
## Using Apache Superset to Connect to Singdata Lakehouse

In this section, we will introduce how to use Apache Superset to connect to Singdata Lakehouse for data queries and BI analysis.

### Prerequisites

* Ensure that the clickzetta-sqlalchemy package has been successfully installed.
* Ensure that Apache Superset has been successfully installed and started.

### Configure the Connection

1. Open Apache Superset and go to the database list page.
2. Click the "Add Database" button in the upper right corner and select "Other" database type.
3. In the "SQLALCHEMY URI" field, fill in the Singdata Lakehouse connection parameters configured above.
4. Click "Test Connection" to ensure the connection is successful.

![Configure Superset Connection](.topwrite/assets/image_1668962209871.png)

### Data Query and BI Analysis

Once the connection is successful, you can use Apache Superset for data queries and BI analysis. For example:

1. Create a new dashboard and add chart components.
2. In the chart configuration page, select the Singdata Lakehouse database connection that was just configured.
3. Write SQL query statements, for example:

```sql
SELECT
  orders.order_id,
  orders.customer_id,
  orders.order_date,
  orders.total
FROM
  orders
WHERE
  orders.order_date BETWEEN '2022-01-01' AND '2022-12-31';
```

4. Click "Execute Query" to view the query results.
5. Adjust the chart style and configuration as needed to complete the BI analysis.

![Superset Data Query and BI Analysis](.topwrite/assets/image_1668962386077.png)

By following the above steps, you can easily use Apache Superset to connect to Singdata Lakehouse for data querying and BI analysis.