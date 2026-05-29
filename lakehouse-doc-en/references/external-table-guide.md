# **Introduction to External Tables**

**Function Overview**: External tables are a feature of Lakehouse that allows you to query data stored in external systems as if the data were stored inside the Lakehouse. This external data is not stored or managed within the Lakehouse.

**Performance Tip**: Since the data in external tables is stored outside the Lakehouse, querying external tables may be slightly slower than querying tables stored locally. To improve query efficiency, it is recommended to use the `INSERT INTO internal_table_name SELECT * FROM external_table_name` statement or the `COPY INTO` command to import data into the Lakehouse.

## Supported External Table Data Sources

* kafka external table
* delta lake external table
* hudi external table

## **Differences Between External Tables and External Schema**

* **External Schema**: Directly interacts with the Hive Metastore Service (HMS) and directly obtains Hive metadata information through the HMS interface.
* **External Tables**: Allow users to create tables by specifying column contents and table names.
* **External Schema Limitations**: Since it directly maps to HMS, it is not possible to directly create, delete, or rename tables under an External Schema.
* **Advantages of External Tables**: Support operations such as renaming and modifying comments because they are created under an internal schema.

## Specific Cases

### Connecting to Alibaba Cloud Oss

```SQL
--Create connection for connecting to object storage
CREATE STORAGE CONNECTION  oss_delta
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com'
    access_id = 'xxxxxx'
    access_key = 'xxxxxx'
    comments = 'delta'
    ;
--Use the above connection information to create an external table
CREATE    EXTERNAL TABLE pepole_delta (id int, name string,dt string) 
USING DELTA 
CONNECTION oss_delta 
PARTITIONED BY (dt ) 
LOCATION 'oss://bucketmy/delta-format/uploaddelta/' 
COMMENT 'edelta-external';
```

### Connect to Google Gcs

When Lakehouse connects to Google Cloud Storage (GCS), it uses a service account key for authentication. Please follow the steps below:

1. **Obtain the service account key**:

   1. Log in to the Google Cloud Console.
   2. Follow the instructions in the [Google Cloud documentation](https://cloud.google.com/docs/authentication/getting-started) to create and download the JSON key file for the service account.

2. **Configure the** \`\` **parameter**:

   1. Open the downloaded JSON key file and copy the entire content of the private key.

3. **Note**:

   1. When configuring the `private_key`, add an 'r' to private\_key to indicate that escape characters will not be escaped.

```SQL
-- Create connection for connecting to object storage
CREATE STORAGE CONNECTION  oss_delta
    TYPE gcs
    private_key=r'{
  "type": "service_account",
  "project_id": "PROJECT_ID",
  "private_key_id": "KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nPRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "SERVICE_ACCOUNT_EMAIL",
  "client_id": "CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/SERVICE_ACCOUNT_EMAIL"
}';
-- Use the above connection information to create an external table
CREATE    EXTERNAL TABLE pepole_delta (id int, name string,dt string) 
USING DELTA 
CONNECTION oss_delta 
PARTITIONED BY (dt ) 
LOCATION 'gs://bucketmy/delta-format/uploaddelta/' 
COMMENT 'edelta-external';
```

## **External Table Billing**

* **Storage Fees**: External tables do not incur storage fees because the data is not stored in the Lakehouse.
* **Compute Fees**: Using external tables for computation will consume compute resources, thus incurring compute fees.

## **External Table Permissions**

External tables have the same permission points as internal tables. Operations such as insert\update\truncate\delete\undrop cannot be performed externally, so there are no corresponding operations.

* **Create Permission**: Requires permission to create tables.
* **Delete Permission**: Requires permission to drop tables.
* **Read Permission**: Requires permission to select.

## **Usage Notes**

* **Connection Configuration**: When creating a connection, ensure the endpoint is configured correctly so that the Lakehouse can connect successfully. If the Lakehouse and the object storage are in the same cloud service and in the same region, usually using the internal network address can achieve network connectivity. If they are not in the same network environment, it is recommended to use the public address of the object storage.

^
