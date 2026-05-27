# SLS(LogHub) Data Source Configuration Guide

## Overview

SLS (Log Service), also known as LogHub, is a real-time log service provided by Alibaba Cloud for the collection, storage, query, and analysis of log data. Configuring an SLS data source can make your data synchronization and analysis work more efficient, especially suitable for handling large-scale log data.

## Parameter Configuration

When configuring an SLS data source, you need to provide the following information to ensure a successful connection to the SLS service:

* **Data Source Name**: Specify a unique and easily recognizable name for your SLS data source, such as `MySLSDataSource`.
* **Project**: Provide the SLS project name, which is the project identifier you set in the SLS console.
* **Alibaba Cloud SLS Service Address**: Fill in the Endpoint connection address of the SLS service, usually the SLS service address in your region.
* **Alibaba Cloud accessKeyId**: Provide the Access Key ID of your Alibaba Cloud account for authentication.
* **Alibaba Cloud accessKeySecret**: Provide the Access Key Secret corresponding to the Access Key ID for authentication.
* **Data Source Description (Optional)**: Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you need to pay attention to the following matters:

* **Direct Connection**: Ensure that the connection information you entered is accessible on the public network. If the source end has enabled an IP access whitelist, make sure that the outbound IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support personnel.

## Notes

* Ensure that all provided connection information is accurate and that the SLS service is accessible.
* Protect your credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in project structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly discover and resolve any potential issues.

After the configuration is complete, you can select this SLS data source in data synchronization tasks to perform log data import or export operations. Through the direct connection method, you can achieve fast log data transmission and improve log processing efficiency.