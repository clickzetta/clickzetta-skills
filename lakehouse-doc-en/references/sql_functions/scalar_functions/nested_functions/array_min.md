###  ARRAY_MIN

####  Description
The `array_min` function is used to find and return the minimum value from the input array. When dealing with arrays of numeric types, this function will ignore `null` values. This allows users to easily handle arrays containing null values without worrying about their impact on the result.

#### Syntax
```
array_min(array)
```
#### Parameters
- `array`: Parameter of type `array<T>`, representing the array from which the minimum value will be found.

#### Return Value
- The return type is inferred from the element type of the input array: `T <- array<T>`. If the array is empty or all values are `null`, it returns `null`.

#### Usage Example

**Example 1:** Find the minimum value in an integer array
```sql
SELECT array_min(array(1, 5, 3, 2, 4));
```
Results:
```
1
```
**Example 2:** Handling arrays containing `null` values
```sql
SELECT array_min(array(1, null, 3, null, 2));
```
Results:
```
1
```
**Example 3:** Find the smallest floating-point value in an array
```sql
SELECT array_min(array(1.2, 4.5, 3.7, 2.9));
```
Results:
```
1.2
```
**Example 4:** Return the minimum value of an empty array
```sql
SELECT array_min(array());
```
Results are empty

**Example 5:** Handling an array with all `null` values
```sql
SELECT array_min(array(null, null, null));
```
Results are empty

Through the above example, you can see the application of the `array_min` function in different situations. This function is very suitable for use in scenarios where it is necessary to compare the size of elements in an array and find the minimum value.