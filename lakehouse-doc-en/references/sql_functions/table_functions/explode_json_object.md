### explode_json_object
#### Description
`explode_json_object` table function, expands a JSON object into multiple rows, with each row containing a key-value pair. Typically used to expand a JSON object into a more query-friendly format. This function only supports JSON objects that contain elements. Must be used with [`LATERAL VIEW`](<../LATERALVIEW>).
#### Syntax
```sql
EXPLODE_JSON_OBJECT(<json>)
```
#### Parameters
* `<json>` JSON type, its content should be a JSON object.
#### Return Results
* Returns a single-column multi-row result set composed of all elements in `<json>`, with the column type being `Nullable<Struct<String, JSON>>`.
* If `<json>` is NULL or is not a JSON object (e.g., an array `[]`), returns 0 rows.
* If `<json>` is an empty object (e.g., `{}`), returns 0 rows.
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

SELECT id, key, value FROM test_explode_json LATERAL VIEW OUTER explode_json_object(j) lv AS key, value ORDER BY id, key;
```
