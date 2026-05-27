### MURMURHASH 
####  Description
The `murmurhash3_32` and `murmurhash3_64` functions use the MurmurHash3 algorithm to compute the hash value of a given expression. MurmurHash3 is a non-cryptographic hash function suitable for hash computations in distributed systems, offering good distribution and performance.

#### Parameter Description
- `expr`: Basic data type, can be a string, integer, float, etc.

#### Return Results
- `murmurhash3_32`: Returns an integer (int) representing the 32-bit hash value.
- `murmurhash3_64`: Returns a long integer (bigint) representing the 64-bit hash value.

####  Example
1. Compute the 32-bit hash value of a string:
```sql
SELECT murmurhash3_32('hello');
-- Result: 613153351
```
2. Calculate the 64-bit hash value of a string:
```sql
SELECT murmurhash3_64('hello');
-- Result: -8014657081559513573
```
3. Calculate and compare the hash values of different strings:
```sql
SELECT murmurhash3_32('world'), murmurhash3_64('world');
-- Result: -74040069  -5394866185914414384
```
4. Calculate the hash value of a numeric type:
```sql
SELECT murmurhash3_32(123), murmurhash3_64(123);
-- Result: 941089142 5808450433748234714
```
Through the above example, you can see how to use the MURMURHASH hash function to compute data of different types. These functions are very useful in scenarios such as data distribution and load balancing, and can help you quickly generate hash values for data.