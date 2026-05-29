### JSON_OBJECT
```sql
json_object([key1, val1, key2, val2, ...])
```
#### Description
Constructs a JSON object. Accepts an even number of parameters, pairing them into key-value pairs.

#### Parameters
* key1, val1, key2, val2, ... : Optional parameters, passed in pairs. key is of string type, val can be of any type.

#### Returns
* JSON type, representing a JSON object

#### Examples
```sql
SELECT json_object();
-- Result: {}
```

```sql
SELECT json_object("a-null", NULL);
-- Result: {"a-null":null}
```

```sql
SELECT json_object('hello', 123, "world", timestamp '2020-10-10 00:00:00');
-- Result: {"hello":123,"world":"2020-10-10 00:00:00"}
```

```sql
SELECT json_object('hello', 123, "world", array(1, 2, 3));
-- Result: {"hello":123,"world":[1,2,3]}
```

```sql
SELECT json_object('hello', json_array(1, "a"), "world", array(1, 2, 3));
-- Result: {"hello":[1,"a"],"world":[1,2,3]}
```

```sql
SELECT json_object('hello', json_object("nested", "b"), "world", struct(1, 2, 3));
-- Result: {"hello":{"nested":"b"},"world":{"col1":1,"col2":2,"col3":3}}
```
#### Notes
* An even number of parameters must be provided, otherwise an error will occur.
* Supports nested JSON objects and arrays.
* Can accept complex types (such as array, struct, etc.), which are automatically converted to JSON format.
