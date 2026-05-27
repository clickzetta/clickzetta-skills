## RIGHT 

The RIGHT function is used to extract a specified number of characters from the right side of a given string. This function is very useful when handling text data, especially in scenarios where you need to truncate a string based on specific rules.

###  Syntax
```sql
RIGHT(string, length)
```
- `string`: The original string from which characters are to be extracted.
- `length`: The number of characters to be extracted, must be an integer greater than or equal to zero.

### Function Behavior Description

- If `length` equals 0, the function returns an empty string.
- If `length` is greater than the length of `string`, the function returns `string` itself.
- If `length` is less than 0, the function returns NULL.
- If `string` is NULL, the function returns NULL.

### Practical Application Case

**Case 1: Extract the last two letters of the student's name**

Suppose there is a table named `student` that contains the names (name) and genders (gender) of students, as shown below:

| id | name  | gender |
|----|-------|--------|
| 1  | Alice | F      |
| 2  | Bob   | M      |
| 3  | Cathy | F      |
| 4  | David | M      |

Now, we want to query the last two letters of each student's name, we can use the following SQL statement:
```sql
SELECT name, RIGHT(name, 2) AS suffix FROM student;
```
The query results are as follows:

| name  | suffix |
|-------|--------|
| Alice | ce     |
| Bob   | ob     |
| Cathy | hy     |
| David | id     |

**Example 2: Extracting the file extension from a filename**

Suppose we have a string containing a filename, and we need to extract the file extension (i.e., the characters after the last dot in the filename). For example, the extension of the string `"report.xls"` is `"xls"`.
```sql
SELECT RIGHT('report.xls', 4) AS file_extension;
```
The query result is:

| file_extension |
|-----------------|
| xls             |

**Case 3: Handling Incomplete Strings**

Suppose we have a string containing partial text and need to extract the last few characters, but the text length may vary. For example, handling the following strings:

- `"This is sample text"` (length is 19)
- `"sample"` (length is 6)

Use the RIGHT function to extract the last 3 characters:
```sql
SELECT RIGHT('This is sample text', 3) AS last_three_chars;
SELECT RIGHT('sample', 3) AS last_three_chars;
```
The result is as follows:

| last_three_chars |
|-------------------|
| ext              |
| ple              |