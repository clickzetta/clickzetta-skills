# Lakehouse MCP Server Introduction and Quick Deployment

## Introduction

MCP (Model Context Protocol) Server is a standardized interface protocol that allows AI assistants (such as Claude) to interact securely and controllably with external systems and tools. Through MCP Server, AI assistants can directly access and manipulate various data sources, perform complex data analysis tasks, and provide more intelligent and efficient services.

Lakehouse MCP Server is an MCP server specifically designed for the Lakehouse platform. It seamlessly integrates the powerful data lakehouse capabilities of Singdata Lakehouse with AI assistants, enabling users to interact with the data lakehouse through natural language.

## Core Features

* **Protocol Support**: Supports HTTP (Streamable), SSE, and Stdio transport protocols
* **Standards Compliance**: Fully compliant with the MCP official specification, providing a standard `/mcp` endpoint
* **Broad Compatibility**: Supports mainstream platforms such as Claude Desktop, Dify, n8n, Cursor

## Deployment Requirements

### System Requirements

* **Operating System**: macOS, Windows, Linux
* **Docker**: Version 20.10+
* **Memory**: Minimum 2GB, recommended 8GB
* **CPU**: Minimum 2 cores, recommended 4 cores
* **Storage**: Minimum 10GB available space

## Quick Start

This example introduces deployment using the **HTTP (Streamable)** protocol (recommended), with both Claude Desktop (MCP Client) and MCP Server running on the same local computer (localhost) (this architecture also supports distributed deployment, where the client, server, and Lakehouse platform can be located on different remote hosts).

![](.topwrite/assets/mcp_arch.jpeg =586)

### Step 0: MCP Server Configuration Preparation

Docker environment preparation: Visit <https://www.docker.com/products/docker-desktop/> to download Docker Desktop for Mac.

1. Verify Docker Desktop installation (macOS environment), ensure Docker version 20.10+

```Bash
docker --version 
```

2. Configure Docker Desktop:

* Allocate at least 4GB of memory to Docker
* Enable file sharing functionality

### Step 1: MCP Server Side: Pull the Latest Singdata MCP Server Image

```Bash
docker pull czqiliang/mcp-clickzetta-server:latest
```

### Step 2: MCP Server Side: Create Working Directory (if not exists)

* macOS:

  ```Bash
  mkdir -p ~/.clickzetta/lakehouse_connection
  ```

* Windows PowerShell:

  ```PowerShell
  New-Item -ItemType Directory -Path "$env:USERPROFILE\.clickzetta/lakehouse_connection" -Force
  ```

Under the above path, create a configuration file named `connections.json` and add the connection information for the Lakehouse instance. The configuration template is as follows (if connecting to two Lakehouse instances, separate them with commas):

```JSON
{
  "connections": [
    {
      "is_default": true,
      "service": "cn-shanghai-alicloud.api.singdata.com",
      "username": "__your_name__",
      "password": "__your_password__",
      "instance": "__your_instanceid__",
      "workspace": "__your_workspacename__",
      "schema": "public",
      "vcluster": "default_ap",
      "description": "UAT environment for testing",
      "hints": {
        "sdk.job.timeout": 300,
        "query_tag": "mcp_uat"
      },
      "name": "Shanghai production env",
      "is_active": false,
      "last_test_time": "2025-06-30T19:55:51.839166",
      "last_test_result": "success"
    }
  ]
}
```

Parameter descriptions:

