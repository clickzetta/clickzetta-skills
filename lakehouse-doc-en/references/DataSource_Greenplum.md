# Greenplum Data Source Configuration Guide

## Overview

Greenplum is a high-performance, scalable open-source data warehouse platform developed based on PostgreSQL. By configuring the Greenplum data source, you can achieve efficient querying and analysis of large-scale datasets to meet complex data processing needs.

## Parameter Configuration

When configuring the Greenplum data source, you need to provide the following information to ensure a successful connection to the Greenplum database:

* **Data Source Name**: Specify a unique and easily recognizable name for your Greenplum data source.
* **JDBC Connection URL**: Provide the JDBC connection URL for the Greenplum database, usually in the format `jdbc:postgresql://host:port/database`. For example, `jdbc:postgresql://gp-server:5432/mydatabase`.
* **Username**: Enter the username used to connect to the Greenplum database.
* **Password**: Provide the database password corresponding to the username.
* **Schema**: Specify the default schema to connect to, such as `public` or any other schema you need to use.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible over the public network. If the source has an IP access whitelist enabled, make sure the outbound IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to Greenplum via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number the SSH server listens to, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the Greenplum service is accessible.
* Protect your database credentials and SSH credentials to avoid leaking them to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this Greenplum data source in data synchronization tasks to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data. Selecting the "Allow using configuration information to connect to all databases/Schemas" option can provide greater flexibility, but use it with caution to avoid security risks.