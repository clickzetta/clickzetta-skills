### IPV4_STRING_TO_NUM 
```
ipv4_string_to_num(expr)
```
####  Description
The IPV4_STRING_TO_NUM function is used to convert an IPv4 address from its string form to an internally used 64-bit integer (bigint) format. This is useful for performing numerical comparisons and calculations based on IP addresses.

#### Parameter Description
* expr: string type, representing the IPv4 address string to be converted.

#### Return Result
* Returns a 64-bit integer (bigint) representing the numerical value corresponding to the input IPv4 address string.

####  Example
1. Convert the local loopback address to a numerical value:
```sql
SELECT ipv4_string_to_num("127.0.0.1");
-- Return result: 2130706433
```
2. Compare two IPv4 addresses numerically:
```sql
SELECT ipv4_string_to_num('192.168.1.1') > ipv4_string_to_num('192.168.1.2');
-- Return result: false
```
3. Calculate the number of hosts within an IPv4 address range:
```sql
SELECT (ipv4_string_to_num('192.168.1.255') - ipv4_string_to_num('192.168.1.0') + 1) AS host_count;
-- Return result: 256
```
Through the above example, you can see the flexibility and practicality of the IPV4_STRING_TO_NUM function when handling IPv4 addresses. This function can help you perform numerical calculations and comparisons related to IP addresses more conveniently.