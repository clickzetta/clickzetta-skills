# BITMAP_HAS_ANY

## Function Description

The BITMAP_HAS_ANY function is used to check if the left bitmap contains any of the elements in the right bitmap. In other words, this function is used to determine if there is an intersection between the two bitmaps.

## Syntax

```Plain
bitmap_has_any(left, right)
```

## Parameters

- `left`: The first parameter of type bitmap.
- `right`: The second parameter of type bitmap.

## Return Value

Returns a boolean value. If the left bitmap contains any element from the right bitmap, it returns `true`; otherwise, it returns `false`.

## Usage Examples

1. Check if two bitmaps intersect:

```sql
SELECT bitmap_has_any(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3)));
```

Result:

```
true
```

2. Two bitmaps have a partial intersection:

```sql
SELECT bitmap_has_any(bitmap_build(array(1, 2, 3, 4)), bitmap_build(array(3, 4)));
```

Result:

```
true
```

3. Determine whether one bitmap is completely contained within another bitmap:

```sql
SELECT bitmap_has_any(bitmap_build(array(1, 2, 3)), bitmap_build(array(1, 2, 3, 4)));
```

Result:

```
true
```

## Notes

- Ensure that the parameter types passed in are correct, otherwise it may cause the function to fail.
- The BITMAP_HAS_ANY function is mainly used for comparing bitmap type data and may not be applicable to other data types.
