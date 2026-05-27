### VECTOR

```sql
vector(value1, value2, ...)
```

#### Description

Creates a vector type value. A vector is a special array type designed specifically for vector computation and similarity search.

#### Parameters

* value1, value2, ...: Numeric values, can be tinyint, smallint, int, bigint, float, double, or decimal.

#### Return Result

* Returns a vector type containing all the parameter values.
* The element type of the vector is automatically inferred from the input parameters.
* The dimension of the vector equals the number of parameters.

#### Examples

```sql
> SELECT vector(1, 2, 3);
[1,2,3]

> SELECT typeof(vector(1Y, 2Y, 3Y));
vector(tinyint,3)

> SELECT typeof(vector(1, 2, 3));
vector(int,3)

> SELECT typeof(vector(1.0F, 2.0F, 3.0F));
vector(float,3)

> SELECT typeof(vector(1.0, 2.0, 3.0));
vector(float,3)

> SELECT size(vector(1, 2, 3));
3
```

#### More Examples

```sql
-- Create vectors of different types
> SELECT vector(1Y, 2Y, 3Y);
[1,2,3]

> SELECT vector(1.0, 2.0, 3.0, 4.0);
[1,2,3,4]

-- Vectors can be compared
> SELECT vector(1, 2, 3) == vector(1, 2, 3);
true

> SELECT vector(1, 2, 3) == vector(2, 3, 4);
false

-- Vectors can be used as arrays
> SELECT array_distinct(vector(1, 2, 1));
[1,2]

-- Vectors can be sorted
> SELECT v FROM VALUES (vector(2, 3, 4)), (vector(1, 2, 3)) AS t(v) ORDER BY v;
[1,2,3]
[2,3,4]
```

#### Notes

* The vector type is a specialized form of the array type, specifically optimized for vector computation.
* Supported element types: tinyint (i8), smallint (i16), int (i32), bigint (i64), float, double.
* Vectors can be mutually converted and used interchangeably with the array type.
* Vectors support basic operations such as equality comparison and sorting.
* Vectors are commonly used for vector similarity search, machine learning, and recommendation systems.
* Use the `size()` function to get the dimension of a vector.
