### FROM_JSON 
```sql
from_json(json_string, schema)
```
####  Description

The `FROM_JSON` function is used to parse a JSON formatted string (`json_string`) and extract the corresponding data based on the provided schema definition (`schema`). During the parsing process, JSON fields not described in the schema will be ignored, and fields defined in the schema that do not match the JSON fields will have their values set to `NULL`. If `json_string` is not in a valid JSON format, the function will return `NULL`.

The syntax for schema definition is the same as when creating a table, supporting the following types:

1. Array type: `array<T>`, where `T` is the type of the array elements.
2. Key-value pair type: `map<K, V>`, where `K` is the type of the key and `V` is the type of the value.
3. Struct type: `struct<f1:T1, f2:T2, ... fn:Tn>`, where `f1, f2, ... fn` are field names and `T1, T2, ... Tn` are field types.

Type mapping (JSON type to LakeHouse type):

* JSON object can be converted to LakeHouse's struct, map, or string.
* JSON array can be converted to LakeHouse's array or string.
* Numeric types can be converted to LakeHouse's tinyint, smallint, int, bigint, float, double, decimal, or string.
* Boolean type can be converted to LakeHouse's boolean or string.
* String type can be converted to LakeHouse's string, char, varchar, binary, date, or timestamp.
* JSON `null` value can be converted to any type.

For floating-point types (float, double), the `FROM_JSON` function will try to ensure parsing precision; for decimal types, it can guarantee precision within the defined range.

#### Parameter Description

* `json_string`: Type `string`, represents the text containing the JSON string.
* `schema`: Type `string`, defines the expected data structure to be extracted, similar to the syntax used when creating a table.

#### Return Type

The return type is consistent with the type described in the schema definition (`schema`).

#### Usage Example
```sql
-- Parse JSON string into a struct containing integers, floats, and dates
SELECT from_json('{"a": 1, "b": 1.0, "c": "2020-10-10"}', 'struct<a:int, b:float, c:date>');
-- Result: {"a":1,"b":1.0,"c":"2020-10-10"}

-- Parse JSON array into an array of integers
SELECT from_json('[1, 2, 3]', 'array<int>');
-- Result: [1,2,3]

-- Parse JSON object into a map
SELECT from_json('{"name": "Alice", "age": 25}', 'map<string, string>');
-- Result: {"name":"Alice","age":"25"}

-- Parse JSON string containing nested structs
SELECT from_json('{"user": {"name": "Bob", "age": 30}, "active": true}', 'struct<`user`:map<string, string>, active:boolean>');
-- Result: {"user":{"name":"Bob","age":"30"},"active":true}

-- Parse JSON array containing nested arrays
SELECT from_json('[{"id": 1, "name": "Product A"}, {"id": 2, "name": "Product B"}]', 'array<struct<id:int, name:string>>');
-- Result: [{"id":1,"name":"Product A"},{"id":2,"name":"Product B"}]
```
#### Notes

* Ensure that the provided JSON string is valid, otherwise the function will return `NULL`.
* The schema definition should match the data structure in the JSON string, otherwise some fields may not be parsed correctly.
* When dealing with floating-point numbers and decimals, be aware that precision may be affected.
* When using the `from_json` function to extract data with a specified schema from a JSON string, case-sensitive keys in the JSON string may cause errors. For example:
    ```SQL
     select from_json('{"A":1,"a":2}','struct<A:bigint,a:bigint>');
    java.lang.IllegalArgumentException: not all nodes and buffers were consumed. nodes: 
    ```
To avoid this error, it is recommended to use the `parse_json` function. The `parse_json` function can correctly handle case-sensitive JSON keys and provides a more flexible way to access data.

```SQL
select parse_json('{"A":1,"a":2}')['A'] as res;
+-----+
| res |
+-----+
| 1   |
+-----+
select parse_json('{"A":1,"a":2}')['a'] as res;
+-----+
| res |
+-----+
| 2   |
+-----+
```