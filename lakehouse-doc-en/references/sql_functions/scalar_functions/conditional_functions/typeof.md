# TYPEOF

```sql
typeof(expr)
```

#### Function

Returns the data type of an expression. Useful for querying type information about expressions or columns, especially in dynamic SQL and type-checking scenarios.

#### Parameters

* `expr`: An expression of any type

#### Return Value

* string type
* Returns the name of the expression's data type
* For primitive types, returns the type name (e.g., `'int'`, `'string'`, `'boolean'`)
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

* `typeof` returns a type name string, not a type object
* For decimal types, the full precision information is returned, e.g., `'decimal(10,2)'`
* For complex types (array, map, struct), the full nested type definition is returned
* Field names in `struct` types default to `col1`, `col2`, `col3`, etc.
* The function resolves types at compile time and does not change at runtime
* Common use cases:
  * Debugging and diagnostics
  * Generating type-related metadata
* Note: `TYPEOF` returns only type information and does not include NULL constraint information
* The function has minimal performance impact because type information is determined at compile time
