### ARRAY_CONTAINS
```
array_contains(array, value)
```
####  Description
The ARRAY_CONTAINS function is used to determine whether an array contains a specified value. When the specified value exists in the array, the function returns true; otherwise, it returns false.

#### Parameter Description
- array: `array<T>`, represents the array to be searched.
- value: T type, represents the value of the element to be found.

#### Return Type
- Returns a boolean value. When the array contains the specified value, it returns true; otherwise, it returns false.

####  Example
1. Determine whether the array contains a specific element:
```sql
SELECT array_contains(array(1, 2, 3, 4, 5), 3); -- Returns true
SELECT array_contains(array(1, 2, 3, 4, 5), 6); -- Returns false
```
2. Using the ARRAY_CONTAINS function in actual queries:
   ```sql
   SELECT * FROM students
   WHERE array_contains(interests, 'Basketball');
   ```
The above query will return student records that contain the interest 'Basketball' in the interests array.

3. Multiple condition judgment:
   ```sql
   SELECT * FROM products
   WHERE array_contains(features, 'Bluetooth') AND array_contains(features, 'Waterproof');
   ```
The above query will return product records that contain both 'Bluetooth' and 'Waterproof' features in the features array.

By using the ARRAY_CONTAINS function, you can easily implement the judgment and filtering of array elements in SQL queries, thereby obtaining the required data more accurately.