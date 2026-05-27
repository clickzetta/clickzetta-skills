# Using Sqlline to Connect to Singdata Lakehouse

## Overview

This document aims to guide users on how to use the Sqlline tool to connect to Singdata Lakehouse for data querying and management. Before starting, please ensure the following prerequisites are met.

## Prerequisites

1. Java 8 or higher is installed on your local computer.
2. You have successfully activated the Lakehouse service.
3. You have downloaded the Sqlline component provided by Lakehouse. Please click [here](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/release/sqlline_cz.tar.gz) to download sqlline_cz.

## Steps

1. **Extract the Sqlline component**: Unzip the downloaded sqlline_cz.tar.gz file.
   ```
   tar vxf sqlline_cz.tar.gz
   ```
2. **Enter the working directory**: Open the terminal and navigate to the extracted sqlline_cz directory.
   ```
   cd sqlline_cz
   ```
3. **Initialize Connection Environment**: Run the `setup.sh` script to initialize the connection environment.
   ```
   sh setup.sh
   ```
4. **Modify the Configuration File**: Edit the `example.properties` file according to the actual situation, mainly modifying the following parameters:
   - `url`: The JDBC URL of the Lakehouse.
   - `user`: The username of the Lakehouse.
   - `password`: The password of the Lakehouse.

   For example, you can use a text editor to modify the configuration file:
   ```
   nano example.properties
   ```
Then enter the following content (replace with your actual information):
   ```
   url=jdbc:lakehouse://your_lakehouse_url
   user=your_lakehouse_username
   password=your_lakehouse_password
   ```
5. **Start Sqlline**: Run Sqlline and load the configuration file.
   ```
   ./sqlline property example.properties
   ```
## Usage Example

1. **Query Data Table**: In Sqlline, you can execute SQL queries to view the contents of a data table. For example, query the data table named `employees`:
   ```
   SELECT * FROM employees;
   ```
2. **Create a Data Table**: You can use Sqlline to create a new data table. For example, create a data table named `departments`:
   ```
   CREATE TABLE departments (
       id INT PRIMARY KEY,
       name VARCHAR(255),
       description TEXT
   );
   ```
3. **Insert Data**: Insert data into the data table. For example, insert a record into the `departments` table:
   ```
   INSERT INTO departments (id, name, description) VALUES (1, 'HR', 'Human Resources Department');
   ```
## Debugging and Troubleshooting

If you need to enable debug mode to output detailed logs for troubleshooting, please set the environment variable `SQLLINE_DEBUG_ENABLE` to `TRUE`:
```
export SQLLINE_DEBUG_ENABLE=TRUE
```
## Conclusion

By following the above steps, you should have successfully connected to the Lakehouse using Sqlline and performed data operations. If you have any questions or need further support, please feel free to contact our technical support team.