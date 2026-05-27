# Logical and Bitwise Operators

## Logical NOT (!)
**Function**: Performs a logical NOT operation on an expression. If the expression is true, returns false; if the expression is false, returns true.

**Parameters**:
- `expr`: Boolean type expression.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT !true; -- Returns false
SELECT !false; -- Returns true
SELECT !NULL; -- Returns NULL
```

## Bitwise NOT (~)
**Function**: Performs a bitwise NOT operation on the expression, turning every 0 into 1 and every 1 into 0.

**Parameters**:
- `expr`: Integer type expression.

**Return Result**:
- A value of the same type as the input expression.

**Example**:
```sql
SELECT ~0; -- Returns -1
```

## Not Equal (!=)
**Function**: Compares two expressions and returns true if they are not equal.

**Parameters**:
- `expr1`: Boolean type expression.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 1 != 0; -- Returns true
SELECT 10 != 10; -- Returns false
SELECT 10 != NULL; -- Returns NULL
```

## Modulus (%)
**Function**: Returns the remainder of dividing two numeric expressions.

**Parameters**:
- `expr1`: Numeric type expression, including float, double, decimal, tinyint, smallint, int, bigint.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- A value of the same type as the input parameters.

**Example**:
```sql
SELECT 2 % 1.8; -- Returns 0.2
SELECT -10 % 3; -- Returns -1
```

## Multiplication (*)
**Function**: Returns the product of two numeric expressions.

**Parameters**:
- `expr1`: Numeric type expression, including float, double, decimal, tinyint, smallint, int, bigint.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- A value of the same type as the input parameters.

**Example**:
```sql
SELECT 1.4 * 2.3; -- Returns 3.22
```

## Addition (+)
**Function**: Returns the sum of two numeric expressions.

**Parameters**:
- `expr1`: Numeric type expression, including float, double, decimal, tinyint, smallint, int, bigint.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- A value of the same type as the input parameters.

**Example**:
```sql
SELECT 1.4 + 2.3; -- Returns 3.7
```

## Positive Sign (+)
**Function**: Returns the value of the expression without making any changes.

**Parameters**:
- `expr`: Numeric type expression.

**Return Result**:
- A value of the same type as the input parameter.

**Example**:
```sql
SELECT +10; -- Returns 10
SELECT +(-10); -- Returns -10
```

## Subtraction (-)
**Function**: Returns the difference between two numeric expressions.

**Parameters**:
- `expr1`: Numeric type expression, including float, double, decimal, tinyint, smallint, int, bigint.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- A value of the same type as the input parameters.

**Example**:
```sql
SELECT 3.3 - 10; -- Returns -6.7
```

## Negative Sign (-)
**Function**: Returns the negative value of the expression.

**Parameters**:
- `expr`: Numeric type expression.

**Return Result**:
- A value of the same type as the input parameter.

**Example**:
```sql
SELECT -(-10); -- Returns 10
SELECT -(1.1); -- Returns -1.1
```

## Division (/)
**Function**: Returns the quotient of dividing two numeric expressions.

**Parameters**:
- `expr1`: Numeric type expression, including float, double, decimal.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- A value of the same type as the input parameters.

**Example**:
```sql
SELECT 3.3 / 1.5; -- Returns 2.2
SELECT 9L / 2L; -- Returns 4.5
```

## Integer Division (DIV)
**Function**: Returns the integer part of dividing two numeric expressions.

**Parameters**:
- `dividend`: The dividend, a numeric type expression.
- `divisor`: The divisor, an expression of the same type as the dividend.

**Return Result**:
- Integer type value.

**Example**:
```sql
SELECT 10 DIV 3; -- Returns 3
SELECT 20 DIV 4; -- Returns 5
SELECT 7 DIV 2; -- Returns 3
```

## Less Than (<)
**Function**: Compares two expressions and returns true if the first expression is less than the second.

**Parameters**:
- `expr1`: Expression of a comparable type.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 1 < 2; -- Returns true
SELECT 10 < 10; -- Returns false
SELECT 'a' < 'b'; -- Returns true
```

## Less Than or Equal (<=)
**Function**: Compares two expressions and returns true if the first expression is less than or equal to the second.

**Parameters**:
- `expr1`: Expression of a comparable type.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 1 <= 2; -- Returns true
SELECT 10 <= 10; -- Returns true
SELECT 'a' <= 'b'; -- Returns true
```

