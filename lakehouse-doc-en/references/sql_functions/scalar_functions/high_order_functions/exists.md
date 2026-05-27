### EXISTS 

#### Description
The EXISTS function is used to determine whether there is an element in the specified array that meets the given condition. By passing in a lambda expression, each element in the array can be evaluated. If at least one element meets the condition, the function returns true; otherwise, it returns false.

#### Parameters
* array: `array<T>` type, representing the array to be evaluated.
* x -> expr: A single-parameter lambda expression, where x corresponds to an element in the array; expr needs to return a boolean type, representing the condition to be evaluated.

#### Return Type
Returns a boolean value.

#### Example Usage
1. Determine if there is an element in the array that is less than or equal to 3:

```sql
SELECT EXISTS(array(1, null, 3), x -> x <= 3);
```
Results:
```
true
```
2. Determine if there are elements in the array that are less than or equal to 0:
```sql
SELECT EXISTS(array(1, null, 3), x -> x <= 0);
```
Result: Returns an empty string

3. Determine if all elements in the array are less than or equal to 0:
```sql
SELECT EXISTS(array(1, 3), x -> x <= 0);
```
Results:
```
false
```
4. Determine if there is at least one null value in the array:
```sql
SELECT EXISTS(array(1, null, 3), x -> x IS NULL);
```
Results:
```
true
```
5. Determine if there are even numbers in the array:
```sql
SELECT EXISTS(array(1, 2, 3, 4), x -> x % 2 = 0);
```
Results:
```
true
```
6. Determine if there are negative numbers in the array:
```sql
SELECT EXISTS(array(1, 2, 3, 4), x -> x < 0);
```
Results:
```
false
```
