# Doris Data Source Configuration Guide

## Overview

Doris is a high-performance distributed data warehouse designed for fast analytics. By configuring the Doris data source, you can achieve efficient data import, export, and real-time analysis to meet the business needs of the big data era.

## Parameter Configuration

When configuring the Doris data source, you need to provide the following information to ensure a successful connection to the Doris cluster:

* **Data Source Name**: Specify a unique and easily recognizable name for your Doris data source.
* **JDBC Connection URL**: Provide the JDBC connection URL for the Oracle database, usually in the format `jdbc:oracle:thin:@host:port:SID` or `jdbc:oracle:thin:@host:port:service_name`. For example, `jdbc:oracle:thin:@oracle-host:1521:ORCL`.
* **Username**: Enter the username used to connect to the Oracle database.
* **Password**: Provide the database password corresponding to the username.
* **ExternalCatalog**: (Optional) Provide external catalog configuration, including type (such as MySQL, PostgreSQL, etc.) and corresponding connection information, for example, `mysql://user:password@host:port/database`.
* **Address Type**: Select the node type, providing two options: "FE Node Address" and "BE Node Address".
  * **FE Node Address**: Provide the address of the Doris Frontend (FE) node for connecting and managing the Doris cluster. For example, `fe-node:8030`.
  * **BE Node Address**: Provide the address of the Doris Backend (BE) node for data storage and query processing. For example, `be-node:9050`.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you need to pay attention to the following:

* Depending on the selected address type, ensure that the entered FE or BE node address is accessible on the public network. If the source end has enabled an IP access whitelist, ensure that the outbound IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.

## Notes

* Ensure that all provided connection information is accurate and that the Doris service is accessible.
* If your Doris cluster has enabled authentication, protect your credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in cluster structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

After the configuration is complete, you can select this Doris data source in data synchronization tasks to perform data import or export operations. Choosing the appropriate node type and ensuring the correctness of the address can provide efficient data transmission and improve data processing efficiency. During the configuration process, ensure to follow best practices and security policies to protect your data security.