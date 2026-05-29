### JSON_EXTRACT

#### Description
The JSON_EXTRACT function series aims to extract specific elements from data in JSON format. These functions extract information from JSON objects or arrays based on the provided JSON path (json_path) and return the result as the corresponding data type. When the specified element does not exist, the function returns NULL.

#### JSON Path Specification
JSON path is a concise query syntax used to access elements within a JSON data structure. Here are some commonly used JSON path symbols:

- `$`: Represents the root element.
- `.key` or `[key]`: Used to find keys in a JSON object. Specifically, `[*]` indicates retrieving values corresponding to all keys.
- `[index]`: Used to access elements in a JSON array by index, starting from 0. Specifically, `[*]` indicates retrieving all elements in the array.

#### Function List
- `json_extract(json, json_path)`: Extracts the specified element from JSON data and returns the result in JSON format.
- `json_extract_boolean(json, json_path)`: Extracts the specified element from JSON data and converts it to a BOOLEAN.
- `json_extract_int(json, json_path)`: Extracts the specified element from JSON data and converts it to an INT.
- `json_extract_bigint(json, json_path)`: Extracts the specified element from JSON data and converts it to a BIGINT.
- `json_extract_float(json, json_path)`: Extracts the specified element from JSON data and converts it to a FLOAT.
- `json_extract_double(json, json_path)`: Extracts the specified element from JSON data and converts it to a DOUBLE.
- `json_extract_string(json, json_path)`: Extracts the specified element from JSON data and converts it to a STRING.
- `json_extract_date(json, json_path)`: Extracts the specified element from JSON data and converts it to a DATE.
- `json_extract_timestamp(json, json_path)`: Extracts the specified element from JSON data and converts it to a TIMESTAMP.

#### Parameter Description
- `json`: The JSON type data to be processed.
- `json_path`: A string specifying the JSON path to extract the element.

#### Return Results
- For the `json_extract_json` function, the extracted data in JSON format is returned.
- For other functions (such as `json_extract_boolean`, etc.), the extracted data is returned as the specified data type.

####  Example
1. Extract nested elements from a JSON object:
```sql
SELECT json_extract(json'{"a": {"b": 1}}', '$.a');
-- Output: {"b":1}
```
2. Extract keys with dots in JSON objects:
```sql
SELECT json_extract(json'{"key": 1, "key.with.dot": 2}', '$.key'),
      json_extract(json'{"key": 1, "key.with.dot": 2}', "$['key.with.dot']");
-- Output: 1       2
```
3. Extract all elements from a JSON array:
```sql
SELECT json_extract(json'[1, 2, 3]', '$[*]');
-- Output: [1,2,3]
```
4. Convert the extracted JSON elements to integers:
```sql
SELECT json_extract_int(json'{"a": {"b": 1}}', '$.a.b');
-- Output: 1
```

5. Convert the extracted JSON elements to boolean values:
```sql
SELECT json_extract_boolean(json'{"a": {"b": 1}}', '$.a.b');
-- Output: true
```
