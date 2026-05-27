# CONNECTION

In Lakehouse, the CONNECTION object plays a crucial role. It is responsible for storing authentication information and access management entities for third-party services, thereby protecting sensitive information during data processing. By using CONNECTION, users do not need to expose authentication information in plain text, ensuring data security. Additionally, CONNECTION supports STS (Security Token Service) authentication, allowing cross-account authorization to access services outside of Lakehouse, further enhancing the flexibility and security of data access.

## Types of CONNECTION

Based on its purpose and the type of external service it connects to, the CONNECTION object is mainly divided into the following three types:

1. **API Connection**: This type of CONNECTION is primarily used to store and protect authentication information for third-party application services. Through API Connection, Lakehouse can securely interact with these services via API calls. Currently, the external services supported by API Connection include Alibaba Cloud Function Compute (FC) and Tencent Cloud Function Service. API Connection is usually used in conjunction with External Function to remotely invoke these services within Lakehouse.
2. **Storage Connection**: Storage Connection is mainly used to store authentication information for third-party storage services, enabling Lakehouse to securely access and manage data in these storage services. The currently supported external storage services include Alibaba Cloud Object Storage Service (OSS), Tencent Cloud COS, and AWS S3.
3. **Catalog Connection**: In a data lake architecture, Catalog Connection is a key component used to associate the data lake with external metadata storage (such as Hive Metastore). By creating a Catalog Connection, users can achieve unified management and access to metadata, thereby directly reading data stored in external systems. Lakehouse currently only supports connecting to Hive.

## Creating and Managing CONNECTION

To use CONNECTION, users need to understand how to create, list, view details, and delete CONNECTION. The following are the basic syntax and usage examples for these operations:

* **Creating CONNECTION**: Users can define a new CONNECTION object through specific creation syntax, specifying the type, name, and related authentication information and parameters of the CONNECTION.
  For example, the syntax for creating an API Connection is as follows:
  ```sql
  CREATE API CONNECTION conn_aliyun_java 
    type cloud_function
    provider = 'xxx'
    region = 'xxx'
    role_arn = 'acs:ram::13843xxxxxxxxxxxxx:role/czudfrole'
    namespace = 'xxx'
    code_bucket = 'xxx';
  ```
The syntax for creating a Storage Connection is as follows:
  ```SQL
  CREATE STORAGE CONNECTION [IF NOT EXISTS] connection_name 
    TYPE COS
    REGION = 'xxx'
    APP_ID = 'xxx'
    ACCESS_KEY='******'
    SECRET_KEY='******';
  ```
The specific syntax and steps can be found in the [Create CONNECTION](CREATECONNECTION.md) document.

* **List all CONNECTIONS**: Users can use the list syntax to view all CONNECTION objects in the current Lakehouse workspace. For example, the command to view the current CONNECTIONS is as follows:
  ```sql
  SHOW CONNECTIONS;
  ```
This helps users manage and select existing CONNECTIONS for operations. Relevant commands and options can be found in the [List All CONNECTIONS](SHOWCONNECTIONS.md) document.

* **View CONNECTION Details**: To better understand and manage CONNECTIONS, users may need to view the details of a specific CONNECTION. This includes authentication information, configuration parameters, etc. For example, the syntax to view the details of an API Connection is as follows:
  ```sql
  DESCRIBE CONNECTION my_api_conn;
  ```
The syntax and methods for viewing details are explained in detail in the [View CONNECTION Details](DESCCONNECTION.md) document.

* **Delete CONNECTION**: When a CONNECTION is no longer needed, the user can remove it using the delete syntax. For example, the command to delete a CONNECTION is as follows:
  ```sql
  DROP CONNECTION my_api_conn;
  ```
This helps keep the workspace tidy and prevents unnecessary security risks. The specific deletion steps and precautions are described in the [Delete CONNECTION](DROPCONNECTION.md) document.

^