# MaxCompute Data Source Configuration Guide

## Overview

MaxCompute is a fully managed big data computing service provided by Alibaba Cloud. It supports the storage, processing, and analysis of massive amounts of data. By configuring the MaxCompute data source, you can achieve data synchronization with other systems and big data analysis.

## Parameter Configuration

When configuring the MaxCompute data source, you need to provide the following information to ensure a successful connection to the service:

* **Data Source Name**: Specify a unique and easily recognizable name for your MaxCompute data source.
* **MaxCompute Service Address**: Provide the Endpoint connection address of the MaxCompute service, which is the main entry point for accessing the MaxCompute service, for example: `<http://service.ap-southeast-1.maxcompute.aliyun.com/api>`.
* **MaxCompute Tunnel Service Address** (optional): If you use the Tunnel service to enhance data transmission security, you need to provide the Tunnel service address. For example: `http://dt.<region-name>.maxcompute.aliyun.com/api`, where `<region-name>` is the region name of your MaxCompute service.
* **Project Space Name**: Fill in the project space name associated with your MaxCompute account, which is the context environment for operating and managing data.
* **Access Key ID**: Provide the Access Key ID of your Alibaba Cloud account for authentication.
* **Secret Access Key**: Provide the secret access key corresponding to the Access Key ID.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you entered is accessible on the public network. If the source end has enabled an IP access whitelist, make sure that the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support personnel.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to MaxCompute via an SSH tunnel. Enable this option and provide the IP address and port of the SSH service. Ensure that your SSH client is correctly configured and that you have permission to connect to the MaxCompute server via SSH.

## Notes

* Ensure that all provided connection information is accurate and that the MaxCompute service is accessible.
* Protect your credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the project space or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

After completing the configuration, you can select this MaxCompute data source in data synchronization tasks to perform data import or export operations. Connecting via SSH tunnel or MaxCompute Tunnel service can enhance data transmission security, especially when handling sensitive data.
