# Data Lake FAQ

#### **Question 1**: **After uploading a file to the Volume path using the PUT command, the file cannot be found during SQL processing**

**Answer**: If the file directory table was enabled when creating the Volume object (`DIRECTORY = (enable = TRUE)`), you need to manually synchronize this change to the Lakehouse metadata system after adding new files to the Volume path. You can use the command `alter volume xxxx refresh;` (the executor needs to have alter permission on the volume object: `GRANT ALTER ON VOLUME xxxx TO USER datalake_user;`)

^

#### **Question 2**: **Does the data lake Volume support CSV files in compressed format**

**Answer**: The current version does not support CSV files in compressed format, but it will be supported in future versions.

^

#### **Question 3: Error when querying CSV files**: **CZLH-00000:CZLH-71001: CZ**\_**SQL\_TIMEZONE should exist in context**;

**Answer**: You need to specify the default time zone in the query: add the option `'timeZone' = 'Asia/Shanghai'` in the options of the select statement querying the volume, for example:
```
select * from volume hz_csv_volume (
  order_id STRING,
  order_item_id INT,
  product_id STRING,
  seller_id STRING,
  shipping_limit_date TIMESTAMP,
  price DECIMAL(10,2),
  freight_value DECIMAL(10,2)
)using csv 
 options(
    'header'='true',
    'sep'=',',
    'timeZone' = 'Asia/Shanghai'
 ) files('brazil-ecommerce/olist_order_items_dataset.csv');
```
#### **Question 4**: **Error when executing remote function**: **CZLH-42000:\[1,8] Semantic analysis exception - function not found**

**Answer**: Possible reasons:

1. The function is a schema-level object. Please ensure that the correct schema information is included when executing the function. For example, the function `fc_orc_schema` belongs to the public schema, so the schema information must be included when referencing it: `public.fc_orc_schema()`
2. Currently, when executing a remote function, you need to include `set cz.sql.remote.udf.enabled=true;` before the SQL statement and execute them together.
```
set cz.sql.remote.udf.enabled = true;
SELECT public.fc_orc_schema('orc','<url>') as schema_orc;
```
####

#### **Question 5: Error when executing remote function**: **CZLH-XX000: failed** **to hook preExecute**: **urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'OpenSSL 1.1.0l 10 Sep 2019**'.

**Answer**: When handling file URL links in python code, there is an incompatibility between the urllib3 library version and the OpenSSL version. You can install version 1.26.9 of urllib3 instead: `pip3 install --upgrade urllib3==1.26.9 -t .`