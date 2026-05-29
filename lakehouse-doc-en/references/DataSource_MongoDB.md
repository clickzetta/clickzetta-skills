# MongoDB Data Source Configuration Guide

## Overview

MongoDB is a high-performance, highly available NoSQL database that offers rich data models and flexible query languages. By configuring a MongoDB data source, you can achieve data synchronization and integration with other systems.

## Parameter Configuration

When configuring a MongoDB data source, you need to provide the following information to ensure a successful connection to the database:

* **Data Source Name**: Specify a unique and easily recognizable name for your MongoDB data source.
* **MongoDB Instance Type**: Choose your MongoDB instance type, which can be a single node, replica set, or sharded cluster.
* **Service Address**: Provide the address of the MongoDB database node in the format `host:port`.
* **Database Name**: Specify the name of the database to be synchronized.
* **Replica Set Name** (if applicable): If it is a replica set instance, provide the name of the replica set.
* **Read Preference** (if applicable): In a replica set instance, choose the read preference, such as `primary` or `secondary`.
* **Username**: If authentication is required, provide the username used to connect to MongoDB.
* **Password**: Provide the database password corresponding to the username.
* **Authentication Database Name**: (optional) The name of the database used when creating the user, usually `admin`.
* **Data Source Description**: (optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Connection Configuration

In terms of connection configuration, you can choose one of the following connection methods:

* **Direct Connection**: Ensure that the connection information you enter is accessible on the public network. If the source has an IP access whitelist enabled, make sure the outbound IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.
* **Via SSH Tunnel**: To enhance security, you can choose to connect to MongoDB via an SSH tunnel. Enable this option and provide the IP address and port of the SSH service. Ensure that your SSH client is properly configured and that you have permission to connect to the MongoDB server via SSH.

## Notes

* Ensure that all provided connection information is accurate and that the MongoDB service is accessible.
* Protect your database credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the database structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

After completing the configuration, you can select this MongoDB data source in data synchronization tasks to perform data import or export operations. Connecting via an SSH tunnel can enhance the security of data transmission, especially when handling sensitive data.