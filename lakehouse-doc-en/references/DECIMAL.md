# DECIMAL

The `DECIMAL` type is used to represent numeric values with a specified maximum precision and fixed number of decimal places. This data type is particularly useful in financial, accounting, or other scenarios requiring precise numeric calculations, as it avoids the rounding errors inherent in floating-point arithmetic.

## Syntax
```
DECIMAL(precision, scale)
```
* `precision`: The total number of digits, including both sides of the decimal point. Valid range: 1 to 38.
* `scale`: The number of digits after the decimal point. Valid range: 0 to `precision`, and must not exceed `precision`.

## Literals

DECIMAL literals can be expressed using the `BD` suffix:

```sql
SELECT 3.14BD;  -- DECIMAL value 3.14
SELECT 1234BD;  -- DECIMAL value 1234
```

Decimal literals without the suffix (e.g., `3.14`) are also parsed as DECIMAL by default.

## Examples
```
SELECT CAST(1234.56 AS DECIMAL(10, 2));  -- Result: 1234.56
SELECT CAST(123.456 AS DECIMAL(5, 3));   -- Result: null
SELECT CAST(1.23 AS DECIMAL(4, 2));      -- Result: 1.23
SELECT CAST(1234 AS DECIMAL(6, 2));      -- Result: 1234.00
SELECT CAST(0.1234 AS DECIMAL(5, 4));    -- Result: 0.1234
```

## Arithmetic Operation Result Types

When performing arithmetic operations on two `DECIMAL` values, the result `precision` and `scale` are computed according to the following rules.

Let the two operands be `DECIMAL(p1, s1)` and `DECIMAL(p2, s2)`:

### Addition and Subtraction

```
result_precision = max(s1, s2) + max(p1 - s1, p2 - s2) + 1
result_scale     = max(s1, s2)
```

**Example**: `DECIMAL(10, 2) + DECIMAL(8, 4)` → `DECIMAL(13, 4)`
- scale = max(2, 4) = 4
- precision = 4 + max(10-2, 8-4) + 1 = 4 + 8 + 1 = 13

### Multiplication

```
result_precision = p1 + p2 + 1
result_scale     = s1 + s2
```

**Example**: `DECIMAL(10, 2) * DECIMAL(8, 3)` → `DECIMAL(19, 5)`
- precision = 10 + 8 + 1 = 19
- scale = 2 + 3 = 5

### Division

```
result_precision = p1 - s1 + s2 + max(6, s1 + p2 + 1)
result_scale     = max(6, s1 + p2 + 1)
```

**Example**: `DECIMAL(10, 2) / DECIMAL(8, 3)` → `DECIMAL(19, 11)`
- scale = max(6, 2 + 8 + 1) = 11
- precision = (10 - 2) + 3 + 11 = 22

### Modulo (%)

```
result_precision = min(p1 - s1, p2 - s2) + max(s1, s2)
result_scale     = max(s1, s2)
```

**Example**: `DECIMAL(10, 2) % DECIMAL(8, 3)` → `DECIMAL(8, 3)`
- scale = max(2, 3) = 3
- precision = min(10-2, 8-3) + 3 = 5 + 3 = 8

### Aggregate Functions

| Function | Result Precision | Result Scale |
|----------|-----------------|--------------|
| SUM      | p + 10          | s            |
| AVG      | p + 4           | s + 4        |

### Adjustment When Precision Exceeds 38

The maximum precision for DECIMAL is 38. When the computed precision from the formulas above exceeds 38, the system applies the following adjustment:

```
intDigits     = precision - scale
adjustedScale = max(min(scale, 6), 38 - intDigits)
final result  = DECIMAL(38, adjustedScale)
```

Core logic of the adjustment:
- Priority is given to preserving integer digits (integer digits = 38 - adjustedScale)
- Decimal places retain at least `min(scale, 6)` digits (at least 6, unless the original scale is less than 6)
- If integer digits already occupy all 38 positions, adjustedScale degrades to `min(scale, 6)`

**Example**: `DECIMAL(38, 7) + DECIMAL(10, 0)` theoretically results in `DECIMAL(39, 7)`. After adjustment for exceeding 38:
- intDigits = 39 - 7 = 32
- adjustedScale = max(min(7, 6), 38 - 32) = max(6, 6) = 6
- Final result: `DECIMAL(38, 6)`

### Operations with Integers

When DECIMAL is operated on with an integer type, the integer is first converted to the corresponding DECIMAL type, then calculated according to the rules above:

| Integer Type | Converted DECIMAL |
|-------------|-------------------|
| TINYINT     | DECIMAL(3, 0)     |
| SMALLINT    | DECIMAL(5, 0)     |
| INT         | DECIMAL(10, 0)    |
| BIGINT      | DECIMAL(20, 0)    |

If the integer is a literal constant, the system infers a more precise type based on the actual value (e.g., the constant `5` is inferred as `DECIMAL(1, 0)` rather than `DECIMAL(10, 0)`).

### Operations with Floating-Point Numbers

When DECIMAL is operated on with FLOAT/DOUBLE, the result type is DOUBLE.

## Usage Guidelines
- When `scale` is 0, the value is an integer.
- When `precision` and `scale` are equal, the value is a pure decimal (all digits are after the decimal point).
- During type conversion, if the result exceeds the `DECIMAL` type range, data truncation or rounding may occur.
- When comparing `DECIMAL` values, consider their precision and scale to avoid comparison errors due to rounding.
- In multi-step calculations, precision may gradually grow until adjustment is triggered. It is recommended to explicitly control precision using `CAST` at key computation points to avoid unexpected precision loss.

## Notes
- When using the `DECIMAL` type, choose `precision` and `scale` values appropriately based on actual requirements to ensure numeric accuracy and computational correctness.
- Division operations always have a scale of at least 6; even if both operands have a scale of 0, the division result retains 6 decimal places.
- When precision exceeds 38 and triggers adjustment, the decimal portion may be truncated, causing precision loss. If your use case is sensitive to decimal precision, plan the operands' precision and scale in advance to avoid triggering adjustment.
