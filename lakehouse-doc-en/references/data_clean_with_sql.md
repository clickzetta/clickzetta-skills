# Writing SQL for Data Cleaning

In the process of data analysis and data mining, data cleaning and preprocessing are crucial steps. This article will introduce various commonly used Lakehouse SQL data cleaning methods to help you better understand and apply these methods.

## Setting Up the Environment

Navigate to Lakehouse Studio Development -> Tasks, and click "+" to create a new SQL task (both methods below are implemented in the same task).

:-: ![](.topwrite/assets/image_1736148597217.png =470)

^

Create two new SQL tasks (as shown below), then [get the code from GitHub](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/QuickStart_SQL_DataClean) and copy the SQL code into the two tasks.

Then run each SQL one by one and observe the results.

:-: ![](.topwrite/assets/image_1736402851987.png =471)

The following are the descriptions of each step.

## Building the Schema and Compute Cluster for the Experiment
```SQL
-- Data_Clean virtual cluster
CREATE VCLUSTER IF NOT EXISTS Data_Clean
   VCLUSTER_SIZE = XSMALL
   VCLUSTER_TYPE = GENERAL
   AUTO_SUSPEND_IN_SECOND = 60
   AUTO_RESUME = TRUE
   COMMENT  'Data_Clean VCLUSTER for test';

-- Use our VCLUSTER
USE VCLUSTER Data_Clean;

-- Create and Use SCHEMA
CREATE SCHEMA IF NOT EXISTS  Data_Clean;
USE SCHEMA Data_Clean;
```
## Set the schema and cluster for each task in the IDE to the newly created one:

:-: ![](.topwrite/assets/image_1736403086331.png =508)

^

## Create a sample table and insert dirty data

First, we need to create a sample table and insert some sample data containing dirty data for demonstration in the following steps.
```SQL
-- Create a sample table named "sales_data"
CREATE TABLE sales_data (
    id INT,
    sale_date DATE,
    customer_id INT,
    product_id VARCHAR(50),
    quantity INT,
    price DECIMAL(10, 2),
    total_amount DECIMAL(10, 2),
    region VARCHAR(50)
);

-- Insert 20 rows of sample data containing dirty data
INSERT INTO sales_data (id, sale_date, customer_id, product_id, quantity, price, total_amount, region) VALUES
(1, '2025-01-01', 101, '201A', 5, 100.00, 500.00, 'North'),
(2, '2025-01-02', 102, '202', 3, 150.00, 450.00, 'East'),
(3, '2025-01-03', NULL, '203', 8, 200.00, 1600.00, 'South'), -- Missing customer_id
(4, '2025-01-04', 104, '204', -10, 50.00, 500.00, 'West'), -- quantity is negative
(5, '2025-01-05', 105, '201@#', 7, 75.00, 525.00, 'North'), -- product_id contains special characters
(6, '2025-01-06', 106, '202', 9, NULL, 1080.00, 'East'), -- Missing price
(7, '2025-01-07', 107, '203', 4, 60.00, 240.00, 'South'),
(8, '2025-01-08', 108, '204', 6, 80.00, 480.00, ''), -- region is empty
(9, '2025-01-09', 109, '201', 2, 110.00, 220.00, 'North'),
(10, '2025-01-10', 110, '202', 1, 130.00, 130.00, 'East'),
(11, '2025-01-11', 111, '203', 5, 140.00, 700.00, 'South'),
(12, '2025-01-12', 112, '204', 3, 70.00, 210.00, 'NULL'), -- region contains illegal characters
(13, '2025-01-13', 113, '201', 8, 160.00, 1280.00, 'North'),
(14, '2025-01-14', 114, '202A', 6, 90.00, 540.00, 'East'), -- product_id contains special characters
(15, '2025-01-15', 115, '203', 7, 170.00, 1190.00, 'South'),
(16, '2025-01-16', 116, '204', 4, 180.00, 720.00, 'West'),
(17, '2025-01-17', 117, '201', 5, 85.00, 425.00, 'North'),
(18, '2025-01-18', 118, '202', 9, 190.00, 1710.00, 'East'),
(19, '2025-01-19', 119, '203', 2, 200.00, 400.00, 'South'),
(20, '2025-01-20', 120, '204', -1, 210.00, 210.00, 'West'); -- quantity is negative
```
### Dirty Data Issues and Handling Methods

1. **Missing Values**

   * **Example**: `customer_id` is missing in row 3.
   * **Issue**: Missing values can lead to incomplete or incorrect analysis.
   * **Handling**: Use `COALESCE` or `IFNULL` to fill in default values, such as `0`.

2. **Negative Values**

   * **Example**: `quantity` is negative in rows 4 and 20.
   * **Issue**: Negative values are unreasonable in certain contexts, such as sales quantities.
   * **Handling**: Use `CASE` statements to convert negative values to reasonable values.

