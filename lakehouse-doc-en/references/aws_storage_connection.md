# Create Amazon Cloud Storage Connection

The goal of this step is to allow the Lakehouse cluster to access Amazon Cloud (AWS) object storage S3. To achieve this goal, two authentication methods provided by AWS's **Identity and Access Management (IAM)** product can be used: **Access Keys** and **Role Authorization**.

## Based on Access Keys

```SQL
CREATE STORAGE CONNECTION aws_bj_conn
    TYPE S3
    ACCESS_KEY_ID = 'AKIAQNBSBP6EIJE33***'
    SECRET_ACCESS_KEY = '7kfheDrmq***************************'
    ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
    REGION = 'cn-north-1';
```

### Parameters:

* `TYPE`: The object storage type, for AWS, fill in S3 (case insensitive)
* `ACCESS_KEY_ID / SECRET_ACCESS_KEY`: The access key for AWS, refer to: [Access Keys](https://docs.aws.amazon.com/zh_cn/IAM/latest/UserGuide/id_credentials_access-keys.html) for how to obtain it
* `ENDPOINT`: The service address for S3. AWS China is divided into Beijing and Ningxia regions. The service address for S3 in the Beijing region is `s3.cn-north-1.amazonaws.com.cn`, and for the Ningxia region is `s3.cn-northwest-1.amazonaws.com.cn`. Refer to: [China Region Endpoints](https://docs.amazonaws.cn/aws/latest/userguide/endpoints-arns.html) to find the endpoints for the Beijing and Ningxia regions -> Amazon S3 corresponding endpoints
* `REGION`: AWS China is divided into Beijing and Ningxia regions, the region values are: Beijing region `cn-north-1`, Ningxia region `cn-northwest-1`. Refer to: [China Region Endpoints](https://docs.amazonaws.cn/aws/latest/userguide/endpoints-arns.html). For the international site, refer to: [Amazon Simple Storage Service endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/s3.html)

## Role-Based Authorization

You need to create a **permission policy** and a **role** in AWS IAM under the account that owns the target S3 bucket. The permission policy defines the rules for accessing AWS S3 data, and this policy is attached to the created role. Singdata Lakehouse achieves read and write operations on S3 data by assuming this role.

### STEP1: Create a Permission Policy (LakehouseAccess) on AWS:

* Log in to the AWS cloud platform and enter the **Identity and Access Management (IAM)** product console
* In the IAM page's left navigation bar, go to **Account Settings**, in the **Security Token Service (STS)** section's **Endpoints** list, find the region corresponding to the current Singdata Lakehouse instance. If the **STS Status** is not enabled, please enable it.
* In the IAM page's left navigation bar, go to **Policies**, in the **Policies** interface, select **Create Policy**, and choose the JSON method in the policy editor
* Add the policy that allows Singdata Lakehouse to access the S3 bucket and directory. Below is a sample policy, please replace `<bucket>` and `<prefix>` with the actual bucket and path prefix names.

> ⚠️ **Note**: Please fill in the `"s3:prefix"` item with: `["*"]` or `["<path>/*"]` to grant access permissions to all prefixes in the specified bucket or path in the bucket respectively.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
              "s3:PutObject",
              "s3:GetObject",
              "s3:GetObjectVersion",
              "s3:DeleteObject",
              "s3:DeleteObjectVersion"
            ],
            "Resource": "arn:aws:s3:::<bucket>/<prefix>/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::<bucket>",
            "Condition": {
                "StringLike": {
                    "s3:prefix": [
                        "<prefix>/*"
                    ]
                }
            }
        }
    ]
}
```

* Select **Next**, enter the policy name (e.g., `LakehouseAccess`) and description (optional)
* Click **Create Policy** to complete the policy creation

### STEP2: Create Role (LakehouseVolumeRole) on AWS:

* Log in to the AWS cloud platform and go to the **Identity and Access Management (IAM)** product console
* In the IAM page, navigate to **Roles** -> **Create Role** -> **AWS Account**, select **Another AWS Account**, and enter `028022243208` (China site) / `014617434350` (international site) in the Account ID

> ⚠️ **Note**: To prevent the ROLE\_ARN from being obtained by third parties for unauthorized data access, you can check **Options** and select **Require external ID (best practice for third parties assuming this role)**. After checking, you can fill in `000000` as a placeholder in the **EXTERNAL ID** field to be filled in later. `EXTERNAL ID` serves as an additional layer of verification, ensuring that access is only allowed when the request includes the preset `EXTERNAL ID`. This means that even if a third party knows some other access information (such as the role ARN), they cannot access the resources without the correct `EXTERNAL ID`.

![](.topwrite/assets/image_1728551322654.png)

* Select **Next**, on the Add permissions page, choose the policy created in STEP1 `LakehouseAccess`, then select **Next**
* Fill in the Role name (e.g., `LakehouseVolumeRole`) and description, click **Create Role** to complete the role creation
* In the role details page, obtain the value of **Role ARN** to use when creating the STORAGE CONNECTION

![](.topwrite/assets/image_1728551348143.png)

^

### STEP3: Create STORAGE CONNECTION on Singdata Lakehouse Side:

* Execute the following commands in Studio or Lakehouse JDBC client:

```SQL
CREATE STORAGE CONNECTION aws_bj_conn_arn
  TYPE S3
  REGION = 'cn-north-1'
  ROLE_ARN = 'arn:aws-cn:iam::02802*******:role/LakehouseVolumeRole';
```

* During the process of creating a storage connection, Lakehouse will generate this EXTERNAL ID. You can configure this EXTERNAL ID into the Trust Policy of the AWS IAM role (`LakehouseVolumeRole`) created in STEP2 to achieve additional access control:

```SQL
-- View EXTERNAL ID 
DESC CONNECTION aws_bj_conn_arn;
```

![](.topwrite/assets/20240626-215920.jpeg)

^

* In the AWS IAM console, navigate to **Roles** in the left sidebar, find the role created in STEP2 and go to the role details page. In **Trust relationships**, replace the value of `sts:ExternalId` `000000` with `EXTERNAL_ID` from the DESC result. Click **Update** to complete the role policy update.
