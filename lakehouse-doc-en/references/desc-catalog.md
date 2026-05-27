## Description

`DESC CATALOG` is a SQL command used to display detailed information about a specific catalog. Using this command, users can obtain a detailed description of the catalog, including its creation time, creator, and other information.

## Syntax
```SQL
DESC  CATALOG [EXTENDED] catalog_name;
```
### Parameter Description

* **catalog\_name**: The name of the catalog to be described. The user must ensure that the provided catalog name exists and is accessible in the system.

## Example
```SQL
DESC CATALOG test_external_catalog;
+--------------------+------------------------+
|     info_name      |       info_value       |
+--------------------+------------------------+
| name               | test_external_catalog  |
| creator            | UAT_TEST               |
| created_time       | 2024-06-27 18:05:36.69 |
| last_modified_time | 2024-06-27 18:05:36.69 |
| comment            |                        |
+--------------------+------------------------+

```


