# HAMMING_DISTANCE

```sql
HAMMING_DISTANCE(vector1, vector2);
```

## Description

Computes the [Hamming Distance](https://en.wikipedia.org/wiki/Hamming_distance) between two vectors of equal length. Hamming distance is the number of positions at which the corresponding elements of two equal-length strings/vectors are different.

## Parameter Description

* `vector1`: The first vector, supported type `vector\<tinyint>`
* `vector2`: The second vector, supported type `vector\<tinyint>`

Note: Both vectors must have the same length.

## Return Result

Returns a `bigint` value representing the number of positions where elements differ between the two vectors.

## Examples

* Compute the Hamming distance between two `vector\<tinyint>` vectors

```sql
SELECT HAMMING_DISTANCE(VECTOR(1y, 0y, 1y), VECTOR(1y, 1y, 0y)) as hamming_dis;
+-------------+
| hamming_dis |
+-------------+
| 2           |
+-------------+
```

* Compute the Hamming distance between longer `tinyint` vectors

```sql
SELECT HAMMING_DISTANCE(VECTOR(1y, 0y, 1y, 0y), VECTOR(1y, 0y, 0y, 1y)) as hamming_dis;
+-------------+
| hamming_dis |
+-------------+
| 2           |
+-------------+
```

* Compute the Hamming distance between identical vectors (result is 0)

```sql
SELECT HAMMING_DISTANCE(VECTOR(1y, 1y, 0y), VECTOR(1y, 1y, 0y)) as hamming_dis;
+-------------+
| hamming_dis |
+-------------+
| 0           |
+-------------+
```
