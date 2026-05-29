# Singdata Conversational AI Analysts: DataGPT

Lakehouse DataGPT is a new generation conversational data analysis tool built on the cloud-native Lakehouse architecture. It combines the natural language understanding capabilities of large language models (LLM) with the processing power of the Lakehouse enterprise-grade data engine, transforming data analysis into an intuitive conversational experience. With DataGPT, even business personnel without a technical background can easily explore data value and drive data-driven intelligent decision-making.

![](.topwrite/assets/20250219-110334.jpeg)

## Technical Architecture:

Multi-source, multi-type data enters the Lakehouse system through warehousing and lake entry methods:

* **Metadata** is uniformly managed and accessed according to the data warehouse's permission system.
* **Data** is transformed and information is extracted through our integrated engine Single Engine and AI engine.

The extracted results are stored in the system in the form of tables, vectors, and inverted indexes, forming a RAG preparation layer. These three parts of the data are then subjected to automated data feature analysis, knowledge graph construction, and automated index extraction through the semantic engine layer. The significance of these last two new layers is: the RAG ready layer provides the basic data ready for AI preparation. If we apply the previously mentioned DIKW model, this data foundation is information, and the role of the semantic engine layer is to annotate, organize, and summarize this information to the knowledge level, laying the foundation for generative AI applications.

![](<.topwrite/assets/screenshot2025-01-15 17.11.19.png>)

## Product Features:

* Seamless integration with the **Lakehouse data platform**, capable of automatically building a semantic layer based on Lakehouse tables, directly transforming into LLM application-ready data. Compared to traditional knowledge base systems, it defaults to using Lakehouse as the underlying data lake warehouse, vector, and scalar storage engine, with stronger concurrent processing capabilities and quickly scalable computing resources.
* Combines conversational interaction with traditional BI exploration to enhance data analysis efficiency and Emphasizes the interpretability of the analysis process, providing business personnel with clear result validation evidence.   ![](.topwrite/assets/20250219-112543.jpeg =789)
* Adopts a Multi-Agent architecture, capable of intelligently decomposing and parallel processing complex customized tasks, significantly improving Q\&A efficiency and accuracy.
* Supports intelligent follow-up questions and multi-turn conversations, allowing users to gradually optimize and clarify requirements, effectively eliminating data understanding ambiguities.
* Utilizes multi-model collaboration to continuously optimize response efficiency and accuracy during the Q\&A process: users can choose different models (such as **Azure-gpt-4o** and **Deepseek-R1**) to handle query or analysis tasks. The system provides open-source models for private deployment to summarize questions, ensuring data does not leave the service.   ![](.topwrite/assets/20250219-112622.jpeg =790)

## Concept System:

Its core concept system consists of two main parts: data assets and analysis domains:

1. Data Assets: Serving as the infrastructure for enterprise-level analysis, it includes all core data elements available for intelligent analysis:

   * Data Tables: Structured basic data sources
   * Metric System: Standardized measurement metrics built based on data tables
   * Business Terms: Unified naming conventions and explanatory definitions
   * Analysis Documents: A collection of knowledge files supporting Q\&A
   * Column Value Index: Indexes established for fields in the dataset tables

2. Analysis Domain (Domain): Serving as the logical boundary for business analysis, it undertakes the dual responsibilities of data classification and access control. Data assets can be flexibly referenced to different analysis domains, achieving efficient reuse of enterprise data:

   * Business Grouping: Aggregates and manages data objects (tables, metrics, documents, etc.) with the same attributes
   * Definition Control: Ensures consistency and uniqueness of data definitions within the domain
   * Permission Isolation: Achieves fine-grained control of data access through the association between users and analysis domains

   :-: ![](.topwrite/assets/whiteboard_exported_image_1739936522979.png =711)

^

## User Roles and Responsibilities:

The DataGPT system is designed to meet the needs of two core user groups in data analysis scenarios: data developers and business analysts. These two types of users play unique and complementary roles in the process of data value mining:

1. **Data Developers**: Lead the full lifecycle management of data, including data access, quality control, model building, and semantic layer design (covering metric systems and answer builders), and continuously optimize the Q\&A experience. They use system functions to prepare data for business analysts.
2. **Business Analysts**: As the core users of the system, they deeply explore data through natural language interaction, quickly obtaining business insights and decision support. Through the feedback process, they communicate with data developers to further refine and explore data for deeper understanding and insights.

## Free Version Limitations:

Thank you for using Singdata DataGPT. You are currently using the free version. To ensure you fully understand the product status, we hereby explain:

1. The features in the current version are early product features, and we reserve the right to optimize, adjust, or change the features.

2. Based on product development plans, some features may be upgraded to paid services or have their service scope adjusted. We will notify affected users in advance before such changes occur.

3. During the free usage period, the product features have the following limitations:
   • 4 Dedicated Analysis Domain
   • Maximum 5 files upload capacity (50MB max size)
   • Concurrent file upload limit: 8 files
   • File size restriction: 50MB per file
   • Data table capacity: 480 rows
   • Daily response quota: 30 queries

If you have any suggestions about the product, feel free to provide feedback using the contact information below.

* **Email**: <service@singdata.com>

^
