### IPV4_NUM_TO_STRING 

####  Description
The `ipv4_num_to_string` function is used to convert the numeric form of an IPv4 address (considering only the lower 32 bits) into a readable string form. This function takes a bigint type parameter and returns a string type IPv4 address.

#### Parameter Description
* `expr`: A bigint type parameter representing the numeric form of the IPv4 address.

#### Return Result
* Returns a string representing the readable form of the input IPv4 address.

#### Usage Example
The following shows several usage examples of the `ipv4_num_to_string` function:
```sql
-- Example 1: Convert a common loopback address
SELECT ipv4_num_to_string(2130706433); -- Returns '127.0.0.1'

-- Example 2: Convert a public address
SELECT ipv4_num_to_string(3232235777); -- Returns '192.168.1.1'

-- Example 3: Convert a private address
SELECT ipv4_num_to_string(1730150097); -- Returns '103.31.254.209'

-- Example 4: Convert a special-purpose address
SELECT ipv4_num_to_string(2130706432); -- Returns '127.0.0.0'
```
Through the above example, we can see that the `ipv4_num_to_string` function can accurately convert a numeric IPv4 address into its corresponding string form, making it convenient for users to perform network-related queries and operations.