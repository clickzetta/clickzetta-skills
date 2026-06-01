# Account & Billing

Account management covers four areas: users, permissions, funds, and billing. Most operations require the `account_admin` role — if you are just taking over account management, start here.

---

## Managing Basic Account Information

The account name (`account_name`) and service instance name (`instance_name`) are two different identifiers. The former is used for login, and the latter is used for SQL and client connections. Both are automatically generated at registration and **cannot be modified**.

> ⚠️ **Note:** Modifying the account registration phone number requires the account administrator (`account_admin`) role.

| Scenario | Action | Reference |
|------|------|---------|
| View account name, login URL, and service instance name | Management Center -> Account Home | [Account & Billing](management.md) |
| Modify the account registration phone number | Management Center -> Account Center -> Account Info -> Registration Phone -> Modify | [Account & Billing](management.md) |
| Fill in connection parameters in JDBC / Python SDK | Use `instance_name` as the connection identifier | [Account & Billing](management.md) |
| Forgot account name | Retrieve via the account registration phone number | [Account & Billing](management.md) |

---

## Managing Users and Permissions

> ⚠️ **Note:** Creating, disabling, and deleting global users and service users, as well as granting or revoking the account administrator role, requires the account administrator (`account_admin`) role.
>
> Passwords and phone numbers can only be modified by the user themselves; the account administrator cannot modify them on behalf of others.

| Scenario | Action | Reference |
|------|------|---------|
| Add a human user (for interactive login) | User Management -> Create User | [Managing Users](account_user_management.md) |
| Add a service user (for programmatic access) | User Management -> Create Custom Service User | [Managing Users](account_user_management.md) |
| Grant or revoke the account administrator role | User Management -> Edit User -> Set as Account Administrator | [Managing Users](account_user_management.md) |
| Immediately stop all operations for a user | User Management -> Disable User | [Managing Users](account_user_management.md) |
| Delete a departed employee's account | User Management -> Delete User (note: existing connections are not immediately terminated) | [Managing Users](account_user_management.md) |
| Change your own password or phone number | Username in the bottom-left corner -> Change Password / User Info | [Managing Users](account_user_management.md) |

---

## Viewing and Topping Up Account Funds

> ⚠️ **Note:** Accessing account funds features requires the account administrator (`account_admin`) role.

Account funds are divided into two categories: **cash account** and **voucher account**, with unified settlement across all regions. When the cash balance reaches 0 and no vouchers are available, continued usage will generate an outstanding balance that must be settled promptly.

| Scenario | Action | Reference |
|------|------|---------|
| View current balance and vouchers | Billing Center -> Account Funds | [Account Funds](account-funds.md) |
| Online top-up (Alipay / WeChat Pay) | Account Funds -> Top Up -> Select Payment Method | [Account Funds](account-funds.md) |
| Corporate bank transfer top-up | Account Funds -> Top Up -> Corporate Transfer; contact sales after remittance | [Account Funds](account-funds.md) |
| View top-up and spending history | Account Funds -> Transaction Details | [Account Funds](account-funds.md) |
| View voucher expiry and usage history | Account Funds -> Vouchers -> View Details | [Account Funds](account-funds.md) |

Top-up method comparison:

| Method | Arrival Time | Notes |
|---------|---------|------|
| Alipay / WeChat Pay | Instant | User agreement must be accepted on first top-up |
| Corporate bank transfer | 3 business days | Contact sales to complete the credit |

---

## Viewing Billing Statements

> ⚠️ **Note:** Accessing billing statement features requires the account administrator (`account_admin`) role.

| Scenario | Action | Reference |
|------|------|---------|
| View today's / yesterday's / this month's spending summary | Billing Center -> Billing Statements -> Billing Overview | [Billing Statements](billing.md) |
| Break down costs by workspace, instance, or time period | Billing Center -> Billing Statements -> Statement Overview -> Filter | [Billing Statements](billing.md) |
| View daily details (list price, discount, discounted price) | Billing Center -> Billing Statements -> Statement Details | [Billing Statements](billing.md) |
| Export billing data (XLSX) | Statement Details -> Export Details | [Billing Statements](billing.md) |
| View historical annual statements | Billing Center -> Billing Statements -> Statement History | [Billing Statements](billing.md) |
| Understand unit prices and calculation formulas for each billing item | — | [Pricing and Billing](pricing.md) |

Billing update frequency: compute and network items update hourly; storage items update the previous day's data in the early hours of the following day.

---

## Controlling and Optimizing Costs

Singdata Lakehouse charges across three categories: compute (CRU\*hours), storage (GiB/month), and network transfer (GB). The key to reducing costs is minimizing idle runtime of compute clusters and controlling storage and network traffic.

| Scenario | Action | Reference |
|------|------|---------|
| Receive alert notifications when costs spike | Data quality rules + monitoring alerts, based on `sys.information_schema.instance_usage` | [Billing Anomaly Alert Configuration Guide](lakehouse_billing_anomaly_alert_configuration_guide.md) |
| Stable costs with a budget cap | Fixed threshold monitoring approach | [Billing Anomaly Alert Configuration Guide](lakehouse_billing_anomaly_alert_configuration_guide.md) |
| Fluctuating costs with focus on abnormal increases | Dynamic baseline monitoring approach (compared against historical median) | [Billing Anomaly Alert Configuration Guide](lakehouse_billing_anomaly_alert_configuration_guide.md) |
| Understand billing principles and pricing for each resource type | — | [Pricing and Billing](pricing.md) |

**Common cost-reduction measures**:
- Stop compute clusters when not in use (general-purpose and analytical clusters are billed by runtime)
- Reuse sync-type compute clusters for real-time sync tasks to avoid spinning up a separate cluster per task
- Reduce public network data export volume (network transfer is only billed for outbound traffic; inbound is free)
- Set a reasonable Time Travel retention period to avoid long-term storage consumption by multiple data versions

---

## Not Sure Where to Start?

```
What do you want to do?
├── Manage basic account information (login URL, registration phone)
│   └── Requires account_admin → Management Center -> Account Center
├── Manage users
│   ├── Add / disable / delete users → Requires account_admin → User Management
│   └── Change your own password or phone number → No special permission required → Username in bottom-left corner
├── Account funds
│   ├── View balance / vouchers → Requires account_admin → Billing Center -> Account Funds
│   └── Top up → Online (instant) or corporate bank transfer (3 business days)
├── View billing statements
│   └── Requires account_admin → Billing Center -> Billing Statements
└── Control costs
    ├── Set up alerts → Billing Anomaly Alert Configuration Guide
    └── Understand billing rules → Pricing and Billing
```
