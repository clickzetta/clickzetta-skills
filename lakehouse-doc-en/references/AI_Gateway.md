## 1. Product Overview

### 1.1 What is Model Management

Model Management (AI Gateway) is an enterprise-grade "unified model invocation and governance hub" that integrates rate limiting, operational monitoring, permission isolation, and cost management capabilities by default. It supports aggregating "cloud service provider hosted models" and "enterprise self-owned external models," enabling standardized model invocation, visualized resource governance, and granular cost attribution across multiple scenarios.

### 1.2 Core Values

| Value Dimension  | Description                                                      |
| ----- | --------------------------------------------------------- |
| Unified Entry Point  | No need to switch between multiple platforms; one-stop management of hosted/external models, reducing cross-platform collaboration costs                           |
| Risk Control  | Role-based permission isolation (RBAC) + dynamic rate limiting + API KEY security management, preventing resource abuse and data leaks          |
| Cost Transparency  | Supports tenant/Endpoint-level quota control, multi-dimensional usage statistics (Token / call count), and cost allocation reports for precise cost attribution |
| Low-Barrier Invocation | Covers three major scenarios: SQL embedding, DataGPT visualization, and OpenAPI development, meeting the needs of both technical and non-technical users       |
| Traceability  | Retains model invocation logs, usage details, and permission change records to meet compliance and audit requirements                             |

### 1.3 Core Concepts

| Concept                    | Definition                                                                    | Applicable Scenarios                   |
| --------------------- | ----------------------------------------------------------------------- | ---------------------- |
| AI Gateway            | The unified entry point for model invocation and governance, responsible for permission verification, rate limiting, usage statistics, and request forwarding                                      | All model invocation and management scenarios            |
| Model Endpoint | The unique access identifier of a model, with a unique name within the tenant (Chinese characters not supported); can be invoked in multiple scenarios after registration                                     | An Endpoint must be created before a model can be used |
| Managed Model                  | Preset models provided by cloud service providers (e.g., Alibaba Cloud Qwen, OpenAI GPT-4o), with Base URL/API KEY managed uniformly by AI Gateway | Enterprises without self-owned models that need to quickly enable general AI capabilities  |
| External Model                  | Enterprise self-owned cloud vendor MaaS models (e.g., self-built Volcengine large models), requiring manual configuration of Base URL/API KEY                      | Scenarios requiring private deployment or self-owned models, such as finance and government   |

## 2. Prerequisites

### 2.1 Preconditions

1. The cloud service provider Studio service must be activated, and you must have access to the "AI - Model Management" module (when empty, only Instance Admin can see the "New Model" entry);
2. If using external models: you must obtain the cloud vendor-provided **Base URL** (must comply with the OpenAI API specification) and **API KEY** (must have model invocation permissions) in advance;
3. If associating business data: you must obtain Lakehouse table read permissions (for SQL invocation scenarios) and AI Function execution permissions (for function invocation scenarios) in advance.

### 2.2 Roles and Permissions Matrix (RBAC)

| Role                 | Core Permissions                                                                  | Target Users            | Typical Operations          |
| ------------------ | --------------------------------------------------------------------- | --------------- | --------------- |
| Account Admin      | 1. Initialize Gateway Admin (auto-synced on first use); 2. Handle billing and service activation                         | Enterprise cloud account admin (low-frequency operations)  | Configure initial admin on first enterprise access  |
| Gateway Admin      | 1. Configure tenant-level quotas and rate limiting policies; 2. Manage all Endpoints/API KEYs; 3. Add/remove admins; 4. View all usage and cost allocation data | Enterprise IT admin, model owner | Enterprise budget allocation, global permission control |
| Endpoint Admin     | 1. Manage specified Endpoints (view usage, modify config, delete); 2. Grant others permission for that Endpoint                   | Business line owner (e.g., e-commerce, finance)  | Business line model permission allocation, usage monitoring  |
| ENDPOINT\_VIEWER   | Read-only access to model metadata; cannot invoke                                                          | Operations analyst           | Model invocation development, data analysis generation   |
| ENDPOINT\_USER     | Can only invoke models                                                                | Development engineer           | Model invocation development, data analysis generation   |
| ENDPOINT\_OPERATOR | Invoke + modify model configuration                                                           | Development engineer           | Model invocation development, data analysis generation   |

## 3. Core Operation Guide

### 3.1 Endpoint Lifecycle Management (Model Access and Monitoring)

#### 3.1.1 Managed Model Management (Quickly Enable Preset Models)

