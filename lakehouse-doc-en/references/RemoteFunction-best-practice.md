# Usage Guide: External Function (Remote Function)

## Document Objective

Through this usage guide, you will be able to:

* Call an offline Java NLP model (see [GitHub](https://github.com/Ruthwik/Sentiment-Analysis)) to analyze the sentiment of strings in Singdata Lakehouse tables
* Call Alibaba Cloud Vision Intelligence Open Platform services (see [documentation](https://help.aliyun.com/document_detail/203520.htm?spm=a2c4g.601126.0.0.39de5a4eqBtLaC)) to parse image data pointed to by URLs in Singdata Lakehouse tables

(The environment used in this Best Practices guide is Singdata Lakehouse based on Alibaba Cloud.)

## Operation Steps

### Step 0: Preparation (Authorization)

The goal of this step is to allow the Singdata Lakehouse cluster to access the customer's Alibaba Cloud Function Compute (FC) and Object Storage Service (OSS). To accomplish this, you need to create a Role and let Singdata Lakehouse assume this Role to access Alibaba Cloud FC and OSS services.

#### 1. Alibaba Cloud Console: Create a Permission Policy (e.g., CzUdfOssAccess) in Alibaba Cloud **Access Control** (RAM):

* Go to the Alibaba Cloud RAM Console.
* In the left navigation bar, go to **Permission Management** -> **Permission Control**. On the **Permission Control** page, click **Create Permission Policy**.
* On the **Create Permission Policy** page, select the **Script Edit** tab (replace the bucket name inside `[]` below).

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

#### 2. Alibaba Cloud Console: Create a Role in Alibaba Cloud RAM (e.g., CzUDFRole):

* In the RAM Console left navigation bar, go to **Identity Management** -> **Roles**, then click **Create Role**.
* On the **Create Role** page, select the type as **Alibaba Cloud Account**. In the role configuration, enter a custom **Role Name** (e.g., CzUDFRole). Under **Select Trusted Cloud Account**, select **Other Cloud Account** and enter: 1384322691904283 (the Singdata Lakehouse Shanghai primary cloud account), then click **Finish**.
* Edit the **AliyunFCFullAccess permission policy** and add the `"acs:Service": "fc.aliyuncs.com"` section below.

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

* After creation, click **Grant Permissions for Role**:
* Under **System Policies**, grant the **AliyunFCFullAccess** policy to the role CzUDFRole.
* Under **Custom Policies**, grant the policy just created (**CzUdfOssAccess**) to the role.

#### 3. On the CzUDFRole detail page, obtain the RoleARN for this role:

* Modify the **Trust Policy** of CzUDFRole:

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

### Scenario 1: Call a Java NLP Offline Model

#### 1. Write the Code

* Write a UDF based on the Hive UDF API. The following is sample code implementing uppercase conversion:

```Java
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

* Compile the code to generate a JAR package and other dependency files, then package them into a ZIP archive.

#### 2. Upload the Function Package to the Specified Path

For example: `oss://hz-oss-lakehouse/functions/sentiment/UDF_code/SentimentAnalysis.zip`

Main class: `com.singdata.nlp.GenericUDFSentiment`

There are two ways to upload the file to the specified path:

* Upload directly via the OSS client.
* Use the [PUT command](put.md) in the Lakehouse JDBC client (PUT command via Lakehouse Web UI is not supported) to upload the package to a [Volume object](datalake_volume.md), and reference the Volume path in the function creation DDL. For example:

```SQL
-- Upload a file to a Volume named fc_volume:
PUT ./SentimentAnalysis.zip to volume fc_volume/udfs/SentimentAnalysis.zip;

-- Reference the Volume path when creating the function:
create external function public.sentiment_demo_hz
    AS 'com.singdata.nlp.GenericUDFSentiment' 
    USING ARCHIVE 'volume://fc_volume/udfs/SentimentAnalysis.zip' 
    CONNECTION udf_sentiment_bj
    WITH
    PROPERTIES (
        'remote.udf.api' = 'java8.hive2.v0'
);

```

You can also specify an internal volume. Although you can use an internal volume, the `code_bucket` parameter in the API CONNECTION creation must be filled with an external address.

* **User Volume format address**: `volume:user://~/upper.jar`
  * `user` indicates the User Volume protocol.

  * `~` indicates the current user, a fixed value.

  * `upper.jar` is the target filename.
* **Table Volume format address**: `volume:table://table_name/upper.jar`
  * `table` indicates the Table Volume protocol.
  * `table_name` is the table name; fill in the actual name.
  * `upper.jar` is the target filename.

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

**Parameter descriptions**:

1. **api_connection**: Creates an API-type Connection for calling third-party service interfaces.

2. **type**: Connection type is cloud function: `cloud_function`. Specific properties include:

* provider: Cloud function provider, e.g., `aliyun`
* region: Region where the cloud function is located, e.g., `cn-shanghai`
* role\_arn: The Role assumed when creating the cloud function, e.g., `acs:ram::12228000000000000:role/czudfrole`
* code\_bucket: The object storage bucket name where the cloud function program files are located

#### 4. Create an External Function in Lakehouse

```SQL
create external function public.sentiment_demo_hz 
as 'com.singdata.nlp.GenericUDFSentiment' 
using archive 'oss://hz-oss-lakehouse/functions/sentiment/UDF_code/SentimentAnalysis.zip'
connection udf_sentiment_hz 
with properties ( 
 'remote.udf.api' = 'java8.hive2.v0'
);
```

**Parameter descriptions**:

1. **as**: Followed by the main class name of the Java function.
2. **using**: Only compiled Java programs are supported. Must be followed by the parameter **archive** (indicating the package is a ZIP-format file) or **jar** (indicating a Java JAR file). You can reference the OSS path of the file directly; if the file has been uploaded to a [Volume object](datalake_volume.md) via the [PUT command](put.md), you can also reference the function file via the Volume path, e.g., `USING ARCHIVE 'volume://fc_volume/udfs/SentimentAnalysis.zip'`
3. **connection**: The connection object used in the program, e.g., `udf_sentiment_bj`. Properties:

* remote.udf.api: For Java UDFs, fill in `java8.hive2.v0`

#### 5. Run Sentiment Analysis

**Construct test data**:

```SQL
create table tbl_wisdom_nlp(id int, qoute string);

insert into tbl_wisdom_nlp values(1,"Honesty and diligence should be your eternal mates");
insert into tbl_wisdom_nlp values(2,"If a man deceives me once, shame on him; if twice,shame on me");
insert into tbl_wisdom_nlp values(3,"I am so damn happy");
insert into tbl_wisdom_nlp values(4,"Today is Sunday");
insert into tbl_wisdom_nlp values(5,"Today is Monday");
```

**Run sentiment analysis**:

```SQL
set cz.sql.remote.udf.enabled = true;
select qoute, public.sentiment_demo(qoute) as sentiment from tbl_wisdom_nlp;
```

## Scenario 2: Python UDF — Call a Third-Party Visual Processing Platform API for Image Parsing

#### 1. Code file: video\_contents.py

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
```

import sys:

```Python
```

to_text = image_to_text():

```Python
```

for url in sys.argv[1:]:

```Python
```

print(f"{to_text.evaluate(url)}"):

```Python
```

#### 2. Reuse the connection from *Scenario 1*

#### 3. Create a New External Function

```SQL
create external function public.image_to_text
as 'video_contents.image_to_text'    # script name + class name
using archive 'oss://derek-bj-oss/bj_remote_udf/image_to_text/image_to_text.zip'
connection udf_sentiment_bj2
with properties (
 'remote.udf.api' = 'python3.mc.v0'
);
```

**Parameter descriptions**:

1. `as` is followed by the Python module name + main class name. If the main program file is `video_contents.py` and the main class name is `image_to_text`, the parameter after `as` is `'video_contents.image_to_text'`.
2. **using archive / file**: Python files must be packaged as a ZIP-format file; single-file scripts are also supported using the `file` parameter.

* **connection**: The connection object used in the program, e.g., `udf_sentiment_bj`. Properties:

  * remote.udf.api: For Python language functions, fill in `python3.mc.v0`

#### 4. Create Test Data to Verify

Import the following 4 images into OSS, generate public URLs, and store them in a Lakehouse table. You can use the following SQL directly to construct the test table:

```SQL
create table tbl_images(id int, url string);

insert into tbl_images values(1,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood1.jpg');
insert into tbl_images values(2,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood2.jpg');
insert into tbl_images values(3,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood3.jpg');
insert into tbl_images values(4,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood4.jpg');
```

Run the query:

```SQL
set cz.sql.remote.udf.enabled = true;
select id, public.image_to_text(url) from tbl_images;
```

***
