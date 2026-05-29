# Data Result Profiling

The Data Result Profiling feature enables users to quickly analyze the basic statistical characteristics, data distribution, and quality of fields based on SQL query results. It is applicable for data cleaning, quality checks, and exploratory analysis.

## Using the Profiling Feature

Access: Under the development function, click on SQL Development and create a data query analysis script on this node. After running the script, the profiling feature section will be displayed by default on the far right of the results page. Alternatively, you can click on the "Profile" button on the right.

Note: Data profiling is only performed on the result data presented on the front end. It does not support profiling of the entire dataset beyond the front - end execution results.

For example, if the total number of rows in the execution result is 20,000, but only 10,000 rows are displayed on the front end, the profiling will be based on the 10,000 rows shown.

The profiling feature provides information on field completion rates and data distribution based on the field information from the query results.

* Completion Rate: This refers to the proportion of specific values, NULLs, and empty characters in a field.
* Empty Character: The proportion of values equal to " " in the field.
* Null: The proportion of null values in the field.
* With Data: The proportion of non - null and non - empty values in the field.
* Field Value Distribution: This shows the distribution of values in a field. For numeric fields, it includes the sum and average of the values.

^
