# TRANS_ARRAY Function


## Function Description


`TRANS_ARRAY` is a user-defined table-valued function (UDTF) used to transform one row of data into multiple rows. It converts arrays stored in columns that are formatted with fixed delimiters into multiple rows, implementing "row-to-column" data transformation. This function is particularly suitable for handling data structures where multiple values are stored in a single string field.


### Core Characteristics


* **Row-to-Column Transformation**: Splits multiple delimiter-separated values in a single row into multiple rows
* **Flexible Key Columns**: Supports specifying one or more columns as Keys that are not involved in the transformation
* **Automatic Padding**: When array lengths are unequal, automatically fills shorter arrays with NULL
* **Configurable Separator**: Supports any string as a separator


## Syntax


```sql
trans_array(<num_keys>, <separator>, <key1>, <key2>, ..., <col1>, <col2>, <col3>)
AS (<key1>, <key2>, ..., <col1>, <col2>)
```


## Parameter Description


| Parameter       | Type     | Required | Description                                                              |
| --------------- | -------- | -------- | --------------------------------------------------------------- |
| num_keys        | BIGINT   | Yes      | The number of columns used as Keys during transformation. Must be a constant with value ≥ 0. Key columns must come before all columns to be transposed                 |
| separator       | STRING   | Yes      | The separator used to split the string into multiple elements. Must be a constant and cannot be an empty string, otherwise an error is returned                          |
| key1, key2, ... | Any Type | Yes      | Columns used as Keys during transformation, with the number specified by num_keys. Key columns maintain their original data type in the result                 |
| col1, col2, ... | STRING   | Yes      | Array columns to be converted into rows. These columns must be of STRING type, and their content must be string-formatted arrays, for example `item1;item2;item3` |


### Special Notes


* **Role of Key Columns**: Key columns are used for grouping and identification. The values of Key columns remain unchanged during the splitting process


* **Requirements for Columns to Be Transposed**: All columns after Key columns are treated as array columns to be transposed and must be of STRING type


* **Output Row Count**: Based on the length of the longest array, other shorter arrays are filled with NULL where insufficient


* **Output Type**: Key columns maintain their original type, and all other columns are of STRING type




## Return Value


Returns transposed multiple rows of data, where:


* The data type of Key columns remains unchanged
* All transposed columns are of STRING type
* New column names are specified by the AS clause


## Usage Examples


**Example 1: Basic Transposition with Single Key**


Scenario Description: In the user login table, each user has multiple login IP and time information stored as delimiter-separated strings. It needs to be split into multiple rows for analysis.


Original Data Table: `test_user_login`


```sql
CREATE TABLE test_user_login (
    login_id STRING,
    login_ip STRING,
    login_time STRING
);

INSERT INTO test_user_login VALUES
('wangwangA', '192.168.0.1,192.168.0.2', '20120101010000,20120102010000'),
('wangwangB', '192.168.45.10,192.168.67.22,192.168.6.3', '20120111010000,20120112010000,20120223080000');
```


SQL Statement:


```sql
SELECT  trans_array(1, ',', login_id, login_ip, login_time)  AS (login_id, login_ip, login_time)
FROM test_user_login;
```


Execution Result:


| login_id  | login_ip      | login_time     |
| --------- | ------------- | -------------- |
| wangwangA | 192.168.0.1   | 20120101010000 |
| wangwangA | 192.168.0.2   | 20120102010000 |
| wangwangB | 192.168.45.10 | 20120111010000 |
| wangwangB | 192.168.67.22 | 20120112010000 |
| wangwangB | 192.168.6.3   | 20120223080000 |


Result Explanation:


* `num_keys=1` means only the `login_id` column serves as the Key
* `separator=','` specifies comma as the separator
* Each user's login records are split into separate rows
* `login_id` remains unchanged, serving as the grouping identifier


**Example 2: Transposition with Multiple Keys**


Scenario Description: The user information table has user ID, name, and multiple login IP and time records. Use two Key columns for transposition.


Original Data Table: `test_user_info`


```sql
CREATE TABLE test_user_info (
    id INT,
    name STRING,
    login_ip STRING,
    login_time STRING
);

INSERT INTO test_user_info VALUES
(1, 'Tom', '192.168.100.1,192.168.100.2', '20211101010101,20211101010102'),
(2, 'Jerry', '192.168.100.3,192.168.100.4', '20211101010103,20211101010104');
```


SQL Statement:


```sql
SELECT  trans_array(2, ',', id, name, login_ip, login_time)  AS (id, name, login_ip, login_time)
FROM test_user_info;
```


Execution Result:


| id | name  | login_ip      | login_time     |
| -- | ----- | ------------- | -------------- |
| 1  | Tom   | 192.168.100.1 | 20211101010101 |
| 1  | Tom   | 192.168.100.2 | 20211101010102 |
| 2  | Jerry | 192.168.100.3 | 20211101010103 |
| 2  | Jerry | 192.168.100.4 | 20211101010104 |


Result Explanation:


* `num_keys=2` means columns `id` and `name` serve as Keys
* The two Key columns remain unchanged in the result
* Login records maintain grouping relationships based on the values of Key columns


**Example 3: Handling Unequal Length Arrays (Automatic NULL Padding)**


Scenario Description: In the user interest table, different users have different numbers of hobbies and sports. Shows how to handle cases where array lengths are unequal.


Original Data Table: `test_unequal_array`


```sql
CREATE TABLE test_unequal_array (
    user_id STRING,
    hobbies STRING,
    sports STRING
);

INSERT INTO test_unequal_array VALUES
('user1', 'reading,coding', 'basketball,tennis,swimming');
```


SQL Statement:


```sql
SELECT  trans_array(1, ',', user_id, hobbies, sports)  AS (user_id, hobbies, sports)
FROM test_unequal_array;
```


Execution Result:


| user_id | hobbies | sports     |
| ------- | ------- | ---------- |
| user1   | reading | basketball |
| user1   | coding  | tennis     |
| user1   | NULL    | swimming   |


Result Explanation:


* The `hobbies` column has 2 elements, and the `sports` column has 3 elements
* The output row count is based on the longer array (3 rows)
* The third row of the `hobbies` column is filled with NULL
* This automatic padding prevents data loss