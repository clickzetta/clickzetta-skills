## Preface

This guide is designed to provide enterprise users with comprehensive instructions for the Singdata AI Gateway product, covering core features, detailed operational workflows, best practices, and frequently asked questions. Singdata AI Gateway is an enterprise-grade AI gateway service launched by the Singdata platform, delivering core capabilities such as unified multi-model API management, intelligent routing and scheduling, BYOK (Bring Your Own Key) model integration, usage statistics and analysis, and permission management. It helps enterprises simplify the process of integrating large models from multiple vendors, reduce operational complexity, and ensure the stability, security, and observability of AI services.

## 1. Product Introduction

### 1.1 Product Positioning

AI Gateway is a **unified access and management gateway** purpose-built by the Singdata platform for enterprise-grade AI applications, serving as the core hub of enterprise AI infrastructure. It connects upward to various internal enterprise AI applications (intelligent customer service, content generation, code assistance, data analysis, etc.) and connects downward to major domestic and international LLM vendors, industry-specific vertical models, and enterprise-owned models.

In light of the common pain points in enterprise AI adoption, Singdata AI Gateway addresses the following core challenges:

* **API Fragmentation**: Different vendors provide inconsistent API specifications, requiring enterprises to develop separate adapter code for each vendor, resulting in high maintenance costs
* **High Operational Complexity**: When using multiple models in parallel, there is a lack of unified monitoring, alerting, and troubleshooting mechanisms
* **Uncontrollable Costs**: Unable to granularly manage AI usage by team, project, or application dimension, leading to easy overspending
* **Data Security Risks**: Increased risk of data leakage when invoking models across multiple channels, with a lack of unified security control and auditing capabilities
* **Insufficient Flexibility**: Switching model vendors or adding new models requires changes to business code, impacting business continuity

With Singdata AI Gateway, enterprises can achieve "integrate once, use everywhere," significantly reducing the development and operational costs of AI applications while enhancing the stability, security, and observability of AI services.

### 1.2 Core Product Value

Singdata AI Gateway delivers four core values for enterprises:

1. **Cost Reduction and Efficiency**: Unified API interface reduces the workload of multi-model adapter development; intelligent routing strategies automatically select the optimal cost-performance model, lowering AI invocation costs
2. **Unified Management**: Centrally manage all model resources and invocation permissions, achieving "one platform to manage all AI"
3. **Flexible Expansion**: Support rapid integration of new model vendors and custom models without modifying business code, enabling flexible expansion on demand

### 1.3 Core Advantages

#### 1.3.1 Multi-Model Unified Access

* **Full Vendor Coverage**: Supports major domestic and international LLM vendors such as Alibaba Cloud Bailian, ByteDance Doubao, and AWS Bedrock
* **Standard Interface Compatibility**: Provides a REST API interface 100% compatible with OpenAI, allowing existing OpenAI-based business code to work without modification -- simply replace the API endpoint and key for a seamless switch
* **Multi-Modal Support**: Comprehensive support for multi-modal capabilities including text generation, image understanding, speech recognition and synthesis, and code generation
* **Model Version Management**: Unified management of different model versions, supporting smooth upgrades and rollbacks

#### 1.3.2 Intelligent Routing and Load Balancing

* **Multi-Dimensional Routing Strategies**: Supports intelligent routing based on multiple dimensions such as price, throughput, latency, and region

  * **Price Priority**: Automatically selects the lowest-price available provider to maximize cost efficiency
  * **Throughput Priority**: Automatically selects the highest-throughput provider to handle high-concurrency scenarios
  * **Latency Priority**: Automatically selects the lowest-latency provider to ensure user experience

#### 1.3.3 BYOK Seamless Integration

* **Multi-Provider Support**: Currently supports BYOK access for major providers such as Alibaba Cloud Bailian - Beijing, AWS Bedrock US-EAST-1, and BytePlus AP-SOUTHEAST
* **Zero-Code Integration**: Simply enter your third-party API key on the platform to integrate your own models without any development work
* **Independent Billing System**: When using BYOK models, billing goes directly through your own third-party provider account, with no additional fees charged by the platform
* **Unified Management Experience**: BYOK models enjoy the same management experience as platform built-in models, supporting unified routing, monitoring, and usage statistics

#### 1.3.4 Granular Usage Management

* **Multi-Dimensional Usage Statistics**: Supports Token consumption statistics by model, account, API Key, user, time, and other dimensions
* **Fine-Grained Quota Control**: Supports setting independent Token quotas and validity periods for each API Key to prevent unexpected overspending
* **Real-Time Usage Monitoring**: Real-time display of Token consumption trends with usage threshold alerts
* **Cost Allocation and Analysis**: Automatically generates multi-dimensional cost analysis reports, supporting cost allocation by team and project
* **Data Export**: Supports exporting all usage data in Excel format for internal financial accounting