3. **Special Characters**

   * **Example**: `product_id` contains special characters in rows 5 and 14.
   * **Issue**: Special characters may cause data parsing errors.
   * **Handling**: Use `REGEXP_REPLACE` to remove special characters.

4. **Missing Fields**

   * **Example**: `price` is missing in row 6.
   * **Issue**: Missing fields lead to incomplete data.
   * **Handling**: Use `COALESCE` or `IFNULL` to fill in default values.

5. **Empty Strings**

   * **Example**: `region` is empty in row 8.
   * **Issue**: Empty strings can lead to inaccurate data parsing.
   * **Handling**: Use the `TRIM` function to remove blank values.

6. **Illegal Characters**

   * **Example**: `region` contains illegal characters in row 12.
   * **Issue**: Illegal characters can cause data parsing errors.
   * **Handling**: Use `REGEXP_REPLACE` to remove illegal characters.

By handling these dirty data issues using the methods above, data quality can be significantly improved, providing a more reliable foundation for subsequent data analysis and mining.

## Handling Missing Values

### Description

Missing values are a common issue in data cleaning. They can lead to inaccurate data analysis results. You can use the `COALESCE` function, `IFNULL` function, or `CASE` statements to fill in default values or replace missing values. In actual projects, handling missing values is often used to ensure that key fields are not empty, thereby ensuring data integrity.

### Implementation
```sql
-- Use COALESCE to fill default values
SELECT id, sale_date, COALESCE(customer_id, 0) AS customer_id, product_id, quantity, price, COALESCE(total_amount, 0) AS total_amount, region FROM sales_data;

-- Use IFNULL to fill default values
SELECT id, sale_date, IFNULL(customer_id, 0) AS customer_id, product_id, quantity, price, IFNULL(total_amount, 0) AS total_amount, region FROM sales_data;

-- Use CASE statement to handle missing values
SELECT id, 
       CASE 
           WHEN sale_date IS NULL THEN '2025-01-01'
           ELSE sale_date
       END AS sale_date,
       customer_id, 
       product_id, 
       quantity, 
       price, 
       total_amount, 
       region 
FROM sales_data;

```
## Remove Special Characters

### Description

Special characters can affect data analysis. You can use the `REGEXP_REPLACE` function to remove these characters. In actual projects, removing special characters is often used to clean up noise characters in text fields, making the data more tidy and standardized.

### Implementation
```sql
-- Remove special characters
SELECT id, sale_date, customer_id, 
       REGEXP_REPLACE(product_id, '[^a-zA-Z0-9]', '') AS cleaned_product_id,
       quantity, 
       price, 
       total_amount, 
       region
FROM sales_data;
```
## Convert Data Types

### Description

Sometimes it is necessary to convert data from one type to another, such as converting a string to a date type. Data type conversion ensures data consistency and accuracy. In actual projects, it is often used to standardize data formats, such as dates, amounts, etc.

### Implementation
```sql
-- Convert string to date
SELECT id, CAST(sale_date AS DATE) AS sale_date, 
    customer_id, product_id, quantity, 
    CAST(price AS DECIMAL(10, 2)) AS price, 
    CAST(total_amount AS DECIMAL(10, 2)) AS total_amount, region 
FROM sales_data;
```
## Remove Spaces

### Description

During the data cleaning process, leading and trailing spaces in strings can lead to inaccurate data analysis results. We can use the `TRIM` function to remove spaces. In actual projects, removing spaces is often used to clean text fields that contain extra spaces.

### Implementation
```sql
-- Delete blank values
SELECT id, 
       TRIM(sale_date) AS sale_date, 
       customer_id, 
       product_id, 
       quantity, 
       price, 
       total_amount, 
       TRIM(region) AS region
FROM sales_data;
```
## Convert Case

### Description

To standardize data formats, text fields can be converted to lowercase or uppercase. In actual projects, case conversion is often used to ensure data consistency, such as in customer names, product names, and other fields.

### Implementation
```sql
-- Convert the region field to lowercase
SELECT id, 
       sale_date, 
       customer_id, 
       product_id, 
       quantity, 
       price, 
       total_amount, 
       LOWER(region) AS region
FROM sales_data;
```
## Delete Outliers

### Description

Outliers may affect the results of data analysis. You can use the `DELETE` statement to remove these records. In actual projects, deleting outliers is often used to eliminate extreme or erroneous data to ensure the accuracy of the analysis results.

### Implementation
```sql
-- Delete records with sales amount less than 50
DELETE FROM sales_data WHERE total_amount < -5000;
## Deduplication

### Description

In datasets, duplicate records can affect the accuracy of data analysis. We can use the `DISTINCT` or `ROW_NUMBER()` functions to remove duplicate records. In real projects, deduplication operations are often used when merging multiple data sources or cleaning historical data.

### Implementation
```sql
-- Use DISTINCT to remove duplicates
SELECT DISTINCT customer_id, product_id, region FROM sales_data;

