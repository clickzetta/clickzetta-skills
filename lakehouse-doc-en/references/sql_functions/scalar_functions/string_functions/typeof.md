### TYPEOF
```sql
typeof(expr)
```
#### Function
Returns the data type of the expression. This function is used to query the type information of an expression or column, and is very useful in dynamic SQL and type checking scenarios.

#### Parameters
* `expr`: An expression of any type

#### Returns
* string type
* Returns the data type name of the expression
* For basic types, returns the type name (e.g., 'int', 'string', 'boolean')
* For complex types, returns the full type definition (e.g., `array<...>`, `map<...>`, `struct<...>`)

#### Examples
```sql
SELECT typeof(true);
-- Result: boolean
```

```sql
SELECT typeof(1);
-- Result: int
```

```sql
SELECT typeof(1.0);
-- Result: decimal(2,1)
```

```sql
SELECT typeof("1");
-- Result: string
```

```sql
SELECT typeof(array(1, 2, 3));
-- Result: array<int>
```

```sql
SELECT typeof(map(1, 2));
-- Result: map<int,int>
```

```sql
SELECT typeof(struct(1, 2, 3));
-- Result: struct<col1:int,col2:int,col3:int>
```

#### Notes
* The typeof function returns a type name string, not a type object.
* For the decimal type, returns complete precision information, such as 'decimal(10,2)'.
* For complex types (array, map, struct), returns the complete nested type definition.
* Field names in `struct` types default to `col1`, `col2`, `col3`, etc.
* This function determines the type at compile time and does not change at runtime.
* Common use cases:
  * Debugging and diagnostics
  * Generating type-related metadata
* Note: `TYPEOF` only returns type information, not NULL constraint information.
* This function has minimal performance impact because type information is determined at compile time.
