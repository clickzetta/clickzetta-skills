# Create API CONNECTION

API CONNECTION is primarily used to store and protect authentication information for third-party application services. Through API CONNECTION, Singdata Lakehouse's EXTERNAL FUNCTIONs can securely interact with these services via API calls. Currently, the external services supported by API CONNECTION include **Alibaba Cloud Function Compute (FC)**, **Tencent Cloud Functions (SCF)**, and **AWS Lambda**.

## Syntax

```
CREATE API CONNECTION [ IF NOT EXISTS ] <connection_name>
  TYPE  CLOUD_FUNCTION
  PROVIDER = '<provider>'
  REGION = '<region>'
  ROLE_ARN = '<role_arn>'
  NAMESPACE = '<namespace>'
  CODE_BUCKET = '<code_bucket>'
```

### Parameter Descriptions

| Parameter | Description |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connection_name` | Name of the API connection to create. |
| `PROVIDER` | Cloud function service provider. Supported values: `'tencent'`, `'aliyun'`, and `'aws'`. |
| `REGION` | Region where the cloud function is deployed. **Examples**: Alibaba Cloud: `'cn-shanghai'` ([region codes](https://help.aliyun.com/document_detail/40654.html)); Tencent Cloud: `'ap-beijing'` ([region codes](https://intl.cloud.tencent.com/document/product/213/6091)); AWS: `'ap-southeast-1'` (international) or `'cn-north-1'` (China) |
| `ROLE_ARN` | Role ARN used to execute cloud functions. **Example (Alibaba Cloud)**: `acs:ram::1222800000000000:role/czudfrole`. **Example (Tencent Cloud)**: `qcs::cam::uin/1000*******:roleName/LakehouseRole`. **Example (AWS)**: `arn:aws:iam::928925945197:role/Lambda-S3-Role` |
| `NAMESPACE` | Namespace for the cloud function. **Required for Tencent Cloud**. For other cloud services, fill in `'default'` or leave blank as appropriate. |
| `CODE_BUCKET` | Name of the object storage bucket containing the cloud function code package. **Tencent Cloud format is `BucketName-APP_ID`**, e.g., `myfunction-131xxxxx`. |

For NAMESPACE: required when using Tencent Cloud. For other cloud services it can be omitted or set to `'default'`. The value is obtained as shown in the image below:
![](.topwrite/assets/image_1735616872087.png)

^

## Case Description

API CONNECTION is primarily used for creating EXTERNAL FUNCTIONs. The EXTERNAL FUNCTION usage flow is:

* User activates cloud function compute services (e.g., Alibaba Cloud Function Compute FC) and object storage services
* Upload function execution code & executables, dependent libraries, models, and data files to object storage
* Grant Singdata Lakehouse permission to operate the above services and access function files
* User calls EXTERNAL FUNCTION in Singdata Lakehouse SQL statements
* Singdata Lakehouse sends an HTTP request to the provided service address using the authentication information to invoke the function
* Singdata Lakehouse retrieves the response and returns the result

Therefore, you must activate function compute and object storage services and grant Singdata Lakehouse the necessary permissions.

### Creating API CONNECTION on Alibaba Cloud

* **Environment Preparation**
  EXTERNAL FUNCTION depends on Alibaba Cloud's "[Object Storage](https://oss.console.aliyun.com/overview)" and "[Function Compute](https://fcnext.console.aliyun.com/overview)" services. Ensure these services are activated.

* Step 1: Activate Function Compute FC and Object Storage OSS services. Keep them in the same region as the Singdata Lakehouse instance (e.g., `cn-shanghai`).

* Step 2: Get OSS Bucket + AccessKey.
  * Go to [OSS Console](https://oss.console.aliyun.com) → Create Bucket (same region as FC).
  * Go to [RAM User Management](https://ram.console.aliyun.com/users) → Create AccessKey, record the **AccessKey ID** and **AccessKey Secret**.

* Step 3: Edit the AliyunFCFullAccess permission policy (add ram:PassRole permission).
  * Go to [RAM Policy Console](https://ram.console.aliyun.com/policies) → search for **AliyunFCFullAccess** → Edit, add the `ram:PassRole` section:

  ```json
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

