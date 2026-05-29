### NEGATIVE
```sql
negative(expr)
```
#### Description
Returns the negation of expr, equivalent to `-expr`.
#### Parameters
* `expr`: Numeric type (`smallint`/`tinyint`/`int`/`bigint`/`decimal`/`double`/`float`)
#### Returns
The return type is the same as the type of the parameter `expr`.
#### Examples
```sql
> SELECT negative(1);
-1
```
