# EXTERNAL FUNCTION Development Guide

## Overview

EXTERNAL FUNCTION is a mechanism to directly execute external programs or scripts within the database. By using external functions, you can interact with external programs or scripts, thereby achieving richer functionalities.

## Supported Programming Languages

Currently, the supported programming languages include Java and Python.

## Java Language

### 1. Writing a Java Class

First, you need to write a Java class and implement a static method that will serve as the entry point for the external function. For example, create a Java class named MyJavaClass and implement a static method hello:
```java
public class MyJavaClass {
    public static String hello(String name) {
        return "Hello, " + name + "!";
    }
}
```
### 2. Compile the Java Class into a JAR File

Compile the written Java class into a JAR file. For example, compile MyJavaClass into myjavaclass.jar.

### 3. Register the Java Class in the Database

Register the Java class in the database so that it can be used in external functions. For example, in a MySQL database, you can register it using the following command:
```sql
CREATE FUNCTION my_hello FUNCTION
  -> 'MyJavaClass.hello'
  -> RETURNS STRING
  -> LANGUAGE JAVA
  -> DATABINARY AS '/path/to/myjavaclass.jar';
```
### 4. Using External Functions

In the database, call external functions, for example:
```sql
SELECT my_hello('World');
```
## Python Language

### 1. Writing a Python Script

First, you need to write a Python script and implement a function that will serve as the entry point for external functions. For example, create a Python script named my_python_script.py and implement a function hello:
```python
def hello(name):
    return "Hello, " + name + "!"
```
### 2. Save Python Script to Database

Save the written Python script to the database. For example, in a MySQL database, you can use the following command to save it:
```sql
CREATE FUNCTION my_hello FUNCTION
  -> 'hello'
  -> RETURNS STRING
  -> LANGUAGE PYTHON
  -> DATABINARY AS '/path/to/my_python_script.py';
```
### 3. Using External Functions

In the database, call external functions, for example:
```sql
SELECT my_hello('World');
```
## Usage Example

### Example 1: Calculate the Area of a Circle

Use a Python script to calculate the area of a circle and call this external function in the database.

1. Write the Python script `calculate_circle_area.py`:
```python
def calculate_circle_area(radius):
    return 3.14159 * radius * radius
```
## 2. Save the Python script to the database: {#save-python-script-to-database}

```sql
CREATE FUNCTION calculate_circle_area FUNCTION
  -> 'calculate_circle_area'
  -> RETURNS DECIMAL(10, 2)
  -> LANGUAGE PYTHON
  -> DATABINARY AS '/path/to/calculate_circle_area.py';
```
3. Calling External Functions in the Database:
```sql
SELECT calculate_circle_area(5);
```
### Example 2: Query Stock Prices

Use a Java class to query stock prices and call this external function in the database.

1. Write the Java class `StockPriceFetcher`:
```java
public class StockPriceFetcher {
    public static String getStockPrice(String stockCode) {
        // Logic to fetch stock price
        return "100.0";
    }
}
```
```markdown
2. Compile the Java class into a JAR file.

3. Register the Java class in the database:
```
```sql
CREATE FUNCTION get_stock_price FUNCTION
  -> 'StockPriceFetcher.getStockPrice'
  -> RETURNS STRING
  -> LANGUAGE JAVA
  -> DATABINARY AS '/path/to/stock_price_fetcher.jar';
```
4. Call external functions in the database:
```sql
SELECT get_stock_price('AAPL');
```
By the above example, you can better understand how to use EXTERNAL FUNCTION to interact with external programs or scripts with the database. Please make the corresponding adjustments and optimizations according to your actual needs.