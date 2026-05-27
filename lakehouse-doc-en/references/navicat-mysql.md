Navicat (full name Navicat Premium) is a powerful database management tool widely used for database development, management, and maintenance. This article describes how to use Navicat to connect to Lakehouse via the MySQL protocol.

# Prerequisites

* Please refer to the [Navicat official website](https://www.navicat.com/en/download/navicat-premium). If already installed, skip this step.

* Use the MySQL protocol to connect. Currently, you need to reset your password, even for newly created accounts. This is because MySQL 5.x uses the `mysql_native_password` authentication plugin, while Lakehouse needs to store the MySQL encryption algorithm. Currently, Lakehouse only saves the MySQL key encryption algorithm when the password is changed. You can reset the password to the same value as before to avoid affecting other task connections.

* Set a compute cluster for the user. Since the MySQL protocol does not provide a way to pass the cluster setting, users can use SQL commands to assign a default compute cluster to a user. This way, the designated cluster will be used when connecting via MySQL.

  * ```SQL
    ALTER USER user_name SET DEFAULT_VCLUSTER = default;
    -- Check if the cluster setting is effective
    SHOW USERS;
    ```

* Prepare the username. When using the MySQL protocol to connect, the address can only accept a single URL and cannot concatenate the Lakehouse instance_name and workspace_name. Therefore, you need to concatenate the instance_name and workspace_name into the username.

  * The username format is as follows:
  * ```Plain
    login_account_name@instance_name.workspace_name
    ```
  * **Obtain instance_name**: Get the JDBC connection string from the workspace page. For example, in `jdbc:clickzetta://``demoinstance.cn-shanghai-alicloud.api.singdata.com/quick_start?virtualCluster=default`, `jnsxwfyr` is the instance_name.
  * **Obtain workspace_name**: The name of the workspace.

# Connecting to Lakehouse

* Click Connection -> Select MySQL

* Fill in the configuration information as follows:

| Field            | Description                                                      |
| ---------------- | ---------------------------------------------------------------- |
| **Connection Name** | Custom connection name, e.g.: clickzetta_lakehouse_mysql                 |
| **Host**             | Connection address for each region. See [Connect using MySQL protocol](use-mysql-client.md) for details |
| **Port**             | Optional. Default: 3306                                           |
| **Username**         | login_account_name@instance_name.workspace_name                |
| **Password**         | Password for the login account                                               |

# Querying Lakehouse Data in Navicat

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

^
