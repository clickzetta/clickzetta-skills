# DB2 Data Source Configuration Guide

## Overview

DB2 is a relational database management system developed by IBM, known for its high performance, high reliability, and powerful data processing capabilities. By configuring a DB2 data source, you can achieve data synchronization and integration with other systems, supporting complex data analysis and transaction processing.

## Parameter Configuration

When configuring a DB2 data source, you need to provide the following information to ensure a successful connection to the DB2 database:

* **Data Source Name**: Specify a unique and easily recognizable name for your DB2 data source.
* **JDBC Connection URL**: Provide the JDBC connection URL for the DB2 database, usually in the format `jdbc:db2://host:port/database`. For example, `jdbc:db2://db2-host:50000/mydatabase`.
* **Username**: Enter the username used to connect to the DB2 database.
* **Password**: Provide the database password corresponding to the username.
* **Schema**: Specify the default schema to connect to, such as `public` or any other schema you need to use.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

For connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible over the public network. If the source has an IP access whitelist enabled, make sure the outbound IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to DB2 via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number on which the SSH server is listening, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the DB2 service is accessible.
* Protect your database credentials and SSH credentials to prevent them from being disclosed to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this DB2 data source in data synchronization tasks to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data. The direct connection method provides a more straightforward data transmission path.