# Analytics Agent Answer Accuracy Improvement - Best Practices

In response to the most frequently asked question: What methods are available to improve answer accuracy? Which scenarios are suitable for each method? How to manage them?

## 1. What Capabilities Improve Accuracy?

Analytics Agent (formerly known as DataGPT) provides **4 core capabilities** to give the model more business information input and improve answer accuracy:

### 1. Table/Column Schema Annotations

![](/.topwrite/assets/image_1779160426141.png)

| Configuration Item              | Purpose                                                                         | Example                                           |
| ------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------- |
| Table Description               | Tells the model what this table represents                                      | "Daily sales transaction records for all stores in Hong Kong region" |
| Column Alias                    | Helps the model understand different names for the same field                   | Column name rev\_amt → alias "revenue", "income"            |
| Column Description              | Explains the business meaning and value rules of a column                       | "payment\_type: payment method, values include cash/card/octopus" |
| Hidden Column                   | When a table has many fields, some columns are irrelevant for business analysis (e.g., system primary keys, ETL timestamps, internal codes). Hiding them prevents them from participating in AI Q&A and analysis, reducing the chance of the model selecting the wrong column | Applicable scenarios:&#xA;Tables with many technical fields that interfere with column selection; or sensitive fields that should not be referenced by AI |
| Virtual Column                  | When schema changes require AI to adapt its understanding, create virtual columns through SQL expressions without modifying the underlying data table | Use case: When raw fields need transformation to help AI understand business meaning |

### 2. Knowledge (Knowledge Base / Analysis Documents)

Business background knowledge provided in file form, injected into conversation context via RAG retrieval.

Content suitable for the knowledge base:

* Business rule descriptions
* Data dictionary / code mapping tables
* Industry terminology explanations
* Analysis methodology / calculation formula specifications
* FAQ frequently asked questions
* Content recalled only in specific scenarios

**Core Value**: Helps the model understand the "business logic behind the data," not just the data structure.

### 3. Metrics / Answer Builder

Predefined calculation formulas supporting alias matching, ensuring consistent metric definitions. Specifically:

* Metrics: Used to define aggregation calculations (e.g., SUM, AVG)
* Answer Builder: Used to define multi-table JOINs and complex filter conditions

| Element       | Description                                                                                           | Screenshot                                            |
| ------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Metric Name   | e.g., "Average Transaction Value"                                                                     | ![](/.topwrite/assets/image_1779160566375.png =215)   |
| Calculation   | SUM(revenue) / COUNT(DISTINCT order\_id)                                                              | ![](/.topwrite/assets/image_1779160586259.png =206)   |
| Alias         | Helps the model understand different names for the same concept                                       | ![](/.topwrite/assets/image_1779160603309.png =204)   |
| Auto-Generation | Basic aggregate metrics (e.g., SUM, COUNT) can now be auto-generated for selected tables. Context-aware metric insights and auto-generation will be available in future releases, enabling smarter metric recommendations | ![](/.topwrite/assets/image_1779160824613.png =218)   |

**Core Value**: Ensures key business metrics are calculated consistently and accurately, preventing different SQL from being generated each time

### 4. Domain Prompt

System prompt at the analysis domain level, equivalent to giving the model a "role setting" and "behavioral guidelines."

* Role setting: "You are a data analyst for the Hong Kong food & beverage industry"
* Answer guidelines: "Monetary amounts default to HKD, date format uses YYYY-MM-DD"
* Business constraints: "When calculating same-store growth, only include stores that have been open for at least 12 months"
* Output preferences: "For trend-related questions, prioritize using line charts"

**Core Value**: Set global rules to avoid repeating prerequisites in every conversation

***

## 2. Which Capability for Which Scenario? (Scenario → Capability Mapping)