## Greater Than (>)
**Function**: Compares two expressions and returns true if the first expression is greater than the second.

**Parameters**:
- `expr1`: Expression of a comparable type.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 2 > 1; -- Returns true
SELECT 10 > 10; -- Returns false
SELECT 'b' > 'a'; -- Returns true
```

## Greater Than or Equal (>=)
**Function**: Compares two expressions and returns true if the first expression is greater than or equal to the second.

**Parameters**:
- `expr1`: Expression of a comparable type.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 2 >= 1; -- Returns true
SELECT 10 >= 10; -- Returns true
SELECT 'b' >= 'a'; -- Returns true
```

## Equal (=)
**Function**: Compares two expressions and returns true if they are equal.

**Parameters**:
- `expr1`: Expression of a comparable type.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 1 = 1; -- Returns true
SELECT 10 = 5; -- Returns false
SELECT 10 = NULL; -- Returns NULL
```

## Equal (==)
**Function**: Compares two expressions and returns true if they are equal. Functionally identical to `=`.

**Parameters**:
- `expr1`: Expression of a comparable type.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 1 == 1; -- Returns true
SELECT 10 == 5; -- Returns false
SELECT 10 == NULL; -- Returns NULL
```

## Not Equal (<>)
**Function**: Compares two expressions and returns true if they are not equal. Functionally identical to `!=`.

**Parameters**:
- `expr1`: Expression of a comparable type.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 1 <> 0; -- Returns true
SELECT 10 <> 10; -- Returns false
SELECT 10 <> NULL; -- Returns NULL
```

## NULL-safe Equal (<=>)
**Function**: Compares two expressions. Similar to `=`, but with special handling for NULL values. If both values are NULL, returns true; if only one is NULL, returns false. Equivalent to the SQL standard `IS NOT DISTINCT FROM`.

**Parameters**:
- `expr1`: Expression of a comparable type.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 1 <=> 1; -- Returns true
SELECT NULL <=> NULL; -- Returns true
SELECT 1 <=> NULL; -- Returns false
SELECT NULL <=> 1; -- Returns false
```

## Logical AND (AND)
**Function**: Performs a logical AND operation on two boolean expressions. Returns true only if both expressions are true.

**Parameters**:
- `expr1`: Boolean type expression.
- `expr2`: Boolean type expression.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT true AND true; -- Returns true
SELECT true AND false; -- Returns false
SELECT false AND false; -- Returns false
SELECT true AND NULL; -- Returns NULL
```

## Logical OR (OR)
**Function**: Performs a logical OR operation on two boolean expressions. Returns true if at least one expression is true.

**Parameters**:
- `expr1`: Boolean type expression.
- `expr2`: Boolean type expression.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT true OR false; -- Returns true
SELECT false OR false; -- Returns false
SELECT false OR NULL; -- Returns NULL
SELECT true OR NULL; -- Returns true
```

## Logical NOT (NOT)
**Function**: Performs a logical NOT operation on a boolean expression. Functionally identical to the `!` operator.

