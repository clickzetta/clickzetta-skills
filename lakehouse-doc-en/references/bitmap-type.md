# Bitmap Type Documentation

Bitmap is an efficient data type in Singdata Lakehouse for storing and processing collection-type data. The Bitmap in Singdata Lakehouse is **64-bit**, optimized using the Roaring Bitmap compression algorithm, enabling efficient storage and processing of large-scale integer sets.

Bitmap represents integer sets through bit-level operations, providing extremely high space compression rates. Compared to directly storing arrays, Bitmap can significantly reduce storage costs while providing fast set operation performance.

### Bitmap Characteristics

* **64-bit Integer Support**: Supports storing integers in the range of 0 to 2^64-1
* **Efficient Compression**: Uses Roaring Bitmap algorithm with minimal space overhead
* **Fast Operations**: Supports union, intersection, complement, and other set operations with excellent performance
* **Binary Serialization**: Can be converted to and from binary type for convenient data exchange
* **Flexible Querying**: Supports set inclusion checking, cardinality calculation, and other operations

## Syntax

### Creating a Table with Bitmap Column

```SQL
CREATE TABLE table_name (
    column_name bitmap
);
```

**Example**:

```SQL
CREATE TABLE bitmap_example (
    user_id bigint,
    preference_tags bitmap
);
```

### Building Bitmap Data

#### Using the bitmap\_build Function

Construct a Bitmap object from an integer array:

```SQL
bitmap_build(array_expression)
```

**Example**:

```SQL
INSERT INTO bitmap_example VALUES(1, bitmap_build(array(1, 3, 5, 7, 9))),(2, bitmap_build(array(2, 4, 6, 8, 10)));
```

#### Using the GROUP\_BITMAP\_STATE Function

Constructs a bitmap type result based on the input expression (expr). This function is typically used to perform grouping operations on integer type data and converts the unique values of each group into a bitmap array.

```SQL
GROUP_BITMAP_STATE(expr)
```

**Example**:

```SQL
INSERT INTO bitmap_example
SELECT user_id, group_bitmap_state(v) AS bitmap_array
FROM VALUES (1, 1), (1, 2), (1, 2), (2, 3) AS v(user_id, v)
GROUP BY user_id;
```

## Notes

### Functional Limitations

1. **No Comparison Operations**: Bitmap type does not support direct comparison operations (<, >, =, !=, etc.)
2. **No Sorting or Grouping**: Bitmap columns cannot be used in ORDER BY, GROUP BY, or DISTINCT operations
3. **Cannot Be Used as Keys**: Bitmap cannot be used as a table's PRIMARY KEY, PARTITION KEY, or CLUSTER KEY
4. **Query Display Requirements**: Singdata Java version must be >3.0.21

### Data Validity

1. **Valid Integer Range**: The input array for bitmap\_build function must contain valid integer values
2. **Binary Conversion**: When using binary\_to\_bitmap for conversion, the input binary data converted using bitmap\_to\_binary must be in valid Bitmap serialization format
3. **NULL Handling**: Bitmap itself can be NULL, but NULL values in the array will be ignored

### Performance Considerations

1. **Ideal Use Cases**: Bitmap is best suited for storing sparse integer sets or large integer sets
2. **Set Operations**: Large-scale set operations should be completed at the database layer rather than in the application layer

## Common Bitmap Functions

