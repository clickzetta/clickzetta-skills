# ARRAY

`ARRAY` is a data type used to represent a value composed of a sequence of elements of the same type. This data type can store a series of elements sharing the same data type, making it convenient for unified management and operations.

## Syntax

```sql
ARRAY <elementType>
```

- `elementType`: Specifies the data type of the elements in the array.

## ARRAY Constant Format

```
select [1,3,4];
```

This format represents an array constant. When defining an array constant, **do not use quotes**, because quotes will cause it to be recognized as a string type, and the string `'[1,3,4]'` cannot be directly converted to `array<int>` type using `CAST`.

## Examples

1. Create an integer array:

   ```sql
   SELECT ARRAY(1, 2, 3);
   ```

   Result:

   | result    |
   | --------- |
   | [1, 2, 3] |

2. Convert an integer array to a string array:

   ```sql
   SELECT CAST(ARRAY(1, 2, 3) AS ARRAY<STRING>);
   ```

   Result:

   | result          |
   | --------------- |
   | ["1", "2", "3"] |

3. Get the data type of array elements:

   ```sql
   SELECT typeof(ARRAY(1.2, 1.4, 1.8));
   ```

   Result:

   | result              |
   | ------------------- |
   | array<decimal(2,1)> |

4. Create a nested array (an array containing other arrays):

   ```sql
   SELECT CAST(ARRAY(ARRAY(10, 20), ARRAY(30, 40)) AS ARRAY<ARRAY<DECIMAL(10,2)>>);
   ```

   Result:

   | result                           |
   | -------------------------------- |
   | [[10.00, 20.00], [30.00, 40.00]] |

5. Get a specific element from an array:

   ```sql
   SELECT a[0] FROM VALUES(ARRAY(10, 20, 30)) AS T(a);
   ```

   Result:

   | result |
   | ------ |
   | 10     |

6. Use `ARRAY_CONTAINS` to check if a specific element exists in an array:

   ```sql
   SELECT array_contains(ARRAY(1, 2, 3),3);
   ```

   Result:

   | Result |
   | ------ |
   | true   |

7. Sort an array:

   ```sql
   SELECT ARRAY_SORT(array(2, 1, 3));
   ```

   Result:

   | result    |
   | --------- |
   | [1, 2, 3] |

8. Merge two arrays:

   ```sql
   SELECT array_union(array(2, 1, 3, 3), array(3, 5));
   ```

   Result:

   | result    |
   | --------- |
   | [2,1,3,5] |
