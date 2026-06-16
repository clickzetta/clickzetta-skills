# What is Volume:

Lakehouse Volume is an object in Singdata Lakehouse that represents the location of cloud object storage. It provides access, storage, management, and organization of files in cloud object storage (such as Alibaba Cloud OSS, Tencent Cloud COS), and can be used to store and access files of various formats, including structured, semi-structured, and unstructured data. It can be organized and managed under the Schema of Lakehouse like tables, views, and other objects. Using the Volume feature brings the following benefits:

* Unified data analysis: Supports calling AI workloads in Singdata Lakehouse to process images, PDFs, and special format unstructured data in object storage, and perform unified processing and analysis with structured data in the platform
* Unified permission management: Supports using the permission system of Singdata Lakehouse platform to perform unified permission management on libraries, tables, and files in object storage
* Unified data governance: The data in object storage will be managed and governed by the Singdata Lakehouse platform

## Data Lake Overview

[Data Lake Overview](datalake_overview.md)

## How to use Volume (Alibaba Cloud):

### Step0: Preparation

The overall goal of this step is: Allow Lakehouse cluster to access the customer's cloud object storage OSS. To achieve this goal, two types of authentication methods can be used: AcessKey id & AcessKey Secret and role authorization. Among them:

* **AK method**: Just provide the AccessKey ID and AccessKey Secret information of the account with OSS access permission, and use this information to create a storage connection (Storage Connection) object, as shown below:

```
CREATE STORAGE CONNECTION if not exists hz_conn_ak
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    access_id = 'LTAI5tMmbq1Ty1xxxxxxxxx'
    access_key = '0d7Ap1VBuFTzNg7gxxxxxxxxxxxx'
    comments = 'OSS public endpoint';
```

* **Role authorization method** (RoleARN): You need to create a role and permission policy: The permission policy represents the access policy of the OSS service, and this policy is authorized to the created role.

The following describes the **role authorization method**:

#### 1. Customer side: Create a permission policy (CzUdfOssAccess) in the Alibaba Cloud RAM console:

* Access the Alibaba Cloud Access Control (RAM) product console
* Left navigation bar **Permission Management** -> **Permission Policy**, select **Create Permission Policy** in the permission control interface
* On the **Create Permission Policy** page, select the **Script Editing** tab, and replace the following `[bucket_name_1|2|3]` with the actual OSS bucket name. Note: According to the convention of Alibaba Cloud OSS, the same bucket needs to have two Resource entries: "acs\:oss:\*:\*:\[bucket\_name\_1]" and "acs\:oss:\*:\*:\[bucket\_name\_1]/\*" must exist at the same time to achieve the authorization effect:

```JSON
{
    "Version": "1",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "oss:GetObject",
                "oss:ListObjects",
                "oss:PutObject",
                "oss:DeleteObject"
            ],
            "Resource": [
                "acs:oss:*:*:[bucket_name_1]",
                "acs:oss:*:*:[bucket_name_1]/*",
                "acs:oss:*:*:[bucket_name_2]",
                "acs:oss:*:*:[bucket_name_2]/*",
                "acs:oss:*:*:[bucket_name_3]",
                "acs:oss:*:*:[bucket_name_3]/*"
            ]
        }
    ]
}
```

![](.topwrite/assets/en_policy.jpeg)

^

#### 2. Customer side: Create role CzUDFRole in Alibaba Cloud RAM:

* In the left navigation bar of the Alibaba Cloud Access Control (RAM) console, **Identity Management** -> **Role, create role**
* On the **Create Role** page, select the type as **Alibaba Cloud Account**, fill in the custom role name (such as CzUDFRole) in **Configure Role**, select **Other Cloud Accounts** in **Select Trusted Cloud Account**, and write in: 1384322691904283, click Finish

```Properties
{
    "Version": "1",
    "Statement": [
        {
            "Action": "fc:*",
            "Resource": "*",
            "Effect": "Allow"
        },
        {
            "Action": "ram:PassRole",
            "Resource": "*",
            "Effect": "Allow",
            "Condition": {
                "StringEquals": {
                    "acs:Service": "fc.aliyuncs.com"
                }
            }
        }
    ]
}
```

* After creation, click **Authorize Role**: In **Custom Policy**, authorize the just created policy (CzUdfOssAccess) to this role. On the CzUDFRole role details page, get the RoleARN information of this role: `'acs:ram::1222808864xxxxxxx:role/czudfrole'`

