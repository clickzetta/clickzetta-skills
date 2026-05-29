### ARRAY_COMPACT
```sql
array_compact(array)
```

#### Description
Removes all null values from an array, returning a new array without nulls.

#### Parameters
* array: `array<T>` - The input array

#### Returns
* `array<T>` - A new array with all null elements removed
* Returns an empty array `[]` if all elements in the array are null or the array is empty

#### Examples
```sql
SELECT array_compact(array(null));
-- Result: []
```

```sql
SELECT array_compact(array());
-- Result: []
```

```sql
SELECT array_compact(array(1, 3, null, 4));
-- Result: [1,3,4]
```

```sql
SELECT array_compact(array(null, 3, null));
-- Result: [3]
```
