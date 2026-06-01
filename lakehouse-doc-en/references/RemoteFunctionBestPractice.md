# Usage Process: External Function

## Document Objective:

Through this usage process, you can achieve:

* Call the offline model of JAVA NLP (see [URL](https://github.com/Ruthwik/Sentiment-Analysis)) to analyze the sentiment of strings in the Singdata Lakehouse table
* Call the Alibaba Cloud Vision Intelligence Open Platform service (see [URL](https://help.aliyun.com/document_detail/203520.htm?spm=a2c4g.601126.0.0.39de5a4eqBtLaC)) to analyze the image data pointed to by the URL in the Singdata Lakehouse table

(This best practice environment is based on Alibaba Cloud's Singdata Lakehouse)

## Operation Steps:

### Step0: Preparation (Authorization Operation)

The goal of this step is to allow the Singdata Lakehouse cluster to access the customer's Alibaba Cloud Function Compute (FC) and Object Storage Service (OSS). To achieve this goal, a role needs to be created, allowing the Singdata Lakehouse to assume this role to access the Function Compute (FC) and OSS services on Alibaba Cloud.

#### 1. Alibaba Cloud Console: Create a permission policy in the **Access Control** (RAM) of the Alibaba Cloud console (e.g., CzUdfOssAccess):

* Enter the Alibaba Cloud RAM console
* Left navigation bar **Permission Management** -> **Permission Control**, select **Create Permission Policy** on the **Permission Control** interface
* On the **Create Permission Policy** page, select the **Script Editing** tab (replace the bucket name in the brackets below)

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

* In the RAM console left navigation bar, go to **Identity Management** -> **Roles**, and click **Create Role**
* On the **Create Role** page, select the type as **Alibaba Cloud Account**, fill in the custom **Role Name** (e.g., CzUDFRole), in the **Select Trusted Cloud Account** section, choose **Other Cloud Account**, and enter: 1384322691904283 (Singdata Lakehouse Shanghai's main cloud account), then click **Complete**
* Edit the **AliyunFCFullAccess** permission policy to add the following "acs\*\*:**Service**": "**fc.aliyuncs.com**"\*\* part

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

* After creation, click **Authorize for Role**:
* In **System Policies**, grant the **AliyunFCFullAccess** policy to the role CzUDFRole
* In **Custom Policies**, grant the newly created policy (**CzUdfOssAccess**) to the role

#### 3. On the CzUDFRole details page, obtain the RoleARN information for this role:&#x20;

* Modify the **Trust Policy** of CzUDFRole:

```Python
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

### Scenario 1: Calling JAVA NLP Offline Model:

#### &#x20;1. Write Code

* Write UDF based on Hive UDF API, here is an example code for case conversion:

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

* Compile the code to generate a Jar package and other dependency files, and package them into a zip archive

#### 2. Upload the function package to the specified path

For example: `oss://hz-oss-lakehouse/functions/sentiment/UDF_code/SentimentAnalysis.zip`

Main function class: `com.clickzetta.nlp.GenericUDFSentiment`

There are two methods to upload files to the specified path:

* Directly upload via the OSS client
* Use the [PUT command](put.md) in the Lakehouse JDBC client (Lakehouse Web UI does not support using the PUT command) to upload the package to the [Volume object](datalake_volume.md), and reference the volume path in the function creation DDL. For example:

```
-- Upload the file to the Volume object named fc_volume:
PUT ./SentimentAnalysis.zip TO VOLUME fc_volume/udfs/SentimentAnalysis.zip;

-- Reference the Volume path when creating the function:
CREATE EXTERNAL FUNCTION public.sentiment_demo_hz
    AS 'com.clickzetta.nlp.GenericUDFSentiment' 
    USING ARCHIVE 'volume://fc_volume/udfs/SentimentAnalysis.zip' 
    CONNECTION udf_sentiment_bj
    WITH
    PROPERTIES (
        'remote.udf.api' = 'java8.hive2.v0'
);
```

#### 3. Create Connection (Connection)

```SQL
CREATE API CONNECTION udf_sentiment_bj
    TYPE CLOUD_FUNCTION 
    PROVIDER = 'aliyun'  
    REGION = 'cn-beijing'
    ROLE_ARN = 'acs:ram::1222808xxxxxxx:role/czudfrole'
    NAMESPACE = 'default'
    CODE_BUCKET = 'derek-bj-oss';
```

**Parameter Explanation**:

1. `API CONNECTION`: Create an API type Connection, allowing users to call third-party service interfaces;

2. `TYPE`: The connection type is cloud function: cloud\_function, with specific attributes as follows:

* `PROVIDER`: Cloud function provider, such as aliyun
* `REGION`: The region where the cloud function is located, such as 'cn-shanghai'
* `ROLE_ARN`: The role assumed when creating the cloud function, such as acs\:ram::12228000000000000\:role/czudfrole
* `CODE_BUCKET`: The name of the object storage bucket where the cloud function program files are located

#### 4. Create External Function in Lakehouse

```SQL
CREATE EXTERNAL FUNCTION public.sentiment_demo_hz 
AS 'com.clickzetta.nlp.GenericUDFSentiment' 
USING ARCHIVE 'oss://hz-oss-lakehouse/functions/sentiment/UDF_code/SentimentAnalysis.zip'
CONNECTION udf_sentiment_hz 
WITH PROPERTIES ( 
    'remote.udf.api' = 'java8.hive2.v0'
);
```

**Parameter Explanation**:

1. `AS` is followed by the main class name of the Java function.
2. `USING`: Only supports compiled Java programs. The parameter： `ARCHIVE` indicates that the package is a zip file; `JAR` indicates that the Java program is a jar file. The file can be directly applied using the OSS path; if the file has been uploaded to the [Volume object](datalake_volume.md) via the [PUT command](put.md), the function file can also be directly referenced through the Volume path, for example: `USING ARCHIVE 'volume://fc_volume/udfs/SentimentAnalysis.zip'`
3. `CONNECTION`: Represents the connection object used in the program, such as udf\_sentiment\_bj; the attribute information:

* `remote.udf.api`: For Java UDF, please fill in `java8.hive2.v0`

#### 5. Execute Sentiment Analysis:

**Construct Test Data**:

```SQL
CREATE TABLE tbl_wisdom_nlp(id INT, qoute STRING);

INSERT INTO tbl_wisdom_nlp VALUES(1,'Honesty and diligence should be your eternal mates');
INSERT INTO tbl_wisdom_nlp VALUES(2,'If a man deceives me once, shame on him; if twice,shame on me');
INSERT INTO tbl_wisdom_nlp VALUES(3,'I am so damn happy');
INSERT INTO tbl_wisdom_nlp VALUES(4,'Today is Sunday');
INSERT INTO tbl_wisdom_nlp VALUES(5,'Today is Monday');
```

**Perform Semantic Analysis**：

```SQL
SET cz.sql.remote.udf.enabled = true;

SELECT qoute, public.sentiment_demo(qoute) AS sentiment 
FROM tbl_wisdom_nlp;
```

## Scenario 2: Python UDF: Call Third-Party Visual Processing Platform API for Image Parsing

#### 1. The code file is video\_contents.py:

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

#### 2. Reuse the connection from *Scenario One*

#### 3. Create a new External Function

```
CREATE EXTERNAL FUNCTION public.image_to_text
AS 'video_contents.image_to_text'    # Script name + Class name
USING ARCHIVE 'oss://derek-bj-oss/bj_remote_udf/image_to_text/image_to_text.zip'
CONNECTION udf_sentiment_bj2
WITH PROPERTIES (
    'remote.udf.api' = 'python3.mc.v0'   
);
```

**Parameter Explanation**:

1. The parameter after 'As' is the Python module name + main class name. For example, if the main program file is video\_contents.py and the main class name is image\_to\_text, the parameter after 'as' would be `'video_contents.image_to_text'`.
2. `USING ARCHIVE / FILE`: The py file needs to be packaged as a zip file representing the package; single file scripts are also supported, specified with the file parameter.

* `CONNECTION`: Represents the connection object used in the program, such as udf\_sentiment\_bj;

#### 4. Create Test Data for Verification

Import the following some images into OSS and generate public URLs to store in the Lakehouse table. You can directly use the following SQL to construct the test table:

```SQL
CREATE TABLE tbl_images(id INT, url STRING);

INSERT INTO tbl_images VALUES(1,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood1.jpg');
INSERT INTO tbl_images VALUES(2,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood2.jpg');
INSERT INTO tbl_images VALUES(3,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood3.jpg');
INSERT INTO tbl_images VALUES(4,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood4.jpg');
INSERT INTO tbl_images VALUES(5,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood5.jpg');
INSERT INTO tbl_images VALUES(6,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood6.jpg');
INSERT INTO tbl_images VALUES(7,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood7.jpg');
INSERT INTO tbl_images VALUES(8,'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood8.jpg');
```

```SQL
SET cz.sql.remote.udf.enabled = TRUE;

SELECT 
    id,
    url as food_images,
    public.image_to_text('dish_recognition', url) as food_recognition
FROM tbl_images;
```

***

![](.topwrite/assets/20250219-165248.jpeg)
