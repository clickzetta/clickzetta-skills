## L2_NORMALIZE

```SQL
 L2_DISTANCE(vector1);
```
###  Description

It is commonly used in data preprocessing and machine learning models to ensure that vectors have a uniform standard when being compared or calculated. L2 normalization adjusts the length of the vector by dividing it by its L2 norm (i.e., the square root of the sum of the squares of the vector elements), so that the L2 norm of the normalized vector is 1.

### Parameter Description

* vector1: The first vector, supported types are array\<decimal>, array\<double>, array\<float>

### Return Result

Returns a result of type array\<double>

### Example

* Calculate normalization for array\<decimal> type
```SQL
 SELECT l2_normalize(array(3bd, 4bd));


+---------------------------------+
| l2_normalize(`array`(3BD, 4BD)) |
+---------------------------------+
| [0.6,0.8]                       |
+---------------------------------+
```
* Normalize array\<double> type
```SQL
 SELECT l2_normalize(array(3d, 4d));
+-------------------------------+
| l2_normalize(`array`(3d, 4d)) |
+-------------------------------+
| [0.6,0.8]                     |
+-------------------------------+
```
* Normalize array\<float> type
```SQL
 SELECT l2_normalize(array(3f, 4f));
+-------------------------------+
| l2_normalize(`array`(3f, 4f)) |
+-------------------------------+
| [0.6,0.8]                     |
+-------------------------------+
```