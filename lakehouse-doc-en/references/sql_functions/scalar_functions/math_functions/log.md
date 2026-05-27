# LOG Function

## 1. Description

The `LOG` function computes the natural logarithm (base `e`) or the logarithm with a specified base of a given numeric value. It converts a positive number to its corresponding logarithmic value and is widely used in mathematical computation, data analysis, and scientific applications. By specifying a base, the `LOG` function can also compute logarithms for any base, meeting diverse computational needs.

## 2. Syntax

The syntax of the `LOG` function is as follows:

```sql
LOG(base, number)
```

### Parameters:

* `number`: Must be a positive number, representing the value for which to compute the logarithm.
* `base` (optional): Specifies the base of the logarithm. If not specified, the natural logarithm (base `e`) is used by default.

### Return value:

* The return value is the logarithm of `number`, of floating-point type.

## 3. Examples

^

Compute the logarithm with a specified base.

```sql
SELECT LOG(2, 8) AS log_base_2;
+------------+
| log_base_2 |
+------------+
| 3          |
+------------+
```

^
