## COSINE_DISTANCE

```SQL
 COSINE_DISTANCE(vector1, vector2);
```
###  Description

cosine\_distance, or cosine distance, is a method for measuring the directional difference between two vectors. It is obtained by subtracting the cosine similarity from 1 and is used to reflect the degree of difference in direction between vectors. Cosine similarity itself is determined by calculating the cosine of the angle between two vectors, with values ranging from -1 to 1.

### Parameter Description

* vector1: The first vector, supported types are array\<decimal>, array\<double>, array\<float>
* vector2: The second vector, supported types are array\<decimal>, array\<double>, array\<float>

### Return Result

Returns a result of type double

### Example

* Calculate the distance between two vectors of type array\<decimal>
```SQL
SELECT cosine_distance(array(1bd, 2bd), array(2bd, 3bd)) as cosDis;
+----------------------+
|        cosDis        |
+----------------------+
| 0.007722123286332261 |
+----------------------+
```
* Calculate the distance between two vectors of type array\<double>
```SQL
SELECT cosine_distance(array(1d, 2d), array(2d, 3d)) as cosDis;
+----------------------+
|        cosDis        |
+----------------------+
| 0.007722123286332261 |
+----------------------+
```
* Calculate the distance between two vectors of type array\<float>
```SQL
SELECT cosine_distance(array(1f, 2f), array(2f, 3f)) as cosDis;
+----------------------+
|        cosDis        |
+----------------------+
| 0.007722123286332261 |
+----------------------+
```