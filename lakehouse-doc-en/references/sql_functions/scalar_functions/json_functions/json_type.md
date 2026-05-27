### JSON_TYPE
```sql
json_type(json)
```
#### Description
Returns the type of a JSON value.

#### Parameters
* json : An expression of json type

#### Returns
* string type, returns one of the following values:
  * `JSON_NULL` - JSON null value
  * `JSON_BOOLEAN` - JSON boolean value
  * `JSON_INTEGER` - JSON integer
  * `JSON_DOUBLE` - JSON floating-point number
  * `JSON_STRING` - JSON string
  * `JSON_ARRAY` - JSON array
  * `JSON_OBJECT` - JSON object
  * `NULL` - Input is NULL or invalid JSON

#### Examples
```sql
SELECT json_type(json_parse('null'));
-- Result: JSON_NULL
```

```sql
SELECT json_type(json_parse('true'));
-- Result: JSON_BOOLEAN
```

```sql
SELECT json_type(json_parse('1'));
-- Result: JSON_INTEGER
```

```sql
SELECT json_type(json_parse('1.1'));
-- Result: JSON_DOUBLE
```

```sql
SELECT json_type(json_parse('"a"'));
-- Result: JSON_STRING
```

```sql
SELECT json_type(json_parse('[1,2,3]'));
-- Result: JSON_ARRAY
```

```sql
SELECT json_type(json_parse('{"a":1, "b":{"c":"x","d": "x"}}'));
-- Result: JSON_OBJECT
```
