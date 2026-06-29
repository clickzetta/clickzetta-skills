# FORMAT

#### Introduction

The `FORMAT` function assembles arguments into a string using a printf-style format string. It is suited for generating formatted output with fixed prefixes, zero-padding, or controlled decimal places. Unlike `DATE_FORMAT`, `FORMAT` is a general-purpose string formatting function and is not specific to dates.

#### Syntax

```Plain
FORMAT(format_str, arg1[, arg2, ...])
```

#### Parameters

* `format_str`: A format template string containing plain characters and format placeholders.
* `arg1, arg2, ...`: Values that replace each placeholder in `format_str` in order.

Common placeholders:

| Placeholder | Meaning              | Example                                 |
|-------------|----------------------|-----------------------------------------|
| `%s`        | String               | `FORMAT('%s', 'hello')` → `hello`       |
| `%d`        | Integer (decimal)    | `FORMAT('%d', 42)` → `42`              |
| `%f`        | Floating-point       | `FORMAT('%f', 3.14)` → `3.140000`      |
| `%.2f`      | 2 decimal places     | `FORMAT('%.2f', 3.14159)` → `3.14`     |
| `%05d`      | Zero-pad integer to 5 digits | `FORMAT('%05d', 42)` → `00042` |
| `%%`        | Literal `%`          | `FORMAT('100%%')` → `100%`             |

#### Return Value

Returns a `VARCHAR` formatted string.

#### Examples

1. Basic usage — combine a string and an integer:

```sql
SELECT FORMAT('%s=%d', 'x', 42);
```

```
+--------------------------+
| format('%s=%d', 'x', 42) |
+--------------------------+
| x=42                     |
+--------------------------+
```

2. Control floating-point decimal places:

```sql
SELECT FORMAT('price: %.2f', 9.9);
```

```
+----------------------------+
| format('price: %.2f', 9.9) |
+----------------------------+
| price: 9.90                |
+----------------------------+
```

3. Zero-pad an integer (generate a fixed-width number):

```sql
SELECT FORMAT('order-%05d', 7);
```

```
+-------------------------+
| format('order-%05d', 7) |
+-------------------------+
| order-00007             |
+-------------------------+
```

4. Multi-argument mixed formatting:

```sql
SELECT FORMAT('user %s has %d points (%.1f%%)', 'alice', 320, 64.5);
```

```
+---------------------------------------------------------------+
| format('user %s has %d points (%.1f%%)', 'alice', 320, 64.5)  |
+---------------------------------------------------------------+
| user alice has 320 points (64.5%)                             |
+---------------------------------------------------------------+
```

#### Notes

* `FORMAT` is a string formatting function; `DATE_FORMAT` is a date formatting function. Their placeholder syntax differs — do not mix them.
* The number of placeholders must match the number of subsequent arguments. Extra arguments are ignored; behavior is undefined when arguments are insufficient.
* Use `%%` to insert a literal `%` character in the output.

#### Related Functions

* [DATE_FORMAT](../date_functions/date_format.md): Date formatting function that uses date-specific placeholders such as `%Y`, `%m`, and `%d`.
* [CONCAT](concat.md): String concatenation without format control.
* [PRINTF](printf.md): An alias function with the same behavior as `FORMAT` (if supported).
