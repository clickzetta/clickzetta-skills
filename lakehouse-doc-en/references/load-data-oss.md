# Batch import data from Object Storage（OSS）

This document details how to use the Lakehouse SQL engine to import data from object storage. Currently, Lakehouse supports two main data import modes:

1. **Import using Volume**: Import data by creating and managing Volumes on object storage.
2. **Import using Copy command**: Load data directly from object storage using the SQL COPY command.

## Reference Documentation

[Data Lake Query](structure_data_analysis.md)

[COPY INTO](copy-into-table.md)

## Application Scenarios

* Quickly read large amounts of data using the performance advantages of the SQL engine, efficiently handling large-scale datasets.
* Support data transformation using SQL during the data import process, achieving ETL (Extract, Transform, Load) processes.
* It is recommended to choose a General Purpose Virtual Cluster when importing data to meet the needs of batch jobs and data loading jobs.

## Usage Restrictions

* **Object Storage Support**: Currently, the target object storage for Volume only supports Alibaba Cloud OSS and Tencent Cloud COS.
* **Cost Description**: Downloading files from external Volume may incur object storage download fees on the cloud account. Please refer to the billing description of the respective cloud service provider for specific fees. If Lakehouse and object storage are located in the same region, using the internal network ENDPOINT can avoid additional costs.
* **Cross-Cloud Import**: Currently, cross-cloud service provider data import is not supported (it will be supported in future versions).

## Use Cases

### Import CSV Data from OSS using Volume

This document details how to use Lakehouse's Volume and COPY command to import the public dataset of [Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_customers_dataset.csv) from Alibaba Cloud Object Storage Service (OSS). Alternatively, you can directly download the dataset for this case through [this link](https://czsampledata.oss-cn-shanghai.aliyuncs.com/eCommerce/BrazilianECommerce/olist_customers_dataset.csv?Expires=1713960305\&OSSAccessKeyId=TMP.3Kj9FumEnKg87NyAXLcgdBykW427fGRqHzTyiLfNtki6Vagmg1zMHEfVcqov1PXETvKM7DKauBXyah4YNWhfdgHNufoq2j\&Signature=afXWkoRTi%2BercYhvlsPKdrpv0Fg%3D\&x-oss-request-payer=requester) and then upload it to OSS. This process includes table creation, object storage connection configuration, Volume management, and data loading and status checking.

#### Prerequisites

* Ensure the target table `brazilian_customer` has been created:

```SQL
create table brazilian_customer( 
  customer_id STRING,
  customer_unique_id STRING,
  customer_zip_code_prefix INT,
  customer_city STRING,
  customer_state STRING
  );
```

* Have INSERT permission on the target table.

#### Create CONNECTION and VOLUME for connecting object storage

* Create a STORAGE CONNECTION to store and desensitize the connection information of object storage, which is convenient for reuse and management in Lakehouse.
* Create an EXTERNAL VOLUME to manage the data on OSS.

```SQL
-- Store the connection information of the object storage. In Lakehouse, the access key (ak) will be desensitized. At the same time, the connection can be conveniently reused in multiple places.
-- The endpoint uses the internal network of OSS because both Lakehouse and OSS are in Shanghai, so the internal network can be directly connected.
CREATE STORAGE CONNECTION  braziliandata_conn
    TYPE oss
    ENDPOINT = 'oss-cn-shanghai-internal.aliyuncs.com'
    access_id = 'xxxx'
    access_key = 'xxxx'
    comments = 'OSS public endpoint';
 -- View the created connection
 SHOW CONNECTIONS;
-- Create Volume to manage the data on the object storage
CREATE EXTERNAL VOLUME braziliandata_csv
    location 'oss://yourbucketname/eCommerce/BrazilianECommerce/'
    using connection braziliandata_conn
    directory = (
        enable=true,
        auto_refresh=true
    );
  SHOW VOLUMES;
```

#### **Using Volume to Load Data**

