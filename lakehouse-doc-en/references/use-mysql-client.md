# Connect Using MySQL Protocol


| Cloud Provider | Region    | Compatible MySQL Protocol Version |
| -------------- | --------- | --------------------------------- |
| Alibaba Cloud  | Singapore | MySQL5.x and MySQL8.x             |
|                | Shanghai  | MySQL5.x and MySQL8.x             |
| Tencent Cloud  | Shanghai  | MySQL8.x                          |
|                | Beijing   | MySQL8.x                          |
|                | Guangzhou | MySQL8.x                          |
| Amazon         | Beijing   | MySQL8.x                          |
|                | Singapore | MySQL8.x                          |

Lakehouse supports the MySQL client-server communication protocol, so you can use MySQL drivers to connect to Lakehouse. However, Lakehouse does not implement MySQL syntax and data types. When connecting to Lakehouse via a MySQL client, SQL statements should use Lakehouse syntax, not MySQL syntax. For example, the `mysqldump` command is not available in Lakehouse.

To accommodate some BI reports, Lakehouse has implemented some commonly used MySQL functions, such as `str_to_date` and `date_format`.

When a MySQL 8.x client connects to the server, the default authentication method is `caching_sha2_password`. For more information on MySQL authentication methods, refer to the [official documentation](https://dev.mysql.com/doc/refman/8.0/en/authentication-plugins.html). Connection example for Alibaba Cloud Shanghai:

```
jdbc:mysql://cn-shanghai-alicloud-mysql.api.singdata.com/public
-- Add port, optional
jdbc:mysql://cn-shanghai-alicloud-mysql.api.singdata.com:3306/public
-- Use SSL, optional
jdbc:mysql://cn-shanghai-alicloud-mysql.api.singdata.com/public?useSSL=true
```

When a MySQL 5.x client connects to the server, the default authentication method is `mysql_native_password`. For more information, refer to the [official documentation](https://dev.mysql.com/doc/refman/8.0/en/authentication-plugins.html). SSL is not required when connecting to Lakehouse. Connection example for Alibaba Cloud Shanghai:

* Currently, you need to reset the password even for newly created accounts. This is because MySQL 5.x uses the `mysql_native_password` key, and Lakehouse needs to store MySQL's encryption algorithm. Lakehouse only stores MySQL key encryption algorithms when the password is changed. You can keep the same password when modifying it to avoid affecting other task connections.

```
jdbc:mysql://cn-shanghai-alicloud-mysql.api.singdata.com/public?useSSL=false
-- Add port, optional
jdbc:mysql://cn-shanghai-alicloud-mysql.api.singdata.com:3306/public?useSSL=false
```

Port: 3306 (optional)

## Usage Scenarios

* Scenarios where the Lakehouse driver cannot be used — for example, when some BI report tools do not support custom JDBC drivers or the Lakehouse native JDBC driver. If possible, use the Lakehouse native driver.

## Usage Restrictions

* Full compatibility with MySQL functions and syntax is not currently available. Some MySQL-specific syntax and functions used in certain reports will produce errors when sent to Lakehouse (contact Lakehouse support).
* Data type restrictions
  * When using the Lakehouse MySQL protocol, if SQL statements contain MySQL-specific types (such as mediumint, numeric, bit, time, year, datetime, varbinary, text, blob, enum, set, or spatial data types), the system will report an error. For example, `CREATE TABLE mysql_table(col numeric)` or `SELECT CAST(xxxx AS text)` — any SQL containing these types will trigger an error. To avoid this, use Lakehouse types as replacements for MySQL data types.
* Syntax restrictions
  * MySQL-specific syntax such as MySQL dump commands and LOAD commands are not supported.
* Function restrictions
  * Lakehouse implements some commonly used MySQL functions. Contact Lakehouse support if you need more.
* Data import restrictions
  * MySQL bulk data import (e.g., MySQL LOAD command) is not supported.
  * Using the MySQL driver does not support Lakehouse local commands ([PUT](put.md), [REMOVE](remove-volume.md), [GET](get.md), etc.), and does not support using the MySQL driver to call Lakehouse's Java SDK for bulk upload and real-time upload.
* When MySQL lists table structures, it needs to query the information schema. There is currently a 15-minute delay in Lakehouse for newly created tables appearing in the information schema, so newly created tables cannot be seen immediately.

## Connection Method

## Set Up the Virtual Cluster

Since the MySQL protocol has no way to pass in a cluster setting, users can use SQL commands to add a default Virtual Cluster for the user. This cluster will be used when connecting via MySQL. Note that BI scenarios often have performance requirements for analysis, so it is recommended to choose an appropriate specification of analytical Virtual Cluster for the BI tool connecting user to provide the best query performance.

```sql
ALTER USER user_name SET DEFAULT_VCLUSTER = DEFAULT;

-- Check if the cluster setting has taken effect
SHOW USERS;
```

## Set Username and Password

Since the MySQL protocol does not include workspace name and instance name, you need to concatenate the instance name and workspace name into the username.

The username format requirement is:

```
account_name@instance_name.workspace_name
```

* **instance_name**: Obtain from the JDBC connection string on the [Workspace](workspace-introduction.md) page. For example, in `jdbc:clickzetta://jnsxwfyr.api.singdata.com/quick_start?virtualCluster=DEFAULT`, `jnsxwfyr` is the instance_name.
* **workspace_name**: The name of the workspace.

Example:

```
user@jnsxwfyr.quick_start
```

## Set Connection Address

Port: 3306

| Cloud Provider | Region    | Connection Address                                         |
| -------------- | --------- | ---------------------------------------------------------- |
| Alibaba Cloud  | Shanghai  | cn-shanghai-alicloud-mysql.api.singdata.com              |
| Tencent Cloud  | Shanghai  | ap-shanghai-tencentcloud-mysql.api.singdata.com          |
|                | Beijing   | ap-beijing-tencentcloud-mysql.api.singdata.com           |
|                | Guangzhou | ap-guangzhou-tencentcloud-mysql.api.singdata.com         |
| Amazon         | Beijing   | cn-north-1-aws-mysql.api.singdata.com                    |

## Other Parameters

* `useSSL=true`: Lakehouse uses `caching_sha2_password` for MySQL 8.x clients, so when connecting with MySQL 8.x drivers, you must set `useSSL=true`. If using MySQL 5.x, set `useSSL=false`.
* Database name: The schema name in Lakehouse
* Port: 3306 (optional)

## BI Report Configuration Parameters

**Connection Tool**

MySQL Java 8.0 driver is recommended. However, some reports may initialize with MySQL-specific syntax — if you encounter errors, contact Lakehouse technical support.

**Set vcluster**:
You need to assign a default Virtual Cluster for the connecting user in Lakehouse. This cluster will be used when connecting via MySQL. Note that BI scenarios often have performance requirements for analysis, so it is recommended to choose an appropriate specification of analytical Virtual Cluster for the BI tool connecting user to provide the best query performance.

```SQL
ALTER USER user_name SET DEFAULT_VCLUSTER = default_ap;
-- Check if the vcluster setting has taken effect
SHOW USERS;
```

**Driver requirements**: MySQL 8.0 or above is recommended

**Connection address (required)**

**Username format (required)**

* Format: username@instance_name.workspace_name, for example, test@jnsxwfyr.ql_ws

**Database name (required)**

* Format: schema name, such as public

**Port: 3306. Required for some reports**

**Additional parameters (required)**:

If using the 8.x driver, some reports can directly fill in the following string in the configuration parameters:

* useSSL=true

If the report does not support filling in parameters:

* In the report interface, there is usually an option to enable SSL — check it.
  If using the 5.x driver, this does not need to be checked.

## Common Issues

* Unable to specify computing resources

  * You need to assign a default Virtual Cluster for the connecting user in Lakehouse
  * ```SQL
    ALTER USER UAT_TEST SET DEFAULT_VCLUSTER = DEFAULT;
    -- Check if the vcluster setting has taken effect
    SHOW USERS;
    ```

## Troubleshooting

Troubleshoot issues through the Lakehouse job history. After connecting via the MySQL protocol, MySQL connections to Lakehouse typically send some SQL, and job history records all submitted SQL. You can view the sent SQL through job history to see error information. Filter quickly using these three conditions:

* Virtual Cluster: The Virtual Cluster specified in the BI report
* Submitter: The username connected in the BI report — for example, if it is `test@jnsxwfyr.ql_ws`, filter by `test`
* Schema: The schema name specified in the BI report
* Click the refresh button in the upper right corner to monitor SQL sent by the BI report

![](.topwrite/assets/image_1722596643860.png)

## Examples

* Using mysql client to connect

mysql client connection to Lakehouse:

```
-- Add the -A option to avoid sending some validation SQL when connecting to mysql
mysql -h cn-shanghai-alicloud-mysql.api.singdata.com -u user_name@instance_name.workspace_name -D public -p -A

-- When connecting with the mysql client, if you get the error: ERROR 2059 (HY000): Authentication plugin 'mysql_clear_password' cannot be loaded: plugin not enabled, add parameters and use the following command to connect
mysql -h cn-shanghai-alicloud-mysql.api.singdata.com -u user_name@instance_name.workspace_name -Dpublic -p -A --enable-cleartext-plugin --default-auth=mysql_native_password
```

* Use [Power BI to connect to Lakehouse](PowerBI.md)
