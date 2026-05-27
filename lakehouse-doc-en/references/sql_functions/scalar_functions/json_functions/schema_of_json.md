## SCHEMA_OF_JSON

###  Description

The `schema_of_json` function is used to parse and generate the corresponding DDL schema from a given JSON string. This function can help users quickly understand the structure of JSON data, facilitating subsequent data operations and processing.

### Syntax 
```
schema_of_json(str)
```
### Parameter Description

- `str`: The JSON format string that needs to be parsed.

### Return Result

- Returns a string representing the JSON data structure, formatted as a DDL schema.

### Example 

1. Below is an example of using the `schema_of_json` function:
```sql
SELECT schema_of_json(' {
  "n": null,
  "s": "hello",
  "i": 123,
  "f": 123.0,
  "a": [ null, 123 ],
  "m": {},
  "st": {"a": "s"}
} ');
```
Function Return Result:
```
struct<n:null,s:string,i:bigint,f:double,a:array<bigint>,m:map<string,string>,st:struct<a:string>>
```

2. Extract schema from a JSON string containing dates:
   ```sql
   SELECT schema_of_json(' {
     "name": "John",
     "age": 30,
     "birthdate": "1991-01-22"
   } ');
   Return results:
   struct<name:string,age:bigint,birthdate:date>
   ```



3. Extract schema from nested JSON string:

   ```sql
   SELECT schema_of_json(' {
     "company": "Example Inc.",
     "employees": [
       {"name": "Alice", "position": "Developer"},
       {"name": "Bob", "position": "Manager"}
     ]
   } ');
    Return results:
    struct<company:string,employees:array<struct<name:string,position:string>>>
   ```