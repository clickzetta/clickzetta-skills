# ADB for PostgreSQL Data Source Configuration Guide

## Overview

ADB for PostgreSQL is a relational database service provided by Alibaba Cloud. It is based on the open-source PostgreSQL database, supports SQL and NoSQL data models, and offers high-performance, high-availability, and elastic scaling data storage solutions. By configuring the ADB for PostgreSQL data source, you can achieve efficient data synchronization and analysis to meet complex business needs.

## Parameter Configuration

When configuring the ADB for PostgreSQL data source, you need to provide the following information to ensure a successful connection to the ADB service:

* **Data Source Name**: Specify a unique and easily recognizable name for your ADB for PostgreSQL data source.
* **JDBC Connection Address**: Provide the JDBC connection address of the ADB for PostgreSQL instance, usually in the format `jdbc:postgresql://host:port/database`.
* **Username**: Enter the username used to connect to the ADB for PostgreSQL instance.
* **Password**: Provide the database password corresponding to the username.
* **Schema**: Specify the default schema to connect to, such as `public` or any other schema you need to use.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible over the public network. If the source has enabled an IP access whitelist, make sure the outbound IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to ADB for PostgreSQL via an SSH tunnel. Enable this option and provide the following SSH tunnel-related configuration information:
  * **SSH Server Address**: Provide the IP address or domain name of the SSH server.
  * **SSH Port**: Specify the port number that the SSH server listens to, usually `22`.
  * **Username**: Provide the login username for the SSH server.
  * **Password**: Provide the password corresponding to the SSH server login username.

## Notes

* Ensure that all provided connection information is accurate and that the ADB for PostgreSQL service is accessible.
* Protect your database credential information and SSH credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this ADB for PostgreSQL data source in data synchronization tasks to perform data import or export operations. Connecting via SSH tunnel can enhance the security of data transmission, especially when handling sensitive data.