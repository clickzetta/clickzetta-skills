# VECTOR_ADD_SCALAR

```sql
VECTOR_ADD_SCALAR(vec, scalar);
```

## Description

Adds the specified scalar value to each element in the vector. This is a broadcast addition operation between a vector and a scalar, adding the scalar value to every component of the vector.

## Parameter Description

* `vec`: Input vector, supported types include `vector\<float>`, `vector\<double>`, and other numeric vector types.
* `scalar`: The scalar value to add to each element, must be of type `integer`.

## Return Result

Returns a vector of the same type as the input vector, where each element is the result of adding the scalar value to the corresponding element of the original vector.

## Examples

* Add an integer scalar to each element of a float vector

```sql
SELECT VECTOR_ADD_SCALAR(VECTOR(1.0f, 2.0f, 3.0f), 5) as result_vec;
+------------+
| result_vec |
+------------+
| [6,7,8]    |
+------------+
```

* Add a negative integer scalar to each element of a vector

```sql
SELECT VECTOR_ADD_SCALAR(VECTOR(10.0f, 20.0f, 30.0f), -5) as result_vec;
+------------+
| result_vec |
+------------+
| [5,15,25]  |
+------------+
```

* Add zero to each element (returns the original vector)

```sql
SELECT VECTOR_ADD_SCALAR(VECTOR(1.5f, 2.5f, 3.5f), 0) as result_vec;
+---------------+
|  result_vec   |
+---------------+
| [1.5,2.5,3.5] |
+---------------+
```
