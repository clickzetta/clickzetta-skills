### ARRAY_PREPEND
```sql
array_prepend(array, element)
```

#### Description
Inserts an element at the beginning of an array, returning a new array.

#### Parameters
* array: `array<T>` - The input array
* element: `T` - The element to insert

#### Returns
* `array<T>` - A new array with the element inserted at the beginning

#### Examples
```sql
SELECT array_prepend(array(1, 2, 3), 3);
-- Result: [3,1,2,3]
```

```sql
SELECT array_prepend(array(1, 2, 3), cast(null as int));
-- Result: [null,1,2,3]
```

```sql
SELECT array_prepend(cast(array() as array<int>), 1);
-- Result: [1]
```
