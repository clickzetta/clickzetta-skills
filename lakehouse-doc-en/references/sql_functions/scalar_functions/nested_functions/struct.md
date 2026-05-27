### STRUCT 

#### Description
The `STRUCT` function is used to create a structured object that contains a specified number of fields, with each field consisting of its name and corresponding value. By using the `STRUCT` function, multiple data values of different types can be combined into a single data type, i.e., a structured object.

#### Syntax
```
STRUCT(v1, v2, ..., vN)
```
#### Parameters
- v1, v2, ..., vN: Any number of data values, which can be of different data types.

#### Return Results
Returns a structured object containing N fields, with field names defaulting to "col1", "col2", ..., "colN", and field values corresponding to the input parameters v1, v2, ..., vN.

#### Usage Example
1. Create a structured object containing two fields, with field names "age" and "name", corresponding to age and name respectively:
```sql
SELECT STRUCT(25 , 'John Doe');
```
Return Results: 
```
{"col1":25,"col2":"John Doe"}
```
2. Combine different types of data (integer, string, boolean) into a structured object:

```sql
SELECT STRUCT(42, 'Hello, world!', TRUE);
```
Return Results: 
```
{"col1":42,"col2":"Hello, world!","col3":true}
```