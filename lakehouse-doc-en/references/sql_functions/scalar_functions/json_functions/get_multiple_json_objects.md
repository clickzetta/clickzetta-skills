# GET_MULTIPLE_JSON_OBJECTS

#### Introduction

The `GET_MULTIPLE_JSON_OBJECTS` function extracts values at multiple paths from a JSON string in a single call, returning a struct. Compared to `GET_JSON_OBJECT`, multi-path extraction requires only one function call, avoiding repeated parsing of the same JSON string for better performance.

| Function                    | Paths per call | Use case                                          |
|-----------------------------|----------------|---------------------------------------------------|
| `GET_JSON_OBJECT`           | 1              | Extract a single field only                       |
| `GET_MULTIPLE_JSON_OBJECTS` | Multiple       | Extract multiple fields at once, reducing re-parsing |

#### Syntax

```Plain
GET_MULTIPLE_JSON_OBJECTS(<json_str>, <path1>, <path2>, ...)
```

#### Parameters

* `json_str` (STRING): A string containing JSON-formatted data.
* `path1, path2, ...` (STRING): One or more JSONPath expressions specifying the field paths to extract. Path syntax is the same as `GET_JSON_OBJECT`: `$` for the root node, `.key` or `['key']` for object fields, and `[index]` for array elements.

#### Return Value

Returns a struct type with fields named `col1`, `col2`, ... in order, corresponding to the input paths. Each field value is of type STRING. If a path does not exist in the JSON, the corresponding field returns `NULL`.

#### Examples

1. Extract two top-level fields in one call:

```sql
SELECT GET_MULTIPLE_JSON_OBJECTS('{"a":1,"b":2}', '$.a', '$.b');
```

```
+------------------------------+
| col1 | col2                  |
+------+-----------------------+
| 1    | 2                     |
+------------------------------+
```

The actual return is a struct: `{"col1":"1","col2":"2"}` — field values are all strings.

2. Extract nested fields:

```sql
SELECT GET_MULTIPLE_JSON_OBJECTS(
  '{"name":"Alice","address":{"city":"New York","zip":"10001"}}',
  '$.name',
  '$.address.city',
  '$.address.zip'
);
```

Returns struct: `{"col1":"Alice","col2":"New York","col3":"10001"}`

3. Path not found returns NULL:

```sql
SELECT GET_MULTIPLE_JSON_OBJECTS('{"a":1}', '$.a', '$.b');
```

Returns struct: `{"col1":"1","col2":null}` — `$.b` does not exist, so `col2` is `NULL`.

4. Use with a table column:

```sql
SELECT
  GET_MULTIPLE_JSON_OBJECTS(event_payload, '$.user_id', '$.action', '$.ts') AS parsed
FROM event_log
LIMIT 5;
```

Access individual fields using `.col1`, `.col2`, `.col3`:

```sql
SELECT
  GET_MULTIPLE_JSON_OBJECTS(event_payload, '$.user_id', '$.action', '$.ts').col1 AS user_id,
  GET_MULTIPLE_JSON_OBJECTS(event_payload, '$.user_id', '$.action', '$.ts').col2 AS action,
  GET_MULTIPLE_JSON_OBJECTS(event_payload, '$.user_id', '$.action', '$.ts').col3 AS ts
FROM event_log;
```

> 💡 **Tip**: When you need to access multiple fields repeatedly, assign the `GET_MULTIPLE_JSON_OBJECTS` result to a column alias first, then access fields via `.colN` to avoid calling the function multiple times on the same JSON string.

#### Notes

* Each field value in the returned struct is of type STRING. Use `CAST` to convert to the target type as needed.
* Field names are always `col1`, `col2`, ... and do not use the JSONPath expressions themselves as field names.
* Path syntax is the same as `GET_JSON_OBJECT`. See the [JSONPath specification](https://goessner.net/articles/JsonPath/) for reference.

#### Related Documentation

* [GET_JSON_OBJECT](get_json_object.md)
* [JSON_EXTRACT](json_extract.md)
