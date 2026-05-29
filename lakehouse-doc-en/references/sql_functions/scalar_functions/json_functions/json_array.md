### JSON_ARRAY
```sql
json_array([val1, val2, ...])
```
#### Description
Constructs a JSON array. Accepts zero or more parameters, converting them into JSON array elements.

#### Parameters
* val1, val2, ... : Optional parameters, expressions of any type, used as array elements

#### Returns
* json type, representing a JSON array

#### Examples
```sql
SELECT json_array();
-- Result: []
```

```sql
SELECT json_array(1);
-- Result: [1]
```

```sql
SELECT json_array(NULL);
-- Result: [null]
```

```sql
SELECT json_array(NULL::int, 1, TRUE, FALSE, NULL::int, "a", 1.2, 1.3d);
-- Result: [null,1,true,false,null,"a","1.2",1.3]
```
#### Notes
* Supports various basic types, including integers, floating-point numbers, booleans, strings, and NULL.
* The returned JSON array is space-compressed.
