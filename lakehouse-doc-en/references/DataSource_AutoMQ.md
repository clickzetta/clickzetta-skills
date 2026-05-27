# AutoMQ Data Source Configuration Guide

## Overview

AutoMQ is a next-generation cloud-native streaming data platform that is 100% compatible with the Apache Kafka protocol. Through innovative storage architecture design, AutoMQ separates data persistence to cloud storage (such as Amazon S3), achieving a 10x cost reduction and 100x elasticity improvement compared to traditional Kafka, while maintaining single-digit millisecond latency. AutoMQ is ideal for building real-time data pipelines, stream processing, and event-driven architectures.

## Parameter Configuration

When configuring an AutoMQ data source, you need to provide the following information to ensure successful connection to the AutoMQ cluster:

### Basic Configuration

* **Data Source Name**: Specify a unique and easily identifiable name for your AutoMQ data source. For example: `UserBehaviorAutoMQ`, `OrderStreamAutoMQ`. It is recommended to use naming conventions that clearly express the data purpose.

* **AutoMQ Connection Configuration**: Enter the Bootstrap Server address of the AutoMQ cluster in the format `host1:port,host2:port,host3:port`.

  * Example: `automq-broker-01.example.com:9092,automq-broker-02.example.com:9092`

### Security Authentication Configuration

* **AutoMQ Security Authentication Protocol**: Select the appropriate authentication method based on your cluster security policy. AutoMQ supports the following authentication protocols:

  * **No Authentication**: Suitable for development and testing environments or protected internal network environments
  * **SASL\_PLAINTEXT**: Uses SASL mechanism for username and password authentication, but data transmission is not encrypted
  * **SASL\_SSL**: Uses SASL authentication with SSL/TLS encrypted data transmission, recommended for production environments

### SASL Authentication Configuration (Required when SASL authentication is selected)

* **JAAS Configuration**: Provide the Java Authentication and Authorization Service (JAAS) configuration string. The configuration format for different authentication mechanisms is as follows:

  **PLAIN Mechanism Example**:

  ```
  org.apache.kafka.common.security.plain.PlainLoginModule required username="automq_user" password="your_password";
  ```

  **SCRAM-SHA-256 Mechanism Example**:

  ```
  org.apache.kafka.common.security.scram.ScramLoginModule required username="automq_user" password="your_password";
  ```

  **SCRAM-SHA-512 Mechanism Example**:

  ```
  org.apache.kafka.common.security.scram.ScramLoginModule required username="automq_user" password="your_password";
  ```

### SSL/TLS Certificate Configuration (Required when SSL encryption is selected)

* **Truststore (CA Certificate) File**: Upload the Truststore file to verify the identity of the AutoMQ server.

  * Supports JKS and PKCS12 formats

* **Truststore Password**: Provide the password to access the Truststore file to ensure certificate security.

* **Keystore (Private Key) File** (Optional): If the AutoMQ cluster has mutual TLS authentication (mTLS) enabled, you need to specify the client Keystore file path.

  * Example: `/security/automq.client.keystore.jks`

* **Keystore Password** (Optional): Provide the password to access the Keystore file.

### Advanced Configuration

* **Data Source Description** (Optional): Add detailed descriptions of the data source purpose and business scenarios to facilitate team member understanding and management. For example: "Production environment user behavior data stream for real-time recommendation systems".

## Connection Configuration Instructions

### Network Connectivity

When configuring AutoMQ connections, please note the following:

* **Public Network Access**: If the AutoMQ cluster is deployed in the cloud, ensure that the Bootstrap Server address you entered is accessible via the public network. If the cluster has an IP whitelist configured, add the egress IP address of the data integration service to the whitelist. Please contact technical support personnel for the specific IP address list.
* **VPC Internal Network Access**: If the data integration service and AutoMQ cluster are deployed in the same VPC or have VPC peering configured, it is recommended to use internal network addresses to reduce network latency and transmission costs.

### Workspace Authorization

* **Specify Workspace**: Authorize the data source for use by specific workspaces, suitable for scenarios requiring strict permission control.
* **All Workspaces**: Allow all workspaces to access this data source, facilitating cross-team collaboration and data sharing.

It is recommended to choose the appropriate authorization scope based on your data security policy and team collaboration needs.

## Connection Testing

After completing the configuration, click the "Test Connection" button to verify the correctness of the configuration:

* **Test Successful**: Indicates that the configuration parameters are correct and a successful connection to the AutoMQ cluster can be established. You can proceed to create the data source.

* **Test Failed**: Please check the following common issues:

  * Is the Bootstrap Server address format correct
  * Is network connectivity normal (firewall, security group rules)
  * Is the authentication information (username, password) accurate
  * Is the SSL certificate configuration complete and valid
  * Does the IP whitelist configuration include the egress IP of the data integration service

## Best Practices

### Security Recommendations

* **Production Environment Encryption**: It is strongly recommended to use the SASL\_SSL authentication protocol in production environments to ensure data transmission confidentiality and integrity.
* **Password Management**: Properly safeguard authentication passwords and certificate keys, and avoid recording them in plaintext in code or logs.
* **Principle of Least Privilege**: Create dedicated AutoMQ users for the data integration service and grant only the necessary Topic read and write permissions.
* **Regular Rotation**: It is recommended to regularly update authentication credentials and SSL certificates to reduce security risks.

### Operations and Monitoring Recommendations

* **Metrics Monitoring**: AutoMQ natively supports Prometheus and OpenTelemetry metrics export. It is recommended to integrate with your monitoring system for real-time monitoring.
* **Key Metrics**: Focus on core metrics such as producer-consumer latency, message backlog, and cluster throughput.
* **Alert Configuration**: Configure timely alert notifications for abnormal situations (such as consumption latency exceeding thresholds or high disk usage).

## Complete Configuration

After completing all parameter configurations and passing the connection test, click "Confirm" to save the data source. You can then select this AutoMQ data source in data synchronization tasks for real-time data collection, transmission, or distribution operations, fully leveraging AutoMQ's cloud-native advantages and cost-effectiveness.

## Related Resources

* **AutoMQ Official Website**: <https://www.automq.com/>
* **AutoMQ Open Source Code**: <https://github.com/AutoMQ/automq>
* **Technical Documentation**: Visit the AutoMQ official website for detailed technical documentation and best practice guides

***

^
