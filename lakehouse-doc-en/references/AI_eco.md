# AI Ecosystem

Singdata Lakehouse is deeply integrated with mainstream AI development frameworks and workflow platforms, providing vector storage, full-text search, file storage, and data query capabilities as the data infrastructure for AI applications.

---

## Contents

| Integration | Description |
|-------------|-------------|
| [Dify Integration](dify_yunqilakehouse_integration_overview.md) | Use Lakehouse as Dify's vector database and file storage service, supporting RAG knowledge base construction and unstructured data management |
| [N8N Integration](N8N_AI_Workflow_Integration.md) | Use Lakehouse nodes in N8N visual workflows, supporting data queries, table data comparison, and multi-database workflow automation |
| [LangChain Integration](langchain_integration.md) | LangChain Singdata plugin that brings Lakehouse capabilities into LangChain AI applications, supporting vector retrieval and RAG application development |
| [Unstructured Data ETL Pipeline](unstructured-io.md) | Use Unstructured to convert PDFs, emails, images, and other unstructured data into JSON, write it to Lakehouse, and build a vector index to feed RAG applications |
| [Datus Data Engineering Agent](Datus_Lakehouse_Integrated_Guide.md) | An open-source data engineering agent that provides domain-aware intelligent assistance for analysts and business users, integrating with Lakehouse via MCP Server |

---

## Quick Selection Guide

**I'm building an AI application with Dify and need knowledge base storage**
→ [Dify Integration](dify_yunqilakehouse_integration_overview.md): configure Lakehouse as a vector database or file storage

**I'm building an automated workflow with N8N and need to operate a database**
→ [N8N Integration](N8N_AI_Workflow_Integration.md): install the Lakehouse N8N node, supporting queries and data comparison

**I'm developing an AI application with LangChain and need vector retrieval**
→ [LangChain Integration](langchain_integration.md): use the LangChain Singdata plugin to connect to Lakehouse

**I have large volumes of PDFs, images, and other unstructured files and need to build RAG**
→ [Unstructured Data ETL Pipeline](unstructured-io.md): complete pipeline from Unstructured to a Lakehouse vector table

**I want to use an AI Agent to automate data engineering tasks**
→ [Datus Integration](Datus_Lakehouse_Integrated_Guide.md): let the agent operate Lakehouse directly via MCP Server
