### explode_json_array_string
#### Description
`explode_json_array_string` table function, accepts a JSON array. Its implementation logic is to convert the JSON array into an array type and then call the `explode` function for processing. Must be used with [`LATERAL VIEW`](<../LATERALVIEW>).
#### Syntax
```sql
EXPLODE_JSON_ARRAY_STRING(<json>)
```
#### Parameters
`<json>` JSON type, its content should be an array.
#### Return Results
* Returns a single-column multi-row result set composed of all elements in `<json>`, with the column type being `Nullable<JSON>`.
* If `<json>` is NULL or an empty array (element count is 0), returns 0 rows.
* If the elements of the JSON array are not of type STRING, an attempt will be made to convert them to STRING. Elements that cannot be converted to STRING will be converted to NULL.
#### Examples
```sql
CREATE TABLE test_explode_json(id int, j json);

INSERT INTO test_explode_json VALUES
(1, parse_json('{"a": 1, "b": "hello", "c": [1,2,3]}')),
(2, parse_json('[1, 2, "three", 4.5, null]')),
(3, parse_json('null')),
(4, null),
(5, parse_json('[]')),
(6, parse_json('{}')),
(7, parse_json('[{"x":1},{"y":2}]')),
(8, parse_json('{"nested": {"a": 1}, "arr": [1,2]}'));

SELECT id, col FROM test_explode_json LATERAL VIEW explode_json_array_string(j) lv AS col ORDER BY id;
```
