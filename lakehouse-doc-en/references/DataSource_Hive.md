# Hive Data Source Configuration Guide

## Overview

Hive is a data warehouse software based on the Hadoop ecosystem. It provides an SQL interface (HiveQL) to query and manage large-scale datasets. By configuring the Hive data source, you can achieve data synchronization with other systems and perform complex data analysis tasks.

## Parameter Configuration

When configuring the Hive data source, you need to provide the following information to ensure a successful connection to the Hive service:

* **Data Source Name**: Specify a unique and easily recognizable name for your Hive data source.
* **HiveServer Connection Information**: Provide the JDBC connection URL for HiveServer, usually in the format `jdbc:hive2://host:port/database`. For example, `jdbc:hive2://hive-server:10000/default`.
* **Authentication Mode**: Choose whether to use anonymous authentication. If anonymous is selected, no username and password are required; if not, you must provide a username and password.
* **Username**: If not using anonymous authentication, provide the username required to connect to the database.
* **Password**: The database password corresponding to the username.
* **defaultFS**: Provide the default parameter for HDFS, corresponding to the `fs.defaultFS` parameter in the core-site.xml file.
* **hiveVersion** (optional): Provide the version information of Hive.
* **hiveMetaStoreUri** (optional): Provide the Hive metastore connection URI.
* **Extended Parameters** (optional): If needed, provide other Hadoop-related parameters, such as the NameNode address.
```JSON
{
    "hadoop.user.name": "datadev",
    "dfs.ha.namenodes.zetta-cluster": "nn1,nn2",
    "dfs.namenode.rpc-address.zetta-cluster.nn1": "test-01:8020",
    "dfs.nameservices": "zetta-cluster",
    "dfs.namenode.rpc-address.zetta-cluster.nn2": "test-02:8020"
}
```
* **Authentication Method**: Choose the authentication method, providing two options: "None" and "Kerberos Authentication".
  * If "None" is selected, no additional authentication information is required.
  * If "Kerberos Authentication" is selected, Kerberos-related authentication information needs to be provided, including:
    * Username: Provide the username for Kerberos authentication.
    * Password: Provide the password corresponding to the username.
    * Kerberos keytab file (optional): If using a Kerberos keytab for authentication, provide the path to the keytab file.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you enter is accessible over the public network. If the source end has enabled an IP access whitelist, make sure the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to Hive via an SSH tunnel. Enable this option and provide the IP address and port of the SSH service. Ensure that your SSH client is properly configured and that you have permission to connect to the Hive server via SSH.

## Notes

* Ensure that all provided connection information is accurate and that the Hive service is accessible.
* Protect your database credential information to prevent leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

After completing the configuration, you can select this Hive data source in the data synchronization task to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data.