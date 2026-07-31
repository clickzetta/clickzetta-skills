# Analytics Agent Pricing

**[Preview Release]** This feature is currently in public preview.

This page describes the fees you may incur when using Analytics Agent and how they are charged.

## Fee Overview

| Fee Item | Description |
| --- | --- |
| Software License Fee | Analytics Agent product license |
| Token Usage Fee | Token consumption from LLM calls during analysis |
| Token Overage Tiered Fee | Additional fee when monthly token usage exceeds the threshold |
| Data Access Fee | Resource fees incurred on the data source side when connecting and analyzing data |

## Software License Fee

| Item | Description |
| --- | --- |
| Fee | **$3,000 / month** |
| Charged | Deducted from your account USD balance as a lump sum (monthly fee x subscription months) at activation |

**Example:** Subscribing for 3 months results in a one-time charge of $3,000 x 3 = **$9,000** at activation.

> ⚠️ **Note**: The software license fee covers product authorization only and does not include any free token allowance. Token consumption is billed from the very first token.

## Token Usage Fee

Analytics Agent calls LLMs to perform data analysis, and token consumption is billed from the first token onward.

| Item | Description |
| --- | --- |
| Billing method | Actual consumption x per-model unit price |
| Billing cycle | Settled monthly at month-end |

Different models and token types (input / output / context cache) have different unit prices. The system calculates charges based on your actual usage. For detailed per-model rates, see [AI Gateway Pricing](pricing-ai-gateway.md).

## Token Overage Tiered Fee

When your total monthly token consumption exceeds **300M** (300 million), an overage tiered fee is triggered.

| Item | Description |
| --- | --- |
| Threshold | Monthly total token usage > 300M |
| Tiered rule | Each additional 100M beyond the threshold incurs **$1,000** (partial 100M blocks are rounded up) |
| Billing cycle | Settled monthly at month-end |
| Accounting period | Calculated independently per calendar month |

> ⚠️ **Note**: 300M is the overage threshold, not a free allowance. Tokens within 300M are still charged at the normal per-model unit price as Token Usage Fee.

**Examples:**

| Monthly Total Token Usage | Overage Tiered Fee |
| --- | --- |
| 200M | $0 (below threshold) |
| 350M | $1,000 (50M over threshold, rounded up to 1 tier) |
| 450M | $2,000 (150M over threshold, rounded up to 2 tiers) |
| 700M | $4,000 (400M over threshold, 4 tiers) |

> ⚠️ **Note**: The overage tiered fee is calculated per calendar month, independent of your subscription start or end date. Whether you activate mid-month, renew, or reactivate after a gap, the monthly threshold remains 300M with no proration or reset.

## Data Access Fee

Analytics Agent supports connecting to multiple data sources for analysis. During analysis, queries executed and views created by the Agent consume compute, storage, and other resources on the data source side. These fees are charged by the data source platform according to its own pricing rules.

- This fee is not included in the Analytics Agent bill; it appears on the corresponding data source's bill
- The amount depends on your actual usage (query frequency, data volume, and so on)

**Example with Lakehouse as data source:** When you connect Lakehouse as a data source, the resulting compute and storage fees are charged according to Lakehouse pricing rules. For details, see [Lakehouse Pricing](pricing-lakehouse.md).
