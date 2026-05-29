### CONTAINS 
`contains(expr, subExpr)`
#### Description
The `contains` function is used to determine whether the string or binary expression `subExpr` exists within the string or binary expression `expr`. If `subExpr` exists within `expr`, it returns `true`; otherwise, it returns `false`.

#### Parameters
- `expr`: The string or binary expression to be searched.
- `subExpr`: The substring or binary expression to be found within `expr`.

#### Return Value
Returns a boolean value indicating whether `subExpr` exists within `expr`.

#### Example Usage
1. Determine if "HelloWorld" contains "Hello":
```sql
SELECT contains('HelloWorld', 'Hello'); -- Returns true
```
2. Determine if "123456" contains "34":
```sql
SELECT contains('123456', '34'); -- Returns true
```
3. Determine whether "Example text" contains "text":
```sql
SELECT contains('Example text', 'text'); -- Returns true
```
#### Notes
- When `expr` or `subExpr` is `NULL`, the `contains` function will return `NULL`.

By using the `contains` function, you can easily implement the detection of specific substrings or binary patterns in data queries, thereby improving the flexibility and efficiency of data processing.