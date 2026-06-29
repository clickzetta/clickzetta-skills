# Studio-Hosted MCP Server Setup Guide

Setting up the Studio-hosted MCP Server involves three steps:

* Go to the MCP Servers page in Studio.
* Create a Personal Access Token and set the default connection environment.
* Add the client configuration to an AI client such as Claude Desktop, Cursor, or Cherry Studio.

This document answers "how to integrate" and "what to watch out for during integration."

## Where to Find the MCP Server Entry Point

The MCP Server entry point is at:

* Lakehouse home page
* Left menu: **AI**
* Click **MCP Servers**

Clicking opens a new Console page and shows the `Lakehouse MCP & CLI` configuration dialog.

This dialog includes both Token management and connection configuration templates for different clients.

## Creating a Personal Access Token

In the `Lakehouse MCP & CLI` dialog, create a Personal Access Token first.

You need to fill in or confirm the following:

* Token name
* Expiry period
* Default environment
    * Region
    * Workspace
    * VCluster
    * Schema (if needed)

The default environment is important. It determines which region, Workspace, VCluster, and Schema the Agent accesses by default when not explicitly switching context.

## Key Points About Tokens

### The plain-text Token is shown only once

After the Token is created, the page displays the full Token once. Once you close the page, only a masked value is shown, so copy and store it immediately when it appears.

### The Token inherits the current user's permissions

The Token essentially inherits the permissions the current user already has in Studio and Lakehouse. It is not a lower-privileged proxy account — it grants the current user's identity to the Agent.

Therefore:

* Do not share the Token with unrelated parties.
* Do not store the Token in plain text in public repositories.
* If you suspect a leak, delete the Token and create a new one immediately.

### Deleting a Token immediately affects connected clients

Deleting a Token invalidates any MCP connections that depend on it. Confirm that no clients are still using the Token before deleting it.

### Token expiry and renewal

Tokens require an expiry period when created. Once a Token expires, any dependent MCP connections immediately fail, and the client receives an authentication error.

To renew: go to the MCP Servers page in Studio and renew an existing Token to extend its validity period. No client reconfiguration is needed and the connection resumes normally. If the Token has already been deleted, you must create a new one, replace the Token value in the client configuration, and restart the client.

## Claude Desktop Configuration

To integrate with Claude Desktop, add an MCP Server entry to the local `claude_desktop_config.json` file.

Common file locations:

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`

In the MCP Servers page, switch to the Claude configuration section and copy the template configuration. Replace the `token` placeholder with the plain-text Token you received when the Token was created.

Example:

```json
{
  "mcpServers": {
    "clickzetta-studio-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://cn-shanghai-alicloud-mcp.api.clickzetta.com/mcp",
        "--allow-http",
        "--transport",
        "http",
        "--header",
        "X-Lakehouse-Token: Bearer <your_token>"
      ]
    }
  }
}
```

If Claude Desktop cannot find `npx`, change `command` to the absolute path of `npx`.

## Cherry Studio Configuration

If you use Cherry Studio, add a new HTTP-based server entry in the MCP settings.

You typically need to fill in:

* Service name
* MCP Server URL
* Token in the request header

Clients of this type do not necessarily require running `npx` locally, but you still need to provide the correct Token and server URL.

## Verifying the Integration

After completing the integration, run a simple verification before starting complex tasks.

For example, ask the Agent:

* List the folders in the current Workspace.
* List the data sources in the current Workspace.
* Show me which tables are in the `public` schema.

If these structured queries return results, the MCP connection is working and the default environment configuration is correct.

## Typical Capabilities After Integration

Once integrated, the Agent can typically:

* Query Lakehouse metadata
* Read and create Studio catalogs and tasks
* Save task content and task configuration
* Publish tasks and run tasks temporarily
* Read task instances, attempts, and execution logs

For how to use these capabilities, continue reading:

* [Studio MCP Task Development and Run Diagnosis Guide](studio-mcp-task-development-and-diagnosis-guide.md)

## Common Integration Issues

### Claude Desktop Cannot Find `npx`

If Claude Desktop reports that `npx` cannot be found or the local command cannot start, check:

* Whether Node.js is installed on your machine
* Whether `node -v` and `npx -v` work correctly in a terminal
* Whether Claude Desktop needs an absolute path to `npx`

### Integration Complete but No New Tools Visible

In some clients, adding a new MCP Server requires restarting the client or opening a new session before the tool list refreshes.

### Connection Succeeds but Points to the Wrong Environment

This is usually related to the default environment set when the Token was created. If the default Workspace, VCluster, or Schema was set incorrectly, the Agent can connect but will query or operate in the wrong context.

## Related Documents

- [MCP Server (Studio-hosted, recommended)](MCPServers.md) — Overview page with recommended reading path
- [Studio MCP Capabilities Overview](studio-mcp-capabilities-overview.md) — What you can do after integration
- [Studio MCP Task Development and Run Diagnosis Guide](studio-mcp-task-development-and-diagnosis-guide.md) — The first hands-on scenario after integration
- [Studio MCP Best Practices](studio-mcp-best-practices.md) — Day-to-day usage principles
