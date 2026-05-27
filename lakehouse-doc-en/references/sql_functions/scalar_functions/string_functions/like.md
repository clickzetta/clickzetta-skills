### LIKE Operator

#### Description
The LIKE operator is used in SQL queries to match strings based on a specified pattern. It helps you find data that contains specific characters or patterns. When using the LIKE operator, you can use wildcards to represent one or more characters.

#### Parameters
* `str` (string): The original string to be matched.
* `pattern` (string): The pattern string containing wildcards.
* `escape_char` (optional): A single character used to escape the wildcard characters `%` and `_` in the pattern, treating them as literal characters.

#### Return Value
Returns a boolean value indicating whether `str` matches `pattern`.

#### Wildcard Description
* `%`: Represents any number of characters (including zero characters).
* `_`: Represents any single character.
* The default escape character is `\`. A custom escape character can be specified using the `ESCAPE` clause.

#### Syntax

```sql
str LIKE pattern
str LIKE pattern ESCAPE escape_char
str NOT LIKE pattern
str NOT LIKE pattern ESCAPE escape_char
```

#### Examples

1. Match strings starting with "Hello":
```sql
SELECT 'HelloWorld' LIKE 'Hello%';
```
Result:
```
true
```

2. Match strings containing "lo":
```sql
SELECT 'HelloWorld' LIKE '%lo%';
```
Result:
```
true
```

3. Match strings that contain "lo" and end with "ld":
```sql
SELECT 'HelloWorld' LIKE '%lo_ld';
```
Result:
```
false
```

4. Use a single-character wildcard to match strings containing "oW":
```sql
SELECT 'HelloWorld' LIKE 'Hello_W%';
```
Result:
```
true
```

5. Use the NOT keyword to find strings that do not match a specific pattern:
```sql
SELECT 'HelloWorld' NOT LIKE 'Hello%';
```
Result:
```
false
```

6. Use the ESCAPE clause to match strings containing a literal `%`:
```sql
SELECT 'h%' LIKE 'h#%' ESCAPE '#';
```
Result:
```
true
```

7. Combine the ESCAPE clause with wildcards:
```sql
SELECT 'h%awkeye' LIKE 'h#%a%k%e' ESCAPE '#';
```
Result:
```
true
```

8. Use ESCAPE to match strings containing a literal `_`:
```sql
SELECT 'i_dio' LIKE 'i$_d_o' ESCAPE '$';
```
Result:
```
true
```

#### Notes

* The ESCAPE character must be a single constant character.
* The ESCAPE character can only be followed by `%`, `_`, or the ESCAPE character itself. Following it with any other character results in an error.
* ILIKE (case-insensitive LIKE) also supports the ESCAPE clause.
