# Answer Explainability

Analytics Agent can generate analysis results based on natural language questions, drawing on data sources, knowledge bases, metric calculation definitions, reference SQL, and Answer Builder. For business users, getting a number is only the first step. What matters more is understanding what the number represents, why it was calculated that way, what evidence was used, and what to do when the result is uncertain.

The **Answer explainability** feature helps you move from "seeing an answer" to "understanding, verifying, and correctly using an answer" through structured responses, calculation definition explanations, source attribution, and anomaly alerts.

> **Tip**: This feature currently focuses on structured presentation of answer results, calculation definition explanations, source tracing, and anomaly handling.

## What Problems It Solves

| Problem during use | How Answer explainability helps |
| --------------------- | ------------------------------------ |
| Only see a result, no idea how the metric is calculated | Business calculation definitions and statistical scope are shown directly in the answer |
| The answer is long and key points are hard to find | Shows a data overview and key insights first; technical details can be expanded on demand |
| Want to know how Agent analyzed the question | Expand the Thinking in the reasoning process to view reasoning stages, judgment basis, and tool call summaries |
| Not sure which configurations or knowledge were referenced in the answer | View referenced metrics, SQL, Answer Builder, knowledge, and change records |
| The question is ambiguous and you worry Agent misunderstood it | Default assumptions are labeled, or candidate calculation definitions and recommended reasons are shown |
| The data source doesn't support the question, but a plausible-sounding analysis is returned | Clearly states what data, fields, or permissions are missing, and gives next-step suggestions |

## Core Capabilities

### Expandable Reasoning Process

During answer generation, Agent shows the current analysis status in progress. After the answer is complete, the process area is collapsed by default to avoid distracting from the result. If you want to understand how Agent interpreted the question, retrieved information, and organized the analysis, you can expand **Reasoning Process** to view the productized process content.

After expanding, you can typically see:

* **Question understanding**: identifies question intent, and possible ambiguities in time range, metrics, dimensions, etc.;
* **Information retrieval**: searches for relevant data tables, metrics, knowledge bases, and user context;
* **Analysis judgment**: explains the analysis direction taken, calculation definition choices, and key decisions;
* **Tool call summary**: view the tools or data retrieval actions used, such as looking up data tables, querying metrics, and reading knowledge;
* **Stage output**: view the summaries or intermediate findings formed at each reasoning stage.

This content helps you understand how the answer was formed. It is not equivalent to a "pre-planned task list." Agent may dynamically enter different analysis stages depending on the complexity of the question.

![](/.topwrite/assets/image_1786696770415.png)

### Structured Presentation of Analysis Results

For complex analytical questions, answers are organized with the following content first:

| Content | What you can see |
| ------------- | ------------------------- |
| **Data overview** | Core metric cards, key values, and results broken down by dimension |
| **Text insights** | 2 to 4 key findings, business implications, and anomalies |
| **Calculation definition** | Metric definitions, calculation formulas, statistical time range, and filter scope |
| **Assumptions / Risk notes** | Default interpretations Agent adopted, and risks that may affect results |

The data overview helps you find the result quickly, text insights help you understand the result, and calculation definition explanations help you judge whether the result applies to your current business scenario.

![](/.topwrite/assets/image_1786696809929.png)

### Metric Calculation Definitions and Source Tracing

Calculation definition explanations in the answer are expressed in business language. If you need further verification, you can expand **Calculation Definition and External References** to view what was referenced in this answer:

* Referenced metrics and formulas;
* Referenced Answer Builder;
* Referenced knowledge or documents.

Technical content such as SQL, field mappings, Request / Response, and query result samples is collapsed by default to avoid disrupting normal reading. You can expand specific sources further when troubleshooting.

:-: ![](/.topwrite/assets/image_1786696837761.png =527)

### Transparent Handling of Ambiguous Questions

Not every ambiguous question requires a clarifying follow-up. Agent handles questions differently based on the potential impact of the ambiguity.

#### Light ambiguity: answer with assumptions labeled

When a question can be answered and the default interpretation would not significantly change the business meaning, Agent provides the result first, states the assumptions adopted, and offers follow-up adjustment options such as "last quarter" or "last 30 days."

For example, you ask:

> How have sales been recently?

Agent's answer might state:

> I interpreted "recently" as the last 7 days and "sales" as revenue from completed orders.

#### :-: ![](/.topwrite/assets/image_1786692913338.png =448)

#### Critical ambiguity: confirm the calculation definition first, then generate results

When the same concept has multiple authoritative definitions and different definitions would significantly affect results, Agent does not randomly pick a calculation definition. Instead, it shows the candidate calculation definitions, result differences, and recommended reasons.