**Business Value**: No configuration required; directly use cloud service provider preset models, suitable for quickly validating business requirements (e.g., temporary data analysis, Demo development).
**Steps**:

1. Go to "Model Management -> Endpoint" page, the system displays the list of managed models configured within the tenant by default;
2. Core operations (varies by role permissions):
   * Steps:
     * Go to "Model Management -> Endpoint" page;
     * Locate the target model in the Endpoint list and perform the following operations:
       * New Endpoint (Gateway Admin only): Click "New" on the right to create an Endpoint. ![](.topwrite/assets/1.png)
       * Copy Endpoint: Click "Copy" to duplicate an existing Endpoint, modify its content, and generate a new Endpoint. ![](.topwrite/assets/ScreenShot_2026-03-10_191249_127.png)
       * Test Connectivity: Click "Test Connection" to trigger a real large model invocation to verify connectivity; this operation consumes a very small amount of Tokens. ![](.topwrite/assets/image_1769764093331.png)
       * View Details: Click the Endpoint name to view model version, invocation volume, authorized users, and change history. ![](.topwrite/assets/image%20(1).png)
       * Delete Model (Gateway Admin and Endpoint Admin only): Click "Delete" -> Confirm in the popup by clicking "OK" (deletion is irreversible).

#### 3.1.2 External Model Access (Enterprise Self-Owned Model Integration)

**Business Value**: Supports enterprises in connecting privately deployed or self-owned copyrighted models to AI Gateway for unified management (e.g., financial risk control models, e-commerce recommendation models).
Access is divided into two scenarios to meet different model specification requirements:
**Scenario 1: Standard Vendor Access (e.g., Volcengine, Anthropic)**
Advantage: Models comply with cloud vendor standard API specifications; no custom URL required.

1. Go to "Model Management -> Endpoint -> New -> External Model";
2. Fill in the configuration:
   * Enter "Endpoint Name" (unique within the tenant, e.g., "finance-risk-model");
   * Select "Vendor" (system auto-fills the standard Base URL);
   * Select "Model Category" (LLM/Embedding/Image Generation);
   * Enter "Model Version" (e.g., "risk-v2.1");
   * Fill in "API KEY ID" (API Key information is only required when invoking external models; you can create it in the API KEY interface and view the specific ID from the generated API Key);
3. AI Gateway Configuration:
   * Set "Access Rate Limit" (e.g., TPM=1000, RPM=50);
   * "Access Quota" (e.g., 100,000 Tokens per month);
4. Click "Test Connection" to verify connectivity (see Chapter 4 for troubleshooting);
5. After a successful test, click "OK"; the Endpoint will be added to the list.
   ![](.topwrite/assets/image%20(2).png)

**Scenario 2: Custom Access (OpenAI-Compatible)**
Advantage: For enterprise self-developed models and third-party non-standard vendor models.

1. Go to "Model Management -> Endpoint -> New -> External Model -> Custom";
2. Fill in the configuration:
   * Enter "Endpoint Name" (e.g., "custom-ocr-model");
   * Fill in "Model Vendor" (e.g., "Enterprise Self-Developed");
   * Select "Model Category" (e.g., "Image Generation");
   * Enter "Model Version" (custom, e.g., "20260120-beta");
   * Fill in "Base URL" (e.g., "https://internal-ocr.example.com/v1/chat/completions");
   * Fill in "API KEY ID" (API Key information is only required when invoking external models; you can create it in the API KEY interface and view the specific ID from the generated API Key);
3. Follow steps 3-5 of "Standard Vendor Access" for the remaining steps.
   ![](.topwrite/assets/image%20(3).png)

#### 3.1.3 Model Monitoring (Real-Time Operational Status)

**Business Value**: Monitor model invocation success rate, latency, and error rate in real time to promptly detect anomalies (e.g., model downtime, rate limit triggered).
**Steps**:

1. Go to "Model Management -> Endpoint", select the target Endpoint, click "More -> Monitoring";
   ![](.topwrite/assets/image%20(4).png)
2. Configure query conditions:
   * Time Range: Default is the last 1 day, supports 1 minute to 60 days (data granularity varies by range, e.g., 1 minute per point within 1 day, 1 hour per point within 30 days);
   * Metric Dimensions: Default display includes "Request Count, Success Rate, End-to-End Latency, Total Token Usage";
