# Data Privacy Agreement

## Data Processing Scope

When the system processes your data queries, the following data will be sent to the large language model service:

**Metadata**:

* Data table structure (Schema)
* Descriptions of tables and fields
* Field aliases
* Definitions of business metrics and answer builders

**Data**:

* Column value data with indexing enabled (You can prevent specific column data from being sent to the large language model by disabling column value indexing)

![](.topwrite/assets/20250115-094842.jpeg)

**Document Segmentation**:

* The system segments document content into chunks
* These document segments are sent to the Large Language Model to enable intelligent question-answering

## Data Protection Measures

To protect your sensitive data:

* It is recommended to disable indexing for columns containing sensitive information
* Before using the document Q\&A feature, please confirm the sensitivity of the document content
* The system only transmits necessary data for query parsing

## Please Note:

* The large language model service may retain processed data for model optimization
* It is recommended not to include highly sensitive personal information in queries
* The system will periodically clean cached query data

## Updates and Changes

We reserve the right to update this agreement based on technological developments and security requirements. Significant changes will be notified to users through system announcements. **By using the DataGPT system, you acknowledge and agree to the above data processing rules**. If you have any questions about the product, please feel free to provide feedback through the following contact methods.

* **Email**: <service@singdata.com>

^
^
