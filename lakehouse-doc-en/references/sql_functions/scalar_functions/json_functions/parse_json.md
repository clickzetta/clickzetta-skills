# PARSE_JSON

#### Introduction

`PARSE_JSON` parses a JSON-formatted string into a semi-structured VARIANT object. The return value can access fields at any level using subscript operators (`['key']` or `[index]`). Unlike `FROM_JSON`, `PARSE_JSON` does not require a schema declaration up front and **preserves the original case of JSON key names**, making it suitable for JSON data with case-sensitive keys or variable structure.

#### Syntax

```Plain
PARSE_JSON(json_string)
```

#### Parameters

* `json_string`: Type `STRING`. The JSON string to parse. Returns `NULL` if the input is not valid JSON.

#### Return Type

Returns a VARIANT type (semi-structured object). Access nested fields using `['key']`, `[index]`, or `.key` syntax.

#### Examples

1. Basic usage — parse a JSON object and preserve key case:

```sql
SELECT PARSE_JSON('{"Name":"Alice"}');
```

```
+------------------------+
| parse_json(...)        |
+------------------------+
| {"Name":"Alice"}       |
+------------------------+
```

The uppercase `N` in the key `Name` is fully preserved.

2. Access fields using subscript notation:

```sql
SELECT PARSE_JSON('{"Name":"Alice","age":30}')['Name'] AS name,
       PARSE_JSON('{"Name":"Alice","age":30}')['age']  AS age;
```

```
+-------+-----+
| name  | age |
+-------+-----+
| Alice | 30  |
+-------+-----+
```

3. `PARSE_JSON` distinguishes between keys with different cases:

```sql
SELECT PARSE_JSON('{"A":1,"a":2}')['A'] AS upper_a,
       PARSE_JSON('{"A":1,"a":2}')['a'] AS lower_a;
```

```
+---------+---------+
| upper_a | lower_a |
+---------+---------+
| 1       | 2       |
+---------+---------+
```

4. Access nested fields:

```sql
SELECT PARSE_JSON('{"user":{"id":101,"name":"Bob"}}')['user']['name'] AS username;
```

```
+----------+
| username |
+----------+
| Bob      |
+----------+
```

5. Parse a JSON array and access by index:

```sql
SELECT PARSE_JSON('["x","y","z"]')[1] AS second_element;
```

```
+----------------+
| second_element |
+----------------+
| y              |
+----------------+
```

6. Case comparison with `FROM_JSON` — demonstrates the difference between the two functions:

```sql
-- FROM_JSON folds field names to lowercase
SELECT from_json('{"Name":"Alice"}', 'struct<Name:string>') AS from_json_result;
-- Result: {"name":"Alice"}  <- key name converted to lowercase

-- PARSE_JSON preserves original case
SELECT PARSE_JSON('{"Name":"Alice"}') AS parse_json_result;
-- Result: {"Name":"Alice"} <- key name unchanged
```

#### Notes

* When `json_string` is not valid JSON, the function returns `NULL` without throwing an exception. Add an `IS NULL` check in the outer query if you need to detect parse failures explicitly.
* The return type is VARIANT. Fields accessed via `['key']` are in string form. Use explicit `CAST` for specific types: `CAST(PARSE_JSON(col)['age'] AS INT)`.
* JSON array indexes start at `0`.
* Choosing between `PARSE_JSON` and `FROM_JSON`:

| Scenario                                                         | Recommended function |
|------------------------------------------------------------------|----------------------|
| Key case must be distinguished (e.g., `A` and `a` are different) | `PARSE_JSON`         |
| JSON structure is variable and you don't want to declare a schema | `PARSE_JSON`         |
| Map JSON fields to strongly typed struct/array/map               | `FROM_JSON`          |
| Downstream operations require explicit column types (JOIN, GROUP BY) | `FROM_JSON`      |

#### Related Documentation

* [FROM_JSON](from_json.md)
* [GET_JSON_OBJECT](get_json_object.md)
* [JSON_EXTRACT](json_extract.md)
