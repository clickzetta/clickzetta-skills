# Create API CONNECTION

This type of CONNECTION is mainly used to store and protect the authentication information of third-party application services. Through API Connection, Lakehouse can securely interact with these services via API calls. Currently, the external services supported by API Connection include Alibaba Cloud Function Compute (FC) and Tencent Cloud Function Service.

## Syntax

Syntax 1
```
CREATE API CONNECTION [ IF NOT EXISTS ] connection_name
TYPE CLOUD_FUNCTION
PROVIDER=''
REGION=''
ROLE_ARN=''
NAMESPCE=''
CODE_BUCKET=''
```
* PROVIDER: Cloud function provider, such as TENCENT, ALIYUN, and AWS
* REGION: The region where the corresponding cloud function is located, such as 'cn-shanghai'. For Alibaba Cloud, refer to the link [region](https://help.aliyun.com/zh/oss/user-guide/regions-and-endpoints?scm=20140722.S_help%40%40%E6%96%87%E6%A1%A3%40%4031837.S_BB2%40bl%2BRQW%40ag0%2BBB1%40ag0%2Bhot%2Bos0.ID_31837-RL_%E5%9F%9F%E5%90%8D-LOC_doc%7EUND%7Eab-OR_ser-V_4-P0_2\&spm=a2c4g.11186623.d_help_search.i3), for Tencent Cloud refer to the link [region](https://cloud.tencent.com/document/product/583/17299#.E6.94.AF.E6.8C.81.E5.9C.B0.E5.9F.9F) such as: ap-beijing, for AWS refer to: [China region endpoints](https://docs.amazonaws.cn/aws/latest/userguide/endpoints-arns.html), international endpoints [region](https://docs.aws.amazon.com/general/latest/gr/lambda-service.html)
* ROLE\_ARN: The role assumed when creating the cloud function, such as acs:ram::12228000000000000:role/czudfrole
* CODE\_BUCKET: The name of the object storage bucket where the cloud function program files are located.
* NAMESPCE: Required when using Tencent Cloud. For other cloud services, you can leave it blank or directly fill in 'default'. This value can be obtained as shown in the figure below
![](.topwrite/assets/image_1740368445142.png)
  Syntax two
```SQL
CREATE API CONNECTION [ IF NOT EXISTS ] connection_name
TYPE CLOUD_FUNCTION 
WITH PROPERTIES('parameter_key'='parameter_value')
[COMMENT 'comment'];
```
**Parameter Description**

* `connection_name`: The name of the connection to be created.
* `TYPE`: Specifies the type of data source for the connection, such as `CLOUD_FUNCTION`.
* `WITH PROPERTIES`: Specifies the authentication and connection information required for the external data source.
* `parameter_key`: Property key.
* `parameter_value`: Property value.
* `IF NOT EXISTS`: Optional parameter. If the specified connection already exists, no changes are made, and a message indicating the connection exists is returned; if not specified and the connection exists, an error message is returned.
* `COMMENT`: Optional parameter for adding comment information.

### Supported Data Source Types and Parameters

The following are the parameters required for the `CLOUD_FUNCTION` type data source:

| Parameter Name                | Description            | Example Value                               | Required |
| ---------------------------- | --------------------- | ----------------------------------------- | ------ |
| `cloud_function.provider`    | Cloud function service provider | `aliyun`                                  | Yes      |
| `cloud_function.region`      | Region where the cloud function service is located | `cn-beijing` / `cn-hangzhou`              | Yes      |
| `cloud_function.role_arn`    | User's ARN authorization information | `acs:ram::123456789012:role/YourRoleName` | Yes      |
| `cloud_function.namespace`   | Specifies the namespace of the external function, required for Tencent Cloud | `your_namespace`                          | Yes      |
| `cloud_function.code_bucket` | Object storage Bucket information where the user's code is stored | `your_bucket_name`                        | Yes      |

## Case Description

API CONNECTION is mainly used for creating EXTERNAL FUNCTION. The usage process of EXTERNAL FUNCTION is as follows:

* Users activate cloud function computing services (such as Alibaba Cloud Function Compute FC) and object storage services.
* Upload the function execution code & executable files, dependent libraries, models, and data files to object storage.
* Grant Singdata Lakehouse permission to operate the above services and access function files.
* Users call Remote function in Singdata Lakehouse SQL statements.
* Singdata Lakehouse sends an HTTP request to call the running function based on the provided service address and authentication information.
* Singdata Lakehouse retrieves the response information and returns the result.
  Therefore, you must activate function computing services and object storage services and grant Lakehouse permissions.

### Example 1: Creating API CONNECTION on Alibaba Cloud

* **Environment Preparation**
  UDF relies on Alibaba Cloud's "[Object Storage](https://oss.console.aliyun.com/overview)" and "[Function Compute](https://fcnext.console.aliyun.com/overview)" services. Please ensure that the relevant services are activated.

* step1: Users activate cloud function computing services (such as Alibaba Cloud Function Compute FC) and object storage services.

* step2. Alibaba Cloud operations: Create a permission policy (CzUdfOssAccess) in the Alibaba Cloud RAM console: Note: Users need to have RAM permissions.
  * Access the Alibaba Cloud Resource Access Management (RAM) [product console](https://ram.console.aliyun.com/policies).
  * In the left navigation bar, **Permission Management** -> **Permission Policies**, search for **AliyunFCFullAccess** in the permission control interface -> Edit the **AliyunFCFullAccess** permission policy to add the following "acs\*\*:**Service**": "**fc.aliyuncs.com**"\*\* part.
    ```JSON
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
* step3: Create a permission policy (CzUdfOssAccess) in the Alibaba Cloud RAM console: Note: The user needs to have RAM permissions

  * Access the Alibaba Cloud Resource Access Management (RAM) product console
  * In the left navigation bar, go to **Permission Management** -> **Permission Policies**, and select **Create Permission Policy** in the permission control interface
  * On the **Create Permission Policy** page, select the **Script Editor** tab, and replace `[bucket_name_1|2|3]` below with the actual OSS bucket names. Note: According to Alibaba Cloud OSS conventions, the same bucket needs to have two Resource entries: `"acs:oss:*:*:bucket_name_1"` and `"acs:oss:*:*:bucket_name_1/*"` must both exist to achieve the authorization effect:
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
* step4 Alibaba Cloud Console: Create a role in Alibaba Cloud RAM (e.g., CzUDFRole):
  * In the RAM console, navigate to **Identity Management** -> **Roles** on the left sidebar, and click **Create Role**
  * On the **Create Role** page, select the type as **Alibaba Cloud Account**, fill in the custom **Role Name** (e.g., CzUDFRole), select **Other Cloud Account** in **Select Trusted Cloud Account**, and enter: 1384322691904283 (Singdata Lakehouse Shanghai's cloud main account), then click **Complete**
  * After creation, click **Authorize Role**:
  * In **System Policies**, grant the **AliyunFCFullAccess** policy to the role CzUDFRole
  * In **Custom Policies**, grant the newly created policy (**CzUdfOssAccess**) to the role

* step5: After creation, click **Authorize Role**: In **Custom Policies**, grant the newly created policy (CzUdfOssAccess) to the role. In the role CzUDFRole details page, obtain the RoleARN information of the role: `'acs:ram::1222808864xxxxxxx:role/czudfrole'`![](.topwrite/assets/image_1740368644886.png)

* step6: Fill the above role\_arn into the syntax parameter, and create an Alibaba Cloud Function Compute connection
```SQL
CREATE API CONNECTION my_funciton_connection
TYPE CLOUD_FUNCTION
PROVIDER='aliyun'
REGION='cn-hangzhou'
ROLE_ARN='acs:ram::1757168149572678:role/czudfrole'
CODE_BUCKET='function-compute-my1';
```
* step7: desc connection to obtain external ID information: In this example, the external ID is: `VW9UaGwYENBQ7cFp`
  ```
  DESC CONNECTION my_funciton_connection;
  ```
![](.topwrite/assets/image_1735638011131.png)
  * In Alibaba Cloud RAM -> Roles -> Trust Policy, modify the **trust policy** of CzUDFRole:
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
### Example 2: Create API CONNECTION on Tencent Cloud

**Environment Preparation**
UDF relies on Tencent Cloud's "[Object Storage](https://console.cloud.tencent.com/cos)" and "[Cloud Functions](https://console.cloud.tencent.com/scf/list?rid=1\&ns=default)" services. Please ensure that the relevant services are activated.

* Object Storage: Required in the Lakehouse deployment region (e.g., ap-shanghai) to store UDF base code;
* Cloud Functions: After activating the **Cloud Functions** service, it is recommended to manually create a function using the template creation feature, preferably using templates with the WebFunc tag such as the Flask framework template. During this process, the Tencent Cloud console will guide users through some initial configurations, such as activating the log service (CLS) and other dependent services, creating necessary Access Control (CAM) roles, and granting necessary Access Control (CAM) permissions.
* **step1**: Users activate Tencent Cloud's cloud function computing service. The cloud function region should be consistent with the Lakehouse service region.
![](.topwrite/assets/image_1740368721078.png)
* **step2**: Data creation permission policy (LakehouseAccess):

  * Log in to Tencent Cloud and go to the **Access Management** [product console](https://console.cloud.tencent.com/cam/policy)
  * In the **Access Management** page, navigate to **Policies** on the left sidebar, and in the permission control interface, select **Create Custom Policy** -> **Create by Policy Generator** -> **Visual Policy Generator**.
  * In the **Visual Policy Generator** tab, **Service**: Select **Cloud Functions**; **Action**: Select **All Actions** (you can make more granular selections based on actual needs); **Resource**: Select **All Resources** or **Specific Resources** as needed. In this case, select specific resources, use namespace authorization as shown below, click the edit button, select the region activated in step1, the resource can be * or a specified namespace, in this case, the namespace from step1: default. As shown in the red-marked area of the cloud function in Figure 2![](.topwrite/assets/image_1740369082106.png)
![](.topwrite/assets/image_1740368445142.png)
    Click to create the policy
* step3: [Create Role](https://console.cloud.tencent.com/cam/role) CzUdfRole
  * Create a new role
  * Select Tencent Cloud Account
  * Select **Other Main Account 100029595716 (Singdata Main Account)**, keep other options as default, and click **Next**
  * In the **Configure Role Policy** configuration, authorize the newly created LakehouseAccess custom policy to the current role. Click **Next**, and in **Role Naming**, fill in `LakehouseRole` to complete the creation.
  * After successful creation, go to the details page of the role `LakehouseRole` in the role list to get the RoleARN information of the role: `qcs::cam::uin/1000*******:roleName/LakehouseRole`
  * Remember the RoleArn, for example: `qcs::cam::uin/1000*******:roleName/LakehouseRole`
* step4: Activate COS and create a new BUCKET
  * Create a new bucket to store udf code, the region should be consistent with the Lakehouse service region. The newly created bucket is myfunction as shown below![](.topwrite/assets/image_1740378042671.png)
  * Authorize Lakehouse to access the bucket (myfunction)
  * Go to the **Access Management** [product console](https://console.cloud.tencent.com/cam/policy). Find the newly created "LakehouseAccess" policy. Select Edit![](.topwrite/assets/image_1740378228008.png)
  * Select the Visual Policy Generator. Add permissions![](.topwrite/assets/image_1740378259906.png)
* **Service**: Select **Object Storage (cos)**; **Action**: Select **All Actions** (you can make more granular selections based on actual needs); **Resource**: Select **All Resources** or **Specific Resources** as needed. In this example, select specific resources, which is `myfunction-131xxxxx` in Shanghai.![](.topwrite/assets/image_1740378387729.png)
* step5: Create Connection on the Lakehouse side
  \* Execute the following command in Studio or the Lakehouse JDBC client:
  `SQL
      CREATE API CONNECTION my_funciton_connection
      TYPE CLOUD_FUNCTION
      PROVIDER='tencent'
      REGION='ap-shanghai'
      ROLE_ARN='qcs::cam::uin/xxxx:roleName/CzUDFRole'
      NAMESPCE='default'
      CODE_BUCKET='myfunction-131xxxx';
      `

  * Note: To prevent the ROLE_ARN from being obtained by third parties for unauthorized data access, you can use `EXTERNAL ID` as an additional layer of verification to ensure that access is only allowed when the request contains the preset `EXTERNAL ID`. This means that even if a third party knows some other access information (such as the role ARN), they cannot access the resource without the correct `EXTERNAL ID`.
  * During the API Connection process, Lakehouse will generate this EXTERNAL ID, which can be configured into the role verification of the COS account to achieve access control:
```
-- View EXTERNAL ID
DESC CONNECITON my_funciton_connection ;
```
![](.topwrite/assets/image_1740378621626.png)

  * Client side: Enter the Tencent Cloud **Access Management** console, **Role** -> **CzUDFRole** -> **Role Carrier** -> **Manage Carrier**, select **Add Account** -> select **Current Main Account**, and fill in the main account ID: `100029595716` (Singdata's Tencent Cloud main account), and check **Enable Verification**, enter the EXTERNAL\_ID from the previous DESC result, click **Confirm** -> **Update**

### Example 3: Create API CONNECTION on AWS

* **Environment Preparation**
  UDF relies on Alibaba Cloud's "[Object Storage](https://cn-north-1.console.amazonaws.cn/s3/get-started?region=cn-north-1\&bucketType=general)" and "[Lambda Function](https://cn-north-1.console.amazonaws.cn/lambda/home)" services. Please ensure that the relevant services are activated.

* step1: User activates Lambda and Object Storage services on the cloud

* step2: Create permission policy on AWS side (LakehouseAccess):
  * Log in to the AWS cloud platform and enter the **Identity and Access Management (IAM)** product console
  * In the IAM page's left navigation bar, go to **Account Settings**, in the **Security Token Service (STS)** section, find the **Endpoint** list, locate the region corresponding to the Singdata Lakehouse for the current instance, and if the **STS Status** is not enabled, please enable it.
  * In the IAM page's left navigation bar, go to **Policies**, in the **Policies** interface, select **Create Policy**, and choose Json in the policy editor.
  * Add the policy to allow Singdata Lakehouse to access the S3 bucket and directory. Below is a sample policy, please replace `<bucket>` with the actual bucket and path prefix name.
    ```JSON
    {
    	"Version": "2012-10-17",
    	"Statement": [
    		{
    			"Sid": "VisualEditor0",
    			"Effect": "Allow",
    			"Action": [
    				"lambda:CreateFunction",
    				"lambda:DeleteProvisionedConcurrencyConfig",
    				"lambda:GetFunctionConfiguration",
    				"lambda:ListProvisionedConcurrencyConfigs",
    				"lambda:GetProvisionedConcurrencyConfig",
    				"lambda:ListLayers",
    				"lambda:ListLayerVersions",
    				"lambda:DeleteFunction",
    				"lambda:GetAlias",
    				"lambda:ListCodeSigningConfigs",
    				"lambda:UpdateFunctionEventInvokeConfig",
    				"lambda:DeleteFunctionCodeSigningConfig",
    				"lambda:ListFunctions",
    				"lambda:GetEventSourceMapping",
    				"lambda:InvokeFunction",
    				"lambda:ListAliases",
    				"lambda:GetFunctionCodeSigningConfig",
    				"lambda:UpdateAlias",
    				"lambda:UpdateFunctionCode",
    				"lambda:ListFunctionEventInvokeConfigs",
    				"lambda:ListFunctionsByCodeSigningConfig",
    				"lambda:GetFunctionConcurrency",
    				"lambda:PutProvisionedConcurrencyConfig",
    				"lambda:ListEventSourceMappings",
    				"lambda:PublishVersion",
    				"lambda:DeleteEventSourceMapping",
    				"lambda:CreateAlias",
    				"lambda:ListVersionsByFunction",
    				"lambda:GetLayerVersion",
    				"lambda:PublishLayerVersion",
    				"lambda:InvokeAsync",
    				"lambda:GetAccountSettings",
    				"lambda:CreateEventSourceMapping",
    				"lambda:GetLayerVersionPolicy",
    				"lambda:PutFunctionConcurrency",
    				"lambda:DeleteCodeSigningConfig",
    				"lambda:ListTags",
    				"lambda:DeleteLayerVersion",
    				"lambda:PutFunctionEventInvokeConfig",
    				"lambda:DeleteFunctionEventInvokeConfig",
    				"lambda:CreateCodeSigningConfig",
    				"lambda:PutFunctionCodeSigningConfig",
    				"lambda:UpdateEventSourceMapping",
    				"lambda:UpdateFunctionCodeSigningConfig",
    				"lambda:GetFunction",
    				"lambda:UpdateFunctionConfiguration",
    				"lambda:UpdateCodeSigningConfig",
    				"lambda:GetFunctionEventInvokeConfig",
    				"lambda:DeleteAlias",
    				"lambda:DeleteFunctionConcurrency",
    				"lambda:GetCodeSigningConfig",
    				"lambda:GetPolicy"
    			],
    			"Resource": "*"
    		},
    		{
    			"Sid": "VisualEditor1",
    			"Effect": "Allow",
    			"Action": [
    				"s3:PutObject",
    				"s3:GetObject",
    				"s3:DeleteObjectVersion",
    				"s3:ListBucket",
    				"s3:DeleteObject",
    				"s3:GetBucketLocation",
    				"s3:GetObjectVersion"
    			],
    			"Resource": "arn:aws-cn:s3:::cz-udf-code"
    		}
    	]
    }
    ```
* Select Next, enter the policy name (e.g., LakehouseAccess) and description (optional)
  * Click Create Policy to complete the policy creation

step3: Create a role on the AWS side (LakehouseVolumeRole):

* Log in to the AWS cloud platform and go to the **Identity and Access Management (IAM)** product console
* In the IAM page's left navigation bar, go to **Roles** -> **Create role** -> **AWS account**, select **Another AWS account**, and enter `028022243208` in the Account ID

> Note: To prevent the ROLE\_ARN from being obtained by third parties for unauthorized data access, you can check **Options** and select **Require external ID (best time for third party to assume this role)**. After checking, you can fill in `000000` as a placeholder in the **EXTERNAL ID** field to be filled in later. `EXTERNAL ID` serves as an additional verification layer, ensuring that access is only allowed when the request includes the preset `EXTERNAL ID`. This means that even if a third party knows some other access information (such as the role ARN), they cannot access the resources without the correct `EXTERNAL ID`.

![](.topwrite/assets/image_1740379714725.png)

* Select Next, on the Add permissions page, choose the policy created in step2 `LakehouseAccess`, then select Next
* Fill in the Role name (e.g., `LakehouseVolumeRole`) and description, click **Create role** to complete the role creation
* On the role details page, obtain the value of **Role ARN** to create the STORAGE CONNECTION

![](.topwrite/assets/image_1740379729037.png)



step4: Create an API CONNECTION on the Singdata Lakehouse side:

* Execute the following commands in Studio or the Lakehouse JDBC client:
```
CREATE API CONNECTION udf_noah 
    TYPE cloud_function
    PROVIDER = 'aws'
    REGION = 'cn-north-1'
    ROLE_ARN = 'arn:aws-cn:iam::028022243208:role/CzUdfRole'
    CODE_BUCKET = 'cz-udf-code'
    NAMESPACE = 'default';
```
* During the process of creating a storage connection, Lakehouse will generate this EXTERNAL ID. You can configure this EXTERNAL ID into the Trust Policy of the AWS IAM role (`LakehouseVolumeRole`) created in step 3 to achieve additional access control:
```
-- View EXTERNAL ID 
DESC CONNECTION udf_noah ;
```
![](.topwrite/assets/image_1740379856735.png)

* In the AWS IAM console, navigate to **Roles** in the left sidebar, find the role created in step 3 and enter the role details page. In **Trust relationships**, replace the value of `sts:ExternalId` `000000` with the `EXTERNAL_ID` from the DESC result. Click **Update** to complete the role policy update.