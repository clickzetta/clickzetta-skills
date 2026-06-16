# JSON Query Syntax

This document aims to guide users on how to efficiently query JSON data using SQL syntax. By mastering these query methods, users can simplify the query process. For creating JSON types, refer to the [JSON Types](json.md) document.

## Syntax

```Plain
-- Access fields in a JSON object by key name
json_column['key']['key']...
-- Access elements in a JSON array by index
json_array[index]
```

**Parameter Description**

* `json_column`: Represents a JSON field of JSON object type. Use a key name (`key`, specified as a string) to locate and retrieve specific data fields within the JSON object. Use single square brackets `[]` to access first-level fields; nested double square brackets `[][]` allow deeper retrieval of second-level or deeper fields.
* `json_array`: A JSON array type field, used to access elements of a JSON array by index. Index starts at 0.

**Return Value**

- The return value is of JSON type. If another type is needed, use the CAST function for conversion. See the [JSON Types](json.md) document for type conversion details.

## Examples

### Extract a First-Level JSON Field

```sql
SELECT parse_json(s)['firstName'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

```
+--------+
|   j    |
+--------+
| "John" |
| "Ada"  |
+--------+
```

> The return value is JSON type — string values include double quotes. To remove the quotes, use `::string`: `parse_json(s)['firstName']::string`.

### Extract a Second-Level JSON Field

```sql
SELECT parse_json(s)['address']['streetAddress'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

```
+----------------+
|       j        |
+----------------+
| "naist street" |
| "naist street" |
+----------------+
```

### Extract an Element from a JSON Array

```sql
SELECT parse_json(s)['phoneNumbers'][0]['number'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

```
+------------------+
|        j         |
+------------------+
| "0123-4567-8888" |
| "0123-4567-8888" |
+------------------+
```