* Specify the files that need to be read from the Volume in the `files` parameter.
* You can set parameters for the CSV file in `options`, such as the delimiter, etc. Refer to the documentation for specific settings.
* In this case, the data will be transformed during loading, excluding records where the city is 'curitiba'.

```SQL
-- Exclude the city 'curitiba' when loading data
insert into brazilian_customer
select * from volume braziliandata_csv (
  customer_id STRING,
  customer_unique_id STRING,
  customer_zip_code_prefix INT,
  customer_city STRING,
  customer_state STRING
)using csv 
 options(
    'header'='true',
    'sep'=','
 ) files('olist_customers_dataset.csv') 
 where customer_city !='curitiba';
```

#### View Import Data Status

Check the job execution status in the job run history of Lakehouse to confirm whether the data import was successful.

![](.topwrite/assets/image_1739882452329.png =777)

### Import Data from OSS Using COPY Command

This article introduces how to use Lakehouse's COPY command to import a public dataset of [Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_customers_dataset.csv) from Alibaba Cloud Object Storage Service (OSS), or you can directly download the dataset for this case through [this link](https://czsampledata.oss-cn-shanghai.aliyuncs.com/eCommerce/BrazilianECommerce/olist_geolocation_dataset.csv?Expires=1713960430\&OSSAccessKeyId=TMP.3Kj9FumEnKg87NyAXLcgdBykW427fGRqHzTyiLfNtki6Vagmg1zMHEfVcqov1PXETvKM7DKauBXyah4YNWhfdgHNufoq2j\&Signature=2bCPx2sokSkMGpwfkipZqfmoWlE%3D\&x-oss-request-payer=requester) and then upload it to OSS. This process involves creating the data table, connecting and configuring the Volume, as well as loading the data and checking the status.

#### Prerequisites

* Ensure that the target table `brazilian_geolocation` has been created:

```SQL
create table brazilian_geolocation( 
  geolocation_zip_code_prefix INT,
  geolocation_lat DECIMAL(10,8),
  geolocation_lng DECIMAL(11,8),
  geolocation_city STRING,
  geolocation_state STRING
  );
```

* Have INSERT permission on the target table.

#### Create CONNECTION and VOLUME for connecting object storage

* Create a STORAGE CONNECTION to store and desensitize the connection information of the object storage, so that it can be reused and managed multiple times in the Lakehouse.

* Create an EXTERNAL VOLUME to manage the data on OSS.

* ```SQL
    --Store the connection information of the object storage. In Lakehouse, the access key (ak) will be desensitized. At the same time, the connection can be conveniently reused and managed in multiple places.
    --The endpoint uses the internal network of OSS because both it and Lakehouse are in Shanghai, so the internal network can be directly connected.
    CREATE STORAGE CONNECTION  braziliandata_conn
        TYPE oss
        ENDPOINT = 'oss-cn-shanghai-internal.aliyuncs.com'
        access_id = 'xxxx'
        access_key = 'xxxx'
        comments = 'OSS public endpoint';
     --View the created connection
     SHOW CONNECTIONS;
    --Create Volume to manage the data on the object storage
    CREATE EXTERNAL VOLUME braziliandata_csv
        location 'oss://czsampledata/eCommerce/BrazilianECommerce/'
        using connection braziliandata_conn
        directory = (
            enable=true,
            auto_refresh=true
        );
      SHOW VOLUMES;
  ```

#### Using the COPY Command to Load Data into a Table

Use the COPY command to load data from an OSS Volume into the `brazilian_customer` table.

```SQL
COPY  INTO brazilian_customer FROM VOLUME  
braziliandata_csv (
  customer_id STRING,
  customer_unique_id STRING,
  customer_zip_code_prefix INT,
  customer_city STRING,
  customer_state STRING
)using csv 
 options(
    'header'='true',
    'sep'=','
 ) files('olist_geolocation_dataset.csv') ;
```

#### View Import Data Status

Check the job execution status in the job run history of Lakehouse to confirm whether the data import was successful.

![](.topwrite/assets/image_1739954649263.png)
