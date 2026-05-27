# Inverted Index
**[Preview Release] This feature is currently in public preview.**

Introduction to the Inverted Index Principle
1. Basic Concepts
The inverted index consists of two parts:
* **Dictionary**: A list that stores all the unique words (or phrases) that have appeared in the entire document collection.
* **Posting List**: For each word in the dictionary, there is a corresponding posting list that records the document IDs of all documents containing that word and the positions where the word appears in the documents.
2. Construction Process
    -  **Tokenization**: The process of splitting the document content into words or phrases.
    -  **Normalization**: Processing the tokenized results, such as converting to lowercase, removing stop words, stemming, etc.
    -  **Building the Dictionary**: Adding the processed words to the dictionary and assigning a unique ID to each word.
    -  **Building the Posting List**: For each document, recording the IDs and positions of all words in the document, and associating this information with the word IDs in the dictionary to form the posting list.
3. Query Process
When a user submits a query request, the search engine performs the following steps:

    -  **Query Parsing**: Breaking down the user's query into words or phrases.
    -  **Dictionary Lookup**: Looking up the IDs of these words or phrases in the dictionary.
    -  **Retrieving the Posting List**: Retrieving the document IDs of all documents containing these words from the posting list based on the word IDs.
    -  **Merging Results**: Merging the retrieval results of different words according to the logic in the query (such as AND, OR, NOT, etc.) to determine the final document list.

4. Application Scenarios
The inverted index is mainly used in the field of full-text search, such as search engines, document retrieval systems, etc. It can quickly respond to user queries and provide efficient retrieval services.

### Feature Introduction

Each row of the Table corresponds to a document in Elasticsearch, and each column corresponds to a field in the document. Therefore, using the inverted index can quickly locate the rows containing the keyword, achieving the purpose of accelerating the WHERE clause. At the same time, as mentioned above, the dictionary and posting list will also occupy Lakehouse storage, so you will see that the data size is higher than that of tables without an inverted index.

1. Supports full-text search for string types, supporting match_all, match_any, match_phrase, match_phrase_prefix, match_regexp functions. The performance will be faster than like. Currently, Lakehouse uses the inverted index for like in some scenarios, but it is recommended to use full-text search functions.

2. Accelerates ordinary equality and range queries
   * Supports fast filtering for string and numeric types with =, !=, >, >=, <, <=

3. Supports comprehensive logical combinations
   * Supports AND, OR, NOT pushdown

4. Flexible and fast index management

   * Creating an Inverted Index: Supports defining an inverted index when creating a table, and adding an inverted index to an existing table. If the index is created on an existing table, the inverted index needs to be added to the existing data. You can execute the build index command.
   * Building an Inverted Index: The inverted index needs to be added to the existing data. Building the index will start an SQL task and consume computing resources.
   * Listing All Inverted Indexes: View all inverted indexes on a table.
   * Viewing Inverted Index Details: View details of the index, including size, etc.
   * Deleting an Inverted Index: Executing drop index will succeed immediately, deleting the index metadata information. However, the index storage information will not be deleted immediately.

5. Currently supported data types for the inverted index:

* Numeric types (TINYINT, SMALLINT, INT, FLOAT, DOUBLE)
* Date types (DATE, TIMESTAMP)
* String types (STRING, VARCHAR, CHAR) When the inverted index field is of string type, you need to specify tokenization. The currently supported tokenization types are:
  * **keyword**: This type of field will not be tokenized. The entire string is treated as a single root word and stored in the inverted index. For searches, the complete field value needs to be provided for exact matching.
  * **english**: A tokenizer designed for English, recognizing continuous ASCII letters and numbers, and converting the text to lowercase. Suitable for processing English content, ignoring non-alphanumeric characters.
  * **chinese**: A Chinese text tokenization plugin that recognizes Chinese and English characters, filters out punctuation, and converts English letters to lowercase. Suitable for processing mixed Chinese and English text.
  * **unicode**: A tokenizer based on the Unicode text segmentation algorithm, capable of recognizing text boundaries in multiple languages, effectively splitting text into words, and converting letters to lowercase. Suitable for processing text in a multilingual environment.
    You can use the tokenize(input[, option]) function to test tokenization. An example of using tokenize to test tokenization is as follows:
