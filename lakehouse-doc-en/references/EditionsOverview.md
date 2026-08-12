# Singdata Editions Overview

**Standard Edition vs. Enterprise Edition**

Singdata Lakehouse provides two product editions—**Standard Edition** and **Enterprise Edition**—designed to meet different scales of analytical workloads and security requirements. Both editions share the same core Lakehouse architecture, while the Enterprise Edition offers expanded capabilities in **scale, governance, and security**.

This document summarizes the key functional differences between the two editions.

***

## 1. Development & Analytics Capabilities

### Task Development and Orchestration

| Capability                  | Standard Edition                                  | Enterprise Edition |
| --------------------------- | ------------------------------------------------- | ------------------ |
| Python Tasks                | Up to 5 tasks (creation and concurrent execution) | Unlimited          |
| Shell Tasks                 | Up to 5 tasks                                     | Unlimited          |
| Databricks-Compatible Tasks | Up to 5 tasks                                     | Unlimited          |

### Observability & Data Management

| Capability               | Standard Edition     | Enterprise Edition |
| ------------------------ | -------------------- | ------------------ |
| Monitoring & Alert Rules | Up to 5 rules        | Unlimited          |
| Data Quality Rules       | Up to 5 active rules | Unlimited          |
| Notebooks (Analysis)     | Up to 5 notebooks    | Unlimited          |
| Data Sharing Objects     | Up to 5 shares       | Unlimited          |
| Dynamic Tables           | Up to 5 tables       | Unlimited          |

### Advanced Indexing

| Capability     | Standard Edition | Enterprise Edition |
| -------------- | ---------------- | ------------------ |
| Vector Index   | Not available    | Supported          |
| Inverted Index | Not available    | Supported          |

***

## 2. Security, Governance & Enterprise Readiness

The Enterprise Edition is designed for organizations with strict security, compliance, and network isolation requirements.

| Capability                                              | Standard Edition | Enterprise Edition |
| ------------------------------------------------------- | ---------------- | ------------------ |
| Private Network Connectivity (PrivateLink / VPC Access) | Not available    | Supported          |
| Private Storage                                         | Not available    | Supported          |
| Network Policy Control                                  | Not available    | Supported          |
| Operation Audit Logs                                    | Not available    | Supported          |
| User Login Audit                                        | Not available    | Supported          |
| Dynamic Data Masking                                    | Not available    | Supported          |
| Single Sign-On (SSO)                                    | Not available    | Supported          |

***

## 3. Edition Selection Guidance

* **Standard Edition** is suitable for:
  * Small teams and individual analysts
  * Lightweight development and analytics
  * Proof-of-concept and early-stage workloads
* **Enterprise Edition** is suitable for:
  * Large-scale production workloads
  * Enterprises requiring advanced security and compliance
  * Organizations with private network, governance, and audit requirements
  * AI, vector search, and advanced indexing scenarios

^
