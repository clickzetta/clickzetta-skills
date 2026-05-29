## Description

This command is used to view the structure of a view, including its fields, types, and so on.

## Syntax

```
DESC[RIBE] [TABLE] [EXTENDED] view_name;
```

**Parameter Description**

1. `DESC[RIBE]`: DESC and DESCRIBE can be used interchangeably; both represent the command to view view structure.
2. `view_name`: Specifies the name of the view whose structure needs to be viewed.

Optional parameters:

3. `EXTENDED`: When this keyword is added, it displays the SQL statement that defines the view.

## Examples

### 1. View view structure (without EXTENDED keyword)

```
DESC customer_masked;
+-------------+-----------+---------+
| column_name | data_type | comment |
+-------------+-----------+---------+
| id          | int       |         |
| name        | string    |         |
| phone       | string    |         |
| email       | string    |         |
+-------------+-----------+---------+

```

After executing this command, the structure information of the `customer_masked` view is displayed, including field names, types, nullability, key information, etc.

### 2. View view structure and extended information (with EXTENDED keyword)

```
DESCRIBE EXTENDED customer_masked;
+------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|         column_name          |                                                                                    data_type                                                                              |
+------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| id                           | int                                                                                                                                                                       |
| name                         | string                                                                                                                                                                    |
| phone                        | string                                                                                                                                                                    |
| email                        | string                                                                                                                                                                    |
|                              |                                                                                                                                                                           |
| # detailed table information |                                                                                                                                                                           |
| schema                       | public                                                                                                                                                                    |
| name                         | customer_masked                                                                                                                                                           |
| creator                      | UAT_TEST                                                                                                                                                                  |
| created_time                 | 2023-11-23 21:47:19.996                                                                                                                                                   |
| last_modified_time           | 2023-11-23 21:47:20.001                                                                                                                                                   |
| comment                      |                                                                                                                                                                           |
| properties                   | ()                                                                                                                                                                        |
| type                         | VIEW                                                                                                                                                                      |
| view_text                    | SELECT customer.id, customer.name, mask_outer(CAST(customer.phone AS string), 3, 4) AS phone, mask_inner(customer.email, 0, 12) AS email FROM example.`public`.customer c |
| view_original_text           | SELECT id, name, mask_outer(phone, 3, 4) AS phone, mask_inner(email, 0, 12) AS email
FROM customer                                                                        |
| format                       | INVALID                                                                                                                                                                   |
| statistics                   | NULL rows NULL bytes                                                                                                                                                      |
+------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```
