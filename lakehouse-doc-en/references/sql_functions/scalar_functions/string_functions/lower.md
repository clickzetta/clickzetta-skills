### LOWER 

####  Description
The LOWER function is used to convert all uppercase characters in the input string (str) to lowercase characters and returns the converted string.

#### Parameter Description
* str: The string that needs to be converted to lowercase letters.

#### Return Result
Returns the string converted to lowercase letters.

#### Usage Example
Here are some examples of using the LOWER function:

1. Convert "HelloWorld" to "helloworld":

```sql
SELECT LOWER('HelloWorld');
```
The result is:
```
helloworld
```
2. Convert "Python" and "JAVA" to lowercase:
```sql
SELECT LOWER('Python'), LOWER('JAVA');
```
The result is:
```
python
java
```


3. Convert the strings "SQL" and "DATABASE" to lowercase letters and concatenate them together:
```sql
SELECT LOWER('SQL') || LOWER('DATABASE');
```
The result is:
```
sqldatabase
```
4. Convert the user input string to lowercase letters and store it in the new column "lower_case":
```sql
SELECT id, LOWER(name) AS lower_case
FROM users;
```
After executing the above query, the result is:
```
id | lower_case
---|-------------
1  | johndoe
2  | alicesmith
```