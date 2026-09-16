# AI Gateway Product Overview

## 1. Product Overview

### 1.1 What is Model Management

Model Management (AI Gateway) is an enterprise-grade unified model invocation and governance hub. It comes with built-in rate limiting, operational monitoring, permission isolation, and cost control capabilities. It supports aggregating both cloud provider-hosted models and enterprise-owned external models, enabling standardized model invocation across scenarios, visualized resource governance, and precise cost attribution.

### 1.2 Core Value

| Value Dimension | Description |
| ----- | --------------------------------------------------------- |
| Unified Entry Point | Manage hosted and external models in one place without switching platforms, reducing cross-platform collaboration costs |
| Controlled Risk | Role-based permission isolation (RBAC) + dynamic rate limiting + API KEY security management to prevent resource abuse and data leakage |
| Cost Transparency | Supports tenant/Endpoint-level quota management, multi-dimensional usage statistics (Token / call count), and chargeback reports for precise cost attribution |
| Low-barrier Invocation | Covers three scenarios — SQL embedding, Data Analytics Agent (DataGPT) visualization, and OpenAPI development — to meet the needs of both technical and non-technical users |
| Auditability | Retains model invocation logs, usage details, and permission change records to meet compliance audit requirements |

### 1.3 Core Concepts

| Concept | Definition | Applicable Scenarios |
| --------------------- | ----------------------------------------------------------------------- | ---------------------- |
| AI Gateway | Unified entry point for model invocation and governance, responsible for permission verification, rate limit enforcement, usage statistics, and request forwarding | All model invocation and management scenarios |
| Model Endpoint | The unique access identifier for a model, unique by name within a tenant (no Chinese characters), usable across scenarios after registration | An Endpoint must be created before a model can be used |
| Hosted Model | Pre-built models provided by cloud vendors (e.g., Alibaba Cloud Qwen, OpenAI GPT-4o), with Base URL/API KEY uniformly managed by AI Gateway | Organizations without proprietary models that need to quickly enable general AI capabilities |
| External Model | Enterprise-owned MaaS models from cloud vendors (e.g., self-hosted Volcano Engine large model), requiring manual configuration of Base URL/API KEY | Scenarios requiring private deployment or proprietary models, such as finance or government |

## 2. Pre-use Preparation

### 2.1 Prerequisites

1. The cloud vendor Studio service has been activated and you have access to the "AI - Model Management" module (in empty state, only Instance Admins can see the "Create Model" entry);
2. If using external models: obtain the **Base URL** (must comply with OpenAI interface specification) and **API KEY** (must have model invocation permission) from the cloud vendor in advance;
3. If connecting business data: obtain Lakehouse database read permissions (for SQL invocation scenarios) and AI Function execution permissions (for function invocation scenarios) in advance.

### 2.2 Role and Permission Matrix (RBAC)

| Role | Core Permissions | Target Users | Typical Scenarios |
| ------------------ | --------------------------------------------------------------------- | --------------- | --------------- |
| Account Admin | 1. Initialize Gateway Admin (auto-synced on first use); 2. Handle billing and service activation | Enterprise cloud account administrator (low-frequency operations) | Configure initial administrator when first onboarding |
| Gateway Admin | 1. Configure tenant-level quotas and rate limiting policies; 2. Manage all Endpoints/API KEYs; 3. Add/remove admins; 4. View all usage and chargeback data | Enterprise IT managers, model owners | Enterprise budget allocation, global permission management |
| Endpoint Admin | 1. Manage designated Endpoints (view usage, modify config, delete); 2. Grant others permission to the Endpoint | Business line managers (e.g., e-commerce, finance) | Business line model permission assignment, usage monitoring |
| ENDPOINT\_VIEWER | Read-only access to model metadata, cannot invoke | Operations analysts | Model invocation development, data analysis generation |
| ENDPOINT\_USER | Can only invoke models | Development engineers | Model invocation development, data analysis generation |
| ENDPOINT\_OPERATOR | Invoke + modify model configuration | Development engineers | Model invocation development, data analysis generation |

## 3. Core Operations Guide

### 3.1 Endpoint Full Lifecycle Management (Model Onboarding and Monitoring)

#### 3.1.1 Hosted Model Management (Quickly Enable Pre-built Models)

