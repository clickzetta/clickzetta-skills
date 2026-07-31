# Introduction to JSON Data Format

JSON (JavaScript Object Notation) is a lightweight, easy-to-read, and easy-to-write semi-structured data format. It is based on a subset of JavaScript, but JSON is language-independent, and many programming languages have parsing and generation code for JSON data format. JSON format uses text to represent simple data structures such as objects, arrays, strings, numbers, and booleans. JSON format has good readability and simplicity, making it an ideal data exchange format.

# JSON Type in LakeHouse

In LakeHouse, JSON type data can be stored and queried efficiently. JSON data in LakeHouse is parsed and optimized for storage based on the actual structure of the data. Here are some characteristics of JSON type in LakeHouse:

1. Query Performance: Using JSON type has a significant advantage in query performance compared to String type because LakeHouse performs column pruning on JSON data, reducing unnecessary data scans.
2. Data Reordering: During parsing, the data of JSON objects may be reordered, so the order of keys in the input and output JSON data may be inconsistent.
3. Number Parsing: When parsing JSON numbers, LakeHouse will first attempt to parse them as bigint type. If the number exceeds the range of bigint, it will be parsed as double type. It should be noted that double type may have precision loss.
4. Error Handling: When using functions to parse JSON data, LakeHouse performs validation. For illegal JSON strings, NULL values will be returned; and when declaring JSON constants, illegal JSON strings will cause errors.

Additionally, during the writing process, LakeHouse will store frequently occurring fields in a columnar storage manner based on the actual JSON Schema to improve storage and query efficiency. For example:

```sql
CREATE TABLE json_table AS
SELECT  parse_json(s) as j
FROM VALUES
('{"id": 1, "value": "200"}'),
('{"id": 2, "value": "300"}'),
('{"id": 3, "value": "400", "extra": 1}'),
('{"value": "100"}') as t(s);
```

1. For the above data, LakeHouse detects that the id and value fields have high frequency, and are suitable for columnar storage with bigint and string types respectively. Internally, it will store them in a structure similar to struct\<id:bigint, value:string>. In subsequent queries, if only the id field is read and converted to bigint, such as `SELECT json_extract_bigint(j, '$.id')`, the id field can be read directly by column, eliminating the overhead of type conversion.
2. For the extra field with low frequency, the JSON structure is retained and stored in a more compact representation to avoid generating overly sparse data.

**Limitations**

* Comparison operations on JSON types are not supported, nor are `ORDER BY`, `GROUP BY`, or using JSON types as keys for `JOIN`.
* Cannot be used as cluster key, primary key, or partition key.
* The maximum length of a JSON string is 16 MB. Length validation is performed on fields during batch and real-time imports. If you have data larger than 16 MB when importing, you can modify the table's Properties to set the JSON length to 32 MB as follows.

```
ALTER TABLE table_name SET PROPERTIES("cz.storage.write.max.json.bytes"="33554432");
```

## Create a Table with JSON Columns

To create a table that includes JSON type columns, you can use the following SQL statement:

```sql
CREATE TABLE json_example
(
    id bigint,
    data json
);
```

## Constructing JSON Data

### JSON Constants

In SQL queries, you can use JSON constants to represent JSON data. For example:

```sql
SELECT
JSON 'null',
JSON '1',
JSON '3.14',
JSON 'true',
JSON 'false',
JSON '{"id":11,"name":"Lakehouse"}',
JSON '[0, 1]';

-- !query output
+-------------+----------+-------------+-------------+--------------+-------------------------------------+---------------+
| JSON 'null' | JSON '1' | JSON '3.14' | JSON 'true' | JSON 'false' | JSON '{"id":11,"name":"Lakehouse"}' | JSON '[0, 1]' |
+-------------+----------+-------------+-------------+--------------+-------------------------------------+---------------+
| null        | 1        | 3.14        | true        | false        | {"id":11,"name":"Lakehouse"}        | [0,1]         |
+-------------+----------+-------------+-------------+--------------+-------------------------------------+---------------+
```

### Syntax

```sql
-- Access fields in a JSON object by key name
json_column['key']['key']...
-- Access elements in a JSON array by index
json_array[index]
```

**Parameter Description**

* json\_column: Represents a JSON field, which is of JSON object type. By specifying the key name (`key`) as a string, you can locate and retrieve specific data fields within the JSON object. Use single square brackets `[]` to access the first-level fields of the object; nested use of double square brackets `[][]` allows you to retrieve second-level or deeper fields within the object.
* json\_array: A JSON array type, used to access elements of a JSON array by index, starting from 0.

#### Example

Retrieve the first-level structure of the JSON

