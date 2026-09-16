# Service Tier & Pricing Guide

## What This Document Covers

When using AI Gateway for the first time, users most commonly confuse "models" and "service tiers."

This document explains three things:

1. What service tiers are;
2. Which scenarios each of the three service tiers is suited for;
3. How to choose a tier based on model availability and business importance.

This document covers domestic services only.

## Glossary

| Term | Meaning |
| --- | --- |
| List Price | The standard base price for a model |
| Full Price | When an account has no custom pricing configured, the model is used at its List Price |
| Service Tier | Economy Tier, Standard Tier, or Premium Tier service mode |


## 1. Service Tiers Are Not Models

Think of it this way:

```text
Model      = what task you want to accomplish
Service Tier = how you want the task delivered
API Key    = which business workload can use this tier
```

A service tier represents a class of service delivery, not the model capability itself. It does not require users to manage providers, channels, or commercial pricing configurations.

In practice, users only need to pay attention to two things:

- Which service tier the current API key is bound to;
- Whether the target model shows as "available" for that tier in the Model Market.

Specific pricing information is always shown in the Model Market and Model Details Page.

## 2. The Three Service Tiers

### Economy Tier

Economy Tier is primarily cost-first.

Suitable for:

- Ad-hoc testing;
- Personal trials;
- Non-critical workloads;
- Repeatable tasks;
- Scenarios with low requirements for service continuity;
- Scenarios where completing basic tasks is sufficient.

Economy Tier is not suitable as the default tier for important production pipelines. If a call failure would directly impact business outcomes, Standard Tier or Premium Tier is recommended.

### Standard Tier

Standard Tier balances cost with everyday availability.

Suitable for:

- Regular internal enterprise tools;
- Everyday Q&A and content generation;
- General code assistance;
- Data analysis support;
- Workloads that require some stability but are not part of critical production pipelines.

Standard Tier is a good starting choice for most everyday business workloads.

### Premium Tier

Premium Tier focuses on service pipeline stability and is suitable for formal business use.

Suitable for:

- Formal production systems;
- Automated agents;
- Multi-step tasks;
- Tasks that need to run to completion without interruption;
- Tasks whose results feed directly into the next step in a pipeline;
- Workloads sensitive to interruption and re-execution.

The emphasis of Premium Tier is a more stable service pipeline — not simply "higher price."

For recommendations on using Premium Tier with formal business and automated products, see the "Prefer Premium Tier for Formal Business" section below.

## 3. Prefer Premium Tier for Formal Business

Premium Tier provides stronger guarantees and better service pipeline stability. It is suited for workloads with high requirements for continuous calls and task completion quality.

The following products are recommended to use Premium Tier by default:

| Product | Usage Characteristics | Reason for Recommendation |
| --- | --- | --- |
| Data Analytics Agent | Multi-step data analysis and result interpretation | An interrupted intermediate call may break the entire analysis pipeline |
| Engineering Agent | Code generation, debugging, and multi-round revisions | Long context and sequential steps require high stability |
| CZ-CLI | Command-line and automated workflow calls | Suited for continuous execution and scripted invocations |
| Lakehouse AI Function | Embedded data processing and function pipelines | Call results may directly affect upstream data tasks |

Premium Tier does not change model capabilities. It primarily provides a more stable service pipeline and stronger SLA. Models should still be selected first based on the specific task, then the tier chosen based on business importance.

## 4. How to Choose a Service Tier

Choose based on "business consequences," not "model name."

### If the task can be retried after failure

For example: ad-hoc testing, exploring model capabilities, internal trials — Economy Tier is a good first choice.

### If the task is part of a regular workflow

For example: general Q&A, everyday content generation, general-purpose analysis — Standard Tier is a good first choice.

### If a task failure would affect downstream business steps

For example: automated agent execution, production data processing, command-line automation, or function pipelines — Premium Tier is recommended directly.

A simple decision guide:

```text
Would failure affect formal business?
       ├── No:  Economy Tier or Standard Tier
       └── Yes: Premium Tier
```

## 5. Service Tiers and Model Availability

The core role of a service tier is to determine which class of service pipeline the current business workload uses. Account-specific pricing and service scope are configured commercially; users do not need to manage these rules in documentation or the UI.

Users only need to check whether a model can be called based on the current API key and the Model Market status:

| Account and Service Scope Status | Current Model Status in Current Tier | Status Shown to User | Callable |
| --- | --- | --- | --- |
| No custom service scope configured | Any model | Full Price, showing List Price | Yes |
| Custom service scope configured | Available in current tier | Available, showing current price | Yes |
| Custom service scope configured | Not available in current tier | Not available | No, request fails |

Full decision flow:

```text
Has the account configured a custom service scope?
├─ No
│  └─ All models available in all tiers, billed at List Price, marked "Full Price"
└─ Yes
   └─ Is the current model available in the current API key's tier?
      ├─ Yes: call allowed
      └─ No:  model not available, request fails
             will not switch to another tier
```

> **Figure 1: Model Market availability indicator**
>![](/.topwrite/assets/2_1787119863665.png)

## 6. API Keys and Service Tiers

One API key corresponds to one service tier.

If the account uses multiple tiers simultaneously, separate API keys must be created:

```text
API Key A: test project  - Economy Tier
API Key B: daily tools   - Standard Tier
API Key C: production app - Premium Tier
```

Select the service tier when creating an API key. After creation, whether a specific model is available is determined by the Model Market status for the current API key's tier.

## 7. No Automatic Cross-Tier Switching

AI Gateway will not automatically switch to another tier if the current tier has no available service.

For example, a request using a Standard Tier API key when Standard Tier service is temporarily unavailable:

```text
Standard Tier request
   ↓
Standard Tier pipeline unavailable
   ↓
Will NOT switch to Economy Tier
Will NOT switch to Premium Tier
   ↓
This request fails
```

Requests always use the service tier selected by the API key and the corresponding price shown in the UI.

If the business requires higher stability, select Premium Tier directly when creating the API key.

## 8. Common Misconceptions

### Misconception 1: Premium Tier applies to all models

Premium Tier means a more stable service pipeline, but the specific model capabilities still need to be assessed in the Model Market.

The correct approach is to select the model based on the task first, then choose the tier based on business importance.

### Misconception 2: If a model is visible in the Model Market, it can always be called

Not necessarily. Whether a model can be called depends on the service tier bound to the current API key. Check the "available" or "not available" status shown in the Model Market; models marked "not available" cannot be called.

### Misconception 3: An API key can switch tiers at any time

One API key corresponds to one service tier. To use a different tier, create a new API key.

### Misconception 4: The system will automatically switch tiers when the current one is unavailable

There is no automatic cross-tier switching. When the current tier has no available service, the request returns as failed.


## Related Documents

- [Product Introduction](Introduction.md)
- [Quick Start](quickstart.md)
- [API Key Management](aigw_api_key.md)
- [Model Market](aigw_model_market.md)
