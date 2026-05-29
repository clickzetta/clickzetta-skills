## DOT_PRODUCT

```SQL
 DOT_PRODUCT(vector1, vector2);
```
###  Description

The dot product (also known as the scalar product or inner product) is a fundamental algebraic operation that takes two sequences of numbers of equal length (usually coordinate vectors) and returns a single number.

### Parameter Description

* vector1: The first vector, supported types are array\<decimal>, array\<double>, array\<float>
* vector2: The second vector, supported types are array\<decimal>, array\<double>, array\<float>

### Return Result

Returns a result of type double

### Example

* Calculate the dot product between two vectors of type array\<decimal>
```SQL
SELECT dot_product(array(1bd, 2bd, 3bd), array(4bd, 5bd, 6bd)) AS res;

+------+
| res  |
+------+
| 32.0 |
+------+
```
* Calculate the dot product between two vectors of type array\<double>
```SQL
SELECT dot_product(array(1d, 2d, 3d), array(4d, 5d, 6d)) AS res;
+------+
| res  |
+------+
| 32.0 |
+------+
```
* Calculate the dot product between two vectors of type array\<float>
```SQL
SELECT dot_product(array(1f, 2f, 3f), array(4f, 5f, 6f)) AS res;
+------+
| res  |
+------+
| 32.0 |
+------+
```