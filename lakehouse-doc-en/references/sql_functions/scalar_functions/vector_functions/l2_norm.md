## L2_NORM

```SQL
 L2_NORM(vector1);
```
###  Description

The L2 norm (L2 Norm), also known as the Euclidean Norm, is a property of a vector that represents the square root of the sum of the squares of the vector's elements. The L2 norm provides a way to measure the magnitude of a vector and is very important in machine learning and data analysis. It is often used in the process of regularization to prevent model overfitting by penalizing large weight values, thereby promoting the model's generalization ability.

### Parameter Description

* vector1: The first vector, supported types are array\<decimal>, array\<double>, array\<float>

### Return Result

Returns a result of type double

### Example

* Calculate the sum of the absolute values of a vector of type array\<decimal>.
```SQL
 SELECT l2_norm(array(1bd, 2bd)) as l2norm;
+------------------+
|      l2norm      |
+------------------+
| 2.23606797749979 |
+------------------+
```
* Calculate the sum of the absolute values of an array\<double> type vector.
```SQL
 SELECT l2_norm(array(1d, 2d)) as l2norm;
+------------------+
|      l2norm      |
+------------------+
| 2.23606797749979 |
+------------------+
```
* Calculate the total sum of the absolute values of an array\<float> type vector.
```SQL
 SELECT l2_norm(array(1f, 2f)) as l2norm;
+------------------+
|      l2norm      |
+------------------+
| 2.23606797749979 |
+------------------+
```