**Business value**: Use cloud vendor pre-built models directly without any configuration, suitable for quickly validating business needs (e.g., ad-hoc data analysis, Demo development).
**Steps**:

1. Go to the "Model Management → Endpoint" page; the system displays the list of hosted models configured within the tenant by default;
2. Core operations (vary by role):
   * Steps:
     * Go to the "Model Management → Endpoint" page;
     * Find the target model in the Endpoint list and perform the following actions:
       * Create Endpoint (Gateway Admin only): click "Create" on the right to create an Endpoint![](/.topwrite/assets/1.png)
       * Copy Endpoint: click "Copy" to copy an existing Endpoint's details, modify the content, and generate a new Endpoint;![](/.topwrite/assets/ScreenShot_2026-03-10_191249_127.png)
       * Test Connectivity: click "Test Connection" to trigger a real large model call to verify connectivity; this operation consumes a minimal amount of Tokens.![](/.topwrite/assets/image_1769764093331.png)
       * View Details: click the Endpoint name to view model version, call volume, authorized users, and change history;\</.topwrite/assets/image (1).png>
       * Delete Model (Gateway Admin and Endpoint Admin only): click "Delete" → confirm by clicking "OK" in the popup (deletion is irreversible).

#### 3.1.2 External Model Integration (Enterprise Proprietary Model Integration)

**Business value**: Allows enterprises to integrate privately deployed or proprietary models into AI Gateway for unified governance (e.g., financial risk control models, e-commerce recommendation models).
Two integration scenarios are available to meet different model specification needs:
**Scenario 1: Standard Vendor Integration (e.g., Volcano Engine, Anthropic)**
Advantage: Models comply with cloud vendor standard interface specifications, no custom URL needed

1. Go to "Model Management → Endpoint → Create → External Model";
2. Fill in the configuration:
   * Enter "Endpoint Name" (unique within tenant, e.g., "finance-risk-model");
   * Select "Vendor" (system auto-fills standard Base URL);
   * Select "Model Category" (LLM/Embedding/Image Generation);
   * Enter "Model Version" (e.g., "risk-v2.1");
   * Fill in "API KEY ID" (only needed for external model invocation; you can create one in the API KEY interface and look up the specific ID from the generated API Key);
3. AI Gateway configuration:
   * Set "Rate Limit" (e.g., TPM=1000, RPM=50)
   * "Access Quota" (e.g., 100,000 Tokens per month);
4. Click "Test Connection" to verify connectivity (see Chapter 4 for troubleshooting failures);
5. After the test passes, click "OK" and the Endpoint is added to the list.
   \</.topwrite/assets/image (2).png>)

**Scenario 2: Custom Integration (OpenAI-compliant)**
Advantage: For enterprise self-developed models and non-standard third-party vendor models

1. Go to "Model Management → Endpoint → Create → External Model → Custom";
2. Fill in the configuration:
   * Enter "Endpoint Name" (e.g., "custom-ocr-model");
   * Fill in "Model Vendor" (e.g., "Enterprise Self-developed");
   * Select "Model Category" (e.g., "Image Generation");
   * Enter "Model Version" (custom, e.g., "20260120-beta");
   * Fill in "Base URL" (e.g., "<https://internal-ocr.example.com/v1/chat/completions>");
   * Fill in "API KEY ID" (only needed for external model invocation; you can create one in the API KEY interface and look up the specific ID from the generated API Key);
3. Follow steps 3–5 of "Standard Vendor Integration" for the remaining steps.
   \</.topwrite/assets/image (3).png>)

#### 3.1.3 Model Monitoring (Real-time Operational Status)

**Business value**: Real-time monitoring of model invocation success rate, latency, and error rate to detect anomalies promptly (e.g., model downtime, rate limit triggers).
**Steps**:

1. Go to "Model Management → Endpoint", select the target Endpoint, click "More → Monitor";
   \</.topwrite/assets/image (4).png>)
2. Configure query conditions:
   * Time range: default is the last 1 day, supports 1 minute to 60 days (different ranges yield different data granularity, e.g., within 1 day: 1 minute/point, within 30 days: 1 hour/point);
   * Metric dimensions: defaults to "request count, success rate, end-to-end latency, total Token usage";
3. View data:
   * Overview panel: displays core KPIs (total Tokens, success rate, error rate, average latency);
   * Trend charts: line charts show metric changes (e.g., a sharp drop in success rate requires investigating model connectivity);
   * Error details: click "Error Rate" to view error types (e.g., rate limiting, insufficient permissions);

