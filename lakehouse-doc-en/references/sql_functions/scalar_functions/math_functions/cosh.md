### COSH

####  Description
The `cosh` function is used to calculate the hyperbolic cosine value of a given numerical expression. The hyperbolic cosine function is a type of hyperbolic function, similar to the cosine function, but it is used to describe the geometry of hyperbolas.

#### Syntax
```
cosh(expr)
```
#### Parameter Description
- `expr`: The numerical expression for which the hyperbolic cosine needs to be calculated, of type `double`.

#### Return Result
Returns the calculated hyperbolic cosine value, of type `double`.

#### Usage Example
1. Calculate the hyperbolic cosine value of 0:
   ```sql
   SELECT cosh(0);
   -> 1.0
   ```
2. Calculate the hyperbolic cosine of the value -1:
   ```sql
   SELECT cosh(-1);
   -> 1.5430806348152437
   ```
3. Calculate the hyperbolic cosine of the number 2:
   ```sql
   SELECT cosh(2);
   -> 3.7621956910836314
   ```
4. Calculate the hyperbolic cosine of each element in a column, for example `column_name`:
   ```sql
   SELECT cosh(column_name) FROM table_name;
   ```
This will return a new column containing the hyperbolic cosine of each element in the `column_name` column of the `table_name` table.

#### Notes
- For very large values, the result of the hyperbolic cosine function may exceed the numerical range, causing an overflow. In such cases, ensure to appropriately limit the range of input values.

By using the `cosh` function, you can easily calculate the hyperbolic cosine in database queries, thereby applying hyperbolic geometric concepts in data analysis and processing.