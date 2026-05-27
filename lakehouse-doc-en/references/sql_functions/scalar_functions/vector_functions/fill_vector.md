### FILL_VECTOR Function

#### Overview

The FILL_VECTOR function creates a vector of the specified dimension and fills all elements with a given value. This function is commonly used to initialize fixed-value vectors, such as creating zero vectors, unit vectors, or reference vectors for vector operations.

#### Syntax

`fill_vector(dimension, fill_value)`

#### Parameter Description

* `dimension`: The dimension of the vector, must be a positive integer constant (determined at compile time), type INT. Specifies the number of elements in the generated vector.
* `fill_value`: The fill value used to populate each element of the vector. Supports the following types:
  - `TINYINT`: Generates a `vector(tinyint, N)` type vector
  - `INT` and other integer types (`SMALLINT`, `BIGINT`): Generates a `vector(int, N)` type vector
  - `FLOAT`, `DOUBLE`, `DECIMAL`: Generates a `vector(float, N)` type vector

#### Return Result

Returns a VECTOR type value where the vector dimension equals the `dimension` parameter, and all elements have the value of `fill_value`. The element type of the vector is determined by the type of `fill_value`.

#### Examples

1. Create a 3-dimensional float vector with all elements filled to 1.0:

    ```sql
    SELECT fill_vector(3, 1.0) AS res;
    +-----------+
    |    res    |
    +-----------+
    | [1,1,1]   |
    +-----------+
    ```

2. Create a 4-dimensional zero vector and use it with cosine_distance:

    ```sql
    SELECT cosine_distance(vector(1.0, 2.0, 3.0, 4.0), fill_vector(4, 1.0)) AS cos_dist;
    +---------------------+
    |      cos_dist       |
    +---------------------+
    | 0.13397459621556141 |
    +---------------------+
    ```

#### Notes

* The `dimension` parameter must be a positive integer constant determinable at compile time; dynamic expressions are not supported.
* `fill_value` does not support NULL; passing NULL will cause a semantic analysis error.
* The type of the fill value determines the element type of the vector: TINYINT generates `vector(tinyint, N)`, other integer types generate `vector(int, N)`, and floating-point and DECIMAL types generate `vector(float, N)`.
* fill_vector is commonly used to create reference vectors, for example when used with vector distance functions such as `cosine_distance` and `l2_distance`.
* The vector type is a specialized form of the array type and can be mutually converted and used interchangeably with the array type.
