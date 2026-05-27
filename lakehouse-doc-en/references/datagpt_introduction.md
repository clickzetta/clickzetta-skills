# Conversational AI Data Analysis Tool: Analytics Agent

Analytics Agent is a next-generation agentic analysis assistant built on cloud-native Lakehouse architecture and other data platforms (formerly known as DataGPT). It deeply integrates AI cognitive capabilities with enterprise-grade data, going beyond simple query functionality. The agent can dynamically construct AI dashboards through natural language, providing imaginative visualization flexibility that surpasses traditional rigid BI tools. It also proactively embeds contextual AI insights into key chart metrics, instantly revealing anomalies and trends, and uncovering hidden data insights within static reports.

^

![](/.topwrite/assets/datagpt_1.png)

^

## Conceptual Framework:

**Core Concepts**:
The core conceptual framework consists of two main components: Data Assets and Analysis Domains.

**Data Assets**
As the infrastructure for enterprise analytics, it encompasses all core elements available for intelligent analysis, enhanced through the Analytics Agent Semantic Layer:

* **Data Tables**: Structured basic data sources from Lakehouse.

* **Semantic Layer Elements**:

  * **Metric System**: Standardized measurement indicators built on data tables.
  * **Business Terms**: Unified naming conventions and explanatory definitions designed to provide context for the agent.

* **Dashboards**: Visual analytics panels built using AI based on the semantic layer and data tables.

* **Documents**: A collection of knowledge documents supporting Agentic RAG-based Q&A.

* **Indexes**: Indexes built on data table fields to accelerate retrieval.

:-: ![](/.topwrite/assets/DataGPT_2.png)

^

## User Roles and Responsibilities:

The Analytics Agent system is designed to serve two core user groups in data analysis scenarios: data developers and business analysts. These two types of users play unique and complementary roles in the process of extracting data value:

1. **Data Developers**: Lead the full data lifecycle management, including data ingestion, quality control, model building, and semantic layer design (covering metric systems and answer builders), while continuously optimizing the Q&A experience. They leverage system capabilities to prepare data for use by business analysts.
2. **Business Analysts**: As the core users of the system, they explore data deeply through natural language interaction, quickly obtaining business insights and decision support. Through the feedback process, they communicate with data developers to further refine and explore data, gaining deeper understanding and insights.

## Technical Architecture:

Multi-source and multi-type data enters the Lakehouse system through warehousing and data lake ingestion (when Lakehouse is chosen as the data engine):

* Metadata is managed and access-controlled uniformly according to the data warehouse's permission system.
* Data undergoes transformation processing and information extraction through our integrated Single Engine and AI engine.
* Extraction results are stored in the form of tables, vectors, and inverted indexes, building an Agentic RAG Preparation Layer for the agent. These are then further processed by the Analytics Agent Semantic Layer, which performs automated feature analysis, knowledge graph construction, and index extraction.
* Based on the DIKW model, the Agentic RAG layer provides "Information," while the Analytics Agent Semantic Layer elevates it to "Knowledge" by annotating, organizing, and summarizing context. This architecture enables the agent to autonomously plan and reason, laying a solid foundation for generative AI applications.
* Agentic RAG: A Semantic Paradigm Shift
  Analytics Agent transcends the linear "retrieve-then-generate" pipeline. By implementing Agentic RAG, we transform the LLM from a passive text generator into a proactive Reasoning Agent within the Analysis Domain.
  * **LLM-Driven Understanding**: Rather than relying solely on vector distance (cosine similarity), Analytics Agent leverages the LLM's internal cognition to interpret user intent. The model determines "what is needed" rather than simply matching keywords.

  * **Proactive Orchestration**: The agent acts as the central brain within the analysis domain. It autonomously decides which objects to interact with:

    * Whether to query **Data Tables** via SQL
    * Whether to read specific **Files**
    * Whether to check **Metric** definitions

  * **Iterative Refinement**: If the initial retrieval information is insufficient, the agent self-corrects. It performs multi-step reasoning to obtain additional context, ensuring the final answer is comprehensive and accurate.
    By internalizing retrieval logic into the LLM itself, Analytics Agent addresses the limitations of traditional RAG:

  * **Semantic Fidelity**: We leverage the model's multi-dimensional understanding of business logic and nuances, breaking through the "ceiling" of standard vector search.

  * **Complex Problem Solving**: The agent can handle multi-hop queries, synthesizing information from different data types (e.g., correlating a sales decline in a **dashboard** with a market report in a **file**).

  * **Dynamic Adaptation**: As new assets are added to the analysis domain, the agent can adjust its reasoning strategies in real time, without relying on rigid, hard-coded index rules.

## Free Version Limitations:

Thank you for using Singdata Analytics Agent. You are currently using the free version. To ensure you fully understand the product status, please note the following:

1. Features in the current version are early-stage product features, and we reserve the right to optimize, adjust, or modify these features.

2. Based on product development plans, some features may be upgraded to paid services or have their service scope adjusted. We will notify affected users in advance before such changes occur.

3. During the free usage period, the product features have the following limitations:

&#x20;       ![](.topwrite/assets/20250114-221654.jpeg =258)

If you have any suggestions for the product, please feel free to provide feedback through the following channels:

* **Phone**: 400-6767-862

* **Email**: <service@singdata.com>

* **Enterprise WeChat**: ![](.topwrite/assets/image_1736856313196.png =116)

^
