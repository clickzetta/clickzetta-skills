# PolarDB Data Source Configuration Guide

## Overview

PolarDB is a high-performance, scalable cloud-native relational database service provided by Alibaba Cloud. It is compatible with multiple database engines such as MySQL, PostgreSQL, and Oracle, offering high availability and elastic scaling capabilities. By configuring a PolarDB data source, you can achieve efficient data synchronization and analysis to meet enterprise-level data management requirements.

## Parameter Configuration

When configuring a PolarDB data source, the following information must be provided to ensure a successful connection to the PolarDB service:

* **Data Source Name**: Specify a unique and easily identifiable name for your PolarDB data source.
* **JDBC Connection Address**: Provide the JDBC connection address for the PolarDB instance, typically in the format `jdbc:engine_type://host:port/database`, for example `jdbc:mysql://polar-db-host:3306/mydatabase`.
* **Username**: Enter the username for connecting to the PolarDB instance.
* **Password**: Provide the database password corresponding to the username.
* **Schema**: Specify the default Schema to connect to, such as `public` or another Schema you need to use.
* **Allow Using Configuration Info to Connect to All Databases/Schemas**: Enable this option so that the configuration information can be used to connect to all databases and schemas in the PolarDB instance. If not enabled, the connection will be limited to the specified Schema.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of this data source.

## Connection Configuration

For connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure the connection information you enter is publicly accessible. If the source has IP access whitelisting enabled, make sure the data integration service's egress IP address has been added to the whitelist. Contact technical support for the specific IP address.
* **Via SSH Tunnel**: To improve security, you can choose to connect to PolarDB through an SSH tunnel. Enable this option and provide the following SSH tunnel configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number the SSH server is listening on, typically `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure all provided connection information is accurate and the PolarDB service is accessible.
* Protect your database credentials and SSH credentials to prevent disclosure to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly detect and resolve potential issues.

After configuration is complete, you can select this PolarDB data source in data synchronization tasks for data import or export operations. Connecting via an SSH tunnel enhances the security of data transmission, especially when handling sensitive data. Checking the "Allow Using Configuration Info to Connect to All Databases/Schemas" option provides greater flexibility, but use it with caution to avoid security risks.