```SQL
--Use keyword tokenizer
SELECT TOKENIZE('Lakehouse inverted index',map('analyzer', 'keyword')) as toke;
+-------------------------------------+
|                toke                 |
+-------------------------------------+
| ["Lakehouse inverted index"]        |
+-------------------------------------+
--Use chinese tokenizer, not supported yet
SELECT TOKENIZE('Lakehouse inverted index',map('analyzer', 'chinese')) as toke;
+----------------------------------+
|              toke                |
+----------------------------------+
| ["lakehouse","inverted","index"] |
+----------------------------------+
--Use unicode tokenizer
SELECT TOKENIZE('Lakehouse inverted index',map('analyzer', 'unicode')) as toke;
+----------------------------------+
|              toke                |
+----------------------------------+
| ["lakehouse","inverted","index"] |
+----------------------------------+
--Use english tokenizer
SELECT TOKENIZE('Lakehouse inverted index',map('analyzer', 'english')) as toke;
+----------------------------------+
|               toke               |
+----------------------------------+
| ["lakehouse","inverted","index"] |
+----------------------------------+
```
### Scenarios Where Inverted Index Cannot Be Optimized
* In most cases, inverted index does not significantly improve the performance of queries with execution times in sub-seconds.
* External tables are not supported
* Does not support forced conversion of table columns, for example
```SQL
-- Can be queried with acceleration, data type in the table is string
where string_col='10086';
-- Convert the value to be matched
where string_col=cast(10086 as string);

-- Cannot be queried with acceleration, because the table column is forcibly converted
where cast(string_col as int)=10086 ;
```
### Using Inverted Index Query

#### Inverted Index Functions

The function requires the tokenization to be consistent with the table; otherwise, the inverted index cannot be used to accelerate the query. The analyzer supports the auto parameter, which can automatically map the tokenization in the table when the auto parameter is added.


| Function Name                                  | Function                                                    | Example                                                                                                                           |
| ---------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| tokenize(input\[, option])                     | Tokenize, returns an array                                   | tokenize('a b', map('analyzer', 'english')) = \["a", "b"]                                                                         |
| match\_all(input, query\[, option])            | Match all, first tokenize the query, then tokenize the input. The tokenized result of the input must contain all the tokenized results of the query. Returns bool | match\_all('a b c', 'b a', map('analyzer', 'english')) = true                                                                     |
| match\_any(input, query\[, option])            | Match any, the tokenized result of the input only needs to contain any element of the tokenized result of the query. Returns bool | match\_any('a b c', 'd a', map('analyzer', 'english')) = true                                                                     |
| match\_phrase(input, query\[, option])         | Match phrase, based on match\_all, the order of the matched results must be consistent and continuous with the order of the tokenized results of the query | match\_phrase('a b c', 'a b', map('analyzer', 'english')) = truematch\_phrase('a b c', 'a c', map('analyzer', 'english')) = false |
| match\_phrase\_prefix(input, query\[, option]) | Match phrase prefix, the tokenization result of input, the first n-1 elements follow the same matching rule as match\_phrase, and the last element follows the prefix matching rule | match\_phrase\_prefix('a b cd', 'b c', map('analyzer', 'english')) = true                                                         |
| match\_regexp(input, query\[, option])         | Match regular expression, the tokenization result of input, using the regular expression of query, any match is sufficient                 | match\_regexp('a b cd', 'c.\*', map('analyzer', 'english')) = true                                                                |

#### Specific Cases

