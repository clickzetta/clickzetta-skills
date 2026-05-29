### TAN 

#### Description
The `TAN` function is used to calculate the tangent of a given angle. In mathematics, the tangent value represents the ratio of the opposite side to the adjacent side in a right-angled triangle. This function has a wide range of applications in trigonometric calculations and angle conversions.

#### Syntax
```
TAN(expr)
```
#### Parameters
- `expr`: The angle for which the tangent value needs to be calculated, of type `DOUBLE`.

#### Return Value
Returns the calculated tangent value, of type `DOUBLE`.

#### Example
1. Calculate the tangent value of 0 degrees:
```sql
SELECT TAN(0);
-- Result: 0.0
```
2. Calculate the tangent value of 45 degrees:
```sql
SELECT TAN(45);
-- Result: 1.6197751905438615
```
3. Calculate the tangent of 90 degrees (result is infinity):
```sql
SELECT TAN(90);
-- Result: -1.995200412208242
```
4. Calculate the tangent of -90 degrees (result is negative infinity):
```sql
SELECT TAN(-90);
-- Result: 1.995200412208242
```
5. Calculate the tangent value of 180 degrees:
```sql
SELECT TAN(180);
-- Result: 1.3386902103511544
```