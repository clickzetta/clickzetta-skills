# SQL Server Data Source Configuration Guide

## Overview

SQL Server is a relational database management system provided by Microsoft. It offers powerful data processing capabilities and extensive application support. By configuring a SQL Server data source, you can achieve data synchronization and integration with other systems.

## Parameter Configuration

When configuring a SQL Server data source, you need to provide the following information to ensure a successful connection to the database:

* **Data Source Name**: Specify a unique and easily recognizable name for your SQL Server data source.
* **JDBC Connection URL**: Provide the JDBC connection URL for the SQL Server database, usually in the format `jdbc:sqlserver://host:port;databaseName=dbname`. For example, `jdbc:sqlserver://sqlserver-host:1433;databaseName=mydatabase`.
* **Username**: The username used to connect to the SQL Server database.
* **Password**: The database password corresponding to the username.
* **Schema**: (Optional) Specify the default schema to use when connecting, such as `dbo`.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible over the public network. If the source has an IP access whitelist enabled, make sure the outbound IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to datasource via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number on which the SSH server is listening, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the SQL Server service is accessible.
* Protect your database credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

After completing the configuration, you can select this SQL Server data source in data synchronization tasks to perform data import or export operations. Connecting via SSH tunnel can enhance the security of data transmission, especially when handling sensitive data.