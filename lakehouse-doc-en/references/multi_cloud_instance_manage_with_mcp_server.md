# Singdata Lakehouse Multi-Cloud Multi-Environment Management Guide

## Overview

This document describes how to achieve unified management of multi-cloud and multi-environment setups through Claude Desktop and Singdata Lakehouse MCP Server, providing enterprise users with a simple and efficient data lakehouse management experience and enabling end-to-end natural language conversational interaction.

```
What Lakehouse environments do I have?
Help me check which workspaces are in each instance of the production environment
Help me switch to the Tencent Cloud Shanghai production environment
What is my current context?
What workspaces are available?
Help me switch to test_ws
What compute clusters and schemas do I have?
Help me switch to DEFAULT
```

## Use Cases

In the process of enterprise digital transformation, the following multi-environment management challenges are common:

* **Multi-cloud deployment**: Simultaneously using Alibaba Cloud, Tencent Cloud, AWS, and other cloud providers
* **Environment isolation**: Development, testing, and production environments need independent management
* **Regional distribution**: Data centers in different regions such as Shanghai, Beijing, Guangzhou
* **Resource switching**: Frequent switching between different environments for operations

Traditional approaches require logging into multiple consoles, which is complex and error-prone. This solution provides a unified approach.

## Technical Architecture

### Core Components

1. **Claude Desktop**: AI assistant client providing a natural language interaction interface
2. **Singdata Lakehouse MCP Server**: Model Context Protocol server connecting Claude with Singdata Lakehouse
3. **Singdata Lakehouse**: Cloud-native data lakehouse platform supporting multi-cloud deployment

### Technical Advantages

* **Natural language interaction**: Manage complex multi-cloud environments through conversation
* **Unified management interface**: One client to manage all cloud environments
* **Real-time status monitoring**: Check environment health status at any time
* **Intelligent switching**: Automatically handle connection establishment and environment switching

## Quick Start

### Step 1: Environment Configuration

First, configure the connection information for multiple Lakehouse instances (simplified):

```json
{
  "connections": {
    "aliyun_shanghai_prod": {
      "service": "cn-shanghai-alicloud.api.singdata.com",
      "workspace": "quick_start",
      "schema": "mcp_demo"
    },
    "tencent_shanghai_prod": {
      "service": "ap-shanghai-tencentcloud.api.singdata.com", 
      "workspace": "quick_start",
      "schema": "mcp_demo"
    },
    "aws_north-1_prod": {
      "service": "cn-north-1-aws.api.singdata.com",
      "workspace": "quick_start", 
      "schema": "public"
    }
  }
}
```

### Step 2: Launch Claude Desktop

Install and launch Claude Desktop, ensuring the Singdata MCP Server is configured.

### Step 3: Start Managing

Interact with Claude using natural language to begin multi-cloud environment management.

## Real-World Use Case

The following is a real multi-cloud environment management conversation example:

### Environment Discovery

**User**: "What Lakehouse environments do I have?"

**System Response**: Automatically scans and displays all configured environments:

```
✅ Found 9 connection configurations

🟢 Currently Active Environment
aliyun_shanghai_prod (Default environment)

📋 All Available Environments
Production Environments:
1. aliyun_shanghai_prod ⭐ (Currently in use)
2. tencent_shanghai_prod  
3. tencent_beijing_prod
4. tencent_guangzhou_prod
5. aws_north-1_prod

Test Environments:
6. uat
7. uat_1  
8. uat_1_1
9. uat_2
```

### Batch Environment Exploration

**User**: "Help me check which workspaces are in each instance of the production environment"

**System Operations**:

* Automatically traverses all production environments
* Connects to each cloud provider instance one by one
* Collects workspace information
* Generates a unified report

**Results Display**:

| Environment | Workspace Count | Details |
| :--- | :--- | :--- |
| Alibaba Cloud Shanghai | 4 | quick_start, lakehouse_quick_experience, ns227206, spark_migration |
| Tencent Cloud Shanghai | 2 | quick_start, test_ws |
| Tencent Cloud Beijing | 1 | quick_start |
| Tencent Cloud Guangzhou | 1 | quick_start |
| AWS North-1 | 2 | quick_start, iceberg_lakehouse_s3 |

