### JSON_NORMALIZE
```sql
json_normalize(json)
```
#### Description
Normalizes a JSON string by sorting the keys of JSON objects in alphabetical order and removing extra spaces.

#### Parameters
* json : An expression of type string

#### Returns
* string type, returns the normalized JSON string
* Returns NULL if the input is NULL or invalid JSON

#### Examples
```sql
SELECT json_normalize('{"b": 1, "a": 2, "c": 3}');
-- Result: {"a":2,"b":1,"c":3}
```

```sql
SELECT json_normalize('[{"a": 4, "c": 5, "b": 6}]');
-- Result: [{"a":4,"b":6,"c":5}]
```

```sql
SELECT json_normalize('1');
-- Result: 1
```

```sql
SELECT json_normalize(null);
-- Result: NULL
```

```sql
SELECT json_normalize('[');
-- Result: NULL
```
#### Notes
* Sorts JSON object keys alphabetically, useful for comparison and deduplication
* Recursively processes nested JSON objects and arrays
* For non-object types (such as numbers, strings, etc.), returns the compressed form of the original value directly
* Returns NULL for invalid JSON strings