For example, "What is the total revenue?" might correspond to:

1. Revenue from completed orders;
2. Total amount of all orders;
3. Net revenue.

You can use the recommended calculation definition, compare multiple calculation definitions, or directly select the one that matches your business definition.

### :-: ![](/.topwrite/assets/image_1786693031276.png =540)

### Identifying Unanswerable Scenarios and Providing Correction Paths

When a core concept has no mapping, required fields or tables are missing, permissions are insufficient, data is empty, or multiple authoritative calculation definitions cannot be resolved, Agent explicitly indicates that it cannot provide a reliable answer and stops generating charts or lengthy analysis that might mislead you.

The feedback typically includes:

* Why the current question cannot be answered;
* What is missing or cannot be confirmed;
* What you can do next, such as switching the data source, adding fields, or rephrasing to a question that can be supported.
  ![](/.topwrite/assets/image_1786696943321.png)

## Usage Recommendations

* **Clarify the question before reviewing the process**: When asking questions, try to specify the metric, time range, subject of analysis, and filter conditions clearly. After the answer is generated, read the conclusion first, then expand Thinking or sources as needed.
* **Choose what to expand based on your verification goal**: To understand how Agent interpreted and analyzed the question, expand Thinking. To confirm metric definitions and data evidence, expand "Calculation Definition and External References." To troubleshoot technical issues, then look at SQL, field mappings, or tool call details.
* **Keep business context for critical questions**: When making operational judgments, add business definitions, time ranges, and filter conditions in follow-up questions. Avoid vague prompts like "more detail" that leave the analysis target unclear.
* **Treat anomaly alerts as entry points for follow-up**: When default assumptions, calculation definition conflicts, or unanswerable alerts appear, prioritize adding information or adjusting the question based on the alert before continuing to use the result.

## Important Notes

* **Explanation content reflects this answer's pipeline**: Thinking, calculation definition explanations, and external references reflect the actual judgments and assets used in generating this answer. They do not represent a unified explanation for all historical answers.
* **Source information does not guarantee result correctness**: Referenced metrics, SQL, knowledge, and Answer Builder help verify evidence but may still be affected by configuration changes, data quality issues, or changes to business calculation definitions.
* **Default interpretations require human confirmation**: For questions with multiple possible meanings such as "recently," "sales performance," or "customer count," confirm the time range, statistical subject, and metric definition before using the result.
* **Critical conclusions still require business review**: Results related to financial reporting, operational decisions, or external disclosures should not be used solely based on Agent's explanation or sources.

## FAQ

### What is the difference between Thinking and "Calculation Definition and External References"?

Thinking answers "how did Agent understand and analyze this question." "Calculation Definition and External References" answers "what definitions were used for this result and which assets were referenced." The former is for understanding the analysis process; the latter is for verifying the result's basis.

### Why do some answers have relatively little Thinking content?

The content shown in Thinking varies based on question type and complexity. Data query questions typically show question understanding, information retrieval, and analysis stages. Consulting-type questions such as "how to ask" or "why was this calculation definition used" typically provide a direct explanation without displaying the full data query process.

### Why does Thinking show summaries and tool names rather than full system logs?

The product prioritizes showing reasoning stages, key judgments, and tool call summaries that business users can understand. Technical details such as SQL, field mappings, and Request / Response can be expanded on demand. Raw system logs are not shown as default answer content.

### Should I expand Thinking first, or sources first?

If you want to judge whether Agent correctly understood the question, look at Thinking first. If you want to confirm how a metric is calculated or what knowledge or SQL was used, look at "Calculation Definition and External References" first. For critical business conclusions, it is recommended to review both.

### Why might the explanation or result for the same question differ at different times?

Answers are generated based on the data, metrics, knowledge, and Answer Builder available at that time. If relevant assets or underlying data have changed, the answer to the same question may also change. When reconciling differences, pay attention to both the sources of this answer and the change records.

Answer explainability is not a one-time technical log display. It is Analytics Agent's result explanation capability for business users: first help you understand the conclusion, then let you verify the calculation definition, trace the source when necessary, and tell you how to proceed when a reliable answer cannot be provided.

## Related Documentation

* [Reading Analysis Results](datagpt-answer-reading-guide.md)
* [Question Asking Guide](datagpt-question-asking-guide.md)
* [Metrics and Answer Builder](metrics_answer_build.md)
* [Knowledge Base](datagpt-knowledge-base-guide.md)
* [Handling Feedback](datagpt-feedback-loop-guide.md)

^
