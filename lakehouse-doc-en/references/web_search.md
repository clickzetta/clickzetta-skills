# Web Search

## Feature Overview

Web Search adds internet search capability to Analytics Agent, enabling the agent to automatically invoke external search engines during data analysis to obtain real-time information, achieving combined analysis of "internal data + external knowledge." This is suitable for scenarios requiring correlation analysis between internal data and external events (such as weather, sports events, news, etc.).

## How to Use

Simply ask questions directly in the conversation window; there is no need to manually select a tool. The Agent will automatically determine whether an internet search is needed based on the question content.

### Example

\> *Question: What caused the change in order volume between March 28-30, 2025?*

The Agent will automatically perform the following steps:

1\. Query the internal database to retrieve the number of comments and rating data for the corresponding time period

2\. Invoke web search to obtain external information such as weather, sports events, and news during the same period

3\. Conduct multi-dimensional attribution analysis and output conclusions along with visualization charts

\:-:
![](/.topwrite/assets/image_1776137592328.png =427)

**Notes**

1\. Web search results are influenced by the content returned by the search engine; it is recommended to manually verify key conclusions

2\. **The Web Search feature is currently in beta. To enable internet search capability, please contact the Singdata team**
