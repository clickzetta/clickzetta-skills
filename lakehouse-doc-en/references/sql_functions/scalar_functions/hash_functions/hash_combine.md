### HASH_COMBINE 

####  Description
The `hash_combine` function is used to combine multiple hash values h1, h2, ..., hN into a new hash value. The characteristic of this function is that the order of the combined values will affect the final hash value.

The `hash_combine_commutative` function is similar to `hash_combine`, and is also used to combine multiple hash values h1, h2, ..., hN into a new hash value. The difference is that the order of the combined values does not affect the final hash value, satisfying the commutative property.

#### Parameter Description
* h1, h2, ... hN: bigint type, representing the hash values to be combined.

#### Return Result
Returns a value of bigint type, representing the combined hash value.

####  Example
The following example demonstrates how to use the `hash_combine` and `hash_combine_commutative` functions:
```sql
-- Using the hash_combine function
SELECT hash_combine(1, 2, 3) AS hash_combine_result1;
-- Result: 175247765312

SELECT hash_combine(3, 2, 1) AS hash_combine_result2;
-- Result: 175247756320

-- Using the hash_combine_commutative function
SELECT hash_combine_commutative(1, 2, 3) AS hash_commutative_result1;
-- Result: 10777284388

SELECT hash_combine_commutative(3, 2, 1) AS hash_commutative_result2;
-- Result: 10777284388
```
From the above example, it can be seen that the `hash_combine` function changes the result when the order of the combined values changes; while the `hash_combine_commutative` function keeps the result unchanged when the order of the combined values changes.

#### Notes
* When the number of combined hash values is small, these two functions can be used to merge the hash values. However, if a large number of hash values need to be merged, it is recommended to use other methods to avoid performance issues.
* In practical applications, you can choose the appropriate function based on specific needs. If the order of the combined values matters, you can use the `hash_combine` function; if the order does not matter, you can use the `hash_combine_commutative` function.