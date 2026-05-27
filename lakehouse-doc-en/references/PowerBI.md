Lakehouse implements the MySQL client-server communication protocol, so you can use a MySQL driver to connect to Lakehouse. However, Lakehouse does not implement MySQL syntax and data types. You can connect to Lakehouse via a MySQL client, but the SQL statements you execute should use Lakehouse syntax, not MySQL syntax. For example, the `mysqldump` command is not available in Lakehouse. This article uses the MySQL driver in PowerBI to connect to Lakehouse, providing a quick overview of how to connect. We use a financial sample dataset.

## Prerequisites

* Currently, you need to reset your password, even for newly created accounts. This is because MySQL 5.x uses the `mysql_native_password` authentication plugin, while Lakehouse needs to store the MySQL encryption algorithm. Currently, Lakehouse only saves the MySQL key encryption algorithm when the password is changed. You can reset the password to the same value as before to avoid affecting other task connections.

* Set a compute cluster for the user. Since the MySQL protocol does not provide a way to pass the cluster setting, users can use SQL commands to assign a default compute cluster to a user. This way, the designated cluster will be used when connecting via MySQL. Note that BI scenarios often have analysis performance requirements. It is recommended to select an appropriately sized analytical compute cluster for the BI tool connection user to provide optimal query performance.

  ```SQL
   ALTER USER user_name SET DEFAULT_VCLUSTER = default_ap;
    
   -- Check if the cluster setting is effective
   SHOW USERS;
  ```

* Prepare the username. The MySQL protocol connection address can only accept a single URL and cannot concatenate the Lakehouse instance name and workspace name. Therefore, you need to concatenate the instance name and workspace name into the username.

  * The username format is as follows:

  * ```Plain
    login_account_name@instance_name.workspace_name
    ```

  * **Obtain instance_name**: Get the JDBC connection string from the workspace page. For example, in `jdbc:clickzetta://``jnsxwfyr.api.singdata.com/quick_start?virtualCluster=default`, `jnsxwfyr` is the instance_name.

    * ![](.topwrite/assets/image_1723468458225.png)

  * **Obtain workspace_name**: The name of the workspace.

* Create a schema and table in Lakehouse, and upload data.

```Plain
create schema sales;
use sales;
create table salesdata (
    segment varchar(255),
    country varchar(255),
    product varchar(255),
    discountband varchar(255),
    unitssold decimal(10, 2),
    manufacturingprice decimal(10, 2),
    saleprice decimal(10, 2),
    grosssales decimal(15, 2),
    discounts decimal(15, 2),
    sales decimal(15, 2),
    cogs decimal(15, 2),
    profit decimal(15, 2),
    date date,
    monthnumber int,
    monthname varchar(50),
    year int
);
```

## Connecting PowerBI

* Click Get Data Source, search for MySQL

![](.topwrite/assets/image_1723468519288.png)

* Enter the Lakehouse MySQL connection address and schema name. The schema in this example is public.

  * ![](.topwrite/assets/image_1723468556557.png)

Connection addresses for each region

| Cloud Provider | Region   | Connection Address                                   |
| -------------- | -------- | ---------------------------------------------------- |
| Alibaba Cloud  | Shanghai | cn-shanghai-alicloud-mysql.api.singdata.com      |
| Tencent Cloud  | Shanghai | ap-shanghai-tencentcloud-mysql.api.singdata.com  |
|                | Beijing  | ap-beijing-tencentcloud-mysql.api.singdata.com   |
|                | Guangzhou| ap-guangzhou-tencentcloud-mysql.api.singdata.com |
| AWS            | Beijing  | cn-north-1-aws-mysql.api.singdata.com            |

* Configure username and password. The MySQL protocol connection address can only accept a single URL and cannot concatenate the Lakehouse instance name and workspace name. Therefore, you need to concatenate the instance name and workspace name into the username. The username format is as follows:

```Plain
login_account_name@instance_name.workspace_name
```

![](.topwrite/assets/image_1723468581688.png)

* Get Lakehouse tables

![](.topwrite/assets/image_1723468606603.png)

* Configure the dashboard

![](.topwrite/assets/image_1723468624662.png)

* Publish the dashboard to Power Service

* Find the published dashboard in Power Service, and configure scheduling and password authentication.

  * ![](.topwrite/assets/image_1723468643893.png)

  * Edit username and password

    * ![](.topwrite/assets/image_1723468662518.png)
    * ![](.topwrite/assets/image_1723468680533.png)

  * Edit scheduling

  * ![](.topwrite/assets/image_1723468702158.png)

* View the dashboard in Power Service

![](.topwrite/assets/image_1723468715463.png)

## References

[Connect using MySQL protocol](use-mysql-client.md)
