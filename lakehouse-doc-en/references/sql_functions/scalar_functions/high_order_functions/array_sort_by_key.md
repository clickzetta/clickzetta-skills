### ARRAY_SORT_BY_KEY

#### Description:
The ARRAY_SORT_BY_KEY function is used to sort an array. Based on the provided lambda expression, this function can sort the array elements according to a specific attribute.

#### Parameters:
* array: The array to be sorted, of type `array<T>`, where T can be any data type that supports sorting.
* e -> key: A lambda expression used to extract the key value for sorting from the array element e. This expression should return a sortable data type.

#### Return Value:
Returns a new array that has been sorted according to the specified key value, of type `array<T>`.

#### Example :
```sql
-- Example 1: Sort an array of dates by month
SELECT ARRAY_SORT_BY_KEY(
  ARRAY(
    DATE '2023-10-10',
    DATE '2021-01-10',
    DATE '2022-03-10',
    DATE '2022-02-10',
    DATE '2020-09-10',
    DATE '2023-11-10'
  ),
  x -> MONTH(x)
);
-- Result: [2021-01-10, 2022-02-10, 2022-03-10, 2020-09-10, 2023-10-10, 2023-11-10]

-- Example 2: Sort an array of strings by string length
SELECT ARRAY_SORT_BY_KEY(
  ARRAY(
    'apple',
    'banana',
    'cherry',
    'date'
  ),
  x -> LENGTH(x)
);
-- Result: ['date', 'apple', 'banana', 'cherry']
```