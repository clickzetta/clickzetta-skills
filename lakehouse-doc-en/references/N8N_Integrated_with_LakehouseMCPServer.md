# Integrating Lakehouse MCP Server in N8N

N8N's Agent node supports directly integrating [tools](https://modelcontextprotocol.io/docs/concepts/tools) from external [MCP](https://modelcontextprotocol.io/introduction) servers. This provides a new way to integrate Lakehouse with your N8N AI workflows.
Lakehouse MCP Server achieves integration with N8N through this approach, allowing the rich tools from Lakehouse MCP Server to be easily invoked in N8N's Agent node.

First, you need to deploy a [Lakehouse MCP Server that supports the SSE protocol](LakehouseMCPServer_intro.md).

## Adding MCP Client in N8N Workflow AI Agent Node

The N8N MCP Client Tool node is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) client that allows you to use tools exposed by external MCP servers. You can connect the MCP Client Tool node to your model to invoke external tools using the N8N agent. **Currently, N8N only supports the SSE protocol and does not yet support communication with MCP Server via HTTP protocol**.

:-: ![](.topwrite/assets/image_1756887369109.png =795)

In the Agent node's System Message, enter:
You are a Singdata Lakehouse senior product expert, skilled at using MCP Server Tools to help users answer questions and solve problems, avoiding fabrication. For questions related to Singdata Lakehouse, if there is no suitable MCP Tool, you should first query the product knowledge base through the `get_product_knowledge` MCP Tool to obtain knowledge, and then use the appropriate Tool to execute and obtain results.

## Configuring the AI Agent Node's MCP

Configure the node using the following parameters.

* **SSE Endpoint**: The SSE endpoint of the MCP server you want to connect to.

* **Authentication**: The authentication method used to authenticate with the MCP server. Select **"None"** to attempt connection without authentication.

* **Tools to Include**: Select which tools to expose to the AI agent:

  * **All**: Expose all tools provided by the MCP server.
  * **Selected**: Activate the **Tools to Include** parameter, where you can select which tools to expose to the AI agent.
  * **All Except**: Activate the **Tools to Exclude** parameter, where you can select tools to avoid sharing with the AI agent. The AI agent will have access to all unselected MCP server tools.

:-: ![](.topwrite/assets/image_1756887446000.png =614)

Select **Selected** to see the Tools list:

\:-:
![](.topwrite/assets/image_1756887497226.png =611)

## Testing the Agent Flow

Enter your question in the dialog to operate Lakehouse:

**Question 1: What Lakehouse environments do I have?**

:-: ![](.topwrite/assets/image_1756887670661.png =629)

^

**Answer 1**:

You currently have the following 4 Lakehouse environment configurations:

1. **aliyun\_shanghai\_prod**

   * **Workspace**: quick\_start
   * **Schema**: mcp\_demo
   * **Virtual Cluster**: default\_ap
   * **Status**: Connected (currently active and default)

2. **tencent\_shanghai\_prod**

   * **Workspace**: quick\_start
   * **Schema**: mcp\_demo
   * **Virtual Cluster**: default\_ap
   * **Status**: Connected

3. **tencent\_beijing\_prod**

   * **Workspace**: quick\_start
   * **Schema**: public
   * **Virtual Cluster**: default\_ap
   * **Status**: Connected

4. **tencent\_guangzhou\_prod**

   * **Workspace**: quick\_start
   * **Schema**: public
   * **Virtual Cluster**: default\_ap
   * **Status**: Connected

The currently active environment is **aliyun\_shanghai\_prod**. If you need to switch environments, please let me know your specific requirements!

**Question 2: Help me switch to tencent_shanghai_prod**

**Answer 2**:

Successfully switched the Lakehouse environment to **tencent\_shanghai\_prod**. Here is the verification information:

* **New Connection Status**:

  * **Service Endpoint**: `ap-shanghai-tencentcloud.api.singdata.com`
  * **Workspace**: `quick_start`
  * **Schema**: `mcp_demo`
  * **Instance ID**: `270738` (Internal identifier)

* **Switch Details**:

  * Physical connection has been re-established with no configuration drift.
  * Processing time: 2.83 seconds.

If you need further verification of the current context, you can execute `get_current_context`.
Please continue to let me know your subsequent operation needs!

**Question 3: What is the current context?**

**Answer 3**:

Current context information is as follows:

* **Instance ID**: `270738`
* **Schema**: `mcp_demo`
* **Username**: `qiliang` (ID: `2162115`)
* **Virtual Cluster**: `default_ap`
* **Workspace**: `quick_start`
* **Connection Time**: `2025-09-03 16:25:45` (UTC+8)

The current environment is **tencent\_shanghai\_prod** (Tencent Cloud Shanghai production environment), with normal status. Please feel free to let me know if you need any other operations!

^

Similarly, you can also enter questions in the dialog for Lakehouse-related knowledge Q&A:

^

:-: ![](.topwrite/assets/image_1756888912810.png =813)

^

As you can see, Lakehouse can be conveniently accessed through N8N workflows!
