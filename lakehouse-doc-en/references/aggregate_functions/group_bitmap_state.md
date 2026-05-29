### GROUP_BITMAP_STATE Function

#### Description
The `GROUP_BITMAP_STATE` function is used to construct a bitmap type result based on the input integer expression (expr). This function can effectively aggregate a set of integer data into a bitmap during data processing, facilitating further data analysis and processing.

#### Parameter Description
* expr: Integer data, representing the input data that needs to construct the bitmap.

#### Return Result
Returns a bitmap type of data, which contains the bitmap information constructed based on the input parameter expr.

#### Usage Example
The following is an example of using the `GROUP_BITMAP_STATE` function to demonstrate how to group by the value of a certain field and construct the corresponding bitmap:

### GROUP_BITMAP_STATE Function

#### Description
The `GROUP_BITMAP_STATE` function is used to construct a bitmap type result based on the input integer expression (expr). This function can effectively aggregate a set of integer data into a bitmap during data processing, facilitating further data analysis and processing.

#### Parameter Description
* expr: Integer data, representing the input data that needs to construct the bitmap.

#### Return Result
Returns a bitmap type of data, which contains the bitmap information constructed based on the input parameter expr.

#### Usage Example
The following is an example of using the `GROUP_BITMAP_STATE` function to demonstrate how to group by the value of a certain field and construct the corresponding bitmap:

```sql
SELECT GROUP_BITMAP_STATE(user_id) 
FROM user_table 
GROUP BY group_id;
-- Group user_id by group_id and construct the corresponding bitmap
```

<Notes>
This function is particularly useful in scenarios where you need to perform bitmap operations on grouped data.
</Notes>

### GROUP_BITMAP_STATE Function

#### Description
The `GROUP_BITMAP_STATE` function is used to construct a bitmap type result based on the input integer expression (expr). This function can effectively aggregate a set of integer data into a bitmap during data processing, facilitating further data analysis and processing.

#### Parameter Description
* expr: Integer data, representing the input data that needs to construct the bitmap.

#### Return Result
Returns a bitmap type of data, which contains the bitmap information constructed based on the input parameter expr.

#### Usage Example
The following is an example of using the `GROUP_BITMAP_STATE` function to demonstrate how to group by the value of a certain field and construct the corresponding bitmap:

```sql
SELECT GROUP_BITMAP_STATE(user_id) 
FROM user_table 
GROUP BY group_id;
-- Group user_id by group_id and construct the corresponding bitmap
```

<Notes>
This function is particularly useful in scenarios where you need to perform bitmap operations on grouped data.
</Notes>
```sql
SELECT c, bitmap_to_array(GROUP_BITMAP_STATE(v)) AS bitmap_array
FROM VALUES ('a', 1), ('a', 2), ('a', 2), ('b', 3) AS v(c, v)
GROUP BY c;
```
After executing the above query, you will get the following result:
```
c    bitmap_array
---  -------------
a    [1, 2]
b    [3]
```
In this example, we first create a table with four records, where column c is the classification field and column v is the integer field that needs to build a bitmap. By using `GROUP_BY` to group by column c and applying the `GROUP_BITMAP_STATE` function to process the values of column v, we get the bitmap array corresponding to each classification.

#### More Examples
To gain a deeper understanding of the usage of the `GROUP_BITMAP_STATE` function, we can look at some more examples:

1. Construct a bitmap containing multiple groups:
```sql
SELECT c, GROUP_BITMAP_STATE(v) AS bitmap
FROM VALUES ('a', 1), ('a', 2), ('b', 3), ('c', 4), ('c', 4), ('d', 5) AS v(c, v)
GROUP BY c;
```
Results:
```
c    bitmap
---  -----
a    [1, 2]
b    [3]
c    [4]
d    [5]
```
2. For groups containing duplicate values, the `GROUP_BITMAP_STATE` function will merge the duplicate integer values into a single bitmap:
```sql
SELECT c, GROUP_BITMAP_STATE(v) AS bitmap
FROM VALUES ('a', 1), ('a', 1), ('b', 2), ('b', 2), ('c', 3) AS v(c, v)
GROUP BY c;
```
Results:
```
c    bitmap
---  -----
a    [1]
b    [2]
c    [3]
```
Through these examples, we can see the powerful functionality of the `GROUP_BITMAP_STATE` function when handling grouped data. It can help us quickly aggregate a set of integer data into a bitmap, thereby providing convenience for subsequent data analysis and processing.