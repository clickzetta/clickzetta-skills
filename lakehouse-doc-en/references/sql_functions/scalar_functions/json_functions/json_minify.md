### JSON_MINIFY
```sql
json_minify(json)
```
#### Description
Compresses a JSON string by removing extra spaces and newlines.

#### Parameters
* `json`: An expression of type string

#### Returns
* string type, returns the compressed JSON string.

#### Examples
```sql
SELECT json_minify('{ "a": 1, "b": 2 }');
-- Result: {"a":1,"b":2}
```

```sql
SELECT json_minify('["a", "b", "c"]');
-- Result: ["a","b","c"]
```
#### Notes
* Primarily used to remove formatting whitespace characters from JSON strings.
* Does not change the content or structure of the JSON, only compresses the format.
