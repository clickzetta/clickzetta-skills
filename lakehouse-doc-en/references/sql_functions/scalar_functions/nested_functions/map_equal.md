### MAP_EQUAL 

####  Description
The MAP_EQUAL function is used to compare two Map data structures (hereinafter referred to as maps) to determine if they are exactly the same. If the key-value pairs of the two maps are completely consistent, the function returns true; otherwise, it returns false.

#### Syntax
```
MAP_EQUAL(m1, m2)
```

#### Parameter Description
- m1, m2: The two maps that need to be compared.

#### Return Result
Returns a boolean value. If the two maps are exactly the same, it returns true; otherwise, it returns false.

#### Usage Example
1. Compare two identical maps:
   ```
   SELECT MAP_EQUAL(MAP('k1', 'v1', 'k2', 'v2'), MAP('k1', 'v1', 'k2', 'v2'));
   → true
   ```
2. Compare two different maps (key-value pairs are inconsistent):
   ```
   SELECT MAP_EQUAL(MAP('k1', 'v1', 'k2', 'v2'), MAP('k1', 'v3', 'k2', 'v4'));
   → false
   ```
3. Compare two different maps (keys are inconsistent):
   ```
   SELECT MAP_EQUAL(MAP('k1', 'v1', 'k3', 'v3'), MAP('k2', 'v2', 'k3', 'v3'));
   → false
   ```