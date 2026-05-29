# OSS Data Source Configuration Guide

## Overview

OSS (Object Storage Service) is an object storage service provided by Alibaba Cloud, suitable for large-scale, high-reliability data storage needs. By configuring the OSS data source, you can achieve efficient data upload, download, and synchronization, supporting various data usage scenarios.

## Parameter Configuration

When configuring the OSS data source, you need to provide the following information to ensure a successful connection to the OSS service:

* **Data Source Name**: Specify a unique and easily recognizable name for your OSS data source, such as `OSSDataSync`.
* **Alibaba Cloud OSS Address**: Provide the Endpoint connection address for the OSS service. For example, `oss-cn-shanghai-internal.aliyuncs.com`.
* **Alibaba Cloud accessKeyId**: The accessKeyId of your Alibaba Cloud account, used for authentication.
* **Alibaba Cloud accessKeySecret**: The private access key corresponding to the accessKeyId.
* **Alibaba Cloud OSS Bucket**: Specify the name of the OSS bucket to connect to, such as `my-oss-bucket`.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you need to pay attention to the following:

* **Direct Connection**: Ensure that the connection information you entered is accessible on the public network. If the source end has enabled an IP access whitelist, make sure that the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support. It also supports accessing via OSS intranet and public network Endpoints, and you can choose the access method based on the "Alibaba Cloud OSS Address" domain name address.

## Notes

* Ensure that all provided connection information is accurate and that the OSS service is accessible.
* Protect your credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the bucket structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any issues that may arise.

After completing the configuration, you can select this OSS data source in data synchronization tasks to perform data import or export operations. Through the direct connection method, you can achieve fast data transmission and improve data processing efficiency.