**Parameters**:
- `expr`: Boolean type expression.

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT NOT true; -- Returns false
SELECT NOT false; -- Returns true
SELECT NOT NULL; -- Returns NULL
```

## Bitwise AND (&)
**Function**: Performs a bitwise AND operation on two integer expressions.

**Parameters**:
- `expr1`: Integer type expression.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- A value of the same type as the input expressions.

**Example**:
```sql
SELECT 12 & 10; -- Returns 8 (binary: 1100 & 1010 = 1000)
SELECT 7 & 3; -- Returns 3 (binary: 0111 & 0011 = 0011)
```

## Bitwise OR (|)
**Function**: Performs a bitwise OR operation on two integer expressions.

**Parameters**:
- `expr1`: Integer type expression.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- A value of the same type as the input expressions.

**Example**:
```sql
SELECT 12 | 10; -- Returns 14 (binary: 1100 | 1010 = 1110)
SELECT 7 | 3; -- Returns 7 (binary: 0111 | 0011 = 0111)
```

## Bitwise XOR (^)
**Function**: Performs a bitwise XOR operation on two integer expressions.

**Parameters**:
- `expr1`: Integer type expression.
- `expr2`: Expression of the same type as `expr1`.

**Return Result**:
- A value of the same type as the input expressions.

**Example**:
```sql
SELECT 12 ^ 10; -- Returns 6 (binary: 1100 ^ 1010 = 0110)
SELECT 7 ^ 3; -- Returns 4 (binary: 0111 ^ 0011 = 0100)
```

## String Concatenation (||)
**Function**: Concatenates two string expressions.

**Parameters**:
- `expr1`: String type expression.
- `expr2`: String type expression.

**Return Result**:
- String type value.

**Example**:
```sql
SELECT 'Hello' || ' ' || 'World'; -- Returns 'Hello World'
SELECT 'abc' || 'def'; -- Returns 'abcdef'
SELECT 'value: ' || 123; -- Returns 'value: 123'
```


## Type Cast (::)
**Function**: Converts an expression to a specified data type. This is PostgreSQL-style type cast syntax, equivalent to `CAST(expr AS type)`. Chained casts are supported.

**Syntax**:
```sql
expr::type
expr::type1::type2  -- Chained cast
```

**Example**:
```sql
SELECT '123'::int; -- Returns 123
SELECT 3.14::int; -- Returns 3
SELECT '2024-01-01'::date; -- Returns 2024-01-01
SELECT '123'::int::string; -- Chained cast, returns '123'
```

## IS [NOT] DISTINCT FROM
**Function**: NULL-safe equality comparison. Unlike `=`, returns true when both values are NULL (instead of NULL), and returns false when one value is NULL and the other is not (instead of NULL). `IS NOT DISTINCT FROM` is equivalent to `<=>`.

**Syntax**:
```sql
expr1 IS DISTINCT FROM expr2
expr1 IS NOT DISTINCT FROM expr2
```

**Return Result**:
- Boolean type value, never returns NULL.

**Example**:
```sql
SELECT 1 IS DISTINCT FROM 1; -- Returns false
SELECT 1 IS DISTINCT FROM 2; -- Returns true
SELECT NULL IS DISTINCT FROM NULL; -- Returns false
SELECT 1 IS DISTINCT FROM NULL; -- Returns true
SELECT 1 IS NOT DISTINCT FROM 1; -- Returns true
SELECT NULL IS NOT DISTINCT FROM NULL; -- Returns true
```

## BETWEEN ... AND
**Function**: Determines whether the value of an expression falls within a specified range (inclusive of boundaries).

**Syntax**:
```sql
expr BETWEEN lower AND upper
expr NOT BETWEEN lower AND upper
```

**Return Result**:
- Boolean type value. `expr BETWEEN lower AND upper` is equivalent to `expr >= lower AND expr <= upper`.

**Example**:
```sql
SELECT 5 BETWEEN 1 AND 10; -- Returns true
SELECT 15 NOT BETWEEN 1 AND 10; -- Returns true
SELECT date '2024-06-15' BETWEEN date '2024-01-01' AND date '2024-12-31'; -- Returns true
```

## LIKE ANY / LIKE SOME / LIKE ALL
**Function**: Matches an expression against multiple patterns using LIKE. `LIKE ANY` (or `LIKE SOME`) returns true if any pattern matches; `LIKE ALL` returns true only if all patterns match.

**Syntax**:
```sql
expr LIKE ANY (pattern1, pattern2, ...)
expr LIKE SOME (pattern1, pattern2, ...)
expr LIKE ALL (pattern1, pattern2, ...)
expr NOT LIKE ANY (pattern1, pattern2, ...)
expr NOT LIKE ALL (pattern1, pattern2, ...)
```

**Return Result**:
- Boolean type value.

**Example**:
```sql
SELECT 'hello' LIKE ANY ('%llo', '%world'); -- Returns true
SELECT 'hello' LIKE ALL ('h%', '%o'); -- Returns true
SELECT 'hello' LIKE ALL ('h%', '%x'); -- Returns false
SELECT 'hello' NOT LIKE ANY ('%x', '%y'); -- Returns true
```

## ILIKE
**Function**: Case-insensitive LIKE matching. Usage is identical to LIKE, but matching ignores case. Also supports the `ESCAPE` clause and `ANY`/`ALL` forms.

**Syntax**:
```sql
expr ILIKE pattern
expr ILIKE pattern ESCAPE escape_char
expr NOT ILIKE pattern
expr ILIKE ANY (pattern1, pattern2, ...)
```

**Example**:
```sql
SELECT 'Hello' ILIKE 'hello'; -- Returns true
SELECT 'Hello' ILIKE 'HELLO%'; -- Returns true
SELECT 'ABC' NOT ILIKE 'abc'; -- Returns false
```

## IS [NOT] TRUE / FALSE / UNKNOWN
**Function**: Determines whether the value of a boolean expression is TRUE, FALSE, or UNKNOWN (NULL). Unlike direct comparison, these predicates do not return NULL due to NULL input.

**Syntax**:
```sql
expr IS TRUE
expr IS NOT TRUE
expr IS FALSE
expr IS NOT FALSE
expr IS UNKNOWN
expr IS NOT UNKNOWN
```

**Return Result**:
- Boolean type value, never returns NULL.

**Example**:
```sql
SELECT true IS TRUE; -- Returns true
SELECT NULL IS TRUE; -- Returns false
SELECT NULL IS UNKNOWN; -- Returns true
SELECT false IS NOT FALSE; -- Returns false
SELECT NULL IS NOT UNKNOWN; -- Returns false
```

## RLIKE / REGEXP
**Function**: Matches a string using a regular expression. `RLIKE` and `REGEXP` are synonyms.

**Syntax**:
```sql
expr RLIKE pattern
expr REGEXP pattern
expr NOT RLIKE pattern
expr NOT REGEXP pattern
```

**Return Result**:
- Boolean type value. Returns true if expr matches the regular expression pattern.

**Example**:
```sql
SELECT 'hello123' RLIKE '[a-z]+[0-9]+'; -- Returns true
SELECT 'hello' REGEXP '^h.*o$'; -- Returns true
SELECT 'abc' NOT RLIKE '[0-9]+'; -- Returns true
```


## Operator Precedence

The following table lists the precedence of operators and predicates, from highest to lowest. Operators on the same row have the same precedence and are all left-associative (unless otherwise noted).

| Precedence | Operator / Predicate | Associativity | Description |
| --- | --- | --- | --- |
| 1 | `.` | Left | Field access (table.column, struct.field) |
| 2 | `::` | Left | Type cast |
| 3 | `[]` | Left | Array/Map subscript |
| 4 | `+` `-` `~` (unary) | Right | Positive sign, negative sign, bitwise NOT |
| 5 | `*` `/` `%` `DIV` | Left | Multiplication, division, modulus, integer division |
| 6 | `+` `-` `\|\|` | Left | Addition, subtraction, string concatenation |
| 7 | `&` | Left | Bitwise AND |
| 8 | `^` | Left | Bitwise XOR |
| 9 | `\|` | Left | Bitwise OR |
| 10 | `=` `<=>` `!=` `<>` `<` `<=` `>` `>=` | Left | Comparison operators |
| 11 | `BETWEEN` `IN` `LIKE` `ILIKE` `RLIKE` `REGEXP` | — | Range, set, pattern matching |
| 12 | `IS NULL` `IS TRUE` `IS FALSE` `IS DISTINCT FROM` | — | IS predicates |
| 13 | `NOT` | Right | Logical NOT |
| 14 | `AND` | Left | Logical AND |
| 15 | `OR` | Left | Logical OR |

**Notes**:
- The lower the precedence number, the higher the precedence.
- Parentheses `()` can be used to change the order of operations.
- `NOT` can serve as a prefix modifier for predicates such as `BETWEEN`, `IN`, `LIKE` (e.g., `NOT BETWEEN`); in this case, it is part of the predicate and is not affected by the precedence of logical NOT.
