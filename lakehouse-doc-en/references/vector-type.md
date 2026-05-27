# VECTOR
## Syntax
```SQL
vector(scalar_type, dimension)
vector(dimension)
```
* scalar type is the element type in the vector, optional, the default value is float type. Supports tinyint/int/float
* dimension: only specifies the dimension

**Example**:
```SQL
CREATE TABLE test_vector (
    vec1 vector(float, 512),  -- Specify element type as float, dimension as 512
    vec2 vector(512),         -- Default element type is float, dimension is 512
    vec3 vector(tinyint, 128) -- Specify element type as tinyint, dimension as 128
);
```
**Create Vector**:
```SQL
SELECT vector(1, 2, 3); -- Automatically infer the element type based on the provided values and create a vector
```
## Usage Restrictions

* The current version of the vector type does not support comparison operations, so it cannot be used in `ORDER BY` or `GROUP BY` clauses.
* The current client does not implement the vector type, but it is supported in the SQL engine. Therefore, when you execute a select statement with a vector type in the result, an error will occur: Unsupported data type: VECTOR\_TYPE

## Vector Type Conversion

Vector types support conversion to and from array types, as well as conversion from string types to vector types:

1. **Implicit Conversion**: In most cases, vector types can be directly converted to array types, trying to keep the element types unchanged.
2. **Array to Vector**: Array types can also be converted to vector types, but the array length must match the vector dimension. If they do not match, the conversion result will be `NULL`.
3. **String to Vector**: Strings in the format `'[1, 2, 3]'` can be converted to vector types (extra spaces will be ignored).

**Performance Tip**: For medium to high dimensions (dimension >= 128) vectors, using `cast('[1,2,3,4]' as vector(4))` is slightly more efficient than `vector(1,2,3,4)`.

**Example**:
```SQL
-- Implicitly convert vector to array
SELECT array_append(vector(1,2,3), 4);

-- Calculate the L2 distance between two vectors
SELECT l2_distance(array(1,2,3), vector(3,2,1));

-- Explicitly convert string to vector
SELECT cast('[1,2,3,4]' as vector(4));
```