For more Bitmap functions, refer to [Bitmap documentation](https://claude.ai/chat/sql_functions/scalar_functions/bitmap_functions/bitmap_to_binary.md)

### Data Construction Functions

**bitmap\_build**

Constructs a Bitmap object from an integer array.

```SQL
bitmap_build(array<integer>)
```

| Parameter | Description                          |
| --------- | ------------------------------------ |
| array     | Array expression containing integers |

**Return Value**: bitmap

***

### Data Conversion Functions

**bitmap\_to\_array**

Converts a Bitmap to an integer array.

```SQL
bitmap_to_array(bitmap)
```

**Return Value**: array\<integer>

***

**bitmap\_to\_binary**

Converts a Bitmap to binary type.

```SQL
bitmap_to_binary(bitmap)
```

**Return Value**: binary

***

**binary\_to\_bitmap**

Converts binary type to Bitmap.

```SQL
binary_to_bitmap(binary)
```

**Return Value**: bitmap

***

### Set Operation Functions

**bitmap\_and**

Computes the intersection (AND operation) of two Bitmaps.

```SQL
bitmap_and(bitmap1, bitmap2)
```

**Return Value**: bitmap

***

**bitmap\_or**

Computes the union (OR operation) of two Bitmaps.

```SQL
bitmap_or(bitmap1, bitmap2)
```

**Return Value**: bitmap

***

**bitmap\_xor**

Computes the XOR (exclusive OR operation) of two Bitmaps.

```SQL
bitmap_xor(bitmap1, bitmap2)
```

**Return Value**: bitmap

***

### Statistical Functions

**bitmap\_cardinality**

Calculates the number of elements (cardinality) in a Bitmap.

```SQL
bitmap_cardinality(bitmap)
```

**Return Value**: bigint

***

### Query Functions

**bitmap\_contains**

Checks whether a Bitmap contains a specified integer.

```SQL
bitmap_contains(bitmap, element)
```

| Parameter | Description            |
| --------- | ---------------------- |
| bitmap    | Bitmap object          |
| element   | Integer value to check |

**Return Value**: boolean

***

## Examples

**Example 1: Create Table and Insert Data**

```SQL
CREATE TABLE bitmap_example (    user_id bigint,    preference_tags bitmap);
INSERT INTO bitmap_example VALUES(1, bitmap_build(array(1, 3, 5, 7, 9))),(2, bitmap_build(array(2, 4, 6, 8, 10))),(3, bitmap_build(array(1, 2, 3, 4, 5))),(4, bitmap_build(array(5, 6, 7, 8, 9, 10)));
```

**Example 2: Query Elements in Bitmap**

```SQL
SELECT user_id, bitmap_to_array(preference_tags) as tags FROM bitmap_example;
```

**Execution Result**:

| user\_id | tags                 |
| -------- | -------------------- |
| 1        | \[1, 3, 5, 7, 9]     |
| 2        | \[2, 4, 6, 8, 10]    |
| 3        | \[1, 2, 3, 4, 5]     |
| 4        | \[5, 6, 7, 8, 9, 10] |

**Example 3: Calculate Bitmap Cardinality (Element Count**)

```SQL
SELECT    user_id,    bitmap_cardinality(preference_tags) as tag_count FROM bitmap_example;
```

**Execution Result**:

| user\_id | tag\_count |
| -------- | ---------- |
| 1        | 5          |
| 2        | 5          |
| 3        | 5          |
| 4        | 6          |

**Example 4: Check if Bitmap Contains Specific Element**

**SQL Execution**:

```SQL
SELECT    user_id,    bitmap_to_array(preference_tags) as my_tags,    bitmap_contains(preference_tags, 5) as has_tag_5 FROM bitmap_example;
```

**Execution Result**:

| user\_id | my\_tags             | has\_tag\_5 |
| -------- | -------------------- | ----------- |
| 1        | \[1, 3, 5, 7, 9]     | TRUE        |
| 2        | \[2, 4, 6, 8, 10]    | FALSE       |
| 3        | \[1, 2, 3, 4, 5]     | TRUE        |
| 4        | \[5, 6, 7, 8, 9, 10] | TRUE        |

**Example 5: Calculate Common Tags Between Two Users (Intersection**)

SQL Execution:

```SQL
SELECT    bitmap_to_array(bitmap_and(        (SELECT preference_tags FROM bitmap_example WHERE user_id = 1),        (SELECT preference_tags FROM bitmap_example WHERE user_id = 3)    )) as common_tags;
```

Execution Result:

| common\_tags |
| ------------ |
| \[1, 3, 5]   |

**Example 6: Calculate All Tags Between Two Users (Union**)

SQL Execution:

```SQL
SELECT    bitmap_to_array(bitmap_or((SELECT preference_tags FROM bitmap_example WHERE user_id = 1),        (SELECT preference_tags FROM bitmap_example WHERE user_id = 2)    )) as union_tags;
```

Execution Result:

| union\_tags                      |
| -------------------------------- |
| \[1, 3, 5, 7, 9, 2, 4, 6, 8, 10] |

**Example 7: Bitmap and Binary Conversion**

SQL Execution:

```SQL
SELECT    user_id,    bitmap_to_array(preference_tags) as original_tags,    bitmap_to_array(binary_to_bitmap(bitmap_to_binary(preference_tags))) as restored_tags FROM bitmap_example;
```

Execution Result:

| user\_id | original\_tags       | restored\_tags       |
| -------- | -------------------- | -------------------- |
| 1        | \[1, 3, 5, 7, 9]     | \[1, 3, 5, 7, 9]     |
| 2        | \[2, 4, 6, 8, 10]    | \[2, 4, 6, 8, 10]    |
| 3        | \[1, 2, 3, 4, 5]     | \[1, 2, 3, 4, 5]     |
| 4        | \[5, 6, 7, 8, 9, 10] | \[5, 6, 7, 8, 9, 10] |

## Writing Bitmap Data Using SDK

### Java SDK Example

Use BulkloadStream in Singdata Java SDK to write Bitmap data in bulk. You need to use `RoaringBitmap` to construct Bitmap objects.

**Constructing Bitmap Objects**:

```Java
import org.roaringbitmap.longlong.Roaring64NavigableMap;
Roaring64NavigableMap roaring64Bitmap = new Roaring64NavigableMap();
roaring64Bitmap.add(1);
roaring64Bitmap.add(3);
roaring64Bitmap.add(5);
roaring64Bitmap.add(7);
row.setValue("preference_tags", roaring64Bitmap);
```

**Maven Dependency**

Add the following dependency to `pom.xml` with version greater than 3.0.23:

```XML
<dependency>
    <groupId>com.clickzetta</groupId>
    <artifactId>clickzetta-java</artifactId>
    <version>${version]</version>
</dependency>
```

### Python SDK Example

**Python Dependencies**:

```python
pip install clickzetta clickzetta-ingestion pyroaring
```

**Constructing Bitmap Objects**:

```python
tags = [i for i in range(1, 21, 2)]
bitmap = pyroaring.BitMap64(tags)
row.set_value('preference_tags', bitmap)
```

## Best Practices

1. **Choose Appropriate Data Types**: When you need to store integer sets, prioritize Bitmap, especially for large or sparse collections

2. **Complete Operations at Database Layer**: Fully leverage Bitmap's set operation functions to complete intersection, union, and other operations at the database layer, reducing data transfer

3. **Use Conversion Functions Appropriately**:

   1. Use `bitmap_to_array` for display and debugging
   2. Use `bitmap_to_binary` for persistent storage

4. **Performance Optimization**:

   1. Use Bitmap instead of Array for set operations on large-scale datasets
   2. Use `bitmap_cardinality` for counting instead of converting to array and then counting


