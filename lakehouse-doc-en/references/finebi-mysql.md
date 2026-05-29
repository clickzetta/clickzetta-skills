FineBI is a Business Intelligence product launched by FanRuan Software Co., Ltd. FineBI is a new-generation big data analytics BI tool designed to help business personnel fully understand and utilize their data. This article describes how to use the MySQL protocol to connect to Lakehouse.

# Prerequisites

* Please refer to the [FineBI official website](https://www.finebi.com/). If already installed, skip this step.

* Use the MySQL protocol to connect. Currently, you need to reset your password, even for newly created accounts. This is because MySQL 5.x uses the `mysql_native_password` authentication plugin, while Lakehouse needs to store the MySQL encryption algorithm. Currently, Lakehouse only saves the MySQL key encryption algorithm when the password is changed. You can reset the password to the same value as before to avoid affecting other task connections.

* Set a compute cluster for the user. Since the MySQL protocol does not provide a way to pass the cluster setting, users can use SQL commands to assign a default compute cluster to a user. This way, the designated cluster will be used when connecting via MySQL.

  * ```SQL
    ALTER USER user_name SET DEFAULT_VCLUSTER = default;
    -- Check if the cluster setting is effective
    SHOW USERS;
    ```

* Prepare the username. The MySQL protocol connection address can only accept a single URL and cannot concatenate the Lakehouse instance name and workspace name. Therefore, you need to concatenate the instance name and workspace name into the username.

  * The username format is as follows:

  * ```Plain
    login_account_name@instance_name.workspace_name
    ```

  * **Obtain instance_name**: Get the JDBC connection string from the workspace page. For example, in `jdbc:clickzetta://``jnsxwfyr.api.singdata.com/quick_start?virtualCluster=default`, `jnsxwfyr` is the instance_name.
  * **Obtain workspace_name**: The name of the workspace.

# Configuring FineBI to Connect to Lakehouse

* Navigate to Data Connection -> Data Connection Management -> New Data Connection -> Select MySQL
* Fill in the configuration information, as shown in the following example

|     Field Name      |   Description                                                                                                                                                                                                              |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Data Connection Name** | Custom connection name, e.g.: clickzetta_lakehouse_mysql                                                                                                                                                                                  |
| **Driver**          | Use the default value: com.mysql.jdbc.Driver                                                                                                                                                                                          |
| **Database Name**   | Lakehouse schema name, e.g.: public                                                                                                                                                                                              |
| **Host**            | Connection address for each region. See [Connect using MySQL protocol](use-mysql-client.md) for details                                                                                                                                                                                          |
| **Port**            | Optional. Default: 3306                                                                                                                                                                                                            |
| **Username**        | login_account_name@instance_name.workspace_name                                                                                                                                                                                 |
| **Password**        | Password for the login account                                                                                                                                                                                                                |
| **Encoding**        | Default value                                                                                                                                                                                                                    |
| **Data Connection URL** | FineBI will automatically generate the URL based on the above connection information. You need to edit the URL and append `?useSSL=false` at the end. This parameter is required for connectivity. Example: `jdbc:mysql://``cn-shanghai-alicloud-mysql.api.singdata.com/dws_clys?useSSL=false`. After adding this parameter, the database name will also have `?useSSL=false` appended, e.g.: `public?useSSL=false`. This is normal. |

# Verifying the Connection

## Creating a Server Dataset

Navigate to Data Connection -> Server Dataset, and create a new SQL dataset.

Dataset Name: Singdata Lakehouse-TPCH-Q01

SQL Statement:

```sql
 select
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
    avg(l_quantity) as avg_qty,
    avg(l_extendedprice) as avg_price,
    avg(l_discount) as avg_disc,
    count(*) as count_order
from
    clickzetta_sample_data.tpch_100g.lineitem
where
    l_shipdate <= date '1998-12-01' - interval '85' day
group by
    l_returnflag,
    l_linestatus
order by
    l_returnflag,
    l_linestatus
limit 1;
```

:-: ![](.topwrite/assets/image_1736938941276.png =657)

## Creating a Dataset

Select New Dataset -> SQL Dataset:

:-: ![](.topwrite/assets/image_1736939075914.png =660)

This shows that tables in Singdata Lakehouse are available to FineBI's "Public Data".

Using Lakehouse data in an analysis topic:

:-: ![](.topwrite/assets/image_1736939239963.png =657)

## Analysis View

Generate new data views via drag and drop:

:-: ![](.topwrite/assets/image_1736994382813.png =660)

Visualization component based on data view - Pie chart: analyzing used car sales revenue by engine type

:-: ![](.topwrite/assets/image_1736994510861.png =665)

Visualization component based on data view - Cross table: analyzing used car yearly sales revenue by engine type

:-: ![](.topwrite/assets/image_1736994646263.png =669)