| Parameter              | Description                                                                                                       | Example Value                                                                                                                                                                                                                                                                                                                            |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| is\_default            | Whether it is the default connection configuration                                                                | true                                                                                                                                                                                                                                                                                                                                     |
| service                | For service endpoint addresses, please refer to [documentation](https://www.singdata.com/documents/Supported_Cloud_Platforms) | **Shanghai Alibaba Cloud**: cn-shanghai-alicloud.api.singdata.com&#xA;**Beijing Tencent Cloud**: ap-beijing-tencentcloud.api.singdata.com&#xA;**Beijing AWS**: cn-north-1-aws.api.singdata.com&#xA;**Guangzhou Tencent Cloud**: ap-guangzhou-tencentcloud.api.singdata.com&#xA;**Singapore Alibaba Cloud**: ap-southeast-1-alicloud.api.singdata.com&#xA;**Singapore AWS**: ap-southeast-1-aws.api.singdata.com |
| username               | Username for authentication                                                                                       | "your\_name"                                                                                                                                                                                                                                                                                                                             |
| password               | Password for authentication                                                                                       | "your\_password"                                                                                                                                                                                                                                                                                                                         |
| instance               | Instance ID, identifies a specific Lakehouse instance                                                             | "your\_instanceid"                                                                                                                                                                                                                                                                                                                       |
| workspace              | Workspace name for data isolation and organization                                                                | "your\_workspacename"                                                                                                                                                                                                                                                                                                                    |
| schema                 | Database schema name                                                                                              | "public"                                                                                                                                                                                                                                                                                                                                 |
| vcluster               | Virtual cluster name for compute resource management                                                              | "default\_ap"                                                                                                                                                                                                                                                                                                                            |
| description            | Description of the connection configuration                                                                       | "UAT environment for testing"                                                                                                                                                                                                                                                                                                            |
| hints                  | Performance optimization and identification configuration object                                                  | {...}                                                                                                                                                                                                                                                                                                                                    |
| hints.sdk.job.timeout  | SDK job timeout (seconds)                                                                                         | 300                                                                                                                                                                                                                                                                                                                                      |
| hints.query\_tag       | Query tag for query tracking and identification                                                                   | "mcp\_uat"                                                                                                                                                                                                                                                                                                                               |
| name                   | Name identifier for the connection configuration                                                                  | "Shanghai production env"                                                                                                                                                                                                                                                                                                                |
| is\_active             | Whether the connection is active                                                                                  | false                                                                                                                                                                                                                                                                                                                                    |
| last\_test\_time       | Timestamp of the last connection test (ISO format)                                                                | "2025-06-30T19:55:51.839166"                                                                                                                                                                                                                                                                                                             |
| last\_test\_result     | Result status of the last connection test                                                                         | "success"                                                                                                                                                                                                                                                                                                                                |

### Step 3: MCP Server Side: Start the MCP Server Image

Create a `docker-compose.yml` file and copy the content into it (see the appendix for the file content).

Open a terminal or command line in the directory containing this file and execute the following command.

```SQL
docker compose up -d
```

Expected output:

```
bash-3.2$ docker compose up -d
[+] Running 4/4
 ✔ Network mcp_docker_clickzetta-net  Created       0.0s 
   ✔ Container clickzetta-sse           Started       0.2s 
   ✔ Container clickzetta-http          Started       0.2s 
   ✔ Container clickzetta-webui         Started       0.2s
```

Verify the status using the `docker compose ps --format "table {{.Name}}\t{{.Service}}\t{{.Status}}"` command. The expected output is as follows (ignore `WARNING` messages):

```
bash-3.2$ docker compose ps --format "table {{.Name}}\t{{.Service}}\t{{.Status}}"

NAME               SERVICE            STATUS
clickzetta-http    clickzetta-http    Up 5 hours (unhealthy)
clickzetta-sse     clickzetta-sse     Up 5 hours (unhealthy)
clickzetta-webui   clickzetta-webui   Up 5 hours (unhealthy)
```

> To shut down, execute the following in the directory containing the `docker-compose.yml` file: `docker compose down`

### Step 4: Configure Claude Desktop

The MCP client tool selected for this example is Claude Desktop, with the host located on the same machine as the MCP Server.

Locate and open the Claude Desktop configuration file:

**macOS Steps**:

* Open Finder
* Press `Cmd+Shift+G`
* Paste the path: `~/Library/Application Support/Claude`
* Double-click to open `claude_desktop_config.json` (with a text editor)

**Windows Steps**:

* Press `Win+R` to open the Run dialog
* Enter `%APPDATA%\Claude` and press Enter
* Right-click `claude_desktop_config.json`
* Select "Edit" or "Open with Notepad"

2\. Copy the following content into the configuration file (replace the existing content or add it to `mcpServers`):

Enter the MCP Server address: if the server and client are running on the same machine, use `localhost`; otherwise, enter the server's IP address.

```JSON
{
  "mcpServers": {
    "clickzetta-http": {
      "command": "npx", 
      "args": [
        "-y", "mcp-remote",
        "http://<YOUR_SERVER_IP>:8002/mcp",
        "--allow-http",
        "--transport", "http"
      ]
    }
  }
}
```

**Configuration complete!**

^

Additionally: Claude Desktop supports connecting to the backend MCP Server through multiple methods to accommodate different deployment environments and performance requirements. The example above introduced the **HTTP (Streamable)** protocol connection method. If you want to use the **SSE** or **STDIO** protocol for connections, the configuration is also straightforward:

**SSE Connection Method (Remote Service**)

SSE (Server-Sent Events) is an HTTP-based long-connection technology that allows the server to push messages to the client unidirectionally. Compared to traditional polling, SSE enables real-time communication with lower latency.

* **Applicable Scenarios**: Scenarios requiring real-time data streams or update notifications from the server.
* **Docker Server Configuration Reference**: This method corresponds to the `clickzetta-sse` service in the started containers, which provides services on port `8003`.
* **Configuration Example**:
  In Claude Desktop's `claude_desktop_config.json` configuration file, update the following information to connect to the remote SSE endpoint.

```JSON

{
  "mcpServers": {
    "clickzetta-remote-sse": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "http://localhost:8003/sse",
        "--allow-http",
        "--transport", "sse"
      ]
    }
  }
}
```

&#x20;**Description**:

* Replace `<YOUR_SERVER_IP>` with the actual IP address or domain name of the MCP Server.
* The target port is `8003`, and the endpoint path is `/sse`.
* The `--transport sse` parameter indicates that the SSE communication protocol is used.

***

**STDIO Connection Method (Local Process**)

This method is primarily used for local development and debugging. Claude Desktop will start the MCP Server directly as a subprocess locally and communicate through standard input/output (STDIO). This method has the lowest latency but is not suitable for remote connections.

* **Applicable Scenarios**: Local development, single-machine deployment.
* **Docker Server Configuration Reference**: This method corresponds to the `clickzetta-stdio` service in the started containers. The container image will be automatically started and stopped as Claude Desktop opens and closes.
* **Configuration Example**: Update the following information in Claude Desktop's `claude_desktop_config.json` configuration file to directly specify the command for starting the local Server.

**Note**:

1. In the configuration file, after `-v`, the `USERNAME` in the path **must be modified according to the actual system path**.
2. Use `docker compose down` to stop the created related containers, because in this mode, Claude Desktop will automatically start and stop the container image as it opens and closes.

```json
{
  "mcpServers": {
    "clickzetta-stdio": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--stop-timeout", "60",
        "-p", "8502:8501",
        "-v", "/Users/derekmeng/.clickzetta:/app/.clickzetta",
        "czqiliang/mcp-clickzetta-server:latest"
      ]
    }
  }
}
```

**Description**:

* `command` and `args` directly define how to start the MCP Server locally.
* No need to specify an IP address and port.
* The `--transport stdio` parameter indicates that the STDIO communication protocol is used.

## Getting Started

### Deployment Verification

1\. Open Claude Desktop and send the following command in the input box:

```Plain
List all MCP tools available for Singdata Lakehouse
```

 If the connection is successful, you will see a list containing 50+ tools (Note: the specific number of tools may change with version updates.)

2\. **Verify the WebUI Interface**

* Visit the following address in your browser: `http://localhost:8503`. The expected page is as follows:

:-: ![](.topwrite/assets/mcp_web_ui.jpeg =753)

^

If both steps above completed successfully, congratulations, your application has been successfully installed!

### Step 2: Configure Your First Data Source (Lakehouse)

Next, let's configure a Lakehouse connection so that Claude can access your data.

1. **Open Connection Manager**

   Access the WebUI interface at `http://localhost:8503`, then select **Connection Management** from the left menu.

2. **Add and Fill in Connection Information**

   Click the **Add New Connection** button and accurately fill in your Lakehouse connection information (such as host, port, credentials, etc.) according to the prompts.

:-: ![](.topwrite/assets/mcp_webui_2.jpeg =765)

***

**Test and Save**

1. After filling in, click the **Test Connection** button to ensure all configuration information is correct and the network is accessible.
2. After the test passes, click **Save** to complete the configuration.

### Step 3: Start Your First Query

Now everything is ready! You can start interacting with your data. Try asking in **Claude Desktop**:

> "Show me what Lakehouse instances are available"

### Advanced Configuration: Configure Singdata Product Documentation Knowledge Base

This step integrates the Singdata Lakehouse product knowledge base table to build an intelligent Q&A knowledge base. Once configured, you will be able to quickly get official guidance and answers about Lakehouse operations by asking questions in natural language through the MCP Client (such as Claude Desktop).

The core of this feature leverages **Embedding Service** and **Vector Search** technologies to transform unstructured documents into a knowledge base that can be understood and retrieved by machines.

#### **Step 1: Configure Embedding Service**

The purpose of this step is to tell the MCP system how to convert the user's "questions" into vectors for matching within the knowledge base.

1. In the MCP Server management interface, navigate to **System Configuration** from the left navigation bar.

2. In the main configuration area, select the **Embedding Service** tab.

3. Locate and fill in the **DashScope Configuration** (default) section:

   * **API Key**: Paste your Alibaba Cloud Bailian platform API key. This is the credential for calling the model; please keep it safe.
   * **Vector Dimension**: Enter the vector dimension output by the embedding model you selected. **This value must be exactly the same as the dimension used when vectorizing the knowledge base documents**. For example, the dimension of the `text-embedding-v4` model in the screenshot is `1024`.
   * **Embedding Model**: Select or enter the name of the model used to convert text into vectors, for example `text-embedding-v4`.
   * **Max Text Length**: Set the maximum number of text units (Tokens) that the model can process at once. If the question is too long, the excess will be ignored.![](.topwrite/assets/MCP_config_1.jpeg)

4. Click the **Save Embedding Service Configuration** button.

#### **Step 2: Configure Vector Search**

The purpose of this step is to tell the MCP system where and how to search the already stored document knowledge base.

1. On the **System Configuration** page, switch to the **Vector Search** tab.

2. Fill in the **Vector Table Configuration** section:

   * **Vector Table Name**: Accurately enter the full table name where document vectors are stored. The format is usually `database_name.schema_name.table_name`, for example `clickzetta_sample_data.clickzetta_doc.kb_dashscope_clickzetta_elements`.
   * **Embedding Column**: Enter the column name in the table used to store **text vectors**, for example `embeddings`.
   * **Content Column**: Enter the column name in the table used to store **original text content**, for example `text`. When the system finds relevant answers, the content here will serve as the primary reference.
   * **Other Columns**: Optional. Enter the metadata columns you wish to retrieve together, such as `file_directory`, `filename`, which helps users trace the original source of the information.

3. Configure **Search Parameters**: Keep the defaults; if you want to make modifications, refer to the explanation below.

   * **Distance Threshold**: Set the strictness of similarity matching. The system calculates the "distance" between the question vector and document vectors. Only documents with a distance less than this value are considered relevant. **The smaller the value, the stricter the matching requirement**. It is generally recommended to start trying from `0.80`.
   * **Number of Results to Return**: Defines the number of the most relevant documents retrieved from the database in a single query. For example, setting it to `5` means finding 5 of the most relevant document fragments each time.
   * **Enable Reranking**: When checked, the system will perform a secondary intelligent ranking of the initially retrieved results to increase the probability that the most accurate answer appears at the top.![](.topwrite/assets/MCP_Vector_2.jpeg)

4. Click the **Save Vector Search Configuration** button.

## Other Typical Use Cases

Please refer to the WeChat official account article: [How MCP Server Empowers Lakehouse to Achieve 6 Major AI-Driven Data Application Scenarios](https://mp.weixin.qq.com/s/6TE2RvCesgqYJzVcnAqHew)

We look forward to exploring the new era of AI-driven data analysis with you!

^

## Appendix

Contents for creating the `docker-compose.yml` file:

```
version: '3.8'
services:
  # HTTP protocol service
  clickzetta-http:
    image: czqiliang/mcp-clickzetta-server:latest
    container_name: clickzetta-http
    restart: unless-stopped
    ports:
      - "8002:8002"  # HTTP protocol port
    volumes:
      - ~/.clickzetta:/app/.clickzetta  # Configuration file mount
    # Bypass uv entirely, use virtual environment Python directly
    entrypoint: []
    command: ["/app/.venv/bin/python", "-m", "mcp_clickzetta_server","--transport","http", "--host", "0.0.0.0", "--port", "8002"]
    environment:
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
      - TZ=Asia/Shanghai  # Timezone setting
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-s", "http://localhost:8002/mcp"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s  # Increased to 60s, allowing 5s for HTTP warmup + FastMCP startup time
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
    networks:
      - clickzetta-net
  # SSE protocol service
  clickzetta-sse:
    image: czqiliang/mcp-clickzetta-server:latest
    container_name: clickzetta-sse
    restart: unless-stopped
    ports:
      - "8003:8003"  # SSE protocol port
    volumes:
      - ~/.clickzetta:/app/.clickzetta  # Configuration file mount
    # Bypass uv entirely, use virtual environment Python directly
    entrypoint: []
    command: ["/app/.venv/bin/python", "-m", "mcp_clickzetta_server","--transport","sse", "--host", "0.0.0.0", "--port", "8003"]
    environment:
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
      - TZ=Asia/Shanghai  # Timezone setting
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-s", "http://localhost:8003/sse"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s  # Increased to 120s, giving SSE more startup time
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
    networks:
      - clickzetta-net
  
  # WebUI service
  clickzetta-webui:
    image: czqiliang/mcp-clickzetta-server:latest
    container_name: clickzetta-webui
    restart: unless-stopped
    ports:
      - "8503:8501"  # WebUI port
    volumes:
      - ~/.clickzetta:/app/.clickzetta  # Configuration file mount
    # Start Streamlit WebUI directly, bypassing all wrapper scripts
    entrypoint: []
    command: ["/bin/bash", "-c", "cd /app/streamlit_webui && /app/.venv/bin/python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false"]
    environment:
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
      - TZ=Asia/Shanghai  # Timezone setting
      - PYTHONPATH=/app/src:/app/streamlit_webui/src
    working_dir: /app/streamlit_webui
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-s", "http://localhost:8501"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
    networks:
      - clickzetta-net

networks:
  clickzetta-net:
    driver: bridge
```

^
