# Aurora MySQL Data Source Configuration Guide

## Overview

Amazon Aurora MySQL is a MySQL-compatible cloud-native relational database that offers high performance, scalability, and a MySQL-compatible programming environment. By configuring the Aurora MySQL data source, you can achieve data synchronization and integration with other systems, supporting complex data analysis and transaction processing.

## Parameter Configuration

When configuring the Aurora MySQL data source, you need to provide the following information to ensure a successful connection to the Aurora MySQL database:

* **Data Source Name**: Specify a unique and easily recognizable name for your Aurora MySQL data source.
* **JDBC Connection URL**: Provide the JDBC connection URL for the Aurora MySQL database, typically in the format `jdbc:mysql://host:port/database`. For example, `jdbc:mysql://aurora-mysql-host:3306/mydatabase`.
* **Username**: Enter the username used to connect to the Aurora MySQL database.
* **Password**: Provide the database password corresponding to the username.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you enter is accessible over the public network. If the source has an IP access whitelist enabled, make sure the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to Aurora MySQL via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number on which the SSH server is listening, typically `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the Aurora MySQL service is accessible.
* Protect your database credentials and SSH credentials to prevent them from being disclosed to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this Aurora MySQL data source in data synchronization tasks to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data. The direct connection method provides a more straightforward data transmission path.