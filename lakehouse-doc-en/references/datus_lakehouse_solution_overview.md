# Datus and Singdata Lakehouse Integration Overview

## What is Datus

[Datus](https://github.com/Datus-ai/Datus-agent) is an open-source data engineering agent designed to build evolvable contextual environments for data systems. Datus represents a paradigm shift in data engineering: from the traditional approach of "building tables and data pipelines" to "providing domain-aware intelligent agents for analysts and business users."

CLI Quick Overview:

:-: ![](/.topwrite/assets/20251127152801_rec_.gif =804)

Web Quick Overview:

:-: ![](/.topwrite/assets/20251127171510_rec_.gif =804)

###

### Core Components

**Datus-CLI**: An AI-driven command-line interface for data engineers, which can be understood as "Claude Code for data engineers." Key features include:

* **Interactive SQL Writing**: Generate and optimize SQL queries through natural language
* **Subagent Building**: Create domain-specific intelligent agents (subagents)
* **Context Building**: Interactively build and evolve contextual knowledge for data systems

**Datus-Chat**: A web chatbot that provides for data analysts:

* **Multi-turn Conversations**: Continuous data exploration and analysis dialogue
* **Feedback Mechanisms**: Built-in feedback systems including likes, issue reporting, success cases, etc.
* **User-friendly**: Optimized interface experience for non-technical users

**Datus-API**: A stable, accurate data service API for other agents or applications.

### Technical Features

* **Multi-AI Model Support**: Integrates Qwen, DeepSeek, OpenAI, Claude, and other AI models
* **Extensible Architecture**: Supports MCP (Model Context Protocol) tool integration.
* **Multi-data Source Connectivity**: Supports various database and data warehouse platforms.
* **Chinese Language Optimization**: Specially optimized for Chinese language contexts and usage habits.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface Layer                       │
├──────────────────────────────┬──────────────────────────────────┤
│         Datus-CLI            │         Datus-Chat               │
│      (Command Line)          │       (Web Interface)            │
│  ┌─────────────────────────┐ │  ┌─────────────────────────────┐ │
│  │ • Natural Lang Query    │ │  │ • Multi-turn Conversations  │ │
│  │ • SQL Generation        │ │  │ • Subagent Selection        │ │
│  │ • MCP Tool Invocation   │ │  │ • Feedback Mechanisms       │ │
│  └─────────────────────────┘ │  └─────────────────────────────┘ │
└──────────────────────────────┴──────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Datus Agent Core                            │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐ │
│ │ AI Models   │ │ Subagents   │ │     Context Management      │ │
│ │             │ │             │ │                             │ │
│ │ • Qwen      │ │ • lakehouse │ │ • Database Schema           │ │
│ │ • DeepSeek  │ │ • mcp_agent │ │ • Query History             │ │
│ │ • OpenAI    │ │             │ │ • Embedding Vectors         │ │
│ │ • Claude    │ │             │ │ • Knowledge Base            │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
    (Datus-Singdata)                 (MCP Protocol)
┌─────────────────────────┐      ┌─────────────────────────┐
│      Data Layer         │      │    Tool Extension       │
├─────────────────────────┤      ├─────────────────────────┤
│  Singdata Lakehouse     │◄─────┤ Singdata MCP Server     │
│                         │      │                         │
│ ┌─────────────────────┐ │      │ ┌─────────────────────┐ │
│ │ • Data Storage      │ │      │ │ • Instance Mgmt     │ │
│ │ • Compute Engine    │ │      │ │ • Job Monitoring    │ │
│ │ • SQL Execution     │ │      │ │ • System Ops        │ │
│ │ • Metadata Mgmt     │ │      │ │ • Analytics         │ │
│ └─────────────────────┘ │      │ └─────────────────────┘ │
│                         │      │                         │
│ Connection:             │      │ Connection:             │
│ • Service Endpoint      │      │ • HTTP Transport        │
│ • Username/Password     │      │ • SSE Transport         │
│ • Instance/Workspace    │      │ • Tool Filtering        │
└─────────────────────────┘      └─────────────────────────┘
```

### Architecture Description

**User Interface Layer**:

* **Datus-CLI**: Provides a command-line interface for data engineers
* **Datus-Chat**: Provides a web interface for data analysts and business users

**Datus Agent Core**:

* **AI Model Layer**: Supports multiple large language models, allowing selection of the most suitable model based on task type
* **Subagent Management**: Different intelligent agents handle different business scenarios.
* **Context Management**: Maintains the knowledge graph and query context of the data system.

**Data Layer**:

* **Singdata Lakehouse**: Provides data storage, computing, and SQL execution capabilities

**Tool Extension Layer**:

* **Singdata Lakehouse MCP Server**: The official MCP server provided by Singdata Lakehouse, extending system capabilities through standardized protocols and offering advanced management and analysis tools

### Connection Relationship Description

1. **Datus <-> Singdata Lakehouse**: Connected via the **Datus-Singdata** connector for database connectivity, supporting SQL query execution and metadata retrieval.
2. **Datus <-> Singdata Lakehouse MCP Server**: Connected via the **MCP protocol**, invoking advanced management and analysis tools.
3. **Singdata Lakehouse MCP Server <-> Singdata Lakehouse**: The MCP Server serves as an extension service for Singdata Lakehouse, able to access and manage the underlying data platform.

## Integration Value

### Datus + Singdata Lakehouse

Singdata Lakehouse, as a modern data lakehouse platform, has powerful data processing and storage capabilities. After integration with Datus:

1. **Lower the Barrier to Entry**: Business users can directly query and analyze massive datasets without learning SQL
2. **Improve Analysis Efficiency**: Natural language queries significantly reduce the time cost of data exploration
3. **Intelligent Insights**: AI-driven query optimization and result interpretation help users better understand data
4. **Chinese-friendly**: Optimized for Chinese language contexts, better suited for local users' habits.

### Datus + Singdata Lakehouse MCP Server

Through integration with the official Singdata Lakehouse MCP Server, system capabilities are further extended:

1. **Instance Management**: Intelligently switch between different Singdata Lakehouse instances and environments
2. **Job Monitoring**: Query and analyze SQL job execution history and performance metrics.
3. **System Operations**: Perform system status queries and configuration management through natural language.
4. **Advanced Analytics**: Utilize specialized analysis tools for deep data insights.
5. **Workflow Automation**: Encapsulate complex data processing workflows as simple natural language instructions.

## Use Cases

* **Data Analysts**: Quickly explore and analyze business data, generate reports and insights
* **Business Users**: Users without technical backgrounds can easily query the data they need
* **Data Engineers**: Perform system management and job monitoring through MCP tools
* **Decision Makers**: Quickly access key business metrics and trend analysis

***

*Last updated: November 2025*
