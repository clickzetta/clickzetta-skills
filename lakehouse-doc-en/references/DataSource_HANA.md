# HANA Data Source Configuration Guide

## Overview

SAP HANA is a high-performance in-memory relational database management system developed by SAP. It supports both OLTP (Online Transaction Processing) and OLAP (Online Analytical Processing), with real-time data processing capabilities and advanced analytics features. By configuring an SAP HANA data source, you can achieve efficient data synchronization and processing to support complex data analysis and business intelligence applications.

## Parameter Configuration

When configuring an SAP HANA data source, provide the following information to ensure a successful connection to the HANA database:

* **Data source name**: Assign a unique, easily identifiable name to your HANA data source. A meaningful naming convention is recommended, such as "Behavioral Data Source".
* **JDBC connection URL**: Provide the JDBC connection URL for the SAP HANA database. The format is typically `jdbc:sap://host:port`, for example `jdbc:sap://hana-server:30015`. For HANA Cloud, the connection URL may look like `jdbc:sap://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.hana.trial-us10.hanacloud.ondemand.com:443/?encrypt=true&validateCertificate=true`.
* **Username**: Enter the username for connecting to the HANA database. This is typically a database user with the appropriate permissions, such as `admin`.
* **Password**: Provide the database password for the corresponding username. Ensure the password is secure and accurate.
* **Allow this configuration to connect to all databases/schemas** (optional): Check this option to allow the configuration to be used for connecting to all databases and schemas in the HANA instance. If unchecked, the connection is limited to the specified schema. Use this option with caution in production environments.
* **Database timezone**: Select the timezone of the HANA database to ensure time data accuracy.
* **Data source description**: (Optional) Add a description to help you or other administrators understand the purpose or characteristics of this data source.

## Connection Configuration

For the connection configuration, you can choose one of the following connection methods:

### Direct Connection

Ensure that the connection information you enter is accessible over the network. If the HANA server has an IP allowlist enabled, make sure the outbound IP address of the data integration service has been added to the allowlist. Contact technical support for the specific IP addresses.

### Via SSH Tunnel

For enhanced security, you can connect to SAP HANA through an SSH tunnel. Enable this option and provide the following SSH tunnel configuration:

* **SSH server address**: Provide the IP address or hostname of the SSH server.
* **SSH port**: Specify the port the SSH server listens on, typically `22`.
* **Username**: Provide the login username for the SSH server.
* **Password**: Provide the password for the SSH server login username.

## Notes

* **Validate connection details**: Ensure all provided connection details are accurate and that the SAP HANA service is accessible. Before saving the configuration, use the "Test Connection" feature to verify connectivity.
* **Security management**: Keep your database credentials and SSH credentials secure and do not expose them to unauthorized parties. Rotate database passwords regularly.
* **Permission configuration**: Ensure the database user used for the connection has the permissions required to perform data synchronization tasks, including but not limited to SELECT, INSERT, UPDATE, and DELETE.
* **Network configuration**: If the HANA database is deployed behind a firewall, ensure the necessary ports (e.g., 30015, 30013) are open.
* **Performance optimization**: As an in-memory database, SAP HANA benefits from properly configured connection pool parameters for optimal performance.
* **Monitoring and maintenance**: Regularly review and update your data source configuration to accommodate changes in database structure or new security requirements. Monitor the status of data synchronization tasks to detect and resolve issues promptly.
* **Version compatibility**: Confirm that your HANA database version is compatible with the data integration platform. HANA Cloud, HANA 2.0 SP04, or later versions are recommended.

## Best Practices

* **Connection pool configuration**: Set an appropriate connection pool size to avoid performance issues caused by too many or too few connections.
* **Schema permissions**: Grant only the necessary schema access permissions, following the principle of least privilege.
* **Data type mapping**: Understand the mapping between HANA data types and the target system to ensure data synchronization accuracy.
* **Backup strategy**: Back up target data before performing important data synchronization operations.

Once configuration is complete, you can select this HANA data source in your data synchronization tasks to import or export data. Connecting via an SSH tunnel enhances the security of data transmission, especially when handling sensitive data. Proper permission configuration and security measures will ensure your HANA data source is both efficient and secure.
