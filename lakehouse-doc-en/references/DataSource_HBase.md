# HBase Data Source Configuration Guide

## Overview

HBase is a distributed, column-oriented open-source NoSQL database that provides random, real-time read/write access to large-scale datasets. Configuring an HBase data source allows you to efficiently utilize HBase for storing and retrieving data in data integration tasks.

## Parameter Configuration

When configuring an HBase data source, you need to provide the following information to ensure a successful connection to the HBase cluster:

* **Data Source Name**: Specify a unique and easily recognizable name for your HBase data source, such as `HBaseSource01`.
* **ZK Connection Address**: Provide the Zookeeper connection address in the format `host1:port,host2:port,host3:port`. For example, `192.168.0.177:2181,192.168.0.179:2181,192.168.0.178:2181`.
* **ZK Parent**: Specify the parent path of Zookeeper, usually `/hbase`.
* **RootDir**: Specify the root directory of HBase, such as `/hbase-data`.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you need to pay attention to the following:

* **Direct Connection**: Ensure that the connection information you enter is accessible on the public network. If the source end has enabled an IP access whitelist, make sure that the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support personnel.

## Notes

* Ensure that all provided connection information is accurate and that the HBase service is accessible.
* Regularly check and update your data source configuration to adapt to changes in the cluster structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

Once the configuration is complete, you can select this HBase data source in data synchronization tasks to perform data import or export operations. Using an SSH tunnel connection can enhance the security of data transmission, especially when handling sensitive data.