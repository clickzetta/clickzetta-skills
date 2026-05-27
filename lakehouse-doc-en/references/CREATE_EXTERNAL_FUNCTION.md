# CREATE EXTERNAL FUNCTION

Create a new external function. EXTERNAL FUNCTION (REMOTE FUNCTION) is a custom function (UDF) created in Singdata Lakehouse using Python & Java languages, executed through remote services (supported remote services include: Alibaba Cloud Function Compute FC, Tencent Cloud Function Service, and AWS Lambda Service). JAVA supports UDF, UDAF, and UDTF.

## EXTERNAL FUNCTION Creation Main Process
* Users activate cloud function compute services (such as Alibaba Cloud Function Compute FC) and object storage services
* Package the function execution code & executable files, dependent libraries, models, and data files, and upload them to object storage
* Grant Singdata Lakehouse permission to operate the above services and access function files
* Users execute connection and external function DDL to generate UDF, and use it in queries
* Users call Remote function in Singdata Lakehouse SQL statements
* Singdata Lakehouse sends an HTTP request to call the running function based on the provided service address and authentication information
* Singdata Lakehouse retrieves the response information and returns the result
## EXTERNAL FUNCTION Advantages
* Remote Function can be used to call external rich data processing capabilities, supplementing the traditional SQL computing model. For example, it can call large language models (LLM), images, audio, and video, supplementing SQL's unstructured data processing capabilities
* It can directly access external networks, not constrained by Singdata Lakehouse network
## Syntax
```SQL
CREATE EXTERNAL FUNCTION [ IF NOT EXISTS] [schema_name.]<function_name>
AS class_name
USING { FILE|JAR|ARCHIVE  resource_uri,...}
CONNECTION api_connection_name
[WITH]
PROPERTIES (
    'remote.udf.api' = 'python3.mc.v0',
    'remote.udf.protocol' = 'http.arrow.v0'
    'retry_timeout' = <num>,
    'max_batch_rows' = <num>
    ...
)
[COMMENT '']
```
## Parameter Description

### Required Parameters

* FUNCTION\_NAME: Specifies the name of the function.
* CLASS\_NAME: For JAVA functions, it is the main class name of the JAVA function; for Python functions, it is a combination of the main class name and module name. For example, if the main program file is video\_contents.py and the main class name is image\_to\_text, the parameter after AS would be `'video_contents.image_to_text'`.
* CONNECTION: Specifies the authentication information for connecting to function computation. For details, please refer to [Create Connection](CREATECONNECTION.md).
* RESOURCE\_URI: Resource connection, referring to the resource files required for UDF operation. The OSS file address must be specified, and the authentication information of the connection must have read permission for the file.

### Optional Parameters

* IF NOT EXISTS: If the specified function already exists, the command will not make any changes and will return a message indicating that the function exists. If not specified, an error message will be returned if the function exists.
* function\_parameter: Type inference will be performed when using Hive UDF, so it can be omitted.
* RETURNS: Type inference will be performed when using Hive UDF, so it can be omitted.
* COMMENT: Specifies the comment information.
* PROPERTIES: Specifies the parameter information of the function.

  * 'remote.udf.api': Specifies the runtime compilation environment, with a default value compatible with Hive 2.
  * 'retry_timeout': Specifies the timeout period for connecting to function computation.
  * 'max_batch_rows': Specifies the maximum number of rows for batch processing.

## Notes

* The process of creating an external function requires reading the function code or executable file, which may take a long time.
* This command does not require starting a VC, so it does not consume CRU.
* Currently, only Java and Python programming languages are supported. Supported runtime environments: Java 8 and Python 3.10 versions.
# Development Guide
- [Create API CONNECTION](<create-api-connection.md>)
- [Java Code Development Guide for External Function](<ExternalFunctionDevGuideJava.md>)
- [Python Language Development Guide for External Function](<RemoteFunctionDevGuidePython3.md>)
# Usage Example
## Create EXTERNAL FUNCTION on Alibaba Cloud
* **Environment Preparation**
  UDF relies on Alibaba Cloud's "[Object Storage](https://oss.console.aliyun.com/overview)" and "[Function Compute](https://fcnext.console.aliyun.com/overview)" services. Please ensure that the relevant services are activated.

