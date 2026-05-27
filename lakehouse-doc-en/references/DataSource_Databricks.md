# Databricks Data Source Configuration Guide

## Overview

Databricks is a popular cloud data platform that offers various data services, including Delta Lake. Configuring a Databricks data source can help you integrate Databricks with your data system, enabling efficient data management and analysis.

## Parameter Configuration

When configuring a Databricks data source, you need to provide the following information to ensure a successful connection:

1. Workspace URL: This is the unique URL of the Databricks workspace, usually in the format `https://<workspace-id>.cloud.databricks.com`. You can determine the workspace URL by logging into the Databricks workspace and checking the URL in the browser's address bar.

2. Workspace ID: The workspace ID is the unique identifier of the Databricks workspace, usually reflected in the workspace URL as a string of numbers. For example, if the URL is `https://<databricks-instance>/?o=6280049833385130`, then the workspace ID is `6280049833385130`.

3. Authentication Method: Databricks supports various authentication methods, including token-based authentication. You need to configure the authentication parameters according to the actual situation, such as using a Personal Access Token (PAT) for authentication. Choose the appropriate authentication method and configure the corresponding authentication information.

4. Sql Warehouse: Please configure the Databricks Sql Warehouse required to run Databricks SQL workloads.

5. Advanced Configuration: Provide advanced parameters for the data source in a Key-Value manner. This parameter is reserved and usually can be ignored. If needed, please contact our technical support for details on how to use it.

## Connection Configuration

When configuring the connection, you need to pay attention to the following:

* Ensure that the workspace URL and workspace ID are correct and that the Databricks service is accessible.
* Configure the corresponding authentication information according to Databricks documentation to ensure a secure connection.

## Notes

* Protect your Databricks credential information to avoid leakage to unauthorized personnel.
* Regularly check and update your data source configuration to adapt to changes in the workspace structure or new security requirements.
* Monitor the running status of data synchronization tasks to promptly identify and resolve any potential issues.

## Completing the Configuration

After completing the configuration, you can select this Databricks data source in data synchronization tasks to perform data import or export operations. Ensure to follow Databricks best practices and security policies to protect your data.

Please refer to the official Databricks documentation and support resources for the most accurate guidance when configuring the Databricks data source.