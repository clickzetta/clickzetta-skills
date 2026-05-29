### JSON_PARSE 

#### Description
The `JSON_PARSE` function is used to parse a JSON-formatted string into a JSON type. The parsed JSON type will automatically remove extra spaces when output, and the order of fields is not guaranteed to be exactly the same as the original JSON string. `PARSE_JSON` is an alias for the `JSON_PARSE` function, and both have the same functionality.

#### Syntax
```
json_parse(str)
parse_json(str)
```
#### Parameters
- `str`: The JSON format string that needs to be parsed.

#### Return Result
- Returns the parsed JSON type.

#### Usage Example

**Example 1**: Parse a simple JSON string
```sql
SELECT json_parse('{"name": "Zhang San", "age": 25}');
Return Results:{"name":"Zhang San","age":25}
```

**Example 2**: Parsing Nested JSON Strings
```sql
SELECT json_parse('{"user":{"name":"Li Si","age":30},"info":{"city":"Beijing","country":"China"}}');
```
**Example 3**: Parsing a JSON string containing an array
```sql
select parse_json('{"fruits":["Apple","Banana","Orange"],"vegetables":["Cabbage","Carrot"]}') as res;
Return Results:
{"fruits":["Apple","Banana","Orange"],"vegetables":["Cabbage","Carrot"]}
```
**Example 4**: Parsing a JSON string containing numbers and boolean values
```sql
SELECT json_parse('{"score":85.5,true_false:true,"count":-100}');
Return Results:
{"score":85.5,"true_false":true,"count":-100}
```

#### Notes
- Ensure that the input string is in a valid JSON format, otherwise it may cause parsing failure.
- When handling complex JSON strings, pay attention to the indentation and use of quotes to ensure correct parsing.
- Since JSON types automatically remove extra spaces when outputting, the order of fields in the output may differ from the original input.