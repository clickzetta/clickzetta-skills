# COS Data Source Configuration Guide

## Overview

COS (Cloud Object Storage) is an object storage service provided by Tencent Cloud. It offers enterprises and developers a massive, secure, and cost-effective data storage solution. By configuring a COS data source, users can achieve efficient data upload, download, and synchronization, supporting various data usage scenarios.

## Parameter Configuration

When configuring a COS data source, you need to provide the following information to ensure a successful connection to the COS service:

1. **Data Source Name**: Specify a unique and easily recognizable name for your COS data source.
2. **regionName**: Specify the region name where the bucket is located, such as `ap-guangzhou`. This parameter is very important for the COS service as it determines the geographical location of the data storage and the access path to the service.
3. **Bucket Name**: Specify the name of the COS bucket to connect to.
4. **SecretId**: The SecretId of your Tencent Cloud account, used for authentication.
5. **SecretKey**: The SecretKey corresponding to the SecretId, used for authentication.
6. **Data Source Description** (optional): Add descriptive information for the data source to help understand the purpose or characteristics of this data source.

## Connection Configuration

In terms of connection configuration, you need to pay attention to the following:

* **Direct Connection**: Ensure that the connection information you entered is accessible on the public network. If the source end has enabled an IP access whitelist, make sure that the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.

## Notes

* Ensure that all provided connection information is accurate and that the COS service is accessible.
* Protect your credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the bucket structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

When configuring the COS data source, refer to Tencent Cloud's official documentation and support resources for the most accurate guidance. Once the configuration is complete, you can select this COS data source in data synchronization tasks to perform data import or export operations.