# RestAPI Data Source Configuration Guide

## Overview

RestAPI is a widely used network architecture style that allows clients to interact with servers via the HTTP protocol. Configuring a RestAPI data source allows users to import or export data from Restful services, achieving data synchronization and integration.

## Parameter Configuration

1. **Data Source Name**: Specify a clear and unique name for the RestAPI data source for identification and management.
2. **URL Address**: Enter the base URL of the Restful service, which is the root address of the API service and will be used for all data synchronization operations.
3. **Request Method**: Select the HTTP request method used in the data synchronization task, which can be `GET` or `POST`.
4. **Default Request Headers** (optional): Add any necessary HTTP request header information, organized in Key-Value format, such as `Content-Type`, with a default value of `application/json`.
5. **Authentication Method**: Choose the authentication method required by the Restful service to ensure the security of data transmission.
   * **No Authentication**: Select this option if the API service does not require authentication.
   * **Basic Authentication** (BasicAuth): Select this option if the API service supports username and password authentication, and configure the corresponding username and password.
   * **Bearer Token Authentication**: Select this option if the API service accepts Bearer Token authentication, and provide a valid Token name and value.
6. **Data Source Description** (optional): Provide descriptive information about the data source to help understand its purpose and characteristics.

## Connection Test

* **Test Connectivity**: Before saving the configuration, you can click the "Test Connectivity" button to verify the correctness and accessibility of the API service address. This step only checks the reachability of the URL address and does not perform authentication verification.

## Notes

* Ensure that all provided connection information is accurate and that the Restful service is accessible.
* Configure request headers and authentication methods according to the requirements of the Restful service to ensure the security and effectiveness of data transmission.
* Protect your authentication information to avoid leakage to unauthorized personnel.
* Comply with the API usage terms of the Restful service, use the request frequency reasonably, and avoid abuse.

After completing the above configuration, you can select this RestAPI data source for data synchronization task development. When configuring the RestAPI data source, refer to the relevant Restful service's API documentation and support resources for the most accurate guidance. Correctly configuring the authentication method is crucial for protecting data security and ensuring the smooth progress of data synchronization.