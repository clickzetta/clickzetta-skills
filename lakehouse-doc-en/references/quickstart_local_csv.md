# Quick Analysis of Local CSV Files

### **Objective**:

Through this document, you will be able to quickly analyze local CSV files using Lakehouse

### **Analyze CSV Format Files**:

#### **Data Preparation**:

This article uses the Brazilian e-commerce public dataset as an example. In the local path /User/Downloads/brazil-ecommerce on the client, there are the following CSV files:
```
-------------/User/Downloads/brazil-ecommerce ------------------ 
olist_customers_dataset.csv.gz 
olist_geolocation_dataset.csv.gz
olist_order_items_dataset.csv.gz 
olist_order_payments_dataset.csv.gz 
olist_order_reviews_dataset.csv.gz 
olist_orders_dataset.csv.gz
olist_products_dataset.csv.gz 
olist_sellers_dataset.csv.gz 
product_category_name_translation.csv.gz
```
Using the Lakehouse JDBC client SQLLine (or DBeaver / Datagrip, etc.) to upload data to the Lakehouse User volume space (restriction: single file must be smaller than 5G):

(USER VOLUME is the file storage space that is automatically enabled for the current user in the current workspace, no need to create it in advance)
```
--Execute in SQLline or any Lakehouse JDBC client to upload a single file: olist_customers_dataset.csv.gz

PUT '/User/Downloads/brazil-ecommerce/olist_customers_dataset.csv.gz' TO USER VOLUME SUBDIRECTORY 'bz_olist_data';
```
In the client tool, or in the Studio SQL task node, execute the following command to display the files that have been uploaded to the USER VOLUME:
```
show user volume directory like '%olist%';
```
#### **Quickly Analyze Data with Lakehouse SQL**

For example: Count the number of users in each state and sort in descending order by the number of users
```
SELECT count(1) as customer_number_by_state,
       customer_state,
FROM USER VOLUME (
    customer_id STRING,
    customer_unique_id STRING,
    customer_zip_code_prefix INT,
    customer_city STRING,
    customer_state STRING
 ) using csv Options
 (
     'sep' = ',',
     'compression'='gzip',  -- Currently supports zstd/gzip/zlib compression formats. Remove this parameter for no compression
     'header'='true'
 )
 FILES ('bz_olist_data/olist_customers_dataset.csv.gz')
group by customer_state
order by customer_number_by_state desc;
```
Options parameters:

* sep: Column separator, default is ",". Supports a maximum length of 1 character, for example: `'sep'=','`
* compression: Configures the file compression format. Supported compression formats are: gzip/zstd/zlib. For example: `'compression'='gzip'`
* header: Whether to parse the header, default is false. Boolean type, for example: `'header'='true'`

In addition, the following parameters are also supported:

* timeZone: Configures the time zone, no default value. Used to specify the time zone for the time format in the file. For example: `'timeZone' = 'Asia/Shanghai'`
* escape: Used to escape quotes within quoted values, default value is "\", for example: `'escape'='\'`
* lineSep: Line separator, default value is "\n". Supports a maximum length of 2 characters, for example: `'lineSep'='$'`
* quote: Sets a single character used to escape quote values. The default value is double quotes '"', for example: `'quote'='"'`

#### **Generate an internal table in the lakehouse**
```
CREATE TABLE OLIST_CUSTOMER_TBL
AS
SELECT * FROM USER VOLUME (
    customer_id STRING,
    customer_unique_id STRING,
    customer_zip_code_prefix INT,
    customer_city STRING,
    customer_state STRING
 ) using csv Options
 (
     'sep' = ',',
     'compression'='gzip',
     'header'='true'
 )
 FILES ('bz_olist_data/olist_customers_dataset.csv.gz');
```

^
