# **Billing**

## Introduction

The Billing feature provides your consumption details on the Lakehouse Cloud Platform. Bills are continuously updated based on product usage.

## Feature Permissions

For multi-user tenants, access to the billing feature is restricted to administrator users.

## Bill Updates

* **Computing and Network Resources**: Bills are updated hourly.
* **Storage Resources**: Bills are updated daily. Data is collected multiple times within a day, and the actual usage for the previous day is updated by midnight.

## Data Scope

You can view billing data generated since **May 2023** through this feature.

## Billing Summary

The Billing Summary displays the total cost of using the Lakehouse Cloud Platform. Costs can also be viewed separately by category: **Computing Resources**, **Storage**, and **Network**.

You can filter costs by specifying **Availability Zone Instances**, **Time Range**, or **Workspace** to trace cost sources and analyze cost distribution across different workspaces.

![](.topwrite/assets/image_1741090093182.png)

## Bill Details

Bill Details show daily billing information, including resource original prices, discounts, and more. Detailed data can be exported.

![](.topwrite/assets/image_1741090174046.png)

| Field                 | Description                                                                                                                                                                         |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Consumption Time**  | Billing date, displayed daily.                                                                                                                                                      |
| **Compute Usage**     | Aggregated usage of computing resources, including: Data Integration, Task Scheduling, General Compute Clusters, Analytic Compute Clusters, Serverless Jobs, Streaming Integration. |
| **Storage Usage**     | Usage of storage resources.                                                                                                                                                         |
| **Network Usage**     | Usage of network resources.                                                                                                                                                         |
| **Original Price**    | Total amount calculated by multiplying the unit price of each billing item by its usage.                                                                                            |
| **Discounted Amount** | Total amount after applying discounts to each billing item.                                                                                                                         |
| **Discount**          | Comprehensive discount rate (not per-item). Calculated as: Discount = (Discounted Amount / Original Price) × 100%.                                                                  |

For specific product pricing and billing rules, refer to [Pricing and Billing](<pricing.md>)

**Export Details**: Click the "Export Details" button at the top-right corner to export billing details in XLSX format.

## Billing Overview

The billing overview displays the current account balance, today's cost, yesterday's cost, and month-to-date cumulative cost statistics, enabling you to quickly identify current consumption trends and effectively manage account fund allocation.

![](.topwrite/assets/image_1741090229327.png =300)

* **Balance**: Current available balance in the account (updated upon recharges or consumption).
* **Today’s Consumption**: Cumulative consumption for the current day (updated hourly).
* **Yesterday’s Consumption**: Total consumption for the previous day.
* **Monthly Accumulated Consumption**: Cumulative consumption for the current month (includes today’s consumption, updated hourly).

## Billing History

Billing History provides a summary of all billing records. By default, monthly aggregated data for the current year is displayed. Use the year selector to view historical billing data.

![](.topwrite/assets/image_1741090336844.png =300)