Create an inverted index table
```SQL
create table bulkload_data(id int,data string,INDEX data_index (data) INVERTED PROPERTIES('analyzer'='unicode'));

* Full-text search

```SQL
--Match All
select * from bulkload_data where match_all(data,'Elfriede Heaney',map('analyzer', 'unicode'));
+------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                   data                                                                   |
+------------------------------------------------------------------------------------------------------------------------------------------+
| {"address":"Apt. 423 78018 Wisozk Meadow, West Marge, WV 16958","name":"Elfriede Heaney","email":"jamar.schoen@gmail.com"}               |
| {"address":"Suite 654 89305 Dan Drive, Haiview, AZ 55461","name":"Elfriede Heaney","email":"kristofer.upton@yahoo.com"}                  |
| {"address":"1133 Cartwright Orchard, Port Jonathon, UT 71589-4026","name":"Elfriede Heaney","email":"douglass.nitzsche@yahoo.com"}       |
| {"address":"115 Avery Mountains, New Elfriede, TN 83686-3466","name":"Clarence Heaney","email":"emmanuel.lockman@yahoo.com"}             |
| {"address":"Suite 342 631 Konopelski Hollow, East Chingview, UT 79212","name":"Elfriede Heaney DDS","email":"mikel.keebler@hotmail.com"} |
| {"address":"415 Elfriede Row, New Adriene, SC 90250","name":"Jefferson Heaney","email":"len.price@yahoo.com"}                            |
+------------------------------------------------------------------------------------------------------------------------------------------+
--Match Phrase
select * from bulkload_data where match_phrase(data,'Elfriede Heaney',map('analyzer', 'unicode'));
+------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                   data                                                                   |
+------------------------------------------------------------------------------------------------------------------------------------------+
| {"address":"Apt. 423 78018 Wisozk Meadow, West Marge, WV 16958","name":"Elfriede Heaney","email":"jamar.schoen@gmail.com"}               |
| {"address":"Suite 654 89305 Dan Drive, Haiview, AZ 55461","name":"Elfriede Heaney","email":"kristofer.upton@yahoo.com"}                  |
| {"address":"1133 Cartwright Orchard, Port Jonathon, UT 71589-4026","name":"Elfriede Heaney","email":"douglass.nitzsche@yahoo.com"}       |
| {"address":"Suite 342 631 Konopelski Hollow, East Chingview, UT 79212","name":"Elfriede Heaney DDS","email":"mikel.keebler@hotmail.com"} |
+------------------------------------------------------------------------------------------------------------------------------------------+
```

* Accelerate ordinary value queries
select * from bulkload_data where data='{"address":"Apt. 423 78018 Wisozk Meadow, West Marge, WV 16958","name":"Elfriede Heaney","email":"jamar.schoen@gmail.com"}'
+----------------------------------------------------------------------------------------------------------------------------+
|                                                            data                                                            |
+----------------------------------------------------------------------------------------------------------------------------+
| {"address":"Apt. 423 78018 Wisozk Meadow, West Marge, WV 16958","name":"Elfriede Heaney","email":"jamar.schoen@gmail.com"} |
+----------------------------------------------------------------------------------------------------------------------------+
```

### Inverted Index Billing

* Storage Resources: Inverted indexes will create additional inverted index files outside of the data files. The storage fees for index files and data files will be collected based on the unified storage size.

## Create Inverted Index

### Define Index When Creating Table

#### Syntax

```SQL
CREATE TABLE table_name(
  columns_difinition,
  INDEX index_name (column_name) INVERTED [COMMENT '']  PROPERTIES('analyzer'='english|chinese|keyword|unicode'),
  INDEX index_name (column_name) INVERTED [COMMENT '']  PROPERTIES('analyzer'='english|chinese|keyword|unicode'),
...
  INDEX index_name (column_name) INVERTED [COMMENT '']  PROPERTIES('analyzer'='english|chinese|keyword|unicode')
);
```

**columns\_difinition**: Defines the field information of the table, the last field must be separated by a comma

**INDEX**: Keyword

**index\_name**: Custom name for the index

**column\_name**: Name of the field to add the index to

**INVERTED**: Keyword, indicates an inverted index

**COMMENT**: Specifies the description information of the index

**PROPERTIES**: Specifies the parameters of the INDEX, currently supports specifying tokenization. Numerical and date types do not need to specify properties, if it is a string type, tokenization must be specified

* Tokenization parameters: 'analyzer'='english|chinese | keyword|unicode', used to specify the text tokenization strategy, suitable for different languages and needs.
  * **keyword**: This type of field will not be tokenized. The entire string is treated as a single root word and stored in the inverted index. When searching, the complete field value needs to be provided for an exact match.
  * **english**: A tokenizer designed specifically for English, recognizing only consecutive ASCII letters and numbers, and converting text to lowercase. Suitable for processing English content, ignoring non-alphanumeric characters.
  * **chinese**: Chinese text tokenization plugin, recognizing both Chinese and English characters, filtering out punctuation, and converting English letters to lowercase. Suitable for processing mixed Chinese and English text.
  * **unicode**: A tokenizer based on the Unicode text segmentation algorithm, capable of recognizing text boundaries in multiple languages, effectively splitting text into words, and converting letters to lowercase. Suitable for text processing in a multilingual environment.

