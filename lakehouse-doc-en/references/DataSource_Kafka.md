# Apache Kafka Data Source Configuration Guide

## Overview

Apache Kafka is a high-throughput, scalable distributed event streaming platform, ideal for building real-time data pipelines and stream processing applications. By configuring a Kafka data source, you can achieve efficient data streaming with other systems.

## Parameter Configuration

When configuring a Kafka data source, you need to provide the following information to ensure a successful connection to the Kafka cluster:

* **Data Source Name**: Specify a unique and easily recognizable name for your Kafka data source, such as `OrderStreamKafka`.
* **Kafka Connection Configuration**: Fill in the service addresses of the Kafka cluster in the format `host1:port,host2:port,host3:port`. For example, `order-kafka-broker-01:9092,order-kafka-broker-02:9092`.
* **Kafka Security Authentication Protocol**: Choose the appropriate security authentication protocol, such as No Authentication, SASL_PLAINTEXT, SASL_SSL/SCRAM.
* **JAAS Configuration**: If using SASL_SSL authentication, provide the Java Authentication and Authorization Service (JAAS) configuration string, for example, `org.apache.kafka.common.security.plain.PlainLoginModule required username="orderuser" password="orderpass";`.
* **Truststore (CA Certificate) File**: If using SASL_SSL authentication, specify the path to the truststore file, for example, `kafka.client.truststore.jks`.
* **Truststore Password**: Provide the access password for the truststore.
* **Keystore (Private Key) File**: If client authentication is required, specify the path to the keystore file, for example, `kafka.client.keystore.jks`.
* **Keystore Password**: Provide the access password for the keystore.

## Connection Configuration

Regarding connection configuration, you need to pay attention to the following:

* **Direct Connection**: Ensure that the connection information you enter is accessible on the public network. If the source end has enabled an IP access whitelist, ensure that the egress IP address of the data integration service has been added to the whitelist. For specific IP addresses, please contact technical support.

## Notes

* Ensure the security and stability of the Kafka cluster, and configure authentication and authorization mechanisms appropriately.
* In a production environment, it is recommended to use encrypted connections (such as SASL_SSL) to protect data transmission security.
* Monitor the running status of the Kafka cluster to promptly identify and resolve potential issues.

After completing the configuration, you can select this Kafka data source in data synchronization tasks to perform data import or export operations.