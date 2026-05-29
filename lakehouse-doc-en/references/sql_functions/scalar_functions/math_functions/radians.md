### RADIANS
####  Description
The `radians` function is used to convert angle values to their corresponding radian values. In mathematics, degrees and radians are two ways to measure a circle, with radians being the more universal unit of measurement. This function ensures accuracy and consistency in calculations.
###  Syntax
```sql
radians(expr)
```

#### Parameter Description
- `expr`: The angle value to be converted, of type `double`.

#### Return Result
Returns the converted radian value, of type `double`.

#### Usage Example
1. Convert 90 degrees to radians:
```sql
SELECT radians(90);
-- Return result：1.5707963267948966
```
2. Convert 180 degrees to radians:
```sql
SELECT radians(180);
-- Return result: 3.141592653589793
```
