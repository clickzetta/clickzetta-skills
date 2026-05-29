# MariaDB Data Source Configuration Guide

## Overview

MariaDB is a popular open-source relational database management system, which is a fork of MySQL, offering high performance, reliability, and compatibility. By configuring the MariaDB data source, you can achieve efficient data synchronization and processing, supporting various data operations and analysis tasks.

## Parameter Configuration

When configuring the MariaDB data source, you need to provide the following information to ensure a successful connection to the MariaDB database:

* **Data Source Name**: Specify a unique and easily recognizable name for your MariaDB data source.
* **JDBC Connection URL**: Provide the JDBC connection URL for the MariaDB database, usually in the format `jdbc:mysql://host:port/database`. For example, `jdbc:mysql://mariadb-host:3306/mydatabase`.
* **Username**: Enter the username used to connect to the MariaDB database.
* **Password**: Provide the database password corresponding to the username.
* **Allow using configuration information to connect to all databases/Schemas** (optional): Check this option to allow the configuration information to be used to connect to all databases and schemas in the MariaDB instance. If unchecked, the connection will be limited to the specified schema.
* **Data Source Description** (optional): Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible over the public network. If the source end has enabled an IP access whitelist, make sure the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to MariaDB via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number on which the SSH server is listening, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the MariaDB service is accessible.
* Protect your database credentials and SSH credentials to prevent unauthorized access.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this MariaDB data source in data synchronization tasks to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data. Checking the "Allow using configuration information to connect to all databases/Schemas" option can provide greater flexibility, but use it cautiously to avoid security risks.