# PostgreSQL Data Source Configuration Guide

## Overview

PostgreSQL is a powerful open-source object-relational database system that provides advanced features such as complex queries, foreign keys, triggers, and views. By configuring a PostgreSQL data source, you can achieve data synchronization and integration with other systems, supporting various data analysis and reporting needs.

## Parameter Configuration

When configuring a PostgreSQL data source, you need to provide the following information to ensure a successful connection to the database:

* **Data Source Name**: Specify a unique and easily recognizable name for your PostgreSQL data source, such as `PGDataSourceExample`.
* **JDBC Connection URL**: Provide the JDBC connection URL for the PostgreSQL database, usually in the format `jdbc:postgresql://host:port/database`. For example, `jdbc:postgresql://postgres-server:5432/mydatabase`.
* **Username**: Enter the username used to connect to the PostgreSQL database, such as `dbuser`.
* **Password**: Provide the database password corresponding to the username, such as `dbpassword`.
* **Schema**: Specify the default schema to connect to, such as `public`.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

Regarding connection configuration, you need to pay attention to the following:

* **Direct Connection**: Ensure that the connection information you entered is accessible over the public network. If the source has an IP access whitelist enabled, make sure the outbound IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to datasource via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number on which the SSH server is listening, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the PostgreSQL service is accessible.
* Protect your database credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this PostgreSQL data source in data synchronization tasks to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data.