-- Use ROW_NUMBER() to remove duplicates
WITH RowNumCTE AS (
    SELECT *,
           ROW_NUMBER() OVER(PARTITION BY customer_id, product_id, region ORDER BY id) AS row_num
    FROM sales_data
)
SELECT id, sale_date, customer_id, product_id, quantity, price, total_amount, region
FROM RowNumCTE
WHERE row_num = 1;
```
## Data Grouping and Aggregation

### Description

Through grouping and aggregation, summary reports can be generated to understand the overall situation of the data. Grouping and aggregation operations can help us discover patterns and trends in the data. In practical projects, they are often used for statistics and data analysis, such as calculating total sales, averages, etc.

### Implementation
```sql
-- Calculate total sales by region
SELECT region, SUM(total_amount) AS total_sales FROM sales_data GROUP BY region;

-- Calculate total sales volume by product
SELECT product_id, SUM(quantity) AS total_quantity FROM sales_data GROUP BY product_id;
```
## Data Filtering

### Description

Use the `WHERE` clause to filter out data that meets specific conditions. In actual projects, data filtering is often used to extract subsets of data of interest, such as filtering out high-value customers, sales data for specific time periods, etc.

### Implementation
```sql
-- Select records where the sales amount is greater than 500
SELECT * FROM sales_data WHERE total_amount > 500;
```
## Data Sorting

### Description

Sorting can help us view data in a specific order and discover patterns and trends in the data. In practical projects, sorting is often used in data presentation, report generation, and other scenarios.

### Implementation
```sql
-- Sort by sales amount
SELECT * FROM sales_data ORDER BY total_amount DESC;
```
## Merge Column Data

### Description

In some cases, we need to merge the data of multiple columns into one column. In actual projects, merging column data is often used to generate comprehensive information fields, such as full addresses, names, etc.

### Implementation
```sql
-- Merge product ID and region fields
SELECT id,       sale_date,       customer_id,       product_id || '-' || region AS combined_field,       quantity,       price,       total_amountFROM sales_data;
```
## Merging Data

### Description

Use the `UNION` operation to merge multiple result sets together to form a complete result set. In actual projects, merging data is often used to integrate multiple query results into a unified analysis dataset.

### Implementation
```sql
-- Merge two result sets
SELECT id, sale_date, customer_id, product_id, quantity, price, total_amount, region FROM sales_data
UNION
SELECT id, sale_date, customer_id, product_id, quantity, price, total_amount, region FROM another_sales_data;
```
Through the above SQL data cleaning and preprocessing techniques, you can effectively handle and transform data, laying a solid foundation for subsequent data analysis and mining. Data cleaning not only improves data quality but also brings more accuracy and reliability to data analysis.

## SQL Functions List for Data Cleaning

The following is a list of commonly used SQL data cleaning functions:

1. **Handling Missing Values**

   * [COALESCE()](sql_functions/scalar_functions/conditional_functions/coalesce.md): Used to replace NULL values with specified default values.
   * [IFNULL()](sql_functions/scalar_functions/conditional_functions/ifnull.md): Similar to COALESCE(), used to replace NULL values with specified default values.
   * `CASE`: Used to handle missing values based on specific conditions.

2. **Removing Special Characters**

   * [REGEXP\_REPLACE()](sql_functions/scalar_functions/string_functions/regexp_extract.md): Used to replace special characters in text using regular expressions.

3. **Converting Data Types**

   * `CAST()`: Used to convert data from one type to another.

4. **Removing Whitespace**

   * [TRIM()](sql_functions/scalar_functions/string_functions/trim.md): Used to remove whitespace characters from strings.

5. **Changing Case**

   * `LOWER()`: Converts text to lowercase.
   * [UPPER()](sql_functions/scalar_functions/string_functions/upper.md): Converts text to uppercase.

6. **Removing Outliers**

   * [DELETE](delete.md): Used to delete records that do not meet conditions.

7. **Deduplication**

   * [DISTINCT](query-syntax.md): Used to remove duplicate rows from the result set.
   * [ROW\_NUMBER()](sql_functions/window_functions/row_number.md): Used to assign a unique row number to each row in the result set.

8. **Grouping and Aggregating Data**

   * [GROUP BY](query-syntax.md): Used to group the result set by one or more columns.
   * [SUM()](query-syntax.md): Used to calculate the sum of a specified column.
   * [AVG()](query-syntax.md): Used to calculate the average of a specified column.
   * [COUNT()](query-syntax.md): Used to count the number of records in a specified column.

9. **Filtering Data**

   * [WHERE](query-syntax.md): Used to filter records that meet specific conditions.

10. **Sorting Data**

    * [ORDER BY](query-syntax.md): Used to sort the result set.

11. **Joining Data**

    * [JOIN](join.md): Used to join two or more tables to form a complete data view.

12. **Merging Column Data**

    * [CONCAT()](sql_functions/scalar_functions/string_functions/concat.md): Used to merge data from multiple columns into one column.

13. **Merging Data**

    * [UNION](query-syntax.md): Used to merge multiple result sets together.

^