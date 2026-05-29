# Data Source Management

DataGPT will by default add the Alibaba Cloud Lakehouse instance in the same region as a built-in data source, without the need for manual addition. If you want to add a Lakehouse data source from another region, please refer to the following operations.

## Function Overview

This function is used to add and configure LakeHouse data source connections, supporting users to connect LakeHouse databases to the system for data analysis.

## Operation Entry

* Location: Product homepage, left navigation bar: Management -> Data Source

## Configuration Item Description

### Basic Information

| Field Name                        | Required | Description                                                 |
| --------------------------------- | -------- | ----------------------------------------------------------- |
| Data Source Name                  | Yes      | The unique name used to identify the data source            |
| Connection String                 | Yes      | The connection address of the LakeHouse database            |
| Username                          | Yes      | The user account for accessing the database, example: admin |
| Password                          | Yes      | The password for accessing the database                     |
| Analytical Computing Cluster Name | No       | Specify the computing cluster used for data analysis        |

## Operation Instructions

1. Enter the data source name
2. Fill in the database connection string

![](.topwrite/assets/20250219-114848.jpeg =691)

![](.topwrite/assets/20250219-114853.jpeg =677)

1. Enter the username and password
2. Fill in the analytical computing cluster name
3. Click the "Connection Test" button to verify if the configuration is correct
4. After passing the test, click the "Save" button to complete the addition

## Precautions

1. The data source name must be unique in the system
2. It is recommended to perform a connection test before saving
3. Please ensure that the username provided has sufficient database access permissions
4. It is recommended to use a strong password to ensure security

## Error Handling

|                        |                                       |                                                     |
| ---------------------- | ------------------------------------- | --------------------------------------------------- |
| Error Type             | Possible Cause                        | Solution                                            |
| Connection Test Failed | Connection string format error        | Check if the connection string format is correct    |
|                        | Username or password error            | Confirm the correctness of the account and password |
|                        | Network issue                         | Check if the network connection is normal           |
| Save Failed            | Duplicate data source name            | Use an unused name                                  |
|                        | Required information not fully filled | Check if all required fields are filled             |

^
