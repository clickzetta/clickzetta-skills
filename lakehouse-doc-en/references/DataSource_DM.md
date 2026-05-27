# DM Data Source Configuration Guide

## Overview

DM Database (DM) is a domestically produced relational database management system that offers high security, high reliability, and high performance data processing capabilities. By configuring the DM database data source, you can achieve data synchronization and integration with other systems, supporting enterprise-level data management and analysis needs.

## Parameter Configuration

When configuring the DM database data source, you need to provide the following information to ensure a successful connection to the DM database:

* **Data Source Name**: Specify a unique and easily recognizable name for your DM database data source.
* **JDBC Connection Address**: Provide the JDBC connection address of the DM database, usually in the format `jdbc:dm://host:port/sid`. For example, `jdbc:dm://dm-host:5236/dm`.
* **Username**: Enter the username used to connect to the DM database.
* **Password**: Provide the database password corresponding to the username.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible on the public network. If the source end has enabled an IP access whitelist, make sure the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to the DM database via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number that the SSH server listens to, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the DM database service is accessible.
* Protect your database credentials and SSH credentials to prevent leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this DM database data source in data synchronization tasks to perform data import or export operations. Connecting via SSH tunnel can enhance the security of data transmission, especially when handling sensitive data. The direct connection method provides a more straightforward data transmission path.