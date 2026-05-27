### SEQUENCE 

#### Overview
The SEQUENCE function is used to generate a sequence that starts from the initial value (start) and ends at the final value (stop), incrementing by the specified step size (step). The sequence result includes both the initial and final values. If the step parameter is not provided, the system will automatically select the default step size based on the relationship between the initial and final values.

#### Functionality
- When the initial value is less than or equal to the final value, if the step size is not specified, the default step size is 1.
- When the initial value is greater than the final value, if the step size is not specified, the default step size is -1.
- Supports integer and time type parameters.

#### Parameters
- start (tinyint/smallint/int/bigint): The initial value of the sequence.
- stop (tinyint/smallint/int/bigint): The final value of the sequence.
- step (tinyint/smallint/int/bigint): The difference (step size) between each element in the sequence, with a default value of 1 or -1, depending on the relationship between the initial and final values.

#### Return Result
Returns an array of the same type as the parameters.

#### Usage Example
1. Generate an integer sequence:
```sql
SELECT sequence(-2, 2); -- Result: [-2, -1, 0, 1, 2]
SELECT sequence(2, -2); -- Result: [2, 1, 0, -1, -2]
SELECT sequence(-2, 2, 3); -- Result: [-2, 1]
```
2. Generate Time Series:
```sql
SELECT sequence(timestamp '2020-10-10 00:00:00', timestamp '2020-10-15 00:00:00', interval '1 12:00:00' day to second);
-- Result: [2020-10-10 00:00:00, 2020-10-11 12:00:00, 2020-10-13 00:00:00, 2020-10-14 12:00:00]
```
#### Notes
- When the start value and the end value are equal, the generated sequence contains only one element.
- When the step size is 0, the SEQUENCE function will return an error.