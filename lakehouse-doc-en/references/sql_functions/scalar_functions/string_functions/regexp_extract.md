### REGEXP_EXTRACT 
```sql
regexp_extract(str, regexp [, idx])
```
####  Description
The REGEXP_EXTRACT function extracts matching text from the input string (str) using the specified regular expression (regexp). This function uses the [re2](https://github.com/google/re2) regular expression engine for matching.

#### Parameter Description
* str (string): The input string to be matched.
* regexp (string): The regular expression string used for matching.
* idx (int, optional): The index of the group to extract. Indexing starts from 1, with the default value being 1, which means extracting the first group. If the specified value is 0, it means matching the entire regular expression.

#### Return Value
Returns a string containing the matched text.

#### Usage Example
```sql
-- Example 1: Extract numbers from a string
> SELECT regexp_extract('Price: 100-500 USD', r'(\d+)-(\d+)', 1);
'100'

-- Example 2: Extract text before a specific character
> SELECT regexp_extract('abc123def', r'^(.*)\d', 1);
'abc12'

-- Example 3: Extract text within parentheses
> SELECT regexp_extract('(sample text here)', r'\((.*)\)', 1);
'sample text here'

-- Example 4: Use the idx parameter to extract the second group
> SELECT regexp_extract('NewYork-USA', r'(.*)-(.*)', 2);
'USA'

-- Example 5: Match the entire regular expression
> SELECT regexp_extract('text to match', r'^(.*)$', 0);
'text to match'
```