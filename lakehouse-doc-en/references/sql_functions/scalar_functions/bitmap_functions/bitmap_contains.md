### BITMAP_CONTAINS 

---

####  Description
The BITMAP_CONTAINS function is used to check whether a bitmap data structure contains a specified value. When the given value exists in the bitmap, the function returns true; otherwise, it returns false.

#### Function Syntax
```
bitmap_contains(bitmap, value)
```
- **bitmap**: The bitmap type data to be checked.
- **value**: The integer value to be queried.

#### Return Result
Returns a boolean value indicating whether the specified value is contained in the bitmap.

#### Usage Example
The following example demonstrates how to use the BITMAP_CONTAINS function to check if a specific value is contained in the bitmap:

1. Check if the bitmap contains the value 2:
```sql
SELECT bitmap_contains(bitmap_build(array(1, 2, 3)), 2);
-- Result: true
```
2. Check if the bitmap contains the value 4:
```sql
SELECT bitmap_contains(bitmap_build(array(1, 2, 3)), 4);
-- Result: false
```
3. Create a bitmap containing multiple values and check if it contains a specific value:
```sql
SELECT bitmap_contains(bitmap_build(array(10, 20, 30, 40, 50)), 30);
-- Result: true
```
4. Check if the bitmap contains multiple different values:
```sql
SELECT bitmap_contains(bitmap_build(array(1, 15, 22, 33, 45, 55, 66, 77, 88, 99, 100)), 45);
-- Result: true
```
#### Notes
- Ensure that the value parameter is an integer, otherwise it may cause the function to execute incorrectly.
- The BITMAP_CONTAINS function is suitable for quickly checking whether a specific value exists in a large amount of data, improving query efficiency.

Through the above examples and explanations, you can better understand the purpose and usage of the BITMAP_CONTAINS function. In practical applications, you can create and query bitmap data structures as needed to achieve efficient data management and querying.