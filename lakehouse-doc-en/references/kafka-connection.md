## Overview

> **[Public Preview]** This feature is currently in public preview phase.

This document describes how to create an external table connected to the Kafka messaging system in SQL. By defining an external table, you can easily read data streams from Kafka and query and analyze this data as a table.

## Create Storage Connection

First, you need to create a storage connection to connect to the Kafka server. Connections requiring client certificates are currently not supported.

### Syntax

```SQL
CREATE STORAGE CONNECTION connection_name
    TYPE kafka
    BOOTSTRAP_SERVERS = ['server1:port1', 'server2:port2', ...]
    SECURITY_PROTOCOL = 'PLAINTEXT';
```

### Parameter Description

* **connection_name**: The name of the connection, used for subsequent reference.
* **TYPE**: The connection type, which is `kafka` here.
* **BOOTSTRAP_SERVERS**: The address list of the Kafka cluster, in the format `['host1:port1', 'host2:port2', ...]`.
* **SECURITY_PROTOCOL**: The security protocol, which can be `PLAINTEXT` or others.

### Example

```SQL
CREATE STORAGE CONNECTION test_kafka_conn
    TYPE kafka
    BOOTSTRAP_SERVERS = ['47.99.48.62:9092']
    SECURITY_PROTOCOL = 'PLAINTEXT';
```

^
