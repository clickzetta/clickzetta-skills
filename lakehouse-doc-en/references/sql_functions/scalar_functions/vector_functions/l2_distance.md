## L2_DISTANCE

```SQL
 L2_DISTANCE(vector1, vector2);
```
###  Description

Calculate the distance between two points (the values of the vectors are the coordinates) in Euclidean space ([Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance)).

### Parameter Description

* vector1: The first vector, supported types are array\<decimal>, array\<double>, array\<float>
* vector2: The second vector, supported types are array\<decimal>, array\<double>, array\<float>

### Return Result

Returns a result of type double

### Example

* Calculate the distance between two vectors of type array\<decimal>
```SQL
SELECT L2_distance(array(1bd, 2bd), array(2bd, 3bd)) as l2dis;
+--------------------+
|       l2dis        |
+--------------------+
| 1.4142135623730951 |
+--------------------+
```
* Calculate the distance between two vectors of type array\<double>
```SQL
SELECT L2_distance(array(1d, 2d), array(2d, 3d)) as l2dis;
+--------------------+
|       l2dis        |
+--------------------+
| 1.4142135623730951 |
+--------------------+
```
* Calculate the distance between two vectors of type array\<float>
```SQL
SELECT L2_distance(array(1f, 2f), array(2f, 3f)) as l2dis;
+--------------------+
|       l2dis        |
+--------------------+
| 1.4142135623730951 |
+--------------------+
```