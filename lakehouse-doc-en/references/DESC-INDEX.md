# View Index Details

## Description

`DESC INDEX` queries the creation date and name of the index

## Syntax
```
DESC INDEX [EXTENDED] index_name;
```
## Parameter Description

* `index_name`: The name of the index to view.
* EXTENDED: Allows viewing more extended information about the index, such as the size of the inverted index. Currently, viewing the size of the BLOOMFILTER index is not supported.

## Usage Example

Example 1: View details of the index named `idx_users_email`
```
DESC INDEX EXTENDED order_year_index;
+--------------------------+--------------------------+
|        info_name         |        info_value        |
+--------------------------+--------------------------+
| name                     | order_year_index         |
| creator                  | UAT_TEST                 |
| created_time             | 2024-12-27 10:51:58.977  |
| last_modified_time       | 2024-12-27 10:51:58.977  |
| comment                  |                          |
| properties               | (("analyzer","chinese")) |
| index_type               | inverted                 |
| table_name               | t                        |
| table_column             | order_year               |
| index_size_in_data_file  | 0                        |
| index_size_in_index_file | 296                      |
| total_index_size         | 296                      |
+--------------------------+--------------------------+
```