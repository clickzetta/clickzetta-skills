## IS_IP_ADDRESS_IN_RANGE
## DESCRIPTION
`IS_IP_ADDRESS_IN_RANGE` is used to determine whether an IP address is within a certain network range. This function accepts an IP address and a network range represented in CIDR notation, returning a boolean value indicating whether the IP address is within the specified network range.

## Syntax
```SQL
IS_IP_ADDRESS_IN_RANGE(address,prefix)
```
## Parameter Description

* **address**: The IP address to be checked, which can be in the form of an IPv4 or IPv6 address string.
* **prefix**: Represents the network range in CIDR notation, also a string.

## Return Result

Returns true if the IP address is within the specified network range, and false if the IP address is not within the specified network range.

## Example

Example 1: IPv4 Address Range Check
```SQL
SELECT is_ip_address_in_range('127.0.0.1', '127.0.0.0/8') as res;
+------+
| res  |
+------+
| true |
+------+
```
Example 2: IPv6 Address Range Check
```SQL
SELECT is_ip_address_in_range('::ffff:192.168.0.1', '::ffff:192.168.0.0/120') as res;
+------+
| res  |
+------+
| true |
+------+
```