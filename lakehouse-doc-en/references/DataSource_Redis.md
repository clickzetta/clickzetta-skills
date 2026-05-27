# Redis Data Source Configuration Guide

## Overview

Redis is an open-source, in-memory key-value data storage system that supports multiple data structures such as strings, hashes, lists, sets, and sorted sets. It is widely used in caching, message queuing, and real-time analytics scenarios due to its high performance, low latency, and rich feature set. Configuring a Redis data source enables you to achieve efficient data reading and writing operations in data synchronization tasks.

## Parameter Configuration

When configuring a Redis data source, you need to provide the following information to ensure successful connection to the Redis service:

* **Data Source Name**: Specify a unique and easily identifiable name for your Redis data source, for example, `BehavioralDataSource`.

* **Authentication User**: Provide the username for connecting to the Redis service. If the Redis service has not enabled ACL (Access Control List) authentication or uses the default user, you can leave this field blank.

* **Access Password**: Provide the connection password for the Redis service. If the Redis service is configured with password authentication (requirepass), please fill in the corresponding password. If no password is set, you can leave this field blank.

* **Node Mode**: Select the deployment architecture mode for Redis. Currently supported:

  * **Standalone**: Single-instance mode, suitable for single Redis instance scenarios
  * **Cluster**: Cluster mode, suitable for Redis Cluster distributed clusters

* **Node Information**: Provide the connection address information for the Redis service, including:

  * **IP**: The IP address of the Redis server, for example, `10.10.10.1`
  * **Port**: The port number of the Redis service, default is `6379`, the example uses `3306`
  * Multiple node addresses can be configured via the "Add Node" button, suitable for cluster or master-slave architecture scenarios

* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of this data source, such as "Production environment user behavior cache" or "Real-time session data storage".

* **Authorize for Workspace Use**: Select the usage permission scope for this data source:

  * **Specified Workspace**: Only authorized for use by specific workspaces
  * **All Workspaces**: Authorized for use by all workspaces

## Connection Configuration

Regarding connection configuration, you need to pay attention to the following matters:

* **Direct Connection**: Ensure that the connection information you enter is network-accessible. If the Redis service has IP access whitelist or firewall rules enabled, please ensure that the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support personnel.
* **Test Connectivity**: After completing the configuration, it is recommended to click the "Test Connectivity" button to verify the correctness of the connection configuration and ensure that the system can successfully connect to the Redis service.
* **Network Connectivity Testing**: Before formal configuration, it is recommended to test network connectivity using `redis-cli` or telnet tool to confirm whether the port is open and the password is correct.

## Notes

* **Ensure all provided connection information is accurate**, and that the Redis service is accessible. Pay special attention to the correctness of IP addresses and port numbers.
* **Data Type Support**: Redis supports multiple data structures (String, Hash, List, Set, Sorted Set, etc.). During data synchronization, it is necessary to clarify the data type mapping relationship between the source and target.
* **Performance Considerations**: Redis is an in-memory data storage system. Large-scale data reading may affect Redis service performance. It is recommended to execute data synchronization tasks during off-peak business hours or use slave nodes for data reading.
* **Protect your credential information** to avoid leakage to unauthorized personnel. It is recommended to regularly change passwords and follow strong password policies.
* **Version Compatibility**: Confirm the compatibility between the Redis service version and the data integration platform. Redis 3.0 and above is recommended for better stability and feature support.
* **Multi-node Configuration**: When configuring multiple nodes, the system will automatically handle connection logic according to the node mode. Please ensure all node information is accurate to avoid data synchronization anomalies.
* **Regularly check and update your data source configuration** to adapt to architectural changes or new security requirements.
* **Monitor the running status of data synchronization tasks** to promptly discover and resolve potential issues.
* **Key Naming Convention**: It is recommended to clarify the naming pattern of Redis keys (such as prefix, separator, etc.) in data synchronization tasks to accurately identify and synchronize target data.

After completing the configuration, you can select this Redis data source in data synchronization tasks to perform data import or export operations. Through direct connection and proper configuration, you can fully leverage Redis's high-performance characteristics to achieve fast data transmission and processing.
