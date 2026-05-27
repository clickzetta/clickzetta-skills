### Array Intersection Check Function: hasany_clickhouse

#### Description
`hasany_clickhouse` is an alias for `array_overlap`, used to check whether two arrays share at least one common element. Specifically, the function behaves as follows:
1. If the two arrays `array1` and `array2` share at least one common element, the function returns `true`.
2. If the two arrays have no intersection, but at least one array contains a `null` value and both arrays are non-empty, the function returns `null`.
3. In all other cases, the function returns `false`.

#### Parameters
- `array1`, `array2`: The two arrays to compare, of type `array<T>`, where `T` can be any data type supported by the database.

#### Return Type
- Returns `boolean` or `null`.

#### Examples
1. Check whether two arrays intersect:
```sql
SELECT hasany_clickhouse(array(1, 2, 3), array(3, 4, 5)); -- Returns true
```
2. When an array contains `null`:
```sql
SELECT hasany_clickhouse(array(1, 2, 3), array(null, 4, 5)); -- Returns false
```
3. Two non-empty arrays with no intersection:
```sql
SELECT hasany_clickhouse(array(1, 2, 3), array(4, 5, 6)); -- Returns false
```
4. One array is empty:
```sql
SELECT hasany_clickhouse(array(), array(1, 2, 3)); -- Returns false
```
5. Both arrays are empty:
```sql
SELECT hasany_clickhouse(array(), array()); -- Returns false
```


#### Notes
- When using the `hasany_clickhouse` function, ensure that the element types of the arrays are consistent, otherwise comparison may fail.
- If an array contains `null` values, the function behavior differs — this should be noted carefully.