```sql
SELECT parse_json(s)['firstName'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

Extract json secondary structure

```sql
SELECT parse_json(s)['address']['streetAddress'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

Extract elements from the json array

```sql
SELECT parse_json(s)['phoneNumbers'][0]['number'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

### Using Functions

### Using Functions (Convert JSON in STRING Format to String)

The `parse_json` function can parse a JSON string of type String into JSON type. For example:

```sql
SELECT parse_json(s) is null, parse_json(s)
FROM VALUES ('null'),
            ('1'),
            ('3.14'),
            ('true'),
            ('false'),
            ('{"id":11,"name":"Lakehouse"}'),
            ('[0, 1]'),
            (''),
            ('invalid') as t(s);
+-------------------------+------------------------------+
| (parse_json(s)) IS NULL |        parse_json(s)         |
+-------------------------+------------------------------+
| false                   | null                         |
| false                   | 1                            |
| false                   | 3.14                         |
| false                   | true                         |
| false                   | false                        |
| false                   | {"id":11,"name":"Lakehouse"} |
| false                   | [0,1]                        |
| true                    | null                         |
| true                    | null                         |
+-------------------------+------------------------------+
```

* If the parameter of `parse_json` is an invalid JSON string, it returns SQL null, and the result of `is null` is true.
* If the input string is `'null'`, it will be interpreted as a JSON null value, and the result of `is null` is false.

### json\_array/json\_object

Similar to array/named\_struct, it can construct the corresponding JSON type based on existing data.

```sql
SELECT json_array(), json_array(NULL),json_array(NULL::int, 1, TRUE, FALSE, NULL::int, "a", 1.2, 1.3d);
+----------------+--------------------+--------------------------------------------------------------------------------------+
| `json_array`() | `json_array`(NULL) | `json_array`(CAST(NULL AS int), 1, true, false, CAST(NULL AS int), 'a', 1.2BD, 1.3d) |
+----------------+--------------------+--------------------------------------------------------------------------------------+
| []             | [null]             | [null,1,true,false,null,"a","1.2",1.3]                                               |
+----------------+--------------------+--------------------------------------------------------------------------------------+

SELECT json_object(), json_object('k', NULL), json_object('k1', json_array(1, "a"), "k2", array(1, 2, 3));
-- !query output
+-----------------+--------------------------+-------------------------------------------------------------------+
| `json_object`() | `json_object`('k', NULL) | `json_object`('k1', `json_array`(1, 'a'), 'k2', `array`(1, 2, 3)) |
+-----------------+--------------------------+-------------------------------------------------------------------+
| {}              | {"k":null}               | {"k1":[1,"a"],"k2":[1,2,3]}                                       |
+-----------------+--------------------------+-------------------------------------------------------------------+
```

## Type Conversion

In LakeHouse, you can use the `::json` or `CAST` function to convert other types to JSON type. Here are some examples of type conversions:

|                       |                       |
| --------------------- | --------------------- |
| Json                  | SQL                   |
| Object                | Struct                |
| Array                 | Array                 |
| String                | string                |
| Number                | bigint/double         |
| true/false            | bool                  |
| Null                  | No corresponding type |
| No corresponding type | binary                |

* For type conversions not listed in the table, they will first be converted to a convertible type (in most cases, string type), and then converted to the target type. For example, cast(1.2 as json) where 1.2 is of decimal type, will first be converted to string type, and then further converted to JSON type. The result is JSON '"1.2"', not JSON '1.2'.
* It should be noted that the semantics of cast(string as json) and parse\_json(string) are not the same. parse\_json will attempt to parse the JSON string into a JSON object. If the JSON format is incorrect, it will generate NULL. However, cast(string to json) **will treat the entire string as a string type in JSON. Therefore, if you are converting a JSON format string, you should use parse\_json**.
  Specific cases

```sql
-- xx::json is equivalent to cast(xxx as json)

SELECT 0::json;
-- !query output
+-----------------+
| CAST(0 AS json) |
+-----------------+
| 0               |
+-----------------+

SELECT 1.2F::json;
-- !query output
+--------------------+
| CAST(1.2F AS json) |
+--------------------+
| 1.2000000476837158 |
+--------------------+

SELECT 1.2::json;
-- !query output
+---------------------+
| CAST(1.2BD AS json) |
+---------------------+
| "1.2"               |
+---------------------+

SELECT 's'::json;
+-------------------+
| CAST('s' AS json) |
+-------------------+
| "s"               |
+-------------------+

SELECT (timestamp '2020-10-10 00:00:00') ::json;
+----------------------------------------------+
| CAST(timestamp'2020-10-10 00:00:00' AS json) |
+----------------------------------------------+
| "2020-10-10 00:00:00"                        |
+----------------------------------------------+

SELECT (date '2020-10-10') ::json;
+---------------------------------+
| CAST(DATE '2020-10-10' AS json) |
+---------------------------------+
| "2020-10-10"                    |
+---------------------------------+

SELECT array(1, 2, 3) ::json;
+--------------------------------+
| CAST(`array`(1, 2, 3) AS json) |
+--------------------------------+
| [1,2,3]                        |
+--------------------------------+

SELECT array(1, null, 3) ::json;
+-----------------------------------+
| CAST(`array`(1, NULL, 3) AS json) |
+-----------------------------------+
| [1,null,3]                        |
+-----------------------------------+

SELECT map("a", 2, "b", 4)::json, map("a", 2, "b", null) ::json;
+-----------------------------------+--------------------------------------+
| CAST(map('a', 2, 'b', 4) AS json) | CAST(map('a', 2, 'b', NULL) AS json) |
+-----------------------------------+--------------------------------------+
| {"a":2,"b":4}                     | {"a":2,"b":null}                     |
+-----------------------------------+--------------------------------------+

SELECT struct(1, 2, 3, 4)::json, struct(1, 2, 3, null::int) ::json;
+---------------------------------------+--------------------------------------------------+
|   CAST(struct(1, 2, 3, 4) AS json)    | CAST(struct(1, 2, 3, CAST(NULL AS int)) AS json) |
+---------------------------------------+--------------------------------------------------+
| {"col1":1,"col2":2,"col3":3,"col4":4} | {"col1":1,"col2":2,"col3":3,"col4":null}         |
+---------------------------------------+--------------------------------------------------+
SELECT null::json;
+--------------------+
| CAST(NULL AS json) |
+--------------------+
| null               |
+--------------------+

SELECT j::string, j::char(2), j::bigint, j::double, j::decimal(9, 4), j::boolean, j::json, j::array<int>
from values (json '123'),
            (json '1.23'),
            (json 'null'),
            (json 'true'),
            (json 'false'),
            (json '"abc"'),
            (json '{"a":2}'),
            (json '[1,2]') t(j);
-- !query output
+-------------------+--------------------+-------------------+-------------------+-------------------------+--------------------+-----------------+-----------------------+
| CAST(j AS string) | CAST(j AS char(2)) | CAST(j AS bigint) | CAST(j AS double) | CAST(j AS decimal(9,4)) | CAST(j AS boolean) | CAST(j AS json) | CAST(j AS array<int>) |
+-------------------+--------------------+-------------------+-------------------+-------------------------+--------------------+-----------------+-----------------------+
| 123               | 12                 | 123               | 123.0             | 123.0000                | true               | 123             | null                  |
| 1.23              | 1.                 | 1                 | 1.23              | 1.2300                  | true               | 1.23            | null                  |
| null              | null               | null              | null              | null                    | null               | null            | null                  |
| true              | tr                 | 1                 | 1.0               | 1.0000                  | true               | true            | null                  |
| false             | fa                 | 0                 | 0.0               | 0.0000                  | false              | false           | null                  |
| abc               | ab                 | null              | null              | null                    | null               | "abc"           | null                  |
| {"a":2}           | {"                 | null              | null              | null                    | null               | {"a":2}         | null                  |
| [1,2]             | [1                 | null              | null              | null                    | null               | [1,2]           | [1,2]                 |
+-------------------+--------------------+-------------------+-------------------+-------------------------+--------------------+-----------------+-----------------------+
```

# Note

It is important to note that the semantics of `cast(string as json)` and `parse_json(string)` are not the same. `parse_json` will attempt to parse the JSON string into a JSON object, and if the JSON format is incorrect, it will generate NULL; whereas `cast(string to json)` will treat the entire string as a JSON string type.

```sql
SELECT parse_json(s), s::json, s::json::string
FROM VALUES ('{"id":11, "name": "Lakehouse"}') as t(s);
+------------------------------+----------------------------------------+---------------------------------+
|        parse_json(s)         |            CAST(s AS json)             | CAST(CAST(s AS json) AS string) |
+------------------------------+----------------------------------------+---------------------------------+
| {"id":11,"name":"Lakehouse"} | "{\"id\":11, \"name\": \"Lakehouse\"}" | {"id":11, "name": "Lakehouse"}  |
+------------------------------+----------------------------------------+---------------------------------+
```

# Using SDK (igs/bulkload) to Write JSON

Lakehouse supports writing String type strings to JSON type columns. The system will automatically parse the strings into JSON type during import. If the user inputs a string that does not conform to JSON standards or a JSON string that is not supported by CZ, the system will report an error and stop the import.

# Exporting JSON Data

Lakehouse supports exporting JSON data in the form of strings.

# Querying JSON Data

To query JSON data, you need to use the `json_extract` series of functions to get the required data through the JSON path. Here are some examples of querying JSON data:

* json\_extract
* json\_extract\_boolean
* json\_extract\_float
* json\_extract\_double
* json\_extract\_int
* json\_extract\_bigint
* json\_extract\_string
* json\_extract\_date
* json\_extract\_timestamp

### JSON Path Specification

The second parameter of json\_extract is the JSON path. You can refer to the [JSON path specification](https://goessner.net/articles/JsonPath/)

* "$" represents the root element
* ".key" or "\['key']" is used to find the key in the JSON object. Specifically, "\[\*]" means to get all values, and it must be single quotes
* "\[index]" is used to access elements of a JSON array by index, starting from 0. Specifically, "\[\*]" means all elements

```sql
SELECT json_extract(j, "$[0]"),
       json_extract(j, "$[1]"),
       json_extract(j, "$[*]")
FROM VALUES (JSON '["a", 1, null]') as t(j);
+-------------------------+-------------------------+-------------------------+
| json_extract(j, '$[0]') | json_extract(j, '$[1]') | json_extract(j, '$[*]') |
+-------------------------+-------------------------+-------------------------+
| "a"                     | 1                       | ["a",1,null]            |
+-------------------------+-------------------------+-------------------------+


SELECT json_extract(j, "$.key"),
       json_extract(j, "$['key.with.dot']"),
       json_extract(j, "$[*]")
FROM VALUES (JSON '{"key":1, "key.with.dot":2}') as t(j);
+--------------------------+----------------------------------------+-------------------------+
| json_extract(j, '$.key') | json_extract(j, '$[\'key.with.dot\']') | json_extract(j, '$[*]') |
+--------------------------+----------------------------------------+-------------------------+
| 1                        | 2                                      | [1,2]                   |
+--------------------------+----------------------------------------+-------------------------+

SELECT json_extract(j, '$.*.city'),
       json_extract(j, '$.phoneNumbers[*]'),
       json_extract(j, '$.phoneNumbers[*].extra'),
       json_extract(j, '$.phoneNumbers[*].extra[*]'),
       json_extract(j, '$.*[*].extra[*]')
FROM (SELECT parse_json(s) as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }'),
                  ('{} ') as t(s));
+-----------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------+-----------------------------------------------+------------------------------------+
| json_extract(j, '$.*.city') |                                  json_extract(j, '$.phoneNumbers[*]')                                   | json_extract(j, '$.phoneNumbers[*].extra') | json_extract(j, '$.phoneNumbers[*].extra[*]') | json_extract(j, '$.*[*].extra[*]') |
+-----------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------+-----------------------------------------------+------------------------------------+
| ["Nara"]                    | [{"number":"0123-4567-8888","type":"iPhone"},{"extra":[],"number":"0123-4567-8910","type":"home"}]      | [[]]                                       | null                                          | null                               |
| ["Nara","NewYork"]          | [{"number":"0123-4567-8888","type":"iPhone"},{"extra":[1,2,3],"number":"0123-4567-8910","type":"home"}] | [[1,2,3]]                                  | [1,2,3]                                       | [1,2,3]                            |
| null                        | null                                                                                                    | null                                       | null                                          | null                               |
+-----------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------+-----------------------------------------------+------------------------------------+
```

# Other JSON Functions

json\_valid is used to verify whether a string type of data can be converted to JSON type

```sql
SELECT json_valid('hello'),
       json_valid('"hello"'),
       json_valid('null'),
       json_valid('{}'),
       json_valid('[]'),
       json_valid('{"a": "b"}'),
       json_valid('[1, "a"]');
+---------------------+-----------------------+--------------------+------------------+------------------+--------------------------+------------------------+
| json_valid('hello') | json_valid('"hello"') | json_valid('null') | json_valid('{}') | json_valid('[]') | json_valid('{"a": "b"}') | json_valid('[1, "a"]') |
+---------------------+-----------------------+--------------------+------------------+------------------+--------------------------+------------------------+
| false               | true                  | true               | true             | true             | true                     | true                   |
+---------------------+-----------------------+--------------------+------------------+------------------+--------------------------+------------------------+
```

# Performance Comparison

The constructed data consists of over 10 million entries in the format `{"address":"89695 Lind Common, Kellymouth, AK 61747","email":"``danita.weber@gmail.com``","name":"Golda Shields"}`, using where for filtering queries.

Using string queries, the execution time is 20.4 seconds.

```sql
create table bulkload_data_string(data string);
select get_json_object(data,'$.email') from bulkload_data_string where get_json_object(data,'$.email')='danita.weber@gmail.com'
;
```

Using json to store data takes 531ms to execute. Since column pruning is performed during reading, the data size is also reduced. As shown in the figure below, only 153MB of data needs to be read, while string type requires reading the full 454MB of data.

```sql
create table bulkload_data(json string);
select json_extract_string(data,'$.name') from bulkload_data where json_extract_string(data,'$.email')='danita.weber@gmail.com'
;
```

^
