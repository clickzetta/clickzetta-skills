# ElasticSearch Data Source Configuration Guide

## Overview

ElasticSearch is a distributed, RESTful search and data analysis engine that enables real-time full-text search and complex data analysis. Configuring an ElasticSearch data source can help you achieve efficient data operations in data synchronization and analysis tasks.

## Parameter Configuration

When configuring an ElasticSearch data source, you need to provide the following information to ensure a successful connection to the ElasticSearch cluster:

* **Data Source Name**: Specify a unique and easily recognizable name for your ElasticSearch data source, such as `ElasticSearchLogAnalytics`.
* **es address**: Provide the connection address of the ElasticSearch cluster in the format `http://host:port`. For example, `http://192.168.0.16:9200`.
* **es username** (optional): If the ElasticSearch cluster is configured with security authentication, provide the connection username for the ElasticSearch cluster.
* **es password** (optional): Provide the connection password for the corresponding username of the ElasticSearch cluster.
* **Data Source Description** (optional): Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you need to pay attention to the following matters:

* **Direct Connection**: Ensure that the connection information you entered is accessible on the public network. If the source end has enabled an IP access whitelist, ensure that the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support personnel.

## Notes

* Ensure that all provided connection information is accurate and that the ElasticSearch service is accessible.
* Protect your credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in cluster structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly discover and resolve any potential issues.

After the configuration is complete, you can select this ElasticSearch data source in data synchronization tasks to perform data import or export operations. Through direct connection, you can achieve fast data transmission and improve data processing efficiency.