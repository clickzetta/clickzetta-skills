# Usage Workflow: External Function

## Document Objective:

Through this usage workflow, you can achieve:

* Invoke a JAVA NLP offline model (see [website](https://github.com/Ruthwik/Sentiment-Analysis)) to parse the sentiment of strings in Singdata Lakehouse tables
* Invoke Alibaba Cloud Visual Intelligence Open Platform services (see [website](https://help.aliyun.com/document_detail/203520.htm?spm=a2c4g.601126.0.0.39de5a4eqBtLaC)) to parse image data pointed to by URLs in Singdata Lakehouse tables

(This best practice uses an Alibaba Cloud-based Singdata Lakehouse environment.)

## Operation Steps:

### Step0: Preparation (Authorization Operations)

The goal of this step is to allow the Singdata Lakehouse cluster to access the customer's Function Compute (FC) and Object Storage Service (OSS) on Alibaba Cloud. To achieve this, you need to create a role so that Singdata Lakehouse can assume this role to access FC and OSS services on Alibaba Cloud.

#### 1. Alibaba Cloud Console: Create a permission policy (e.g., CzUdfOssAccess) in the Alibaba Cloud **Resource Access Management** (RAM) console:

* Enter the Alibaba Cloud RAM console
* In the left navigation bar: **Permissions** -> **Policies**, on the **Policies** page, select **Create Policy**
* On the **Create Policy** page, select the **Script Editor** tab (replace the bucket name in the brackets [] below).

```JSON
{
    "Version": "1",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "oss:GetObject",
                "oss:PutObject",
                "oss:DeleteObject"
            ],
            "Resource": [
                "acs:oss:*:*: [bucket_name]/*",
                "acs:oss:*:*:[bucket_name]/*"
            ]
        }
    ]
}
```

^

#### 2. Alibaba Cloud Console: Create a role in Alibaba Cloud RAM (e.g., CzUDFRole):

* In the RAM console left navigation bar: **Identities** -> **Roles**, click **Create Role**
* On the **Create Role** page, select the type as **Alibaba Cloud Account**, fill in a custom **Role Name** (e.g., CzUDFRole) in the role configuration, choose **Other Cloud Account** under **Select Trusted Cloud Account**, and enter: 1384322691904283 (the Singdata Lakehouse Shanghai main cloud account), click **Finish**.
* Edit the **AliyunFCFullAccess Permission Policy**, adding the "acs:Service": "fc.aliyuncs.com" section below.

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

* After creation, click **Grant Permission to Role**:
* Under **System Policies**, grant the **AliyunFCFullAccess** policy to the role CzUDFRole.
* Under **Custom Policies**, grant the newly created policy (**CzUdfOssAccess**) to this role.

#### 3. Obtain the RoleARN information for the role CzUDFRole from its details page:

* Modify CzUDFRole's **Trust Policy**:

```json
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "RAM": [
          "acs:ram::1384322691904283:root"
        ],
        "Service": [
          "fc.aliyuncs.com"
        ]
      }
    }
  ],
  "Version": "1"
}
```

***

### Scenario 1: Invoking the JAVA NLP Offline Model:

#### &#x20;1. Write Code

* Write a UDF based on the Hive UDF API. Below is sample code for implementing case conversion:

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

* Compile the code to generate a Jar package and other dependency files, then package them into a zip archive.

#### 2. Upload Function Package to the Specified Path

For example: `oss://hz-oss-lakehouse/functions/sentiment/UDF_code/SentimentAnalysis.zip`

Main function class: `com.clickzetta.nlp.GenericUDFSentiment`

There are two ways to upload files to the specified path:

* Upload directly via an OSS client
* In the Lakehouse JDBC client (the Lakehouse Web UI does not support file uploads via the PUT command), upload the package to a [Volume object](datalake_volume.md) using the [PUT command](PUT.md), and reference the volume path in the function creation DDL. For example:

```
-- Upload file to a Volume object named fc_volume:
PUT ./SentimentAnalysis.zip to volume fc_volume/udfs/SentimentAnalysis.zip;

-- Reference the Volume path when creating the function:
create external function public.sentiment_demo_hz
    AS 'com.clickzetta.nlp.GenericUDFSentiment' 
    USING ARCHIVE 'volume://fc_volume/udfs/SentimentAnalysis.zip' 
    CONNECTION udf_sentiment_bj
    WITH
    PROPERTIES (
        'remote.udf.api' = 'java8.hive2.v0'
);

```

You can also specify an internal volume. Although you can use an internal volume, the code_bucket parameter in the API CONNECTION creation must be filled with an external address.

* **User Volume address format**: `volume:user://~/upper.jar`
  * `user` indicates using the User Volume protocol.

  * `~` represents the current user and is a fixed value.

  * `upper.jar` represents the target file name.
* **Table Volume address format**: `volume:table://table_name/upper.jar`
  * `table` indicates using the Table Volume protocol.
  * `table_name` represents the table name and should be filled in based on the actual situation.
  * `upper.jar` represents the target file name.

#### 3. Create a Connection

```SQL
create api connection udf_sentiment_bj
type cloud_function 
provider = 'aliyun'
region = 'cn-beijing'
role_arn = 'acs:ram::1222808864467016:role/czudfrole'
namespace = 'default'
code_bucket = 'derek-bj-oss';
```

**Parameter Explanation**:

1. **api_connection**: Creates an API-type Connection for invoking third-party service interfaces;

2. **type**: The connection type is cloud function: cloud\_function, where the specific properties are:

* provider: The cloud function provider, e.g., aliyun
* region: The region where the cloud function is located, e.g., 'cn-shanghai'
* role\_arn: The role assumed when creating the cloud function, e.g., acs\:ram::12228000000000000\:role/czudfrole
* code\_bucket: The object storage bucket name where the cloud function program files are located

#### 4. Create External Function in Lakehouse

```SQL
create external function public.sentiment_demo_hz 
as 'com.clickzetta.nlp.GenericUDFSentiment' 
using archive 'oss://hz-oss-lakehouse/functions/sentiment/UDF_code/SentimentAnalysis.zip'
connection udf_sentiment_hz 
with properties ( 
 'remote.udf.api' = 'java8.hive2.v0'
);
```

**Parameter Explanation**:

1. **as**: Followed by the main class name of the Java function
2. **using**: Only supports compiled Java programs. The parameter **archive** indicates the package is a zip-format file; **jar** indicates a Java Jar package file. You can directly reference the file's OSS path; if the file has been uploaded to a [Volume object](datalake_volume.md) via the [PUT command](PUT.md), you can also directly reference the function file via the Volume path, for example: `USING ARCHIVE 'volume://fc_volume/udfs/SentimentAnalysis.zip' `
3. **connection**: Represents the connection object used in the program, e.g., udf\_sentiment\_bj; with the following property:

* remote.udf.api: For Java UDF, fill in java8.hive2.v0

#### 5. Execute Semantic Sentiment Analysis:

**Construct Test Data**:

```SQL
create table tbl_wisdom_nlp(id int, qoute string);

insert into tbl_wisdom_nlp values(1,"Honesty and diligence should be your eternal mates");
insert into tbl_wisdom_nlp values(2,"If a man deceives me once, shame on him; if twice,shame on me");
insert into tbl_wisdom_nlp values(3,"I am so damn happy");
insert into tbl_wisdom_nlp values(4,"Today is Sunday");
insert into tbl_wisdom_nlp values(5,"Today is Monday");
```

**Execute Semantic Analysis**:

```SQL
set cz.sql.remote.udf.enabled = true;
select qoute, public.sentiment_demo(qoute) as sentiment from tbl_wisdom_nlp;
```

## Scenario 2: Python UDF: Invoking Third-Party Vision Processing Platform API for Image Recognition

#### 1. Code file is video\_contents.py:

```Python
from alibabacloud_imagerecog20190930.client import Client
from alibabacloud_imagerecog20190930.models import RecognizeFoodRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions

from cz.udf import annotate

@annotate("string->string")
class image_to_text(object):

    def evaluate(self,url):
        if url is None:
            return None
        try:
            config = Config(
                access_key_id='xxxxx',
                access_key_secret='xxxxxxxx',
                endpoint='imagerecog.cn-shanghai.aliyuncs.com',
                region_id='cn-shanghai'
            )
            # Initialize a request and set parameters
            
            client = Client(config)
            recognize_food_request = RecognizeFoodRequest(image_url=url)
            runtime = RuntimeOptions()
            response = client.recognize_food_with_options(recognize_food_request, runtime)

            if len(str(response.body)) >= 1:
                return str(response.body)
            else:
                return ""
        except Exception as exc:
            return "[error] " + exc.__str__()
        finally:
            pass

#if __name__ == "__main__":
#   import sys
#    to_text = image_to_text()
#    for url in sys.argv[1:]:
#        print(f"{to_text.evaluate(url)}")
```

#### 2. Reuse the connection from Scenario 1

#### 3. Create a New External Function

```SQL
create external function public.image_to_text
as 'video_contents.image_to_text'    # Script name + class name
using archive 'oss://derek-bj-oss/bj_remote_udf/image_to_text/image_to_text.zip'
connection udf_sentiment_bj2
with properties (
 'remote.udf.api' = 'python3.mc.v0'
);
```

**Parameter Explanation**:

1. After **AS**, specify the Python module name + main class name. For example, if the main program file is video\_contents.py and the main class name is image\_to\_text, the parameter after AS is `'video_contents.image_to_text'`
2. **using archive / file**: Python files must be packaged into a zip file; single-file scripts are also supported, specified using the file parameter

* **connection**: Represents the connection object used in the program, e.g., udf\_sentiment\_bj; with the following property:

  * remote.udf.api: For Python language functions, fill in python3.mc.v0

#### 4. Create Test Data for Verification

Import the following 4 images into OSS and generate public URLs stored in the Lakehouse table. You can directly construct the test table using the following SQL:

```SQL
create table tbl_images(id int, url string);

insert into tbl_images values(1,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood1.jpg');
insert into tbl_images values(2,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood2.jpg');
insert into tbl_images values(3,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood3.jpg');
insert into tbl_images values(4,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood4.jpg');
```

Execute the query:

```SQL
set cz.sql.remote.udf.enabled = true;
select id, public.image_to_text(url) from tbl_images;
```

***

^
