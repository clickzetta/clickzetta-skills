# AWS DocumentDB Data Source Configuration Guide

## Overview

AWS DocumentDB (with MongoDB compatibility) is a fully managed document database service provided by Amazon Web Services that offers a MongoDB-compatible database engine in the cloud. By configuring an AWS DocumentDB data source, you can easily achieve data synchronization and integration with other systems while enjoying the high availability, scalability, and security of a cloud-native database.

## Parameter Configuration

When configuring an AWS DocumentDB data source, you need to provide the following information to ensure a successful connection to the database:

### Basic Configuration

* **Data Source Name** (Required): Specify a unique and easily identifiable name for your AWS DocumentDB data source. It is recommended to use meaningful naming conventions, such as "Behavioral Data Source", to facilitate subsequent management and maintenance.
* **URL Address** (Required): Provide the connection endpoint address of your AWS DocumentDB cluster in the format `hostname:port`. For example: `docdb-example.cluster-abc123.us-east-1.docdb.amazonaws.com:27017`. This address can be obtained from the DocumentDB cluster details page in the AWS Console.

### Authentication Information

* **Username** (Required): Provide the master username or a database user with appropriate permissions for connecting to AWS DocumentDB. The default master username is typically `admin`, though you can also use custom-created users.
* **Password** (Required): Provide the database password corresponding to the username. Please ensure password security and avoid using weak passwords. The system will encrypt and store the password.

### Security Configuration

* **CA Certificate** (Optional): AWS DocumentDB enables TLS encrypted connections by default to ensure secure data transmission. If TLS is enabled on your cluster, you need to upload the CA certificate file (rds-combined-ca-bundle.pem) provided by AWS. Click the "Upload File" button to select the local CA certificate file.

### Connection Method

* **Connect via SSH Tunnel** (Optional): To enhance security, especially when the DocumentDB cluster is located in a private VPC, you can choose to connect through an SSH tunnel. When this option is enabled, data will be transmitted to DocumentDB through a secure SSH channel. You need to provide information about a bastion host that has public network access and can reach the DocumentDB cluster:

  * SSH server IP address
  * SSH port (default 22)
  * SSH username and key or password

### Additional Configuration

* **Data Source Description** (Optional): Add descriptive information for the data source, such as "Production Environment User Behavior Database", to help you or other administrators understand the purpose, environment, or business scenario of this data source.

### Authorize Workspace Access

* **Specific Workspace**: Authorize only specific workspaces to use this data source, suitable for scenarios requiring strict permission control.
* **All Workspaces** (Recommended): Allow all workspaces to use this data source, facilitating cross-team collaboration and data sharing.

## Connection Configuration Instructions

### Network Access Configuration

Depending on your AWS DocumentDB deployment architecture, you can choose from the following connection methods:

#### 1. Public Network Direct Connection (Requires VPC and Security Group Configuration)

If your DocumentDB cluster is configured for public network access (via VPN or Direct Connect), ensure that:

* The security group inbound rules of the DocumentDB cluster allow the data integration platform's egress IP addresses to access port 27017
* VPC network ACL rules allow the corresponding traffic to pass through
* For the specific list of platform egress IP addresses, please contact technical support personnel

#### 2. Connect via SSH Tunnel (Recommended)

For DocumentDB clusters located in a private VPC, using SSH tunnel connection is strongly recommended:

* Deploy an EC2 instance as a bastion host in the same VPC as the DocumentDB cluster
* This EC2 instance must have a public IP or Elastic IP
* Ensure the security group of the EC2 instance allows SSH connections (port 22) from the data integration platform
* The security group of the DocumentDB cluster must allow access from the EC2 instance (port 27017)
* This approach prevents direct exposure of DocumentDB to the public network, enhancing security

## Connection Testing

After completing all configurations, click the "Test Connection" button at the bottom of the page to verify the connection configuration:

* The system will attempt to connect to the AWS DocumentDB cluster using the provided parameters
* Verify network reachability, authentication information, and permission settings
* After a successful test, you can save the data source configuration and use it in data synchronization tasks

## Important Considerations

### Security Recommendations

* **TLS Encryption**: AWS DocumentDB enables TLS by default. It is strongly recommended to keep it enabled and upload the correct CA certificate to ensure encrypted data transmission.
* **Principle of Least Privilege**: Create dedicated database users for data synchronization with only the necessary read/write permissions; avoid using the master account.
* **Password Management**: Regularly rotate database passwords and avoid reusing the same password across multiple systems.
* **Network Isolation**: Prioritize SSH tunnels or VPC private connections to avoid exposing the database directly to the public network.

### Performance Optimization

* **Connection Pool Configuration**: The system automatically manages connection pools to ensure efficient connection reuse.
* **Network Latency**: Choose data integration services in the same region as the DocumentDB cluster to reduce network latency.
* **Read Performance**: For large-scale data synchronization, consider reading data from replica instances to reduce pressure on the primary instance.

### Operations Recommendations

* **Monitor Synchronization Status**: Regularly check the running status and logs of data synchronization tasks to promptly identify and resolve potential issues.
* **Backup Strategy**: Ensure that automatic backups are configured for the DocumentDB cluster to avoid data loss risks.
* **Version Compatibility**: Note the compatibility between AWS DocumentDB versions and the MongoDB protocol; some advanced features may have differences.
* **Quota Limits**: Understand AWS DocumentDB's quotas for connections, storage capacity, etc., to avoid service interruptions due to exceeding limits.

### Troubleshooting

If the connection test fails, please check the following common issues:

1. **Network Connectivity**: Use the `telnet` or `nc` command to test network connectivity from the data integration platform to DocumentDB
2. **Security Group Configuration**: Verify that security group rules for DocumentDB and EC2 (if using SSH tunnel) are correctly configured
3. **Authentication Information**: Verify that the username and password are correct and that the user has permissions to access the target database
4. **CA Certificate**: If TLS is enabled, ensure the uploaded CA certificate file is valid and not expired
5. **SSH Configuration**: If using SSH tunnel, verify that the bastion host's SSH service is functioning properly and that the key or password is correct

## Complete Configuration

After completing all parameter configurations and passing the connection test, you can:

* Select this AWS DocumentDB data source in data synchronization tasks
* Configure specific collections and field mappings
* Set scheduling strategies and incremental update rules for data synchronization
* Execute data import or export operations