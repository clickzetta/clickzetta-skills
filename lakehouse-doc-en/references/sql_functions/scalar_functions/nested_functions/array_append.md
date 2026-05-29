### ARRAY_APPEND
```sql
array_append(array, element)
```

#### Description
Appends an element to the end of an array, returning a new array.

#### Parameters
* `array`: `array<T>` - The input array
* `element`: `T` - The element to append

#### Returns
* `array<T>` - A new array with the element appended.

#### Examples
```sql
SELECT array_append(array(1, 2, 3), 3);
-- Result: [1,2,3,3]
```

```sql
SELECT array_append(array(1, 2, 3), cast(null as int));
-- Result: [1,2,3,null]
```

```sql
SELECT array_append(cast(array() as array<int>), 1);
-- Result: [1]
```
