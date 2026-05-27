### BITMAP_CARDINALITY Function

#### Function Description
The BITMAP_CARDINALITY function is used to calculate the number of elements in a bitmap type. This function accepts a bitmap type parameter and returns a bigint type value representing the number of elements in the bitmap.

#### Parameter Description
- bitmap: The input bitmap type data.

#### Return Result
- Returns a bigint type value representing the number of elements in the bitmap.

#### Usage Example
1. Calculate the number of elements in a single bitmap:

<Notes>
</Notes>

<permalink>
</permalink>
   ```sql
   SELECT bitmap_cardinality(bitmap_build(ARRAY[1, 2, 3, 4, 5]));
   ```
Result:
   ```
   5
   ```
In the above example, we used the `bitmap_build` function to create a bitmap containing 1 to 5, and used the `bitmap_cardinality` function to calculate the number of elements in the bitmap, which is 5.

2. Calculate the number of elements after combining multiple bitmaps:
   ```sql
   SELECT bitmap_cardinality(bitmap_union(bitmap_build(ARRAY[1, 2]), bitmap_build(ARRAY[3, 4])));
   ```
Result:
   ```
   4
   ```
In this example, we created two bitmaps separately, one containing 1 and 2, and the other containing 3 and 4. Then we used the `bitmap_union` function to merge these two bitmaps, and finally used the `bitmap_cardinality` function to calculate the number of elements in the merged bitmap, which is 4.

3. Calculate the number of elements in the intersection of two bitmaps:
   ```sql
   SELECT bitmap_cardinality(bitmap_intersect(bitmap_build(ARRAY[1, 2, 3]), bitmap_build(ARRAY[2, 3, 4])));
   ```
Result:
   ```
   2
   ```
In this example, we created two bitmaps, one containing 1, 2, and 3, and the other containing 2, 3, and 4. Using the `bitmap_intersect` function, we calculate the intersection of the two bitmaps, and then use the `bitmap_cardinality` function to calculate the number of elements in the intersection result, which is 2.

Through the above example, you can better understand the usage and scenarios of the BITMAP_CARDINALITY function. In practical applications, you can create and manipulate bitmap type data as needed, and use this function to calculate the number of elements.