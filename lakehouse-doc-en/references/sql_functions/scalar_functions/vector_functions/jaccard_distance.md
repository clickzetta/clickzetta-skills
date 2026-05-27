# JACCARD_DISTANCE

```sql
JACCARD_DISTANCE(vector1, vector2);
```

## Description

Computes the [Jaccard Distance](https://en.wikipedia.org/wiki/Jaccard_index) between two vectors. Jaccard distance is defined as 1 - Jaccard similarity coefficient, used to measure the degree of difference between two sets. For binary vectors, Jaccard distance = 1 - |A∩B| / |A∪B|, where A and B represent the sets of non-zero elements in the two vectors respectively.

## Parameter Description

* `vector1`: The first vector, supported type `vector\<tinyint>`
* `vector2`: The second vector, supported type `vector\<tinyint>`

## Return Result

Returns a `double` value in the range [0, 1]. 0 indicates the two vectors are identical, 1 indicates they are completely different.

## Examples

* Compute the Jaccard distance between two `vector\<tinyint>` vectors

```sql
SELECT JACCARD_DISTANCE(VECTOR(1y, 0y, 1y), VECTOR(1y, 1y, 0y)) as jaccard_dis;
+----------------------+
|     jaccard_dis      |
+----------------------+
| 0.6666666269302368   |
+----------------------+
```

* Compute the Jaccard distance between longer `tinyint` vectors

```sql
SELECT JACCARD_DISTANCE(VECTOR(1y, 0y, 1y, 0y), VECTOR(1y, 0y, 0y, 1y)) as jaccard_dis;
+----------------------+
|     jaccard_dis      |
+----------------------+
| 0.6666666269302368   |
+----------------------+
```

* Compute the Jaccard distance between identical vectors (result is 0)

```sql
SELECT JACCARD_DISTANCE(VECTOR(1y, 1y, 0y), VECTOR(1y, 1y, 0y)) as jaccard_dis;
+-------------+
| jaccard_dis |
+-------------+
| 0           |
+-------------+
```