| Scenario/Problem Type                       | Recommended Capability            | Why                                       |
| -------------------------------------------- | --------------------------------- | ----------------------------------------- |
| Model selects wrong table or column          | Table/Column Schema Annotations   | Unclear descriptions cause matching errors |
| Filter values are wrong (e.g., using full name but data stores abbreviations) | Column Value Index                 | Establish fuzzy matching                  |
| Calculation formula is wrong (e.g., "gross profit" algorithm is incorrect) | Metrics                          | Predefined exact formulas                  |
| Complex calculation logic (multi-table JOIN + conditional filtering) | Answer Builder                   | Provides SQL templates                     |
| Model does not understand business terms (e.g., "table turnover rate") | Knowledge Base                   | Provides terminology documentation         |
| Background knowledge needed to answer (e.g., "why did March revenue decline") | Knowledge Base                   | Provides business context documentation    |
| Need to repeat prerequisites every time      | Domain Prompt                     | Set once, effective globally               |
| Same metric has multiple names               | Metric Alias / Column Alias       | Support matching with multiple expressions  |

### Decision Flowchart

```

User question is inaccurate

↓

Is it "wrong table/column selection"? → Yes → Improve Schema Annotations + Column Value Index

↓ No

Is it "wrong calculation logic"? → Yes → Create Metrics or Answer Builder

↓ No

Is it "not understanding business concepts"? → Yes → Add Knowledge Base documents

↓ No

Is it "need to repeat prerequisites every time"? → Yes → Configure Domain Prompt

↓ No

Investigate using a combination of the above methods

```

***

## 3. How to Use? (Knowledge Base Management)

### 3.1 Knowledge Base Organization

The new knowledge base uses a hierarchical folder structure (similar to Lark/Feishu knowledge base):
![](/.topwrite/assets/image_1779161523552.png)

### 3.2 Content Creation Methods

| Method         | Applicable Scenarios                           |
| -------------- | ----------------------------------------------- |
| Create directly | Manually write business rules, terminology explanations, etc. |
| Local upload   | Upload existing PDF/Word/Excel/Markdown documents |
| Cloud import   | Batch import existing documents from OSS/S3     |

### 3.3 Associate with Analysis Domains (Critical!)

Knowledge base content must be associated with an analysis domain for conversations under that domain to retrieve it:

* Can associate at the folder level → child files automatically inherit
* A single file can be associated with multiple analysis domains
* Unassociated files will not be retrieved by any conversation

**Best Practices**:

* Create folders by business theme, associate at the folder level
* General knowledge (e.g., company glossary) associates with all analysis domains
* Specific business knowledge associates only with the corresponding domain

### 3.4 What Content is Suitable for Knowledge Base?

✅ Content suitable for knowledge base:

| Content Type     | Example                                                    |
| ---------------- | ---------------------------------------------------------- |
| Business rules   | Table turnover rate = tables served / total tables; Average transaction value = revenue / customer count |
| Code mapping     | Store code A01 = Causeway Bay store, A02 = Mong Kok store |
| Industry terms   | Definitions of "dine-in", "takeaway", "table turnover", "preparation time" |
| Data definitions | "Valid orders" exclude refunded orders and test orders     |
| Analysis methods | Same-store growth only counts stores open for 12+ months   |
| Common FAQ       | "Why don't the report numbers match finance?" → Because the report excludes tax |
| Background info  | In Q1 2026, the company adjusted stores: 3 new openings, 2 closures |

❌ Content NOT suitable for knowledge base:

| Content Type                | What to Use Instead           |
| --------------------------- | ----------------------------- |
| Exact calculation formulas  | → Use the Metrics feature     |
| Complex SQL templates       | → Use the Answer Builder      |
| Column aliases/descriptions | → Use Schema Annotations      |
| Global answer guidelines    | → Use Domain Prompt           |

### 3.5 Management Recommendations

| Recommendation          | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| Organize by theme folder | Facilitates management and batch domain association  |
| Keep documents concise  | Focus each file on one topic; avoid being overly broad |
| Update regularly        | Sync knowledge base when business rules change        |
| Naming conventions      | File name reflects content, e.g., "table-turnover-rate-rules.md" |
| Verify before rollout   | Test a few questions after adding knowledge before broad use |

## 4. Summary: Synergy of the 4 Capabilities

In one sentence:

* Schema Annotations help the model "find the right data"
* Metrics help the model "calculate the right numbers"
* Knowledge Base helps the model "understand the business"
* Domain Prompt helps the model "follow the rules"

Use all four together for the highest accuracy.
