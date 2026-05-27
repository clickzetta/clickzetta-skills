### BTRIM 
```
btrim(str [, trimStr])
```
####  Description
The BTRIM function is used to remove specified characters or spaces from both sides of the string str. If the trimStr parameter is not provided, all whitespace characters at both ends of the string are removed by default.

#### Parameter Description
* str (string): The original string that needs to be processed.
* trimStr (string, optional): Specifies the set of characters to be removed from both ends of the string.

#### Return Result
Returns the processed string.

#### Usage Example
```sql
-- Remove all spaces from both ends of the string
SELECT 'X' || btrim('    HelloWorld    ') || 'X'; -- Result is 'XHelloWorldX'

-- Remove specific characters from the left side of the string
SELECT btrim('abcHelloWorld', 'abc'); -- Result is 'HelloWorld'

-- Remove specific characters from the right side of the string
SELECT btrim('HelloWorldabc', 'abc'); -- Result is 'HelloWorld'

-- Remove specific characters from both ends of the string
SELECT btrim('abcHelloWorldabc', 'abc'); -- Result is 'HelloWorld'

-- Remove numbers from both ends of the string
SELECT btrim('123HelloWorld123', '0123456789'); -- Result is 'HelloWorld'

-- Remove multiple characters from both ends of the string
SELECT btrim('!@#HelloWorld!@#', '!@#'); -- Result is 'HelloWorld'
```
#### Notes
* If the trimStr parameter is an empty string, the original string will not be modified.
* When the characters contained in the trimStr parameter do not exist in the original string, the function will still work properly and return the original string.
* If you need to remove characters in the middle of the string, consider using other string processing functions.