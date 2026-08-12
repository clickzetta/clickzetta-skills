# Studio Managed MCP Server

Singdata Lakehouse Studio includes a built-in managed MCP Server. You do not need to deploy a service process yourself. Create a Personal Access Token in Studio, then configure the corresponding client to connect Claude Desktop, Cursor, Cherry Studio, or other AI agents — and the agent can directly operate Lakehouse and Studio data, tasks, and operations capabilities.

This capability is designed for two types of users:
 
* Users who want to connect Lakehouse and Studio to a general-purpose AI client
* Users who want AI agents to participate directly in task development, task execution, and operations troubleshooting

The difference between this and the [standalone Lakehouse MCP Server](LakehouseMCPServer.md) is:

* **Studio Managed**: Hosted by Singdata, suited for quick onboarding and day-to-day use
* **Self-Hosted**: Deployed by the user, suited for scenarios that require custom deployment or integration strategies

## What This MCP Can Do

The Studio managed MCP Server covers the following typical scenarios:

* Query Lakehouse data sources, schemas, tables, and other metadata
* Create and read Studio directories, tasks, task content, and configurations
* Publish tasks, run tasks ad hoc, and read task instances, execution attempts, and execution logs
* Provide dedicated tools for more complex objects such as CDC tasks, data quality tasks, and composite tasks

This means the agent is not limited to "running a SQL query" — it can be integrated into actual Studio workflows.

## Recommended Reading Path

If you are new to the Studio managed MCP Server, read the following in order:

* [Studio Managed MCP Server Setup Guide](studio-mcp-setup-guide.md)
* [Studio MCP Usage: Explore First, Then Execute](studio-mcp-how-to-ask-guide.md)
* [Studio MCP Capabilities Overview](studio-mcp-capabilities-overview.md)
* [Studio MCP: SQL Tasks](studio-mcp-sql-task-guide.md)
* [Studio MCP: Python Tasks](studio-mcp-python-task-guide.md)
* [Studio MCP: Batch Sync Tasks](studio-mcp-offline-integration-task-guide.md)
* [Studio MCP Scenario: Batch Sync followed by SQL Modeling](studio-mcp-offline-sync-to-sql-elt-guide.md)
* [Studio MCP: Configure Task Parameters and Scheduling](studio-mcp-parameters-and-scheduling-guide.md)
* [Studio MCP: Publish, Unpublish, and Run Diagnostics](studio-mcp-release-and-diagnosis-guide.md)
* [Studio MCP Task Development and Run Diagnostics Guide](studio-mcp-task-development-and-diagnosis-guide.md)
* [Studio MCP: Data Integration Tasks](studio-mcp-integration-task-guide.md)
* [Studio MCP: Multi-Table Real-Time Sync Tasks](studio-mcp-cdc-realtime-sync-guide.md)
* [Studio MCP Best Practices](studio-mcp-best-practices.md)

## When MCP Works Well

The following scenarios are generally better handled by letting an agent operate through MCP rather than clicking through the UI:

* Quickly inventorying the data sources, schemas, tables, and tasks in the current workspace
* Viewing task basic info, task configurations, and task status in bulk
* Adding content to existing SQL, Python, or batch sync tasks, updating descriptions, or reading execution logs
* Having the agent run an initial diagnostics pass before deciding whether to return to the UI for more detailed manual inspection

## When to Return to the UI

MCP is well suited for structured operations, but it is not meant to replace all UI interactions. The following scenarios typically still benefit from using the UI:

* When you need to manually review complex graphical configurations
* When you need to browse long execution results, graphical dependency views, or lengthy logs
* When you need to visually compare multiple candidate objects

A natural usage pattern is:

* Use MCP first for quick queries, navigation, and execution
* Then use the UI for visual confirmation, fine-tuning, and final review