### Intelligent Environment Switching

**User**: "Help me switch to the Tencent Cloud Shanghai production environment"

**System Processing**:

```
✅ Switch successful!
Original environment: aliyun_shanghai_prod  
New environment: tencent_shanghai_prod
Service endpoint: ap-shanghai-tencentcloud.api.singdata.com
Processing time: 1.13 seconds

📍 Current Environment Configuration
Workspace: quick_start
Schema: mcp_demo  
Virtual cluster: default_ap
```

### Context Awareness

**User**: "What is my current context?"

**System Response**:

```
📍 Your Current Context Information
Connected environment: Tencent Cloud Shanghai production environment

🔧 Environment Configuration
Instance ID: 270738
Workspace: quick_start  
Data schema: mcp_demo
Virtual cluster: default_ap

👤 User Information
Username: qiliang
User ID: 2162115
```

### Resource Management

**User**: "What compute clusters and schemas do I have?"

**System Analysis**:

```
⚡ Compute Clusters (VCLUSTERS) - 2
1. DEFAULT (General-purpose) - SUSPENDED 
2. DEFAULT_AP (Analytical) - RUNNING ⭐

📁 Schemas (Data schemas) - 2  
1. information_schema (System schema)
2. public (Public schema)
```

## Core Feature Details

### 1. Environment Discovery and Management

* **Automatic scanning**: Discover all configured Lakehouse instances
* **Health check**: Real-time monitoring of environment connection status
* **Intelligent classification**: Automatically group by cloud provider, region, and purpose

### 2. Seamless Environment Switching

* **One-click switching**: Switch environments with natural language commands
* **Connection management**: Automatically handle connection establishment and disconnection
* **State persistence**: Maintain context information after switching

### 3. Unified Resource View

* **Workspace management**: View and switch workspaces
* **Compute resources**: Manage virtual clusters (VCluster)
* **Data organization**: View schemas and table structures

### 4. Intelligent Operation Suggestions

* **Context awareness**: Understand the current environment
* **Operation hints**: Provide suggestions for next steps
* **Error handling**: Automatically handle connection exceptions

## Management Tool Introduction

### Singdata Lakehouse MCP Server

**Features**:

* 50+ data operation tools
* Multi-cloud environment connection management
* Real-time status monitoring
* Intelligent error recovery

**Core Tools**:

| Tool Category | Main Functions | Typical Tools |
| :--- | :--- | :--- |
| Environment Management | Instance switching, context viewing | `switch_lakehouse_instance`, `switch_workspace`, `get_current_context` |
| Resource Management | Object viewing, creation, deletion | `show_object_list`, `create_table` |
| Data Operations | Query, import, export | `read_query`, `import_data_src` |
| Compute Management | Cluster management, task monitoring | `alter_vcluster`, `show_job_history` |

### Claude Desktop

**Interaction Advantages**:

* Natural language understanding
* Context memory
* Intelligent suggestions
* Visual display

## Enterprise Application Scenarios

### Scenario 1: Development and Operations

```
Developer: "Switch to the development environment and check today's task execution status."
System: Automatically switches to the development environment and displays task history and status.
```

### Scenario 2: Data Analysis

```
Analyst: "Switch to the production environment and view the sales data table structure."
System: Switches environment and displays table schema and data preview.
```

### Scenario 3: Cross-Cloud Comparison

```
Architect: "Compare resource configurations across different cloud environments."
System: Generates a cross-cloud environment resource comparison report.
```

## Best Practices

### 1. Environment Naming Conventions

* **Cloud provider identifier**: aliyun, tencent, aws
* **Region identifier**: shanghai, beijing, guangzhou
* **Environment type**: prod, test, dev

Example: `tencent_shanghai_prod`

### 2. Permission Management

* Production environment: Restrict access to specific users
* Test environment: Shared by the development team
* Development environment: Personal use

## Conclusion

The Singdata Lakehouse multi-cloud multi-environment management solution provides enterprises with a unified, intelligent, and efficient data lakehouse management experience. Through natural language interaction, it significantly reduces the complexity of multi-cloud environment management and improves operational efficiency. As AI technology continues to evolve, we will keep optimizing the product experience to create greater value for users.