* Step 4: Create custom permission policy CzUdfOssAccess.
  * Go to [RAM Policy Console](https://ram.console.aliyun.com/policies) → **Create Permission Policy** → **Script Editor**.
  * Replace `bucket_name_1` etc. with actual OSS bucket names. Note: the same bucket needs both `bucket_name` and `bucket_name/*` Resource entries:

  ```json
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
                  "acs:oss:*:*:bucket_name_1/*"
              ]
          }
      ]
  }
  ```

  * Click **Next**, enter the policy name **CzUdfOssAccess**, click **Done**.

* Step 5: Create a RAM Role and authorize it.
  * Go to [RAM Role Console](https://ram.console.aliyun.com/roles) → **Create Role**:
  * Role type: **Alibaba Cloud Account** → **Other Cloud Account**
  * Enter Account ID `1384322691904283` (Singdata Lakehouse's main account), click **Next**
  * Under **Select Permissions**, check both the system policy **AliyunFCFullAccess** and the custom policy **CzUdfOssAccess**
  * Click **Next**, enter the role name (e.g., `CzUDFRole`), click **OK**
  * After successful creation, go to the role detail page to get the **Role ARN**: `acs:ram::<your_account_id>:role/CzUDFRole`

* Step 6: Execute SQL to create API CONNECTION.

  ```sql
  CREATE API CONNECTION my_funciton_connection
      TYPE CLOUD_FUNCTION
      PROVIDER = 'aliyun'
      REGION = 'cn-shanghai'
      ROLE_ARN = 'acs:ram::1757168149572678:role/CzUDFRole'
      CODE_BUCKET = 'function-compute-my1';
  ```

* Step 7 (optional): Configure External ID.

  After successful creation, run the following to get the External ID:

  ```sql
  DESC CONNECTION my_funciton_connection;
  ```

  ![](.topwrite/assets/image_1735638011131.png)

  Go back to Alibaba Cloud [RAM Roles](https://ram.console.aliyun.com/roles) → `CzUDFRole` → **Trust Policy** → **Edit**, replace the `sts:ExternalId` value with the value from the DESC result:

  ```json
  {
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Condition": {
          "StringEquals": {
            "sts:ExternalId": "Replace with the ExternalId from DESC result"
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

  > The `1384322691904283` in the trust policy is the Singdata main account and must not be changed.

### Creating API CONNECTION on Tencent Cloud

**Environment Preparation**
EXTERNAL FUNCTION depends on Tencent Cloud's "[Object Storage](https://console.cloud.tencent.com/cos)" and "[Cloud Functions](https://console.cloud.tencent.com/scf/list?rid=1\&ns=default)" services. Ensure these services are activated.

* Object Storage: Required in the Singdata Lakehouse deployment region (e.g., ap-shanghai) for storing function base code.
* Cloud Functions: After activating **Cloud Functions**, it is recommended to manually create a function using the template creation feature, preferably Flask framework templates or other templates with a WebFunc tag. During this process, the Tencent Cloud console will guide users through initial configurations such as activating log services (CLS) and other dependencies, creating necessary Access Control (CAM) roles, and granting necessary CAM permissions.

* Step 1: Activate Tencent Cloud's Cloud Functions (SCF) service. Keep the cloud function region consistent with the Singdata Lakehouse service region.
  ![](.topwrite/assets/image_1735616566747.png)

* Step 2: Activate COS and create a storage bucket.
  * Go to [COS Console](https://console.cloud.tencent.com/cos) → Create bucket (same region as SCF, e.g., `ap-shanghai`).
  * After creation, the full name in the bucket list is `BucketName-APP_ID` (e.g., `myfunction-1310000503`). **Record the Bucket name and APP_ID**—both are needed for configuration.

* Step 3: Obtain API credentials.
  * Go to [Access Management](https://console.cloud.tencent.com/cam/capi) → Create credentials, record **SecretId** and **SecretKey**.

* Step 4: Create CAM custom policy (LakehouseAccess).
  * Log in to Tencent Cloud, go to the **Access Management** [product console](https://console.cloud.tencent.com/cam/policy)
  * In the left navigation bar go to **Policies**, select **Create Custom Policy** → **Create by Policy Syntax** → select **Blank Template**, paste the following JSON (replace `<region>`, `<APP_ID>`, `<bucket>` with actual values):

  ```json
  {
      "statement": [
          {
              "action": ["scf:*"],
              "effect": "allow",
              "resource": ["*"]
          },
          {
              "action": ["cos:*"],
              "effect": "allow",
              "resource": [
                  "qcs::cos:<region>:uid/<APP_ID>:<bucket>-<APP_ID>/*"
              ]
          }
      ],
      "version": "2.0"
  }
  ```

  > Example: `qcs::cos:ap-shanghai:uid/1253896122:qiliang-external-function-1253896122/*`

  * Click **Next**, set the policy name to **`LakehouseAccess`** (must use this name exactly), click **Done**.

  > ⚠️ The policy must include both `scf:*` and `cos:*` rules. Missing the COS permission will cause `AccessDenied (Status Code: 403)` during `CREATE FUNCTION`. The COS Resource format is `qcs::cos:<region>:uid/<APP_ID>:<bucket>-<APP_ID>/*`; the trailing `/*` is required.

* Step 5: Create CAM Role (LakehouseRole).
  * Go to [Access Management](https://console.cloud.tencent.com/cam/role) → Create role:
  * Role entity: **Tencent Cloud Account** → **Other Main Account**
  * Enter Account ID `100029595716` (Singdata's Tencent Cloud main account), click **Next**
  * Check the newly created `LakehouseAccess` policy, click **Next**
  * Set the role name to **`LakehouseRole`** (must use this name exactly), click **Done**
  * After successful creation, go to the role detail page to get the Role ARN: `qcs::cam::uin/<your_account_id>:roleName/LakehouseRole`

  > ⚠️ The role name must be `LakehouseRole`. The role entity must be set to "Other Main Account" and trust Singdata account `100029595716`—**not** "Tencent Cloud Product Services".

* Step 6: Execute SQL to create API CONNECTION.

  ```sql
  CREATE API CONNECTION my_funciton_connection
      TYPE CLOUD_FUNCTION
      PROVIDER = 'tencent'
      REGION = 'ap-shanghai'
      ROLE_ARN = 'qcs::cam::uin/<your_account_id>:roleName/LakehouseRole'
      NAMESPACE = 'default'
      CODE_BUCKET = 'myfunction-1310000503';
  ```

  > ⚠️ `CODE_BUCKET` format is `BucketName-APP_ID` (cannot be just the Bucket name). `NAMESPACE` is required for Tencent Cloud and is typically `default`.

* Step 7 (optional): Configure External ID.
  > ⚠️ **Note**: To prevent the ROLE_ARN from being obtained by third parties for unauthorized data access, you can use `EXTERNAL ID` as an additional verification layer, ensuring that access is only allowed when the request includes the preset `EXTERNAL ID`. This means that even if a third party knows other access information (such as the role ARN), they cannot access the resource without the correct `EXTERNAL ID`.

  After the API CONNECTION is successfully created, run the following to get the External ID:

  ```sql
  DESC CONNECTION my_funciton_connection;
  ```

  ![](.topwrite/assets/image_1735630257317.png)

  * On the client side: Go to the Tencent Cloud **Access Management** console, **Role** → **LakehouseRole** → **Role Entity** → **Manage Entities**, select **Add Account** → select **Current Main Account**, enter the main account ID `100029595716` (Singdata's Tencent Cloud main account), check **Enable Verification**, enter the EXTERNAL_ID from the DESC result, click **Confirm** → **Update**.

### Creating API CONNECTION on AWS

* **Environment Preparation**
  EXTERNAL FUNCTION depends on AWS's "[Object Storage](https://s3.console.aws.amazon.com)" and "[Lambda Functions](https://console.aws.amazon.com/lambda/home)" services. Ensure these services are activated.
  * For China region, use the [Beijing console](https://cn-north-1.console.amazonaws.cn); for international regions, use the appropriate regional console.

* Step 1: Activate Lambda and S3 services.
  * Go to the [Lambda Console](https://console.aws.amazon.com/lambda) and [S3 Console](https://s3.console.aws.amazon.com) and confirm the services are activated.

* Step 2: Create an S3 storage bucket.
  * Go to [S3 Console](https://s3.console.aws.amazon.com) → Create bucket (same region as Lambda, e.g., `ap-southeast-1`).
  * Record the Bucket name—it will be needed in the SQL later.

* Step 3: Create an IAM user and get an AccessKey.
  * Go to [IAM Users](https://console.aws.amazon.com/iam) → Create user:
  * Any username (e.g., `qiliang-udf`); do not check "Provide user access to the AWS Management Console"
  * Attach policy directly: search and select `AmazonS3FullAccess`
  * After creation, go to the user → **Security credentials** → **Create access key**
  * Select **Command Line Interface (CLI)** → Create → Save the **Access Key ID** and **Secret Access Key**

* Step 4: Create IAM permission policy.
  * Log in to the AWS platform, go to the **Identity and Access Management (IAM)** product console.
  * In the left navigation bar go to **Policies**, select **Create policy** → **JSON**, paste the following policy (replace `<bucket>` with the Bucket name from Step 2):

  ```json
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": [
                  "s3:GetObject",
                  "s3:GetObjectVersion",
                  "s3:PutObject",
                  "s3:ListBucket"
              ],
              "Resource": [
                  "arn:aws:s3:::<bucket>",
                  "arn:aws:s3:::<bucket>/*"
              ]
          },
          {
              "Effect": "Allow",
              "Action": "lambda:*",
              "Resource": "*"
          }
      ]
  }
  ```

  > ⚠️ S3 must include `PutObject` (the platform needs to write code packages to S3). Lambda uses `lambda:*` to avoid missing operations by listing them individually.

  * Click **Next**, set the policy name to `LakehouseAccess`, click **Create policy**.

* Step 5: Create IAM Role.
  * Go to [IAM Roles](https://console.aws.amazon.com/iam/home#/roles) → Create role:
  * Trusted entity type: **AWS service** → Use case: **Lambda**
  * Permission policies: check the newly created `LakehouseAccess` and the AWS built-in `AWSLambdaBasicExecutionRole`
  * Click **Next**, set the role name to `Lambda-S3-Role`, click **Create role**
  * After successful creation, go to the role detail page and copy the **Role ARN**: `arn:aws:iam::<your_AWS_account_id>:role/Lambda-S3-Role`

* Step 6: Edit the trust policy (add Singdata account's AssumeRole permission).
  * Role detail page → **Trust relationships** → **Edit trust policy**, add both the Lambda service and the Singdata account:

  ```json
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Principal": {
                  "Service": "lambda.amazonaws.com"
              },
              "Action": "sts:AssumeRole"
          },
          {
              "Effect": "Allow",
              "Principal": {
                  "AWS": "arn:aws:iam::014617434350:root"
              },
              "Action": "sts:AssumeRole"
          }
      ]
  }
  ```

  > ⚠️ `014617434350` is Singdata's international AWS account; China site uses `028022243208`. Missing Singdata account's trust relationship will result in `AccessDenied: sts:AssumeRole`.

  > ⚠️ This is the **trust policy** (Trust relationships), not the permissions policy (Permissions). Do not paste the permissions policy JSON here—they are on different pages.

* Step 7: Execute SQL to create API CONNECTION.

  ```sql
  CREATE API CONNECTION udf_noah
      TYPE CLOUD_FUNCTION
      PROVIDER = 'aws'
      REGION = 'ap-southeast-1'
      ROLE_ARN = 'arn:aws:iam::928925945197:role/Lambda-S3-Role'
      CODE_BUCKET = 'qiliang-udf-code';
  ```

  > International region endpoint format is `s3.<region>.amazonaws.com`; China region is `s3.<region>.amazonaws.com.cn`.

* Step 8 (optional): Configure External ID.
  After the API CONNECTION is successfully created, run the following to get the External ID:

  ```sql
  DESC CONNECTION udf_noah;
  ```

  ![](.topwrite/assets/image_1735802829076.png)

  Go back to **IAM Roles** → `Lambda-S3-Role` → **Trust relationships** → **Edit trust policy**, add a `Condition` to the Singdata account's `Statement`:

  ```json
  {
      "Effect": "Allow",
      "Principal": {
          "AWS": "arn:aws:iam::014617434350:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
          "StringEquals": {
              "sts:ExternalId": "ExternalId value from DESC result"
          }
      }
  }
  ```

### Next Steps:

After completing the API CONNECTION creation, you can proceed to create external functions, supporting Python and Java scripts to process data in Singdata Lakehouse. See: [Create External Function](create_external_function.md)