3. View Data:
   * Overview Panel: Displays core KPIs (Total Tokens, Success Rate, Error Rate, Average Latency);
   * Trend Charts: Line charts show metric changes (e.g., a sudden drop in success rate requires checking model connectivity);
   * Error Details: Click "Error Rate" to view error types (e.g., rate limiting, insufficient permissions);

### 3.2 API KEY Management (Secure Access Credentials)

**Business Value**: The API KEY is the sole credential for external model invocation; strict management prevents resource abuse and data leaks.
**Steps (Gateway Admin only)**:

1. Go to "Model Management -> API KEY" page;
2. Create a New API KEY:
   * Click "New KEY" -> Enter a name (should be associated with a business scenario, e.g., "ecommerce-recommend-key");
   * Click "Confirm"; the system generates the KEY;
3. Daily Management:
   * Disable/Enable: Click "Disable" (invocation is blocked after disabling, suitable for temporary suspension); click "Enable" when needed;
   * Delete: Must first stop associated invocations (e.g., SQL/OpenAPI invocations), click "Delete" -> Confirm (KEY becomes invalid immediately);
   * Filter: Quickly locate target KEYs by "Status (Normal / Disabled)" and "Owner";
4. Security Notes:
   * Avoid plaintext storage (e.g., in code repositories, configuration files);
   * Rotate regularly (recommended every 3 months);
   * If leaked, delete and recreate immediately, and update all associated invocation configurations;
     ![](.topwrite/assets/image%20(5).png)

### 3.3 Permission Management (Granular Resource Control)

#### 3.3.1 Gateway Admin Management (Global Permission Control)

**Business Value**: Ensures that only authorized personnel within the enterprise are responsible for global configuration, avoiding permission chaos.
**Steps (Current Gateway Admin only)**:

1. Go to "Model Management -> Permissions -> Gateway Admin";
2. Add Admin:
   * Click "Add" -> Select target users (must be registered within the tenant);
   * Click "Confirm"; the user immediately obtains full Gateway Admin permissions;
3. Remove Admin:
   * Locate the target user in the list and click "Remove";
   * System validation: (1) The currently logged-in user cannot be removed; (2) At least 1 Admin must remain after removal;
4. View Records: The page displays the "Username, Addition Time, Operator" for all Admins;
   ![](.topwrite/assets/image%20(6).png)

#### 3.3.2 Endpoint Permission Management (Business Line Permission Isolation)

**Business Value**: Allocate Endpoint permissions by business line to prevent cross-business resource abuse (e.g., an e-commerce Endpoint can only be invoked by the e-commerce team).
**Steps (Endpoint Admin only)**:

1. Go to "Model Management -> Permissions -> Endpoint Permissions";
2. Authorization:
   * Click "Add" -> Select target user -> Choose permission type (refer to 2.2 Roles and Permissions);
   * Select the Endpoints to authorize (multiple selection supported);
   * Click "Confirm"; the user obtains the corresponding permissions;
3. Revoke Permissions:
   * Find the target user and Endpoint in the "Authorized List";
   * Click "Remove" -> Confirm; permissions take effect immediately;
     ![](.topwrite/assets/image%20(7).png)

### 3.4 Quota and Usage Management (Cost Control)

#### 3.4.1 Tenant Quota Configuration (Enterprise-Level Budget Control)

**Business Value**: Set an enterprise monthly total Token upper limit to avoid budget overruns (e.g., 5 million Tokens per month covering all business lines).
**Steps (Gateway Admin only)**:

1. Go to "Model Management -> Usage -> Tenant Quota";
2. First-Time Configuration:
   * If empty (prompt "No quota has been set for the current tenant"), click "Set Tenant Quota";
   * Fill in configuration: Granularity defaults to "Tenant Level", Cycle defaults to "Monthly", Token Quota (e.g., 5000000, i.e., 5 million/month);
   * Click "Save" and navigate to the quota page to view "Total Quota, Used, Remaining, Daily Usage Trend";
3. Adjust Quota: Click "Edit Quota" -> Modify the value -> Save (takes effect immediately);
   ![](.topwrite/assets/image%20(8).png)

#### 3.4.2 Endpoint Quota Configuration (Business Line Budget Allocation)

**Business Value**: Allocate independent quotas for individual Endpoints (e.g., 1 million Tokens per month for the e-commerce recommendation model) to achieve business line cost isolation.
**Steps (Gateway Admin/Endpoint Admin)**:

1. Go to "Model Management -> Endpoint", select the target Endpoint, click "Edit";
2. Locate the "AI Gateway -> Access Quota" module;
3. Fill in configuration: Granularity defaults to "Endpoint Level", Cycle "Monthly", Token Quota (e.g., 1000000);
4. Key Rule: The actual available quota = the smaller of the tenant quota and the Endpoint quota (e.g., if the tenant has 500,000 remaining and the Endpoint quota is 1,000,000, the actual available is 500,000);
5. Click "Save" and view quota usage on the Endpoint details page;
   ![](.topwrite/assets/image%20(9).png)

#### 3.4.3 Usage Statistics Query (Multi-Dimensional Cost Attribution)

**Business Value**: Query usage by Endpoint / User / API KEY dimensions to identify high-cost resources (e.g., abnormal invocation volume by a specific user).
**Steps (varies by role permissions)**:

1. Go to "Model Management -> Usage -> Usage Statistics";
2. Configure query conditions:
   * Time Range: Default is the last 1 month, supports switching to "Last 1 Week / Custom";
   * Statistical Dimensions:
     * Regular Users: Only view "their associated Endpoints / Users";
     * Gateway Admin: View "Endpoint / User / API KEY / Account / Account Details";
3. View Data:
   * List View: Displays "Statistical Dimension, Date, Call Count, Input Tokens, Output Tokens, Total Usage";
   * Chart View: Click "Switch Chart" to view usage trends via line/bar charts;
4. Download Details (Gateway Admin only):
   * Click "Download Details" -> Select year and month (supports the last 1 year) -> Confirm;
     ![](.topwrite/assets/image%20(10).png)

### 3.5 Multi-Scenario Model Invocation (Adapting to Different User Needs)

#### 3.5.1 SQL Invocation (Data Analysts / Development Engineers)

**Business Value**: Invoke models directly in SQL, enabling integrated "data query + AI analysis" (e.g., order text embedding, user review sentiment analysis).
You can invoke directly in SQL, for example:

```Plain
select ai_complete('endpoint\:lis\_aliyun\_qwen\_max','What is the capital of China?')
```

#### 3.5.2 DataGPT Invocation (All Roles)

DataGPT enables AI model invocation through standardized interfaces, allowing rapid model integration and replacement. You simply replace the existing model configuration on the DataGPT model settings page with our dedicated invocation address (Base URL) and access credential (API Key) to switch the model invocation pipeline, leveraging AI Gateway for stable, governable AI capability invocation.

#### 3.5.3 OpenAPI Standard Invocation (Development Scenarios)

* Invocation Address: The "Access Address" in the Endpoint list;
* API KEY: Obtain from "API KEY Management" (only Gateway Admin can create);
* Invocation Method:
  * Go to "Model Management -> Endpoint" page, click the Endpoint name to enter the details page;
  * At the bottom of the details page, the "Endpoint Invocation Examples" section shows example code for OpenAI-python and REST API-cURL invocation methods.

## 4. Key Notes

1. **Permission Control**: Confirm your role permissions before operating (e.g., regular users cannot delete Endpoints) to avoid operation failures due to insufficient permissions; if you need extended permissions, contact the corresponding Admin (Gateway Admin handles global permissions, Endpoint Admin handles business line permissions).

2. **Data Retention**:
   * Account detail data: Only retained for the last 1 year; download monthly backups for long-term storage (Gateway Admin operation);
   * Usage monitoring data: Retained for up to 60 days; regularly take screenshots and archive key metrics (e.g., monthly quota usage).

3. **Model Deletion Risks**:
   * Endpoints cannot be recovered after deletion. Before deletion, you must: (1) Stop all associated invocations (SQL/OpenAPI/DataGPT); (2) Notify all authorized users;
   * After a built-in managed model is deleted, contact technical support if you need to use it again (self-recovery is not supported).

4. **API KEY Security**:
   * Avoid leakage (e.g., plaintext sharing, storage in code repositories);
   * Rotate regularly (recommended every 3 months);
   * If leaked, immediately delete and recreate in "API KEY Management" and update all associated configurations.

5. **Quota Effective Rules**: The actual available Endpoint quota = the smaller of the tenant quota and the Endpoint quota. When setting, avoid the Endpoint quota far exceeding the tenant quota (e.g., tenant 1 million/month, Endpoint set to 2 million, actual only 1 million available, resulting in configuration waste).

6. **Compatibility Notes**: External models must comply with the OpenAI API specification, otherwise they cannot be connected (e.g., models that do not support the "messages" parameter require vendor adaptation); when editing model versions, confirm whether downstream invocation systems support the new version (to avoid compatibility issues).
