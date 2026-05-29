### JSON_TUPLE Function

#### Description

The `JSON_TUPLE` function is used to parse key-value pairs in a `JSON` string and extract the values corresponding to specified keys. This function takes a `JSON` string as input and extracts the corresponding values based on the provided list of keys (`c1`, `c2`, ..., `cN`). If the `JSON` string fails to parse, the function returns a result with all columns set to `NULL`; if a key does not exist in the `JSON` object, the corresponding column is filled with `NULL`. Note that the `JSON_TUPLE` function can only parse top-level keys of the `JSON` object.

This function can be used directly or in conjunction with the `LATERAL VIEW` clause to extract `JSON` data in more complex queries.

#### Parameter Description

* `str` (string): The `JSON` string to be parsed, which should be a `JSON` object.
* `c1`, `c2`, ... `cN` (string): The keys in the `JSON` object to be extracted.

#### Return Type

* Returns a string array containing the extracted values, with the number of elements matching the length of the provided key list.

#### Usage Examples

**Example 1: Basic Usage**

```sql
SELECT json_tuple('{"x" : "1", "y" : 2}', 'x', 'z');
+------+------+
| col0 | col1 |
+------+------+
| 1    |      |
+------+------+
```

The above query attempts to extract the values of keys `x` and `z`. Since the `z` key does not exist, the value corresponding to `z` in the result is empty (`NULL`).

**Example 2: Using with LATERAL VIEW**

```sql
SELECT a, b, c FROM VALUES ('{"a" : 1.0, "b" : 2}') AS t(word) LATERAL VIEW json_tuple(word, 'a', 'b', 'c') lv AS a, b, c;
+-----+---+---+
|  a  | b | c |
+-----+---+---+
| 1.0 | 2 |   |
+-----+---+---+
```

In this example, we first create a table containing a `JSON` string, and then use `LATERAL VIEW` and the `json_tuple` function to extract the values of keys `a`, `b`, and `c`. Since the `c` key does not exist, its corresponding value is empty.

**Example 3: Handling Nested JSON Objects**

`JSON_TUPLE` only parses top-level keys. If a key's value is itself a JSON object, that value is returned as-is in string form and is not further expanded.

```sql
SELECT json_tuple('{"a": {"x": 1}, "b": 2}', 'a', 'b');
+----------+------+
|   col0   | col1 |
+----------+------+
| {"x":1}  | 2    |
+----------+------+
```

To extract nested fields, you can call `json_tuple` again on the returned string or use `get_json_object`.

**Example 4: Behavior When JSON Parsing Fails**

When the input string is not a valid JSON object, all columns return `NULL`:

```sql
SELECT json_tuple('not-a-json', 'a', 'b');
+------+------+
| col0 | col1 |
+------+------+
|      |      |
+------+------+
```
