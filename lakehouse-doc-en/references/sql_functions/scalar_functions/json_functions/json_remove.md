### JSON_REMOVE
```sql
json_remove(jsonObj, jsonPath)
```

#### Function
Removes elements that match the `jsonPath` from the `jsonObj` and returns the remaining elements.
- `jsonPath` does not support wildcards.
- If the `jsonPath` does not exist, the original `jsonObj` is returned.

#### Parameters
- `jsonObj`: json
- `jsonPath`: string

#### Return Value
- json

#### Example
```sql
> SELECT parse_json(j), json_remove(parse_json(j), '$.b'), json_remove(parse_json(j), '$.b.c')
FROM VALUES
('{}'),
('{"a":1}'),
('{"a":2, "b":"y"}'),
('{"a":3, "b":{"c":"x"}}'),
('{"b":"y"}'),
(NULL),
('{"c":3}')
AS t(j);
{}      {}      {}
{"a":1} {"a":1} {"a":1}
{"a":2,"b":"y"} {"a":2} {"a":2,"b":"y"}
{"a":3,"b":{"c":"x"}}   {"a":3} {"a":3,"b":{}}
{"b":"y"}       {}      {"b":"y"}
NULL    NULL    NULL
{"c":3} {"c":3} {"c":3}
```