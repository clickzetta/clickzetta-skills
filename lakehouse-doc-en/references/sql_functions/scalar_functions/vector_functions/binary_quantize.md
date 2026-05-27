# BINARY_QUANTIZE

```sql
BINARY_QUANTIZE(vec);
```

## Description

Binarizes the input vector by converting each floating-point element into a binary representation. Typically used for vector compression and fast similarity computation, where each bit represents the binarization result of the corresponding element in the original vector (typically using 0 as the threshold: >= 0 becomes 1, < 0 becomes 0).

## Parameter Description

* `vec`: Input vector, supported types are `vector<float>`, `vector<double>`, and other numeric vector types.

## Return Result

Returns a `vector<tinyint>` type result, where each `tinyint` element (typically 8 bits) packs the binarization results of multiple elements from the original vector.

## Examples

* Binarize a floating-point vector

```sql
SELECT BINARY_QUANTIZE(VECTOR(1.5f, -0.5f, 2.0f, -1.0f, 0.5f, -2.0f, 1.0f, 0.0f)) as binary_vec;
+------------+
| binary_vec |
+------------+
| [-86]      |
+------------+
```

* Binarize a vector with all positive values

```sql
SELECT BINARY_QUANTIZE(VECTOR(1.0f, 2.0f, 3.0f, 4.0f)) as binary_vec;
+------------+
| binary_vec |
+------------+
| [-16]      |
+------------+
```

* Binarize a vector with all negative values

```sql
SELECT BINARY_QUANTIZE(VECTOR(-1.0f, -2.0f, -3.0f, -4.0f)) as binary_vec;
+------------+
| binary_vec |
+------------+
| [0]        |
+------------+
```
