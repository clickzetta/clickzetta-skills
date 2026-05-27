# Integrating Lakehouse MCP Server in Dify

Dify's Agent application supports direct integration of external [MCP](https://modelcontextprotocol.io/introduction) server [tools](https://modelcontextprotocol.io/docs/concepts/tools). This provides a new way to integrate Lakehouse with your Dify AI applications.
Lakehouse MCP Server achieves integration with Dify in this way, and the rich tools from Lakehouse MCP Server can be easily invoked in Dify's Agent.

## Dify MCP Server Management Interface

After logging into Dify, click **Tools** → **MCP** in the left navigation bar to enter the external MCP server management page. Here, you can centrally manage all MCP servers configured for your applications.

## Adding a Lakehouse MCP Server

First, you need to deploy a [Lakehouse MCP Server supporting HTTP protocol](LakehouseMCPServer_intro.md).

:-: ![](.topwrite/assets/image_1756885164463.png =815)

Click **Add MCP Server (HTTP)** to integrate the Lakehouse MCP Server tool service. You need to fill in the following information:

* **Server URL**: The HTTP interface address of the Lakehouse MCP server, e.g., `http://192.168.1.220:8001/mcp`.
* **Name & Icon**: Custom server name; it is recommended to choose a name that clearly reflects the tool's purpose. Dify will automatically attempt to fetch the server's domain icon; you can also manually upload one. E.g., singdata-mcp-server-mcp-220
* **Server Identifier**: A unique ID used by Dify to distinguish servers. Rules: lowercase letters, numbers, underscores, or hyphens, up to 24 characters. E.g., singdata_mcp_mcp_220

The server ID cannot be changed once created. If you change the server ID, all Agents or Workflows that depend on that server's tools will become invalid. This design is particularly important for [application portability](https://docs.dify.ai/guides/tools/mcp##application-portability).

After adding the server, Dify will automatically perform the following operations:

1. **Detect Available Tools**: Automatically identify which tool functions the server can provide.
2. **Process Authorization Flow**: If the server requires authentication, automatically initiate the OAuth authorization flow.
3. **Retrieve Tool Definitions**: Download the interface definitions (schemas) for each tool.
4. **Sync Tool List**: Add the identified tools to the build page of the Agent or Workflow application.

When Dify successfully retrieves at least one available tool, it will display the server information card on the page:

:-: ![](.topwrite/assets/image_1756885349165.png =806)

## Managing Connected Servers

Click the corresponding server card to perform the following operations:

* **Update Tools**: Re-fetch the latest tool information from the server, suitable after the service provider has added or adjusted features.

* **Re-authorize**: Click the authorization status to update the server's access permissions (e.g., when a token has expired and needs re-authorization).

* **Edit Configuration**: Modify server information.

Changing the server URL will trigger re-authorization, and modifying the server ID will invalidate existing applications!

:-: ![](.topwrite/assets/image_1756885405845.png =478)

* **Remove Server**: Disconnect the server. After this, all applications that depend on this server's tools will report errors until you reconnect or delete the related tools.

:-: ![](.topwrite/assets/image_1756885449635.png =473)

Once the server configuration is complete, its tools will appear in the tool selection area when building applications:

## Designing Agent Applications

:-: ![](.topwrite/assets/image_1756885639345.png =816)

* In the Agent configuration interface, MCP tools are displayed alongside built-in tools.
* You can click "Add All" to quickly enable all tools under that server.
* In the instruction section of the Agent node, set it to: You are a Singdata Lakehouse senior product expert. Please help users answer questions and solve problems. For questions related to Singdata Lakehouse, if there is no suitable tool, you need to first query the product knowledge base using the get_product_knowledge tool to obtain knowledge. As a product expert, you must not fabricate any hypothetical product knowledge or judgments. Everything must be based on the knowledge and objective results obtained from MCP tool calls.

## Publishing Agent Applications

:-: ![](.topwrite/assets/image_1756885966336.png =786)

## Accessing Agent Applications

After publishing, click "Open in Explore" to access the Agent application in your browser. Here, you can invoke the tools corresponding to the Lakehouse MCP Server based on the conversation content.

![](.topwrite/assets/image_1756886184934.png)