### 3.2 API KEY Management (Secure Access Credentials)

**Business value**: API KEYs are the sole credentials for external model invocation; strict management prevents resource abuse and data leakage.
**Steps (Gateway Admin only)**:

1. Go to the "Model Management → API KEY" page;
2. Create an API KEY:
   * Click "Create KEY" → enter a name (associate with business scenario, e.g., "ecommerce-recommend-key");
   * Click "Confirm" and the system generates the KEY;
3. Day-to-day management:
   * Disable/Enable: click "Disable" (disables invocation, use for temporary suspension), click "Enable" when needed again;
   * Delete: first stop associated invocations (e.g., SQL/OpenAPI calls), then click "Delete" → confirm (KEY becomes immediately invalid);
   * Filter: quickly locate target KEYs using "Status (Active / Disabled)" and "Owner";
4. Security considerations:
   * Avoid storing in plaintext (e.g., code repositories, config files);
   * Rotate regularly (recommended every 3 months);
   * After a leak, immediately delete and recreate, then update all associated invocation configurations;
     \</.topwrite/assets/image (5).png>)

### 3.3 Permission Management (Fine-grained Resource Control)

#### 3.3.1 Gateway Admin Management (Global Permission Control)

**Business value**: Ensures only authorized personnel are responsible for global configuration, preventing permission chaos.
**Steps (current Gateway Admin only)**:

1. Go to "Model Management → Permissions → Gateway Administrators";
2. Add an administrator:
   * Click "Add" → select the target user (must be registered within the tenant);
   * Click "Confirm" and the user immediately gains full Gateway Admin permissions;
3. Remove an administrator:
   * Find the target user in the list and click "Remove";
   * System check: ① Cannot remove the currently logged-in user; ② At least 1 Admin must remain after removal;
4. View records: the page shows "username, date added, operator" for all Admins;
   \</.topwrite/assets/image (6).png>)

#### 3.3.2 Endpoint Permission Management (Business Line Permission Isolation)

**Business value**: Assign Endpoint permissions by business line to prevent cross-business resource abuse (e.g., only the e-commerce team can invoke the e-commerce Endpoint).
**Steps (Endpoint Admin only)**:

1. Go to "Model Management → Permissions → Endpoint Permissions";
2. Grant permission:
   * Click "Add" → select the target user → check permission type (refer to Section 2.2 role permissions);
   * Select the Endpoint(s) to authorize (multiple selection supported);
   * Click "Confirm" and the user gains the corresponding permissions;
3. Revoke permission:
   * Find the target user and Endpoint in the "Authorized List";
   * Click "Remove" → confirm; permission takes effect immediately;
     \</.topwrite/assets/image (7).png>)

### 3.4 Quota and Usage Management (Cost Control)

#### 3.4.1 Tenant Quota Configuration (Enterprise-level Budget Management)

**Business value**: Set an enterprise monthly Token cap to prevent budget overruns (e.g., 5 million Tokens per month covering all business lines).
**Steps (Gateway Admin only)**:

1. Go to "Model Management → Usage → Tenant Quota";
2. Initial configuration:
   * If empty (showing "No quota has been set for this tenant"), click "Set Tenant Quota";
   * Fill in configuration: granularity defaults to "Tenant Level", period defaults to "Monthly", Token quota (e.g., 5000000, i.e., 5 million/month);
   * Click "Save" and navigate to the quota page to view "total quota, used amount, remaining amount, daily usage trend";
3. Adjust quota: click "Edit Quota" → modify value → save (takes effect immediately);
   \</.topwrite/assets/image (8).png>)

#### 3.4.2 Endpoint Quota Configuration (Business Line Budget Allocation)

**Business value**: Assign an independent quota to a single Endpoint (e.g., 1 million Tokens/month for the e-commerce recommendation model) to achieve business line cost isolation.
**Steps (Gateway Admin/Endpoint Admin)**:

1. Go to "Model Management → Endpoint", select the target Endpoint, click "Edit";
2. Find the "AI Gateway → Access Quota" section;
3. Fill in configuration: granularity defaults to "Endpoint Level", period "Monthly", Token quota (e.g., 1000000);
4. Key rule: actual usable quota = the smaller of tenant quota and Endpoint quota (e.g., if tenant has 500,000 remaining and Endpoint quota is 1,000,000, actual usable is 500,000);
5. Click "Save" and view quota usage in the Endpoint details page;
   \</.topwrite/assets/image (9).png>)