* step1: Users activate the cloud function compute service (such as Alibaba Cloud's Function Compute FC) and object storage service.

* step2. Operations on the Alibaba Cloud side: Create a permission policy (CzUdfOssAccess) in the Alibaba Cloud RAM console: Note: The user needs to have RAM permissions.
  * Access the Alibaba Cloud Access Control (RAM) [Product Console](https://ram.console.aliyun.com/policies)
  * In the left navigation bar, **Permission Management** -> **Permission Policy**, in the permission control interface, search for **AliyunFCFullAccess** -> edit the **AliyunFCFullAccess** permission policy to add the following "acs\*\*:**Service**": "**fc.aliyuncs.com**"\*\* part.
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
  * On the **Create Permission Policy** page, select the **Script Editing** tab, and replace `[bucket_name_1|2|3]` below with the actual OSS bucket names. Note: According to Alibaba Cloud OSS conventions, the same bucket needs to have two Resource entries: `"acs:oss:*:*:bucket_name_1"` and `"acs:oss:*:*:bucket_name_1/*"` to achieve the authorization effect:
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
  * On the **Create Role** page, select the type as **Alibaba Cloud Account**, fill in the custom **Role Name** (e.g., CzUDFRole), in the **Select Trusted Cloud Account** section, choose **Other Cloud Account**, and enter: 1384322691904283 (Singdata Lakehouse Shanghai's cloud main account), then click **Complete**
  * After creation, click **Authorize Role**:
  * In **System Policies**, grant the **AliyunFCFullAccess** policy to the role CzUDFRole
  * In **Custom Policies**, grant the newly created policy (**CzUdfOssAccess**) to the role

* step5: After creation, click **Authorize Role**: In **Custom Policies**, grant the newly created policy (CzUdfOssAccess) to the role. In the role CzUDFRole details page, obtain the RoleARN information for this role: `'acs:ram::1222808864xxxxxxx:role/czudfrole'`![](.topwrite/assets/image_1740368644886.png)

* step6: Fill the above role\_arn into the syntax parameter to create an Alibaba Cloud Function Compute connection
```SQL
CREATE API CONNECTION my_function_connection
TYPE CLOUD_FUNCTION
PROVIDER='aliyun'
REGION='cn-hangzhou'
ROLE_ARN='acs:ram::1757168149572678:role/czudfrole'
CODE_BUCKET='function-compute-my1';
```
* step7: desc connection to obtain external ID information: In this instance, the external ID is: `VW9UaGwYENBQ7cFp`
  ```
  DESC CONNECTION my_function_connection;
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
STEP8: Write UDF based on Hive UDF API, here is an example code for case conversion:
```java
package com.example;

import org.apache.hadoop.hive.ql.exec.UDFArgumentException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDF;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector.PrimitiveCategory;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;

import java.util.Locale;

public class GenericUdfUpper extends GenericUDF {
  @Override
  public ObjectInspector initialize(ObjectInspector[] arguments) throws UDFArgumentException {
    checkArgsSize(arguments, 1, 1);
    checkArgPrimitive(arguments, 0);
    if (((PrimitiveObjectInspector) arguments[0]).getPrimitiveCategory() != PrimitiveCategory.STRING) {
      throw new UDFArgumentException("argument 0 requires to be string rather than " + arguments[0].getTypeName());
    }
    return PrimitiveObjectInspectorFactory.javaStringObjectInspector;
  }

  @Override
  public Object evaluate(DeferredObject[] arguments) throws HiveException {
    Object arg = arguments[0].get();
    if (arg == null) {
      return null;
    }
    return ((String) arg).toUpperCase(Locale.ROOT);
  }

  @Override
  public String getDisplayString(String[] children) {
    return "upper";
  }
}
```
Compile the code to generate a Jar package and other dependency files, and package them into a zip archive

step9: Upload the function package to the specified path
For example: `oss://hz-oss-lakehouse/functions/sentiment/UDF_code/my_upper.zip`
Function main class: `com.clickzetta.my_upper`
There are two ways to upload files to the specified path:
* Directly upload via OSS client
* Use the [PUT command](PUT.md) to upload the package to the [Volume object](datalake_volume.md) via the Lakehouse JDBC client (Lakehouse Web UI does not support using the PUT command), and reference the volume path and the API CONNECTION created above in the function DDL creation. For example:
```
-- Upload file to the Volume object named fc_volume:
PUT ./my_upper.zip to volume fc_volume/udfs/my_upper.zip;
-- Reference the Volume path when creating the function:
create external function public.my_upper
    AS 'com.clickzetta.my_upper' 
    USING ARCHIVE 'volume://fc_volume/udfs/my_upper.zip' 
    CONNECTION my_function_connection
    WITH
    PROPERTIES (
        'remote.udf.api' = 'java8.hive2.v0'
);
```
STEP10: Using Functions
```
select public.my_upper('a');
```