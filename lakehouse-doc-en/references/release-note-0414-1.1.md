This release introduces a series of new features, enhancements, and fixes. Please note that these updates will be rolled out gradually to the following regions. Deployment will complete within one to two weeks of the release date, with timing depending on your region.

* **China Regions**

  * Alibaba Cloud (Shanghai)
  * Tencent Cloud (Shanghai/Beijing/Guangzhou)
  * AWS (Beijing)

* **International Regions**

  * Alibaba Cloud (Singapore)
  * AWS (Singapore)

## New Features

* [Web Search](https://www.singdata.com/documents/web_search) (**Web Search**):

  * Added the WebSearch tool, enabling the Agent to invoke external search engines during data analysis to retrieve real-time information (currently only available to select customers; whitelist activation required).
* [Scheduled Tasks](https://www.singdata.com/documents/scheduled_task):

  * Supports conversational creation of scheduled analysis tasks via ASK AI (e.g., "Execute at 6 PM daily to check DataGPT usage"). The system automatically performs the analysis at the configured time and delivers results via email.
* [Table Rendering Optimizations](https://www.singdata.com/documents/table_rendering):

  * Supports describing table styles using natural language, automatically generating data tables with complex layouts including grouping, aggregation, color marking, fixed headers, and column sorting.
* [Row-Level Permissions](https://www.singdata.com/documents/row_level_permission):

  * Added row-level permission management. Administrators can define permission rules and apply them to specific users, controlling the range of data rows accessible to each user.

## Improvements

* **Session Memory Instructions**:

  * Optimized in-session context memory, making the Agent more focused within a single session and improving multi-turn conversation coherence and accuracy.
* **Skills Mechanism**:

  * Introduced the Skills mechanism to address declining Agent performance and rising costs caused by an increasing number of tools and features, improving overall analysis quality and response efficiency.
* **Chart Computation Optimization**:

  * Optimized chart computation tool effects, revised chart title generation logic, and improved `save chart` compatibility with model hallucination issues.
* **Dashboard Optimizations**:

  * Improved dashboard creation/editing effects and enhanced the stability of the dashboard list retrieval tool.

## **Bug Fixes**

* Fixed a bug where document Q&A content was missing.

* Fixed an issue where JDBC connections did not support custom parameters.

* Fixed a JDBC URL whitespace issue.

* Fixed a bug where chart computation time was not displayed.

* Fixed a dashboard list tool bug.

^
