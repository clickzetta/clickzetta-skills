###COLLATION\_SORT\_KEY


####  Description
The COLLATION\_SORT\_KEY function generates a sort key for the input string based on the specified character set, which is used to sort the string according to the rules of the particular character set.

#### Syntax
```
collection_sort_key(str, coll)
```
* str: The input string.
* coll: The specified character set.

#### Return Value
Returns a binary value representing the sort key generated for the input string according to the specified character set.

####  Example
1. Sort strings according to the specified character set:
```
SELECT s, collation_sort_key(s, 'en') AS sort_key
FROM ('hello', 'apple', 'banana', 'pear', 'strawberry', 'watermelon', 'world') AS t(s)
ORDER BY sort_key;
```
The result is as follows:
```
s           | sort_key
------------|----------
apple       | 0100000001000000
banana      | 0100000002000000
hello       | 0100000003000000
pear        | 0100000004000000
strawberry  | 0100000005000000
watermelon  | 0100000006000000
world       | 0100000007000000
```
2. Sort English strings according to the English character set:
```
SELECT s, collation_sort_key(s, 'en') AS sort_key
FROM ('apple', 'banana', 'cherry', 'grape', 'orange', 'strawberry') AS t(s)
ORDER BY sort_key;
```
The result is as follows:
```
s    | sort_key
-----|----------
apple | 0100000001000000
banana | 0100000002000000
cherry | 0100000003000000
grape | 0100000004000000
orange | 0100000005000000
strawberry | 0100000010000000
```
#### Notes
* The COLLATION\_SORT\_KEY function is only applicable to string type inputs.
* The input character set must be valid, otherwise NULL will be returned.
* The generated sort key is a binary value that can be used for sorting in the ORDER BY clause.