#### 3.4.3 Usage Statistics Query (Multi-dimensional Cost Attribution)

**Business value**: Query usage by Endpoint / user / API KEY dimension to identify high-cost resources (e.g., abnormally high call volume from a specific user).
**Steps (vary by role)**:

1. Go to "Model Management → Usage → Usage Statistics";
2. Configure query conditions:
   * Time range: default is the last 1 month, supports switching to "last 1 week / custom";
   * Statistics dimensions:
     * Regular users: only view "their own associated Endpoints / users";
     * Gateway Admin: view "Endpoints / users / API KEYs / accounts / account details";
3. View data:
   * List view: shows "statistics dimension, date, call count, input Tokens, output Tokens, total usage";
   * Chart view: click "Switch to Chart" to view usage trends via line charts / bar charts;
4. Download details (Gateway Admin only):
   * Click "Download Details" → select year and month (supports the most recent 1 year) → confirm;
     \</.topwrite/assets/image (10).png>)

### 3.5 Multi-scenario Model Invocation (Adapting to Different User Needs)

#### 3.5.1 SQL Invocation (Data Analysts / Development Engineers)

**Business value**: Call models directly in SQL to achieve integrated "data query + AI analysis" (e.g., order text embedding, user review sentiment analysis).
You can call directly in SQL, for example:

```Plain
select ai_complete('endpoint\:lis\_aliyun\_qwen\_max','What is the capital of France?')
```

#### 3.5.2 Data Analytics Agent (DataGPT) Invocation (All Roles)

Data Analytics Agent (DataGPT) implements AI model invocation through a standardized interface, enabling fast model integration and replacement. You only need to replace the existing model configuration in the Data Analytics Agent (DataGPT) model configuration interface with the exclusive invocation address (Base URL) and access credential (API Key) we provide, and the model invocation pipeline will be switched. This leverages AI Gateway to achieve stable, governable AI capability invocation.

#### 3.5.3 OpenAPI Standard Invocation (Development Scenarios)

* Invocation URL: the "Access Address" in the Endpoint list;
* API KEY: obtained from "API KEY Management" (only Gateway Admins can create);
* Invocation methods:
  * Go to the "Model Management → Endpoint" page, click the Endpoint name to enter the details page;
  * At the bottom of the details page, the "Endpoint Invocation Examples" section shows sample code for both OpenAI-python and REST API-cURL invocation methods.

## 4. Key Considerations

1. **Permission Control**: Confirm your role permissions before performing operations (e.g., regular users cannot delete Endpoints) to avoid operation failures due to insufficient permissions. If you need expanded permissions, contact the relevant Admin (Gateway Admin handles global permissions, Endpoint Admin handles business line permissions).

2. **Data Retention**:
   * Account detail data: only the most recent 1 year is retained; for long-term storage, download a backup each month (Gateway Admin operation);
   * Usage monitoring data: retained for a maximum of 60 days; key metrics (e.g., monthly quota usage) should be regularly screenshot-archived.

3. **Model Deletion Risks**:
   * Endpoint deletion is irreversible. Before deleting: ① stop all associated invocations (SQL/OpenAPI/DataGPT); ② notify all users with permissions;
   * After a built-in hosted model is deleted, contact technical support to re-enable it (cannot be self-restored).

4. **API KEY Security**:
   * Avoid leaking (e.g., sharing in plaintext, storing in code repositories);
   * Rotate regularly (recommended every 3 months);
   * After a leak, immediately delete in "API KEY Management" and recreate, then update all associated configurations.

5. **Quota Enforcement Rules**: The actual usable Endpoint quota = the smaller of tenant quota and Endpoint quota. Avoid setting Endpoint quotas far exceeding tenant quotas (e.g., if tenant has 1 million/month and Endpoint is set to 2 million, only 1 million is actually usable, wasting configuration effort).

6. **Compatibility Notes**: External models must comply with the OpenAI interface specification to be integrated (e.g., models that do not support the "messages" parameter need vendor adaptation). When editing model versions, confirm that downstream calling systems support the new version to avoid compatibility issues.
