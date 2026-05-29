### SPACE 

#### Description
The SPACE function is used to generate a string consisting of a specified number of spaces. This function is very useful when aligning text or filling spaces.

#### Syntax
```
SPACE(n)
```
#### Parameters
- n: bigint type, representing the number of spaces to generate.

#### Return Result
- Returns a string containing n spaces.

#### Usage Example

1. Generate a string containing 5 spaces:
```sql
SELECT SPACE(5);
```
2. Add spaces in the name to generate the full address format:
```sql
SELECT 'Name' || SPACE(10 - LENGTH('Name')) || 'Street Address' AS address;
```
Results:
```
Name                Street Address
```
Through the above examples, you can see the application of the SPACE function in different scenarios. The SPACE function can conveniently generate a space string of a specified length, thereby meeting various alignment and padding needs.