# Lakehouse DataGPT Quick Tour

Lakehouse DataGPT is a cutting-edge, cloud-based conversational data analysis tool that leverages the power of natural language interaction to make data analysis as easy as chatting. By utilizing advanced large language models (LLMs), it allows users to explore data conversationally, delivering accurate and insightful analysis results with remarkable efficiency.

Embrace the future of data analysis with DataGPT, where the power of artificial intelligence meets the diversity of data sources. Whether your data resides in the powerful Lakehouse or in personal files (such as Excel, CSV, or PDF), DataGPT helps you unlock its analytical potential. This innovative tool breaks down the barriers to data accessibility, ensuring that no matter where your data is stored, you can leverage DataGPT's AI capabilities to discover insights, make informed decisions, and drive success in the era of advanced data analytics.

To learn more about DataGPT concepts and technical architecture, refer to [DataGPT Introduction](datagpt_intro.md).

## Supported Data Sources

Lakehouse GPT can analyze data already stored in [Lakehouse tables](table.md). This means users can directly engage in conversational data analysis with Lakehouse GPT, extending Lakehouse's use cases from data engineering and SQL/Python-based analysis to interactive, visual data analysis experiences. This provides users with an easier way to explore data, allowing them to quickly obtain data results and corresponding SQL code through simple Q\&A interactions.

Additionally, Lakehouse GPT supports directly loading files such as Excel, CSV, and PDF, with the loaded data stored in Lakehouse. This way, users no longer need to worry about Lakehouse-specific concepts (such as schemas, tables, or SQL), significantly lowering the barrier to entry for data analysis.


## Engage with DataGPT and Seamlessly Receive Comprehensive Data Analysis Results


We received a notification indicating that "**Results require verification**." Upon investigating the details, we found that the query involved "**Haidian District**." DataGPT is a data analysis tool powered by large language models (LLMs). It intelligently handled the multilingual nature of the data by interpreting "Haidian District" and associating it with the Chinese value "Haidian" in the table's district field. Since the table contains only Chinese district information, DataGPT's reasoning capabilities allowed it to recognize this correspondence and seamlessly align the data to produce accurate results. Nevertheless, the tool prompts users to verify the accuracy of the results.


This case clearly demonstrates the powerful capabilities of DataGPT, leveraging the strengths of large language models (LLMs) to overcome challenges commonly encountered by traditional business intelligence (BI) tools in data analysis. By harnessing the power of large language models (LLMs), DataGPT effectively addresses complex multilingual data issues, providing a solution that goes beyond the limitations of traditional BI tools, thereby elevating the entire analysis process.

## Comparative Analysis and Multi-Dimensional Drill-Down

[Metrics](metrics_answer_build.md) computed based on database fields are quantifiable measures used to evaluate performance, trends, and other key data points. These metrics can be generated through aggregation, which summarizes large datasets into one or a few values, or through custom code methods that apply specific algorithms or calculations to the data. DataGPT leverages large models to provide an automated way to create these metrics, simplifying the process and reducing the need for manual intervention. These metrics offer a concise way to understand complex data, facilitating informed decision-making.

Metric-based data analysis includes comparative analysis across different time periods and multi-dimensional drill-down.

### Comparative Analysis

Comparative analysis involves examining changes and trends over time, such as month-over-month, year-over-year, or quarter-over-quarter comparisons, to identify patterns, growth, or decline in performance metrics. This analysis is crucial for understanding progress and making strategic decisions.


### Multi-Dimensional Drill-Down

Multi-dimensional drill-down refers to the process of exploring data from multiple perspectives or dimensions. This may involve segmenting data by region, product line, customer group, or other relevant categories to gain deeper insights. Through drill-down, analysts can uncover the factors influencing overall metrics, enabling more targeted and information-driven decisions.


## Quick Start

* [DataGPT Quick Start](datagpt_quickstart.md): Quickly experience conversational analysis using **sample datasets**. We have prepared a well-configured dataset with complete table configurations and metric systems. You can start asking questions right away and quickly experience intelligent analysis features. Additionally, this sample can serve as a template to help you create analysis domains suited to your business scenarios.


* [DataGPT Data Source Management](config-datasource.md): Connect to Lakehouse instances in other regions.

* **Once your data is ready, you can start asking questions in natural language**.


## Configuration

* [Metrics & Answer Builder](metrics_answer_build.md): For specific computational requirements, the system can provide answers using predefined SQL templates.
* [How to Make Answers More Accurate](answer-accuracy-improve.md): Methods to improve the accuracy of DataGPT responses.

## Data Privacy

* [DataGPT Data Privacy](data_privacy.md): Data privacy concerns during the Q\&A process.

^
