# ClickHouse Data Source Configuration Guide

## Overview

ClickHouse is an open-source columnar database management system that supports efficient data analysis using SQL and can quickly generate reports. By configuring the ClickHouse data source, you can achieve fast data import, export, and analysis.

## Parameter Configuration

When configuring the ClickHouse data source, you need to provide the following information to ensure a successful connection to the database:

* **Data Source Name**: Specify a unique and easily recognizable name for your ClickHouse data source, such as `ClickHouseSource01`.
* **JDBC Connection URL**: Provide the JDBC connection URL for the ClickHouse database, in the format `jdbc:clickhouse://host:port/`. For example, `jdbc:clickhouse://host01:8123/`.
* **Username**: Enter the username used to connect to the ClickHouse database, such as `user01`.
* **Password**: Provide the database password corresponding to the username, such as `password`.
* **Schema**: Specify the default database to connect to, such as `default`.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible over the public network. If the source end has enabled an IP access whitelist, make sure the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to datasource via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number on which the SSH server is listening, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the ClickHouse service is accessible.
* Protect your database credentials to prevent them from being disclosed to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

After completing the configuration, you can select this ClickHouse data source in data synchronization tasks to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data.