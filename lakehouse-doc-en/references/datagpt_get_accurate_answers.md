# How to Make DataGPT's Answers More Accurate

As a data-based Q\&A system, accuracy is particularly important. The system provides the following means to ensure the accuracy of answers.

## 1. Data Governance

* **Data Profile**: The system provides a data profile function that allows you to understand the data status of the underlying dataset tables: through **Left Navigation Bar -> Data -> Data Tables**, on the **Statistical Analysis** tab of the table details page, you can view the data status to help you with data governance; by establishing a data profile, it also helps to find the appropriate target data through natural language.

> Note: DataGPT only provides the **statistical analysis** function for customers to view data distribution and statistical analysis. Data quality is guaranteed by the upstream data platform.

* **Table, Column Descriptions, and Column Alias Configuration**: Adding accurate descriptions and alias information to table columns helps the system accurately match questions with data. In **Left Navigation Bar -> Data -> Data Tables**, you can configure table-level descriptions, column aliases (Alias), and column description information (Description) respectively. The clearer and more accurate the aliases and descriptions of tables and columns are, the less ambiguity there is in names and descriptions, and the higher the accuracy of answers.

* **Index Switch**: For columns that are frequently referenced by questions, you can choose to index the specific values of those columns. Common dimension columns such as region, product category, and channel can be considered for indexing. (If the underlying data is updated, you can refresh the column value index in Action.)

  * For example, the question: `In the year of 2017, the total sales trend both undefined and undefined state by mouth, present Separately？` The actual values stored in the `customer_state` field of the table is `MG` and `RJ`. Without adding index, using `customer_state` `in ['undefined','undefined']` as a filter will not return any value. If an index is added, the system will match `undefined and undefined state `with the original value `MG` and `RJ` for similarity and provide a suggestion: ![](.topwrite/assets/20250219-120022.jpeg =725)

> Note: Indexing will incur additional creation and maintenance costs. DataGPT defaults to no more than 10,000 index values on a single column. If you need to create a larger number of index values on the target column, you need to communicate with Singdata to lift the restriction.

* **Column Type and Intended Use**: Please fill in the column type (ColumnType) and intended use (Intended For) based on the actual values of the column. **This option will affect whether the column is selected as a data source for questions**.

## 2. Divide Analysis Domains

Splitting business domains helps the system focus more on specific data.

1. Pre-divide analysis domains to reduce the range of data tables and knowledge involved in each Domain.
2. Asking questions for a specific Domain is more focused, and the Domain will be bound to the user, enabling table-level data isolation.

## 3. Create Metrics and Answer Builders

Metrics are the results of aggregate functions or calculations of aggregate functions, and answer builders are SQL template definitions for predefined objects. Answering questions based on metrics and answer builders will significantly improve accuracy. If there are strict requirements for Q\&A accuracy, it is recommended to predefine them. Metrics support aliases to match more expressions.

:-: ![](.topwrite/assets/20250219-115256.jpeg)

## 4. Use Input Prompts

Column Value Intelligent Matching: After enabling the column value index function, the system will provide real-time data value prompts as you input, ensuring the accuracy and relevance of query results.

![](.topwrite/assets/20250219-120653.jpeg)

^