#### **Example**

```SQL
CREATE TABLE inverted_index_test(
  id int,
  name string,
  INDEX id_index (id) INVERTED  ,
  INDEX name_index (name) INVERTED  PROPERTIES('analyzer'='keyword')
);
```

### Adding Inverted Index to Existing Table

#### Syntax

```SQL
CREATE  INVERTED INDEX [IF NOT EXISTS] index_name ON TABLE 
[schema].table_name(col_name)
[COMMENT 'comment']
PROPERTIES('analyzer'='english|chinese|keyword|unicode')
```

**INVERTED**: Index type, inverted index

**index\_name**: Table name, located under schema, index name under schema must be unique

**col\_name**: Column name, only supports single column

**PROPERTIES**: Specifies the parameters of the INDEX, currently supports specifying tokenization. Numerical and date types do not need to specify properties, if it is a string type, tokenization must be specified

#### Description

Executing CREATE INDEX is only effective for new data. To index existing data, please use the BUILD INDEX command.

#### **Example**

```SQL
CREATE TABLE inverted_index_test(
  id int,
  name string
);


CREATE  INVERTED INDEX  id_index ON TABLE 
public.inverted_index_test(name)
PROPERTIES('analyzer'='unicode')
```

## Using Inverted Index Query

### Building Index

Add inverted index to existing data

### Syntax
-- Syntax 1, by default adds an inverted index to the entire table's existing data
BUILD INDEX index_name ON [schema].table_name;
-- Syntax 2, can specify partition, can specify one or more, supports =, !=, >, >=, <, <=
BUILD INDEX index_name ON table_name WHERE partition_name1 = '1' and partition_name2 = '2';
```

* index\_name: Specify the name of the inverted index to be added
* Support for specifying partition construction: One or more can be specified

### Description

Executing BULD INDEX is a synchronous task, and the execution process will consume computing resources. You can check the progress through Job Profile.

When the data volume of the partition table is large, it is recommended to create indexes sequentially by partition.

### Example

```SQL
BUILD INDEX bulkload_data_index ON public.bulkload_data ;
```

## List All Inverted Indexes on a Table

The command is used to list the inverted indexes that have been created on the specified table.

### Syntax
SHOW INDEX FROM [schema].table_name;
```

### Case
 show index from public.bulkload_data;
+---------------------+------------+
|     index_name      | index_type |
+---------------------+------------+
| bulkload_data_index | inverted   |
+---------------------+------------+
```

## View Inverted Index Details

This command is used to list the details of the inverted indexes that have been created in the specified table. Adding the keyword `extended` allows you to view the size of the inverted index.

### Syntax

```SQL
DESC INDEX [EXTENDED]  index_name;
```

### Example
```
desc index bulkload_data_index;
+--------------------+-------------------------+
|     info_name      |       info_value        |
+--------------------+-------------------------+
| name               | bulkload_data_index     |
| creator            | system_admin            |
| created_time       | 2024-05-27 16:11:23.928 |
| last_modified_time | 2024-05-27 16:11:23.928 |
| comment            |                         |
| index_type         | inverted                |
| table_name         | bulkload_data           |
| table_column       | data                    |
+--------------------+-------------------------+

desc index extended  bulkload_data_index;
+--------------------------+--------------------------+
|        info_name         |        info_value        |
+--------------------------+--------------------------+
| name                     | bulkload_data_index      |
| creator                  | system_admin             |
| created_time             | 2024-05-27 16:11:23.928  |
| last_modified_time       | 2024-05-27 16:11:23.928  |
| comment                  |                          |
| properties               | (("analyzer","unicode")) |
| index_type               | inverted                 |
| table_name               | bulkload_data            |
| table_column             | data                     |
| index_size_in_data_file  | 0                        |
| index_size_in_index_file | 0                        |
| total_index_size         | 0                        |
+--------------------------+--------------------------+
```

## Delete Inverted Index

### Syntax

```SQL
DROP INDEX [IF EXISTS] index_name;
```

Parameter Description:

* `DROP INDEX`: Keyword to delete an index.
* `IF EXISTS`: Optional parameter, no error is reported if the specified index does not exist.
* `index_name`: The name of the index to be deleted.

### Description

Executing drop index will succeed immediately and will delete the index metadata. However, it will not immediately delete the index storage information.
