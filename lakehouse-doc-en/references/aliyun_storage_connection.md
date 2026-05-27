# Create Alibaba Cloud Storage Connection

The goal of this step is to allow the Lakehouse cluster to access object storage OSS on Alibaba Cloud. To achieve this goal, you can use two authentication methods provided by Alibaba Cloud: **Access Key** and **Role Authorization**.

## Method 1: Access Key (AK Information):

You only need to provide the AccessKey ID and AccessKey Secret information of an account with access to OSS permissions. Use this information to create a Storage Connection object, as shown in the example below:

```
CREATE STORAGE CONNECTION IF NOT EXISTS hz_conn_ak
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    ACCESS_ID = 'LTAI5tMmbq1Ty1xxxxxxxxx'
    ACCESS_KEY = '0d7Ap1VBuFTzNg7gxxxxxxxxxxxx'
    COMMENTS = 'OSS public endpoint';
```

## Method 2: Role Authorization (RoleARN):

You need to create a role and a permission policy: the permission policy represents the access policy for the OSS service, and this policy is authorized to the created role.

**The following mainly describes** **the specific steps for the role authorization method (RoleARN**):

#### 1. Operations on the Alibaba Cloud side: Create a permission policy (CzUdfOssAccess) in the Alibaba Cloud RAM console:

> Note: The user needs to have RAM

* Access the Alibaba Cloud Resource Access Management (RAM) product console
* In the left navigation bar, go to **Permission Management** -> **Permission Policies**, and select **Create Permission Policy** in the permission control interface
* On the **Create Permission Policy** page, select the **Script Editor** tab, and replace `[bucket_name_1|2|3]` below with the actual OSS bucket names. Note: According to Alibaba Cloud OSS conventions, the same bucket needs to have two Resource entries: `"acs:oss:*:*:bucket_name_1"` and `"acs:oss:*:*:bucket_name_1/*"` to achieve the authorization effect:

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
                "acs:oss:*:*:bucket_name_1",
                "acs:oss:*:*:bucket_name_1/*",
                "acs:oss:*:*:bucket_name_2",
                "acs:oss:*:*:bucket_name_2/*",
                "acs:oss:*:*:bucket_name_3",
                "acs:oss:*:*:bucket_name_3/*"
            ]
        }
    ]
}
```

![](.topwrite/assets/screenshot-20250219-151752.png)

^

#### 2. Alibaba Cloud Side: Create a Role CzUDFRole in Alibaba Cloud RAM:

* In the Alibaba Cloud Access Control (RAM) console, navigate to **Identity Management** -> **Roles** on the left sidebar, and create a role.
* On the **Create Role** page, select the type as **Alibaba Cloud Account**, fill in the custom role name (e.g., CzUDFRole) in **Configure Role**, select **Other Cloud Account** in **Select Trusted Cloud Account**, and enter: 1384322691904283, then click Finish.

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

* After creation, click **Authorize for Role**: In **Custom Policy**, authorize the newly created policy (CzUdfOssAccess) to the role. On the CzUDFRole role details page, obtain the RoleARN information for that role: `'acs:ram::1222808864xxxxxxx:role/czudfrole'`

![](.topwrite/assets/screenshot-20250219-151930.png)

^

#### 3. Lakehouse Side: Create Connection

* Execute the following command in Studio or Lakehouse JDBC client:

```SQL
CREATE STORAGE CONNECTION hz_oss_conn_rolearn 
    TYPE oss 
    REGION = 'cn-hangzhou' 
    ROLE_ARN = 'acs:ram::12228088xxxxxxxx:role/czudfrole' 
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';
```

* Execute `desc connection` to get the external ID information: In this instance, the external ID is: `O0lQUogDJajHqnAQ`

#### 4. Client Side: In Alibaba Cloud RAM -> Roles -> Trust Policy, modify the **trust policy** of CzUDFRole:

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

After creation, you can use this storage connection object in the statements of common external volumes to mount the object storage path.
