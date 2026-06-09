# Web Search

> \[Preview Release] This feature is currently in an invite-only preview release. Contact technical support if you need access.

## Feature Overview

Web Search adds internet search capability to Analytics Agent, enabling the Agent to automatically invoke external search engines during data analysis to obtain real-time information, achieving combined analysis of "internal data + external knowledge." This is suitable for scenarios requiring data attribution analysis in conjunction with external events (such as weather, sports events, news, etc.).

## Usage

Simply ask questions directly in the conversation window; there is no need to manually select a tool. The Agent will automatically determine whether an internet search is needed based on the question content.

### Example

\> *Question: What caused the change in order volume between March 28–30, 2025*?

The Agent will automatically perform the following steps:

1\. Query the internal database to retrieve the number of comments and rating data for the corresponding time period

2\. Invoke web search to obtain external information such as weather, sports events, and news during the same period

3\. Conduct multi-dimensional attribution analysis and output conclusions along with visualization charts

![](/.topwrite/assets/image_1780907641261.png)

**Notes**

1\. Web search results are influenced by the content returned by the search engine; it is recommended to manually verify key conclusions.

2\. **The Web Search feature is currently in beta. To enable internet search capability, please contact the Singdata team**.

## Related Documentation

* [Improve Answer Accuracy](answer-accuracy-improve.md) — Further improve answer quality with a knowledge base and semantic layer
* [Scheduled Task](scheduled_task.md) — Automatically run data analysis on a schedule and push results
* [Conversational Data Analytics (Analytics Agent)](datagpt_introduction.md) — Return to the feature overview

^
