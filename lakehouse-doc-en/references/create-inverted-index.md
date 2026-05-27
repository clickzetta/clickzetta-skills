## Create Inverted Index

For detailed introduction, refer to [Inverted Index](inverted-index.md) introduction

### Syntax
```SQL
CREATE TABLE table_name(
  columns_difinition,
  INDEX index_name (column_name) INVERTED [COMMENT '']  PROPERTIES('analyzer'='english｜chinese|keyword｜unicode'),
  INDEX index_name (column_name) INVERTED [COMMENT '']  PROPERTIES('analyzer'='english｜chinese|keyword｜unicode'),
....
  INDEX index_name (column_name) INVERTED [COMMENT '']  PROPERTIES('analyzer'='english｜chinese|keyword｜unicode')
);
```
**columns\_difinition**: Defines the field information of the table, the last field must be separated by a comma

**INDEX**: Keyword

**index\_name**: Custom name for the index

**column\_name**: The name of the field to add the index to

**INVERTED**: Keyword, indicates an inverted index

**COMMENT**: Specifies the description information of the index

**PROPERTIES**: Specifies the parameters of the INDEX, currently supports specifying tokenization. Numerical and date types do not need to specify properties, if it is a string type, tokenization must be specified

* Tokenization parameters: 'analyzer'='english｜chinese | keyword｜unicode', used to specify the text tokenization strategy, suitable for different languages and needs.
  * **keyword**: This type of field will not be tokenized. The entire string is treated as a single root word and stored in the inverted index. When searching, the complete field value needs to be provided for an exact match.
  * **english**: A tokenizer designed specifically for English, only recognizes continuous ASCII letters and numbers, and converts the text to lowercase. Suitable for processing English content, ignoring non-alphanumeric characters.
  * **chinese**: Chinese text tokenization plugin, recognizes Chinese and English characters, filters out punctuation, and converts English letters to lowercase. Suitable for processing mixed Chinese and English text.
  * **unicode**: A tokenizer based on the Unicode text segmentation algorithm, capable of recognizing text boundaries in multiple languages, effectively splitting text into words, and converting letters to lowercase. Suitable for text processing in a multilingual environment.

### Reference Documents

* [Build Index](build-inverted-index.md)
* [Delete Index](DROP-INDEX.md)
* [List All Indexes](SHOW-INDEX.md)
* [View Index Details](DESC-INDEX.md)

### Examples
```SQL
CREATE TABLE inverted_index_test(
  id int,
  name string,
  INDEX id_index (id) INVERTED ,
  INDEX name_index (name) INVERTED  PROPERTIES('analyzer'='keyword')
);
```
## Adding Inverted Index to Existing Tables

### Syntax
```SQL
CREATE  INVERTED INDEX [IF NOT EXISTS] index_name ON TABLE 
[schema].table_name(col_name)
[COMMENT 'comment']
PROPERTIES('analyzer'='english｜chinese|keyword｜unicode')
```
**INVERTED**: Index type, inverted index

**index\_name**: Table name, located under schema, index name under schema must be unique

**col\_name**: Column name only supports single column

**PROPERTIES**: Specify parameters for INDEX, currently supports specifying tokenization. Numerical and date types do not need to specify properties, if it is a string type, tokenization must be specified

### Description

Executing CREATE INDEX is only effective for new data. To index existing data, please use the BUILD INDEX command.

### **Example**

1. Specify inverted index when creating a table
```SQL
DROP TABLE IF EXISTS t;
CREATE    TABLE t (
          order_id INT,
          customer_id INT,
          amount DOUBLE,
          order_year string,
          order_month string,
          INDEX order_id_index (order_id) INVERTED COMMENT 'INVERTED'
          );
INSERT INTO t
VALUES (1, 101, 100.0, '2023','01'),
       (2, 102, 200.0, '2023','02'),
       (3, 103, 300.0, '2023','03'),
       (4, 104, 400.0, '2023','04'),
       (5, 105, 500.0, '2023','04');
DESC INDEX order_id_index;	
+--------------------+-------------------------+
|     info_name      |       info_value        |
+--------------------+-------------------------+
| name               | order_id_index          |
| creator            | UAT_TEST                |
| created_time       | 2024-12-27 10:39:44.778 |
| last_modified_time | 2024-12-27 10:39:44.778 |
| comment            | INVERTED                |
| index_type         | inverted                |
| table_name         | t                       |
| table_column       | order_id                |
+--------------------+-------------------------+
--Using inverted index query
SELECT    *
FROM      t
WHERE     match_any (order_id, 3);
+----------+-------------+--------+------------+-------------+
| order_id | customer_id | amount | order_year | order_month |
+----------+-------------+--------+------------+-------------+
| 3        | 103         | 300.0  | 2023       | 03          |
+----------+-------------+--------+------------+-------------+
```
2. Add BLOOMFILTER Index to Existing Columns
```
CREATE INVERTED INDEX order_year_index
ON TABLE public.t (order_year)
PROPERTIES('analyzer'='chinese');
-- After the inverted index is added, only newly written data will take effect. Old data will not take effect. If old data needs to be effective, you can use the BUILD INDEX command.
BUILD INDEX order_year_index ON public.t;
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

SELECT    *
FROM      t
WHERE     match_all (order_year, '2023');
+----------+-------------+--------+------------+-------------+
| order_id | customer_id | amount | order_year | order_month |
+----------+-------------+--------+------------+-------------+
| 1        | 101         | 100.0  | 2023       | 01          |
| 2        | 102         | 200.0  | 2023       | 02          |
| 3        | 103         | 300.0  | 2023       | 03          |
| 4        | 104         | 400.0  | 2023       | 04          |
| 5        | 105         | 500.0  | 2023       | 04          |
+----------+-------------+--------+------------+-------------+

```