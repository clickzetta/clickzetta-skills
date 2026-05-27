### BITMAP_ANDNOT
```
bitmap_andnot(left, right)
```
#### Function Description
The BITMAP_ANDNOT function is used to compute the set difference (andnot operation) of two bitmap type parameters, returning a new bitmap type result. This function has a high performance advantage when processing large amounts of data.

#### Parameter Description
* left, right: These two parameters are both of bitmap type, representing the left and right bitmap data for the set difference operation, respectively.

#### Return Result
Returns a new bitmap type result that contains elements present in the left bitmap but not in the right bitmap.

####  Example
1. Compute the set difference of two simple bitmaps:
```sql
SELECT bitmap_andnot('01', '10');
```
Result: `00`

2. Use an array to construct a bitmap and calculate the set difference:
```sql
SELECT bitmap_to_array(bitmap_andnot(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4))));
```
Result: Represented as an array `[1]`, the specific bitmap printing method supported by the client may vary.

3. Calculate the difference between two large-scale bitmap sets:
```sql
SELECT bitmap_to_array(bitmap_andnot(
  bitmap_build(array(1, 2, 3, 4, 5, 6, 7, 8, 9)),
  bitmap_build(array(3, 4, 5, 6, 7, 8, 9, 10))
));
```
Results: Represented as an array `[1, 2]`

4. In actual business scenarios, the BITMAP_ANDNOT function can be used to filter user interest tags. For example, exclude tags that certain user groups are not interested in from the interest tag library:
```sql
SELECT user_interests
FROM users
WHERE user_id = 1;
```
Assuming the above query results are:
```
user_id | user_interests
--------+-----------------
1       | 0000000000001111
```
Now we need to exclude tags 4 and 5 that the user is not interested in:
```sql
SELECT bitmap_andnot(user_interests, bitmap_build(array(4, 5)))
FROM users
WHERE user_id = 1;
```
Results:
```
user_id | user_interests
--------+-----------------
1       | 0000000000000101
```
By using the BITMAP_ANDNOT function, we successfully excluded the uninterested tags 4 and 5 from the user interest tags.