### IPV6_STRING_TO_NUM 

#### Description

The `ipv6_string_to_num` function is used to convert an IPv6 address from its string form to the binary format used for internal storage. This function is very useful for processing and comparing IPv6 addresses, as it can eliminate differences between various representation methods.

#### Function Syntax
```
ipv6_string_to_num(expr)
```
#### Parameter Description

* `expr`: A valid IPv6 address string.

#### Return Result

* Returns a binary format of the IPv6 address.

#### Usage Example

1. Convert the IPv6 address to binary format:
   ```sql
   SELECT ipv6_string_to_num('2001:0db8:85a3:0000:0000:8a2e:0370:7334') as res;
   +---------------------------------------------------+
   |                        res                        |
   +---------------------------------------------------+
   | [20 01 0d b8 85 a3 00 00 00 00 8a 2e 03 70 73 34] |
   +---------------------------------------------------+
   ```
The result is a binary format IPv6 address.

2. Compare two IPv6 addresses:
   ```sql
   SELECT ipv6_string_to_num('2001:0db8:85a3:0000:0000:8a2e:0370:7334') = ipv6_string_to_num('2001:0db8:85a3:0:0:8a2e:370:7334');
   ```
The result is true, indicating that the two IPv6 addresses are equal.

#### Notes

* Ensure that the input IPv6 address string is valid, otherwise the function will return an error.