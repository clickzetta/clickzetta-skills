# Introduction

\[**Preview Release] This feature is currently in public preview**.

| Cloud Provider | Region    | Compatible MySQL Protocol Version |
| -------------- | --------- | --------------------------------- |
| Alibaba Cloud  | Singapore | MySQL5.x and MySQL8.x             |
|                | Shanghai  | MySQL5.x and MySQL8.x             |
| Tencent Cloud  | Shanghai  | MySQL8.x                          |
|                | Beijing   | MySQL8.x                          |
|                | Guangzhou | MySQL8.x                          |
| Amazon         | Beijing   | MySQL8.x                          |
|                | Singapore | MySQL8.x                          |

Lakehouse supports the MySQL client-server communication protocol, so you can use MySQL drivers to connect to Lakehouse. However, Lakehouse does not implement MySQL syntax and data types. When connecting to Lakehouse via a MySQL client, the SQL statements executed should use Lakehouse syntax, not MySQL syntax. For example, the `mysqldump` command is not available in Lakehouse.

To accommodate some BI reports, Lakehouse has implemented some commonly used MySQL functions, such as `str_to_date` and `date_format`. Currently, Lakehouse supports the following protocols:
The default authentication method used when a MySQL8.x client connects to the server is caching\_sha2\_password. For more information on MySQL authentication methods, please refer to the [official documentation](https://dev.mysql.com/doc/refman/8.0/en/authentication-plugins.html). SSL must be enabled to connect to Lakehouse. The connection method is as follows, for example, connecting to Alibaba Cloud in Shanghai.

```
jdbc:mysql://ap-southeast-1-aws-mysql.api.singdata.com/public?useSSL=true
--Add port, optional
jdbc:mysql://ap-southeast-1-aws-mysql.api.singdata.com:3306/public?useSSL=true
```

```markdown
When the MySQL 5.x version client connects to the server, it uses the mysql_native_password authentication method by default. For more information on MySQL authentication methods, please refer to the [official documentation](https://dev.mysql.com/doc/refman/8.0/en/authentication-plugins.html). Connecting to Lakehouse does not require SSL to be enabled. The connection method is as follows, for example, connecting to Shanghai Alibaba Cloud.

* Currently, you need to reset the password, even for newly created accounts. This is because the MySQL 5.x version uses the `mysql_native_password` key, and Lakehouse needs to store MySQL's encryption algorithm. Currently, Lakehouse will only store MySQL key's encryption algorithm when the password is changed. You can keep the same password when modifying it to avoid affecting other task connections.
```

```
jdbc:mysql://cap-southeast-1-aws-mysql.api.singdata.com/public?useSSL=false
--Add port, optional
jdbc:mysql://ap-southeast-1-aws-mysql.api.singdata.com:3306/public?useSSL=false
```

Port: 3306 Optional

## Usage Scenarios

* Unable to use Lakehouse driver scenarios, such as some report scenarios that do not support custom JDBC drivers or do not support Lakehouse native JDBC drivers. If the Lakehouse native driver can be used, use it as much as possible.

## Usage Restrictions

* Currently unable to fully support MySQL functions and syntax, some MySQL-specific syntax and functions in some reports will cause errors when sent to Lakehouse (please contact Lakehouse support).
* Data type restrictions
  * Using the MySQL driver does not support MySQL types such as mediumint, numeric, bit, time, year, datetime, varbinary, text, blob, enum, set, spatial data types. If the SQL sent contains these keywords, an error will occur, for example, cast(xxxx as datetime).
  * Using the MySQL driver does not support complex types such as array, struct, map, json, binary, etc., which are unique to Lakehouse. This is because the MySQL client cannot handle Lakehouse-specific types.
* Syntax restrictions
  * Does not support MySQL-specific syntax such as MySQL dump command, Load command, etc.
* Function restrictions
  * Lakehouse implements some commonly used MySQL functions, such as `str_to_date` and `date_format`. If you need more, please contact Lakehouse support.
* Data import restrictions
  * Does not support MySQL bulk data import, such as the MySQL load command.
  * Using the MySQL driver does not support Lakehouse local commands ([COPY LOCAL file](copy.md), [PUT](PUT.md), [REMOVE](remove-volume.md), [GET](GET.md), etc.), and does not support using the MySQL driver to call Lakehouse's Java SDK for bulk upload and real-time upload of data.
* When MySQL lists the table structure, it needs to query the information schema. Currently, there is a 15-minute delay for newly created tables in the information schema in Lakehouse, so newly created tables cannot be seen immediately.

## Connection Method

## 1. Set up the computing cluster

Since there is no way to set the cluster in the MySQL protocol, users can use SQL commands to add a default computing cluster for the user. This way, the cluster will be used when connecting to MySQL. It should be noted that BI scenarios often have performance requirements for analysis, so it is recommended to choose an appropriate specification of the analytical computing cluster for the BI tool connection user to provide the best query performance.

```sql
ALTER USER user_name SET DEFAULT_VCLUSTER = default;

-- Check if the cluster settings have taken effect
SHOW USERS;
```

## 2. Set Username and Password

Since the MySQL protocol does not include workspace name and instance name, you need to concatenate the instance name and workspace name into the username.

The username format requirements are as follows:

```
The account name used to log in@instance_name.workspace_name
```

* **instance\_name Retrieval**: Obtain the JDBC connection string from the [workspace](workspace-introduction.md) page. For example, in `jdbc:clickzetta://jnsxwfyr.api.singdata.com/quick_start?virtualCluster=default`, `jnsxwfyr` is the instance\_name.
* **workspace\_name Retrieval**: The name of the workspace.

Example:

```
user@jnsxwfyr.quick_start
```

## 3. Set Connection Address:

Port: 3306

| Cloud Service Provider | Region    | Connection Address                                 |
| ---------------------- | --------- | -------------------------------------------------- |
|  Alibaba Cloud                      | Singapore | ap-southeast-1-alicloud-mysql.api.singdata.com     |
|     Amazon                   | Singapore | ap-southeast-1-aws-mysql.api.singdata.com          |

## 4. Other Parameters:

* useSSL=true: Lakehouse uses caching\_sha2\_password for MySQL 8.x clients, so when connecting with MySQL 8.x drivers, you must set useSSL=true. If using MySQL 5.x versions, set useSSL=false.
* Database Name: The schema name of Lakehouse
* Port: 3306 optional

## General BI Report Configuration Parameters

**Connection Tool**

It is recommended to use the MySQL Java 8.0 driver to run SQL. However, some reports may initialize with MySQL-specific syntax. If you encounter errors, please contact Lakehouse technical support.

**Set vcluster**:
You need to specify the default vcluster for the connecting user in Lakehouse. This way, the specified cluster will be used when connecting via MySQL. Note that BI scenarios often have performance requirements for analysis, so it is recommended to choose an appropriate specification of the analytical computing cluster for the BI tool connecting user to provide the best query performance.

```SQL
ALTER USER user_name SET DEFAULT_VCLUSTER= default_ap;
--Check if the vcluster setting is effective
show users;
```

**Driver Requirements**: MySQL 8.0 or above is recommended

**Connection Address (must be configured**)

**Username Format (must be configured**)

* Format: <<<username@instance_name.workspace_name>>>, for example, <<<test@jnsxwfyr.ql_ws>>>

**Database Name (must be configured**)

* Format: schema name, such as public

**Port: 3306. Some reports need to be configured**

**Additional Parameters (must be configured**):

If using the 8.x driver, some reports can directly fill in the configuration parameters by entering the following string

* useSSL=true

If the report does not support filling in parameters

* The useSSL option can be selected in the report interface if SSL needs to be used
  If using the 5.x version driver, it does not need to be selected

## Common Issues

* Unable to specify computing resources

  * The user connected needs to be assigned a default vcluster, which can be specified in Lakehouse for the user's default vcluster
* ```SQL
    alter user UAT_TEST set DEFAULT_VCLUSTER= default;
    -- Check if the vcluster setting is effective
    show users;
  ```

## Troubleshooting

Troubleshoot issues through lakehouse job history. After connecting via the MySQL protocol, the MySQL connection to Lakehouse usually sends some SQL, and the job history will record the sent SQL. At this point, we can view the sent SQL through the job history to see the error information. Quickly locate through filtering, with the following three filtering conditions:

* Compute Cluster: The compute cluster specified in the BI report
* Submitter: The username connected in the BI report, for example, if it is <<<<<test@jnsxwfyr.ql_ws>>>>>, then filter here as test
* Schema: The schema name specified in the BI report
* Monitor the SQL sent by the BI report by clicking the refresh button in the upper right corner

  ![](.topwrite/assets/image_1739867274817.png)

## Case

* Using MySQL client connection

MySQL client connects to Lakehouse:

```
-- Add the -A option to avoid sending some verification SQL when connecting to mysql
mysql -h cn-shanghai-alicloud-mysql.api.clickzetta.com -u user_name@instance_name.worksapace_name -D  public -p -A

-- When using the mysql client to connect, if the error message is: ERROR 2059 (HY000): Authentication plugin 'mysql_clear_password' cannot be loaded: plugin not enabled, you can add parameters and use the following command to connect
mysql -h cn-shanghai-alicloud-mysql.api.clickzetta.com -u user_name@instance_name.worksapace_name -Dpublic -p -A --enable-cleartext-plugin --default-auth=mysql_native_password
```

* Use [Power BI to connect to Lakehouse](<power_bi.md>)

^
