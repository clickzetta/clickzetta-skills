# Hologres Data Source Configuration Guide

## Overview

Hologres is a high-performance, highly available distributed data warehouse service that provides powerful data storage and analysis capabilities. By configuring the Hologres data source, you can achieve efficient data synchronization and complex analysis, supporting various data operations and reporting needs.

## Parameter Configuration

When configuring the Hologres data source, you need to provide the following information to ensure a successful connection to the Hologres service:

* **Data Source Name**: Specify a unique and easily recognizable name for your Hologres data source.
* **JDBC Connection URL**: Provide the JDBC connection URL for the Hologres database, typically in the format  `jdbc:postgresql://host:port/database`, such as `jdbc:postgresql://xxxxxxxxxx-cn-hangzhou.hologres.aliyuncs.com:80/test`。
* **Username**: Enter the username used to connect to the Hologres database.
* **Password**: Provide the database password corresponding to the username.
* **Schema**: Specify the default schema to connect to, such as `public` or any other schema you need to use.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible over the public network. If the source has enabled an IP access whitelist, make sure the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to Hologres via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server, such as `ssh.example.com`.
  * **SSH PORT**: Specify the port number that the SSH server listens on, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the Hologres service is accessible.
* Protect your database credentials and SSH credentials to prevent unauthorized access.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this Hologres data source in data synchronization tasks to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data.
