## Description

This command is used to view the structure of the view, including the fields, types, etc.

## Syntax
```
DESC[RIBE] [TABLE] [EXTENDED] view_name;
```
**Parameter Description**

1. `DESC[RIBE]`: DESC and DESCRIBE can be used interchangeably, both representing the command to view the structure of a view.
2. `view_name`: Specifies the name of the view whose structure needs to be viewed.

Optional parameter:

3. `EXTENDED`: Adding this keyword allows displaying the SQL statement that defines the view.

##  Example

1. View the structure of a view (without using the EXTENDED keyword)
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
After executing this command, the structure information of the `my_view` view will be displayed, including field names, types, whether null is allowed, key information, etc.

2. View the structure and extended information of the view (using the EXTENDED keyword)
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
| view_text                    | SELECT customer.id, customer.name, mask_outer(CAST(customer.phone AS string), 3, 4) AS phone, mask_inner(customer.email, 0, 12) AS email FROM qingyun.`public`.customer c |
| view_original_text           | SELECT id, name, mask_outer(phone, 3, 4) AS phone, mask_inner(email, 0, 12) AS email
FROM customer                                                                        |
| format                       | INVALID                                                                                                                                                                   |
| statistics                   | NULL rows NULL bytes                                                                                                                                                      |
+------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```