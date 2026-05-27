### BITMAP_HAS_ALL 
```
bitmap_has_all(left, right)
```
####  Description
The BITMAP_HAS_ALL function is used to check whether the bitmap of the second parameter (right) is a subset of the first parameter (left). It returns true if all bits in the right bitmap are present in the left bitmap, otherwise it returns false.

#### Parameter Description
- left: The first input parameter of bitmap type.
- right: The second input parameter of bitmap type.

#### Return Type
The return value type is boolean.

#### Usage Example
1. Check if there is an inclusion relationship between two bitmaps:
```sql
SELECT bitmap_has_all(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3)));
-- Return result: true
```
In this example, the right bitmap (2, 3) is a subset of the left bitmap (1, 2, 3) because all the bits in the right bitmap are in the left bitmap, so it returns true.

2. Check if two bitmaps do not contain each other:
```sql
SELECT bitmap_has_all(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4)));
-- Return result: false
```
In this example, the right bitmap (2, 3, 4) is not a subset of the left bitmap (1, 2, 3) because the right bitmap contains bits (4) that are not in the left bitmap, so it returns false.

3. Check if one bitmap contains all the bits of another bitmap:
```sql
SELECT bitmap_has_all(bitmap_build(array(1, 2, 3, 4)), bitmap_build(array(3, 4)));
-- Return result: true
```
In this example, the left bitmap (1, 2, 3, 4) contains all the bits of the right bitmap (3, 4), so it returns true.

4. Check if a bitmap does not contain all the bits of another bitmap:
```sql
SELECT bitmap_has_all(bitmap_build(array(1, 2, 3, 5)), bitmap_build(array(4, 5, 6)));
-- Return result: false
```
In this example, the left bitmap (1, 2, 3, 5) does not contain all the bits of the right bitmap (4, 5, 6) because the left bitmap is missing the bits (4) and (6) from the right bitmap, so it returns false.

#### Notes
- When the left or right parameter is NULL, the function will return NULL.
- Ensure the input parameter types are correct, otherwise, it may cause the function to execute incorrectly or return unexpected results.

Through the above examples and explanations, you can better understand the purpose and usage of the BITMAP_HAS_ALL function. In practical applications, you can check the containment relationship of bitmaps as needed for corresponding data processing and analysis.