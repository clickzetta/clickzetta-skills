### IPV6_NUM_TO_STRING

####  Description

The `ipv6_num_to_string` function is used to convert a binary-form IPv6 address into a readable string form. This function accepts a binary type parameter and returns a string type result.

#### Parameter Description

* `expr`: Binary type IPv6 address.

#### Return Result

* Returns a string type IPv6 address.

####  Example

The following example demonstrates how to use the `ipv6_num_to_string` function to convert a binary-form IPv6 address into a readable string form:

Convert the IPv6 address `::ffff:127.0.0.1` from string form to binary form, and then convert it back to string form:
```sql
SELECT ipv6_num_to_string(ipv6_string_to_num('::ffff:127.0.0.1'));
+------------------+
|       res        |
+------------------+
| ::ffff:127.0.0.1 |
+------------------+
```
#### Notes

* Please ensure that the input binary parameter is a valid IPv6 address.
* During the conversion process, if the input parameter is not a valid IPv6 address, the function will return an empty string.