\`\`

![](.topwrite/assets/en_role.jpeg)

^

#### 3. Lakehouse side: Create Connection

* Execute the following command in Studio or Lakehouse JDBC client:

```SQL
CREATE STORAGE CONNECTION hz_oss_conn_rolearn 
    TYPE oss 
    REGION = 'cn-hangzhou' 
    ROLE_ARN = 'acs:ram::1222808864467016:role/czudfrole' 
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';
```

* Execute desc connection to get external ID information: In this example, the external ID is: `O0lQUogDJajHqnAQ`

![](.topwrite/assets/desc_connection_1710725915229.jpeg)

#### 4. Client side: In Alibaba Cloud RAM -> Role -> Trust Policy, modify the **Trust Policy** of CzUDFRole:

```Python
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "O0lQUogDJajHqnAQ"
        }
      },
      "Effect": "Allow",
      "Principal": {
        "RAM": [
          "acs:ram::1384322691904283:root"
        ]
      }
    }
  ],
  "Version": "1"
}
```

^

### Step1: Creation and use of Volume objects:

After the preparation work is completed, you can create a Volume object and access object storage data through it. Take Alibaba Cloud OSS as an example:

#### 1. Create a Volume object

```SQL

CREATE EXTERNAL VOLUME sh_image_volume
    location 'oss://sh-oss-derek/images'
    using connection sh_oss_conn_public
    directory = (
        enable=true,
        auto_refresh=true
    )
recursive=true;
```

#### 2. View detailed information of the created Volume object

```SQL
desc volume sh_image_volume
```

#### 3. View the files under the created Volume path

```SQL
show volume directory sh_image_volume;
```

#### 4. Display the images under the Volume path in Lakehouse Studio

When developing in the Lakehouse Studio interface, you can directly click on the url -> **Preview** to open the image when you get the access url of the image through the [get\_presigned\_url](get_presigned_url.md) function:

![](.topwrite/assets/presigned_url_1710729090982.jpeg)

#### 5. Call UDF such as: fc\_image2text, analyze the dishes and calorie information in the OSS image

For creating Remote Function, please refer to: [Remote Function Usage Document (Alibaba Cloud Version)](remotefunction.md).

The function to get the file access URL is [get\_presigned\_url](get_presigned_url.md)

```SQL
set cz.sql.remote.udf.enabled = true;
SELECT relative_path,public.fc_image2text(pre_signed_url) as content
from
(
    select relative_path, get_presigned_url(
        volume sh_image_volume,
        relative_path, 7200
    ) as pre_signed_url
    from directory(volume sh_image_volume)
);
```

^

### Step2: Management of Volume objects:

#### 1. Permission management:

After the preparation work is completed, you need to configure the permissions for specific users to access the object storage data object (Volume). For example: The administrator user grants the user `datalake_user` the permission to create Volume and read Volume data, and also needs to grant the use of Virtual Cluster computing resources to successfully access the data object. The following SQL statement can be executed with administrator privileges:

```SQL
-- Grant datalake_user READ permission
GRANT READ ON volume hz_image_volume TO USER datalake_user;
GRANT USE VCLUSTER ON VCLUSTER DEFAULT TO USER datalake_user;
```

* View the authorization of datalake\_user

```SQL
SHOW grants FOR USER datalake_user;
```

* Revoke the authorization of datalake\_user

```SQL
REVOKE READ ON volume hz_image_volume FROM USER datalake_user;
```

#### 2. Other management operations

View the Volume objects under the current schema

```SQL
show volumes
```

View detailed information of the specified Volume object

```SQL
desc volume sh_image_volume
```

Synchronize the file metadata information in the Volume path to Lakehouse

**Note**: This operation requires specifying the directory attribute enable = true during the volume creation process

```SQL
ALTER volume sh_image_volume REFRESH;

--Query the volume directory file in the local meta
SELECT * FROM DIRECTORY (volume hz_image_volume);
```

Get the access url of the file in the Volume path

```SQL
SELECT get_presigned_url (volume sh_image_volume, relative_path, 7200) pre_signed_url
FROM DIRECTORY (volume sh_image_volume);
```

Delete Volume

```SQL
drop volume sh_image_volume;
```

## Usage restrictions:

* The target object storage of the current Volume only supports Alibaba Cloud OSS and Tencent Cloud COS
* Downloading files from external Volume will generate download costs for the cloud account's object storage. For specific charges, please refer to the billing instructions of the cloud vendor's object storage

^
^
