# conv Function

## Introduction

The `conv` function is used to convert a number from one base to another. It supports conversions between bases 2 and 36 and can handle both signed and unsigned numbers.

## Syntax

```sql
conv(num, fromBase, toBase)
```

## Parameters

- **`num`**: `STRING` type, representing the number to be converted. The number is expressed as a string, and its base is specified by `fromBase`.
- **`fromBase`**: `INTEGER` type, representing the base of the source number. The value range is from 2 to 36.
- **`toBase`**: `INTEGER` type, representing the target base. The value range is from 2 to 36.

## Return Value

Returns a `STRING` type result, representing the converted number.

- If `fromBase` is less than 2 or greater than 36, or if `toBase` is less than 2 or greater than 36, the function returns `NULL`.
- If `toBase` is negative, the number `num` is interpreted as a signed number; otherwise, it is treated as an unsigned number.

## Examples

 Example 1: Binary to Decimal

```sql
> SELECT conv('100', 2, 10);
4
```

 Example 2: Hexadecimal to Decimal

```sql
> SELECT conv('1A', 16, 10);
26
```


 Example 3: Decimal to Hexadecimal

```sql
> SELECT conv('255', 10, 16);
FF
```