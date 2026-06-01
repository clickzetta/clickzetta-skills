# Configuring and Using Singdata Lakehouse MCP Server

## Advanced Configuration

### 1. Enabling MCP Tool Integration

If your environment supports MCP (Model Context Protocol) tools, you can add an [MCP server](lakehousemcpserver.md) via the command line:

Add an HTTP-type MCP server:

```bash
Datus> .mcp add --transport http clickzetta_mcp_http http://localhost:8002/mcp

```

Or add an SSE-type MCP server:

```bash
Datus> .mcp add --transport sse clickzetta_mcp_sse http://localhost:8003/sse

```

View the list of added MCP servers:

```bash
Datus> .mcp list

```

Check MCP server connection status:

```bash
Datus> .mcp check clickzetta_mcp_http

```

Call an MCP tool (format: server_name.tool_name; check specific tool names via .mcp check):

```bash
Datus> .mcp call clickzetta_mcp_http.<tool_name>

```

Configure tool filters (optional):

```bash
Datus> .mcp filter set clickzetta_mcp_http --allowed tool1,tool2 --enabled true

```

View tool filter configuration:

```bash
Datus> .mcp filter get clickzetta_mcp_http

```

Remove an MCP server (if needed):

```bash
Datus> .mcp remove clickzetta_mcp_http
```

**MCP Command Reference**:

* `.mcp list` - View all MCP servers
* `.mcp check <name>` - Check server connection status and display available tools
* `.mcp call <server.tool>` - Call a specific tool, format: "server_name.tool_name"
* `.mcp filter set <server> --allowed tool1,tool2` - Set the allowed tools list
* `.mcp filter get <server>` - View current filter configuration
* `.mcp remove <name>` - Remove an MCP server

**Important Note**: To find specific available tool names, first add the MCP server, then view them using the `.mcp check <server_name>` command.

#### Using MCP Tools via Subagent (Recommended)

After adding an MCP server, it is recommended to use MCP tools through a subagent, which allows you to select the desired tools during the addition process:

Add a subagent (launches interactive wizard):

```bash
Datus> .subagent add

```

View all configured subagents:

```bash
Datus> .subagent list

```

Build a knowledge base for a subagent (optional):

```bash
Datus> .subagent bootstrap agent_name

```

Remove a subagent (if needed):

```bash
Datus> .subagent remove agent_name
```

**Subagent Command Reference**:

* `.subagent add` - Launch the interactive wizard to add a new intelligent agent; MCP tools can be selected during this process
* `.subagent list` - List all configured subagents
* `.subagent bootstrap <agent_name>` - Build a specialized knowledge base for the specified agent
* `.subagent remove <agent_name>` - Remove the specified subagent

**When adding a subagent, set the following**:

```
agent_description: ClickZetta Lakehouse assistant with MCP tool integration
```

```
rules:
      - Detect user intent: distinguish between analysis requests and SQL generation
        requests
      - For analysis/explanation requests: focus on interpreting results, use markdown
        format
      - For SQL generation requests: provide executable statements with explanations
        in JSON format
      - Use MCP tools for instance switching, job history, system operations,etc
      - When users mention "instance switching", "job history", or similar operations
        - call MCP tools
      - Prefer specialized analysis tools over basic data collection tools when available
      - Use single comprehensive tools over multiple basic tool combinations when
        possible
      - Choose tools designed for the specific analysis type rather than generic tools
      - When using MCP analysis tools: focus on explaining the tool results rather
        than auto-generating SQL
```

Benefits of using MCP tools through the subagent approach:

* Interactively select desired tools during the addition process
* Create specialized intelligent agents for each scenario
* Support building specialized knowledge bases to enhance analysis capabilities

**Features After Enabling MCP Tools**:

* Instance management and switching
* Job history queries
* Advanced data analysis tools
* System monitoring functions

***

*Last updated: November 2025*
