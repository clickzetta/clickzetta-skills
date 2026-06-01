# Integrating Lakehouse MCP Server in Dify

Dify's Agent applications support direct integration of [tools](https://modelcontextprotocol.io/docs/concepts/tools) from external [MCP](https://modelcontextprotocol.io/introduction) servers. This provides a new way to integrate Lakehouse with your Dify AI applications.
Lakehouse MCP Server achieves integration with Dify through this approach, allowing the rich set of tools from Lakehouse MCP Server to be easily invoked within Dify Agents.

## Dify MCP Server Management Interface

After logging into Dify, click **Tools** -> **MCP** in the left navigation bar to access the management page for external MCP servers. Here, you can centrally manage all MCP servers configured for your applications.

## Adding a Lakehouse MCP Server

First, you need to deploy the [Lakehouse MCP Server supporting HTTP protocol](lakehousemcpserver-intro.md)

:-: ![](.topwrite/assets/image_1756885164463.png =815)

Click **Add MCP Server (HTTP)** to integrate Lakehouse MCP Server tool services. You need to fill in the following information:

* **Server URL**: The HTTP endpoint address of the Lakehouse MCP server, for example when integrating Notion it would be `http://192.168.1.220:8001/mcp`.
* **Name and Icon**: Custom server name; it is recommended to choose a name that clearly reflects the tool's purpose. Dify will automatically attempt to obtain the server domain's icon; you can also upload one manually. For example: clickzetta-mcp-server-mcp-220
* **Server Identifier**: A unique ID used by Dify to distinguish servers. Rules: lowercase letters, digits, underscores, or hyphens, up to 24 characters. For example: clickzetta\_mcp\_mcp\_220

Once created, the server ID cannot be changed. If the server ID is changed, all Agents or Workflows that depend on that server's tools will become invalid. This design is particularly important for [application migration](https://docs.dify.ai/zh-hans/guides/tools/mcp##application-portability).

After adding a server, Dify automatically performs the following operations:

1. **Detect Available Tools**: Automatically identify which tool functions the server can provide.
2. **Handle Authorization Flow**: If the server requires authentication, automatically initiate the OAuth authorization flow.
3. **Obtain Tool Definitions**: Download the interface definitions (schema) for each tool.
4. **Sync Tool List**: Add the identified tools to the build page of the Agent or Workflow application.

When Dify successfully obtains at least one available tool, it will display an information card for that server on the page:

:-: ![](.topwrite/assets/image_1756885349165.png =806)

## Managing Connected Servers

Click the corresponding server card to perform the following operations:

* **Update Tools**: Re-fetch the latest tool information from the server, suitable for updating when the service provider adds or adjusts functionality.

* **Re-authorize**: Click the authorization status to update the server's access permissions (e.g., when a token expires and needs re-authorization).

* **Edit Configuration**: Modify server information.

Changing the server URL will trigger re-authorization; modifying the server ID will invalidate existing applications!

:-: ![](.topwrite/assets/image_1756885405845.png =478)

* **Remove Server**: Disconnect the server. After this, all applications that depend on this server's tools will report errors until you reconnect or delete the relevant tools.

:-: ![](.topwrite/assets/image_1756885449635.png =473)

After the server is configured, its tools will appear in the tool selection area when building applications:

## Designing an Agent Application

:-: ![](.topwrite/assets/image_1756885639345.png =816)

* In the Agent configuration interface, MCP tools are displayed alongside built-in tools.
* You can click "Add All" to quickly enable all tools under that server.
* In the instructions section of the Agent node, set it to: You are a Singdata Lakehouse senior product expert. Please help users answer and solve problems. For questions related to Singdata Lakehouse, if there is no suitable tool, you need to first query the product knowledge base through the `get_product_knowledge` tool to obtain knowledge. As a product expert, you must not fabricate any hypothetical product knowledge or judgments. Everything must be based on the knowledge and objective results from MCP tool calls.

## Publishing the Agent Application

:-: ![](.topwrite/assets/image_1756885966336.png =786)

## Accessing the Agent Application

After publishing, click "Open in Explore" to access the Agent application in your browser. Here, the tools corresponding to the Lakehouse MCP Server can be invoked based on the conversation content.

![](.topwrite/assets/image_1756886184934.png)
