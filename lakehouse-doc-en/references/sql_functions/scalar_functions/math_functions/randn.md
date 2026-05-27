###  RANDN 

###  Description
The RANDN function is a non-deterministic function used to generate a random number that follows a standard normal distribution (mean of 0, standard deviation of 1). This function has a wide range of applications in various scenarios, such as simulation data, numerical analysis, and statistical testing.

### Return Type
This function returns a value of type double.

###  Example
1. Generate a random number with a standard normal distribution:
   ```sql
   SELECT RANDN();
   ```
The result might be similar to: `0.635793277734877`

2. Generate multiple normally distributed random numbers and calculate the average value:
   ```sql
   SELECT AVG RANDN() FROM (SELECT NULL) AS x;
   ```
The result might be similar to: `0.0`
   In this example, by generating random numbers and calculating their average, we can see that the result approaches 0, which is consistent with the mean characteristic of the normal distribution.


### Conclusion
The RANDN function is a simple yet powerful tool that can help users generate normally distributed random numbers in SQL queries. By flexibly using this function, users can achieve more possibilities in data analysis and processing.