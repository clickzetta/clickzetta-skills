^

**Product Upgrade Notice**: Starting with this release, DataGPT is officially renamed to **Analytics Agent**. Product capabilities remain unchanged; only the product name has been upgraded. Subsequent documentation and UI will gradually switch to the new name.

This release introduces a series of new features, enhancements, and fixes. Please note that these updates will be rolled out gradually to the following regions. Deployment will complete within one to two weeks of the release date, with timing depending on your region.

* **China Regions**

  * Alibaba Cloud (Shanghai)
  * Tencent Cloud (Shanghai/Beijing/Guangzhou)
  * AWS (Beijing)

* **International Regions**

  * Alibaba Cloud (Singapore)
  * AWS (Singapore)

## New Features

* [Row-Level Permissions](https://www.singdata.com/documents/row_level_permission) Enhancements:
  * When configuring row-level permissions, administrators can now dynamically obtain permission scopes from other data tables using expressions (e.g., automatically retrieving a user's assigned store list from a store table), in addition to manually entering fixed values. Suitable for scenarios where permission values change frequently or need to follow business data updates automatically.
* **Dashboard Version Management**:
  * Each modification to a dashboard chart via ASK AI conversation automatically generates a version. Users can view thumbnail previews and modification history of historical versions in the version panel, with support for one-click preview and restore. Solves the pain point of "can't undo after breaking things" — revert at any time if unsatisfied.
* **Open API**:
  * Supports initiating data analysis requests and retrieving results via API, making it easy to embed Analytics Agent's analysis capabilities into internal enterprise systems, workflows, or custom applications for automated data Q&A.
* **Automatic Chart Error Correction**:
  * When AI generates charts, the system automatically detects rendering errors and attempts to fix them, reducing cases of "chart display anomalies" — users can get correct visualization results without manual retries.
* **Scheduled Task Email: Chinese/English Bilingual and Multiple Recipients**:
  * Scheduled analysis report emails now support Chinese/English language adaptation and can be sent to multiple recipients simultaneously.
* **Chart Auto-Refresh Configuration**:
  * Dashboard charts now support setting an auto-refresh interval (default: 24 hours). The system automatically updates chart data at the configured time without manual refresh.

## Improvements

* **GPT-5.5 Model Support**:
  * Compatible with the GPT-5.5 model, enhancing Agent reasoning capability and answer quality.

* **Response Speed Optimization**:
  * Removed the summary tool and disabled streaming summary output, reducing unnecessary processing steps and improving overall response speed.
  * Large dataset creation no longer requires waiting for page load completion; the system processes it automatically in the background, with creation progress viewable on the page at any time.

* **Knowledge Search Parallelization**:
  * Knowledge search now supports parallel execution of multiple keywords, significantly reducing knowledge retrieval latency and improving Agent knowledge citation efficiency.

* **ML Analysis Capability Integration**:
  * Consolidated ML-related tools into a single Skill, optimizing the invocation effectiveness and stability of machine learning analysis.

## Bug Fixes

* Fixed an issue where dataset attribute fields could be missing.

* Fixed an issue where `replace` in subqueries was not taking effect and Chinese column names were not properly quoted.

* Fixed validation errors caused by missing table names when referencing columns in metric validation.

* Fixed an issue where the knowledge editing tool was outputting results in Chinese.

* Fixed ECharts formatter syntax errors causing chart rendering failures.

* Fixed an issue where KG Service unavailability affected frontend operations.

* Fixed time format compatibility — now supports the `yyyy-MM-dd HH:mm:ss` format.

^
