# AWS OpenSearch Data Source Configuration Guide

## Overview

AWS OpenSearch is a managed search and analytics engine service provided by Amazon Web Services, built on the open-source OpenSearch project. It enables real-time full-text search, log analysis, and complex data analytics. Configuring an AWS OpenSearch data source helps you efficiently operate and manage data stored in AWS OpenSearch for data synchronization and analysis tasks.

## Parameter Configuration

When configuring an AWS OpenSearch data source, you need to provide the following information to ensure successful connection to the AWS OpenSearch domain:

* **Data Source Name**: Specify a unique and easily identifiable name for your AWS OpenSearch data source, such as `Behavioral Data Source`.
* **Domain EndPoint**: Provide the access endpoint address of the AWS OpenSearch domain in the format `<domain-name>-<identifier>.<region>.es.amazonaws.com:443`. For example, `search-example-domain-abc123.us-east-1.es.amazonaws.com:443`.
* **Authentication Method**: Select `Access Key ID & Access Key Secret` as the authentication method.
* **Access Key ID**: Provide the Access Key ID of an AWS IAM user with OpenSearch access permissions.
* **Access Key Secret**: Provide the corresponding Access Key Secret credential.
* **Connect via SSH Tunnel**: (Optional) When the OpenSearch domain is located within a VPC and cannot be directly accessed, you can enable SSH Tunnel to establish a secure connection.
* **Data Source Description**: (Optional) Add descriptive information for the data source to help you or other administrators understand the purpose or characteristics of this data source.
* **Authorize for Workspace Usage**: Select the visibility scope of the data source, you can choose `Specified Workspace` or `All Workspaces`.

## Connection Configuration

Regarding connection configuration, you need to pay attention to the following matters:

* **Direct Connection**: Ensure that your AWS OpenSearch domain is configured with appropriate access policies. If the domain has IP address access control enabled, please ensure that the egress IP addresses of the data integration service have been added to the allow list. For specific IP addresses, please contact technical support personnel.
* **SSH Tunnel**: If the OpenSearch domain is deployed within a VPC, you can enable SSH Tunnel mode to establish a secure connection through a bastion host.

## Notes

* Ensure that all provided connection information is accurate and that the AWS OpenSearch domain is accessible.
* Protect your Access Key credentials to prevent disclosure to unauthorized personnel. The Access Key Secret will be stored encrypted.
* Ensure that the IAM user has the necessary permissions to access the OpenSearch domain. It is recommended to attach the `AmazonOpenSearchServiceFullAccess` policy or a custom policy.
* Regularly review and update your data source configuration to adapt to changes in domain structure or new security requirements.
* Monitor the operational status of data synchronization tasks to identify and resolve potential issues in a timely manner.
* Be aware of costs associated with AWS data transfer, especially in cross-region access scenarios.

After configuration is complete, you can select this AWS OpenSearch data source in data synchronization tasks to perform data import or export operations. Through appropriate connection methods, you can achieve rapid data transfer and improve data processing efficiency.

## Related Documentation

* [AWS OpenSearch Service Official Documentation](https://docs.aws.amazon.com/opensearch-service/)
* [AWS IAM User Management](https://docs.aws.amazon.com/IAM/latest/UserGuide/)
