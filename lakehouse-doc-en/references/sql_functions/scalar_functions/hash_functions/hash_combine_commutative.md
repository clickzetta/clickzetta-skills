### HASH_COMBINE_COMMUTATIVE
```sql
hash_combine_commutative(value1, value2, ...)
```
#### Description
Performs commutative hash combination on multiple values. Unlike the regular `hash_combine`, the result of `hash_combine_commutative` is not affected by the order of parameters, meaning `hash_combine_commutative(a, b, c)` yields the same result as `hash_combine_commutative(c, b, a)`. This function is commonly used in scenarios requiring hash computation for unordered sets.

#### Parameters
* `value1`, `value2`, ...: any type, the values to combine hashes for. At least one parameter is required.

#### Return Result
* `bigint` type
* Returns the commutative hash combination result of all input values
* The result is independent of parameter order

#### Examples
```sql
SELECT hash_combine_commutative(1, 2, 3);
-- result: 10777284388
```

```sql
SELECT hash_combine_commutative(3, 2, 1);
-- result: 10777284388
```

```sql
SELECT
  general_murmurhash3(bitmap_build(array(1L, 2L, 3L))),
  hash_combine_commutative(
    general_murmurhash3(3L),  -- size
    general_murmurhash3(1L),
    general_murmurhash3(2L),
    general_murmurhash3(3L)
  );
-- result: -4327490212287121842	-4327490212287121842
```

```sql
SELECT general_murmurhash3(map(1, '2', 3, '4')),
  hash_combine(
    general_murmurhash3(size(map(1, '2', 3, '4'))),
    hash_combine_commutative(
      hash_combine(general_murmurhash3(1), general_murmurhash3('2')),
      hash_combine(general_murmurhash3(3), general_murmurhash3('4'))
    )
  );
-- result: -7258238779908172255	-7258238779908172255
```

#### Notes
* `hash_combine_commutative` is commutative, meaning parameter order does not affect the result
* Difference from `hash_combine`: `hash_combine` considers parameter order, while `hash_combine_commutative` does not
* Commonly used for computing hash values of unordered data structures (such as `set`, `bitmap`, `map`)
* This function works together with `general_murmurhash3` to implement hash computation for complex data structures
* Suitable for scenarios requiring deduplication or comparison of sets, where the order of elements is typically not important
