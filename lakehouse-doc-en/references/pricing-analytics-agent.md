# Analytics Agent Pricing
This page describes the fees you may incur when using Analytics Agent and how they are charged.

## Fee Overview

| Fee Item | Description |
| --- | --- |
| Tiered License Fee | Monthly base license plus token overage fee when monthly usage exceeds the threshold |
| Token Usage Fee | Token consumption from LLM calls during analysis |
| Web Search Fee | Per-call charge when the Agent invokes a web search during analysis |

> ⚠️ **Note**: Data Access Fee is not included. When Analytics Agent connects to a data source (such as Lakehouse) to run queries or create views, the resulting resource consumption is charged by that platform according to its own pricing rules and appears on a separate bill.   

## Tiered License Fee

The tiered license fee consists of a Monthly subscription fee and a Token Overage fee that applies when monthly usage exceeds the threshold.

### Monthly Subscription

| Item | Description |
| --- | --- |
| Fee | **$3,000 / month** (30-day period) |
| Billing cycle | Deducted from your account USD balance as a lump sum (monthly fee x subscription months) at activation |

**Example:** Subscribing for 3 months results in a one-time charge of $3,000 x 3 = **$9,000** at activation.

> ⚠️ **Note**: Monthly subscription covers product authorization only and does not include any free token allowance. 

### Token Overage

When your total monthly token consumption exceeds **300M** (300 million), an overage fee is triggered.

| Item | Description |
| --- | --- |
| Threshold | Monthly total token usage > 300M |
| Fee | Each additional 100M beyond the threshold incurs **$1,000** (partial 100M blocks are rounded up) |
| Billing cycle | Billed in real time |
| Accounting period | Calendar month |

> ⚠️ **Note**: The Token Overage fee is an independent license charge. It does not include a free token allowance and has no effect on the per-token billing rate.

**Examples:**

| Monthly Total Token Usage | Overage Fee | Total Token-Related Fees |
| --- | --- | --- |
| 200M | $0 (below threshold) | Token Usage Fee + $0 |
| 350M | $1,000 (50M over threshold, rounded up to 1 tier) | Token Usage Fee + $1,000 |
| 450M | $2,000 (150M over threshold, rounded up to 2 tiers) | Token Usage Fee + $2,000 |
| 700M | $4,000 (400M over threshold, 4 tiers) | Token Usage Fee + $4,000 |

> ⚠️ **Note**: The overage fee is calculated per calendar month, independent of your subscription start or end date. Whether you activate mid-month, renew, or reactivate after a gap, the monthly threshold remains 300M with no proration or reset. The threshold counts all token types consumed by Analytics Agent within the calendar month, including input, output, and context cache tokens.

## Token Usage Fee

Analytics Agent calls LLMs to perform data analysis, and token consumption is billed from the first token onward.

| Item | Description |
| --- | --- |
| Fee | Actual consumption x per-model unit price |
| Billing cycle | Settled hourly |

Different models and token types (input / output / context cache) have different unit prices. The system calculates charges based on your actual usage. For detailed per-model rates, see [AI Gateway Pricing](pricing-ai-gateway.md).

## Web Search Fee

When Analytics Agent invokes a web search during analysis, each successful call is billed. Calls that time out or return an error (4xx/5xx) are not charged.

| Item | Description |
| --- | --- |
| Fee | **$0.008 / call** |
| Billing cycle | Settled hourly |
