## Feature Overview

> **[Preview Release]** This feature is currently in public preview.

This document describes how to create an external table in SQL connected to a Kafka message queue system. By defining an external table, you can conveniently read data streams from Kafka and query and analyze this data as a table.

## Creating a Storage Connection

First, you need to create a storage connection for connecting to the Kafka server. Connections requiring client certificates are not currently supported.

### Syntax

```SQL
CREATE STORAGE CONNECTION connection_name
    TYPE kafka
    BOOTSTRAP_SERVERS = ['server1:port1', 'server2:port2', ...]
    SECURITY_PROTOCOL = 'PLAINTEXT';
```

### Parameter Description

* **connection_name**: The name of the connection, used for subsequent referencing.
* **TYPE**: The connection type, which is `kafka` here.
* **BOOTSTRAP_SERVERS**: The list of Kafka cluster addresses, in the format `['host1:port1', 'host2:port2', ...]`.
* **SECURITY_PROTOCOL**: The security protocol, which can be `PLAINTEXT`, etc.

### Example

```SQL
CREATE STORAGE CONNECTION test_kafka_conn
    TYPE kafka
    BOOTSTRAP_SERVERS = ['47.99.48.62:9092']
    SECURITY_PROTOCOL = 'PLAINTEXT';
```

^