#### 1.3.5 Enterprise-Grade Security Management

* **Fine-Grained Permission Management**: Supports Role-Based Access Control (RBAC), with different users having different operational permissions

### 1.4 Core Functional Modules

Singdata AI Gateway includes the following five core functional modules, corresponding to the left navigation menu:

| Functional Module           | Core Capabilities                                                                                             | Business Value                                                    |
| --------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **API Key Management**      | Key creation / editing / deletion / disabling, validity period configuration, Token quota settings, routing policy binding, batch operations, usage viewing | Achieve permission isolation and usage control across different businesses and teams |
| **Model Marketplace**       | Model display and search, model detail viewing, one-click copy of invocation examples, model runtime status monitoring | Quickly understand platform-supported model capabilities, obtain integration code, and monitor model runtime status |
| **BYOK**                    | Third-party provider management, own key configuration, model selection, connectivity testing, BYOK model management | Seamlessly integrate enterprise-owned third-party model services while retaining original accounts and billing systems |
| **Usage Statistics**        | Multi-dimensional usage query, trend analysis, detail viewing, data export, cost analysis                     | Gain comprehensive insight into AI cost composition and achieve granular cost management and allocation |
| **Permission Management**   | User authorization, role management, permission revocation                                                    | Ensure platform security and achieve permission isolation for different users |

### 1.5 Architecture

Singdata AI Gateway adopts a cloud-native distributed architecture consisting of four layers: access layer, routing layer, model layer, and management layer:

1. **Access Layer**: Provides a unified API access endpoint, responsible for request authentication, rate limiting, and protocol conversion
2. **Routing Layer**: The core intelligent routing engine, responsible for forwarding requests to the optimal model access point based on routing strategies
3. **Model Layer**: Interfaces with various model vendor APIs, responsible for request forwarding and response processing
4. **Management Layer**: Provides management capabilities including API Key management, model management, BYOK management, usage statistics, and permission management

### 1.6 Applicable Scenarios

#### 1.6.1 Enterprise Multi-Model Unified Management Scenario

**Business Pain Point**: Enterprises simultaneously use large models from multiple vendors, each with its own API interface, key management, and billing system, resulting in high development and operational complexity and difficult cost control.

**Solution**: Unify access to all models through Singdata AI Gateway, provide a standardized API interface, and achieve centralized key management, routing and scheduling, usage statistics, and monitoring and alerting.

#### 1.6.2 Rapid AI Application Development Scenario

**Business Pain Point**: Developers need to spend significant time learning API documentation from different vendors and writing adapter code, resulting in long development cycles and low efficiency.

**Solution**: Singdata AI Gateway provides a standard API interface 100% compatible with OpenAI, allowing developers to invoke all models by learning a single API specification. The platform also provides rich invocation examples and SDKs to further lower the development barrier.

#### 1.6.3 Granular AI Cost Management Scenario

**Business Pain Point**: Enterprise AI costs grow rapidly, but it is impossible to accurately track AI usage by team or project, making cost allocation difficult and overspending likely.

**Solution**: Singdata AI Gateway supports creating independent API Keys for each team and project, with independent Token quotas. The platform provides multi-dimensional usage statistics and cost analysis reports, helping enterprises achieve accurate cost allocation and control.

#### 1.6.4 Self-Owned Model Integration Scenario

**Business Pain Point**: Enterprises have already activated model services with third-party providers and wish to retain their original accounts and billing systems while managing them through a unified gateway.

**Solution**: Through Singdata AI Gateway's BYOK feature, simply enter your enterprise's own API key to integrate third-party models into the unified gateway, enjoying a management experience fully consistent with platform built-in models.

### 1.7 Comparison with Traditional Integration Approaches

| Comparison Dimension | Traditional Multi-Model Integration Approach           | Singdata AI Gateway Integration Approach                      |
| -------------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Development Effort   | Develop separate adapter code for each vendor, high workload | Develop once, invoke all models; 80% workload reduction       |
| Operational Complexity | Parallel operation of multiple systems, high complexity | Unified platform management, simple operations                |
| Cost Control         | Unable to achieve granular control, costs uncontrollable | Multi-dimensional usage statistics and quotas, precise cost control |
| Model Switching      | Requires modifying business code, impacts business continuity | No code changes required, one-click switching                 |
| Security Control     | Decentralized management, high security risk            | Unified security control, comprehensive data protection       |
| Observability        | Lack of unified monitoring, difficult troubleshooting  | Full-link observability, rapid issue localization             |
