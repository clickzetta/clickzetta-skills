## 1. Overview

A **Network Policy** is intended to control the sources that can access a particular service instance. Typical use cases include:

* Restricting web service access of a Lakehouse service instance so that only specific IPs or CIDR ranges are allowed.
* Restricting JDBC connections to a Lakehouse service instance so that only specific IPs or CIDR ranges are allowed.
* Blocking (blacklisting) suspicious or risky IP address segments.
* When necessary, and to avoid impacting production or administrator logins, a user with the instance administrator role (**instance\_admin**) can **temporarily bypass** and modify network policy settings.

In actual operations and maintenance, combining both IP allowlists (whitelists) and blocklists (blacklists) can significantly enhance data security and compliance.

***

## 2. Introduction to Network Policy

* **Core Function**: Control which network sources can access a target service instance by using an allowlist (**Allow\_IP\_List**) and a blocklist (**Block\_IP\_List**).
* **Typical Effects**:
  1. Manage and filter IP addresses or CIDR ranges.
  2. Support both allowlist (Allow\_IP\_List) and blocklist (Block\_IP\_List) configurations for network policies.
  3. When multiple policies are active and combined, the “deny-first” principle is adopted.

***

## 3. How Network Policies Work & Their Use Cases

### 3.1 Default Allow and Explicit Deny

* **When there are no network policies at all**, the system allows all IP addresses by default (equivalent to “Allow 0.0.0.0/0”).
* Once at least one network policy has been created and activated, the system filters requests based on **all effective policies**’ allowlist and blocklist rules.

### 3.2 Calculations for Allowlist (Allow) and Blocklist (Block)

Within the same network policy or among multiple active policies:

* If there is any active allowlist policy, then any IP/CIDR not in the allowlist policies will be blocked.
* If there are no active allowlists at all, then all IP/CIDRs are allowed except those specified by the active blocklists.
* Finally, if any blocklist rule is matched, that IP is denied.

### 3.3 Multiple Policies and Priority

* When multiple policies are active at the same time, the allowlists are combined into a union, and the blocklists are also combined into a union.
* There is no priority order among multiple network policies. The system performs logical operations on all active network policies and derives a final consolidated network policy result.

### 3.4 Scope of Application

Network policies apply to controlling requests from external networks that access the Lakehouse service via:

* JDBC
* SDK
* Web pages

They currently **do not** apply to:

* Access via MySQL-compatible protocols.

***

## 4. Key Attributes and Limitations

### 4.1 Network Policy Attributes

| Attribute Name      | Required | Value Range                                                                                                    | Default  | Description                                                                       |
| ------------------- | -------- | -------------------------------------------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------- |
| **Name**            | Yes      | Starts with a letter or underscore, 3-28 characters, automatically lowercased, letters/digits/underscores only | None     | Policy name is unique within an instance.                                         |
| **Allow\_IP\_List** | Yes      | IPv4 single IP or CIDR, comma-separated, up to \~100,000 entries                                               | None     | Allowed IPs or CIDR ranges. `0.0.0.0/0` is not permitted.                         |
| **Block\_IP\_List** | No       | IPv4 single IP or CIDR, comma-separated, up to \~100,000 entries                                               | None     | Blocked IPs or CIDR ranges. `0.0.0.0/0` is not permitted.                         |
| **Status**          | Yes      | `Activate` or `Inactive`                                                                                       | Activate | Newly created policies default to “active.” Multiple active policies can coexist. |

### 4.2 Limitations and Notes

1. **Maximum Policy Count**: A single instance can have up to 20 network policies.
2. **Maximum IP Entries per Policy**: Each allowlist and blocklist can hold up to 100,000 IP/CIDR entries.
3. **Propagation Delay**: Network policies are subject to a caching mechanism. They typically take effect within 5 minutes.
4. **Irrecoverable Once Deleted**: Please proceed cautiously. Especially when multiple network policies are active at once, the logical relationships can be complex. Deleting an active policy could greatly change the overall rules for allowed or denied access.

***

## 5. User Guide

The following operations can be performed via SQL commands or through a front-end management console, depending on how your product implements it.

### 5.1 Create a Network Policy

This operation can only be performed by users with the **instance\_admin** role.

**Web Operation**:

In **Management** - **Security** - **Network Policy**, click +**New Policy**.

In the pop-up dialog, enter the **Policy Name** and then fill in the IP allowlist or IP blocklist fields as needed.

:-: ![](.topwrite/assets/image_1742472044590.png =776)

**SQL Operation**:

```sql
CREATE [ OR REPLACE ] NETWORK POLICY <name>
ALLOWED_IP_LIST = ( [ '<ip_address>' ] [ , '<ip_address>' , ... ] )
[ BLOCKED_IP_LIST = ( [ '<ip_address>' ] [ , '<ip_address>' , ... ] ) ];


-- Example:
CREATE NETWORK POLICY policy1
  ALLOWED_IP_LIST = ('192.168.11.1','192.168.11.2','10.0.0.1/24')
  BLOCKED_IP_LIST = ('192.168.11.99');
```

Notes:

* Within the same service instance, network policy names cannot be duplicated.
* IP allowlists and blocklists support IPv4 IP or CIDR entries, but `0.0.0.0/0` is not allowed. When the allowlist is empty, it means all IPs are allowed.
* Within a single network policy, you cannot add the same IP/CIDR twice in the allowlist or blocklist, but overlaps are allowed. Across different network policies, overlapping or duplicate IP/CIDRs are permitted.
* After successful creation, the default status is `Activate` (it either takes effect immediately or can be activated/used again, depending on your product).
* The IP you are currently using to access the Lakehouse can also be included in either the allowlist or blocklist. If you add your current IP to the blocklist, once the policy is effective, your access to the service instance will be immediately blocked. Please use caution.

### 5.3 Modify a Network Policy

**Web Operation**:

In **Management** - **Security** - **Network Policy**, click the **Edit** button in the **Actions** column for the policy you want to modify. A pop-up dialog will allow you to edit that policy.

* The name of a network policy cannot be changed. Only the IP addresses (IP/CIDR) in the allowlist/blocklist can be modified.

:-: ![](.topwrite/assets/image_1742472109817.png =767)

:-: ![](.topwrite/assets/image_1742472134880.png =767)

**SQL Operation**:

```
ALTER NETWORK POLICY [ IF EXISTS ] <name> SET  
ALLOWED_IP_LIST = ( [ '<ip_address>' ] [ , '<ip_address>' , ... ] )
[ BLOCKED_IP_LIST = ( [ '<ip_address>' ] [ , '<ip_address>' , ... ] ) ];

-- Example:
ALTER NETWORK POLICY policy1 SET 
ALLOWED_IP_LIST = ('192.168.11.1') 
BLOCKED_IP_LIST = ('192.168.11.99');
```

Notes:

* Modifying a network policy with SQL is a “**replace**” operation. When using the ALTER statement, you must include **all** IP ranges you want in ALLOWED\_IP\_LIST and BLOCKED\_IP\_LIST.

For example:

```
--Create a sample network policy
CREATE NETWORK POLICY policy1  
BLOCKED_IP_LIST = ('192.168.11.99');

-- After the following statement, policy1 only contains ALLOWED_IP_LIST = ('192.168.11.100')
ALTER NETWORK POLICY policy1 SET 
ALLOWED_IP_LIST = ('192.168.11.100');

-- Not executing the above ALTER, but instead executing the following ALTER statement, 
-- policy1 will then have ALLOWED_IP_LIST = ('192.168.11.1') 
-- and BLOCKED_IP_LIST = ('192.168.11.99')
ALTER NETWORK POLICY policy1 SET 
ALLOWED_IP_LIST = ('192.168.11.1')  
BLOCKED_IP_LIST = ('192.168.11.99');
```

### 5.4 Activate or Inactivate a Network Policy

**Web Operation**:

In **Management** - **Security** - **Network Policy**, click **Disable** / **Enable** in the **Actions** column for the policy you want to change, to toggle its status.

:-: ![](.topwrite/assets/image_1742472177085.png =817)

**SQL Operation**:

```

ALTER NETWORK POLICY <name> ACTIVATE;
ALTER NETWORK POLICY <name> INACTIVATE;

-- Example:
CREATE NETWORK POLICY policy1 ACTIVATE;CREATE NETWORK POLICY policy1 INACTIVATE;
```

* You can choose **Activate** or **Inactivate** in the policy list or details page.
* The impact on other policies after activation or deactivation depends on whether your product allows multiple policies to be active at the same time (some only allow a single policy, so activating a new one automatically replaces the previous one; others allow several policies to be active in parallel).

### 5.5 Delete a Network Policy

**Web Operation**:

In **Management** - **Security** - **Network Policy**, click **Disable** / **Enable** in the **Actions** column for the policy you want to change, to toggle its status.

:-: ![](.topwrite/assets/image_1742472214987.png =791)

**SQL Operation**:

```
DROP NETWORK POLICY <name>;

-- Example:
DROP NETWORK POLICY policy1;
```

* Once deleted, it cannot be restored.

### 5.6 View Network Policies

**Web Operation**:

In **Management** - **Security** - **Network Policy**, you can see all network policies for the current service instance.

:-: ![](.topwrite/assets/image_1742472291079.png =779)

**SQL Operation**:

* **Show all policies**:

  ```
  SHOW NETWORK POLICY;
  ```

  Returned fields include:

  | **Field**     | **Description**                    |
  | ------------- | ---------------------------------- |
  | NAME          | The name of the policy             |
  | CREATOR       | The username of the policy creator |
  | CREATED\_TIME | Format: yyyy-mm-dd hh\:mm\:ss      |
  | STATUS        | active or inactive                 |

* **View details**:

  ```
  sql
  CopyEdit
  DESC NETWORK POLICY <name>;
  ```

  * Returns the policy’s `ALLOWED_IP_LIST` / `BLOCKED_IP_LIST`:

    | **Field**         | **Description**                    |
    | ----------------- | ---------------------------------- |
    | NAME              | The name of the policy             |
    | ALLOWED\_IP\_LIST | The username of the policy creator |
    | BLOCKED\_IP\_LIST | Format: yyyy-mm-dd hh\:mm\:ss      |

### 5.7 Temporary Bypass of Network Policies

* In extreme cases (e.g., a misconfigured allowlist or blocklist blocks all network segments), a user with the instance\_admin role can create a **temporary bypass** so that a specified user is not restricted by network policies for 30 minutes.
* In some products or environments, this feature is implemented by setting a user object attribute `MINS_TO_BYPASS_NETWORK_POLICY`. You may need to contact your administrator or official support to configure it.

***

## 6. Permissions and Security Control

| Privilege code        | Operations                       | Default Role / Permission       |
| --------------------- | -------------------------------- | ------------------------------- |
| create network policy | CREATE                           | Granted only to instance\_admin |
| alter                 | ALTER/RENAME/Activate/Inactivate | Granted only to instance\_admin |
| drop                  | DROP                             | Granted only to instance\_admin |
| read metadata         | SHOW / DESC                      | Granted only to instance\_admin |

***

## 7. Frequently Asked Questions (FAQ)

1. **If the same IP appears in both the allowlist and blocklist, which result takes precedence**?

   * The blocklist takes priority, so access is denied.

2. **If no network policies have been created at all, is access allowed or denied by default**?

   * Access is allowed by default, equivalent to having all IPs in the allowlist.

3. **Why is** \`\` **not permitted in the allowlist or blocklist**?

   * That notation indicates “all IPs.” In an allowlist, it has no practical effect (i.e. fully open), and in a blocklist it would deny all access. If there are no exceptions, nobody can access the service instance.

4. **Can multiple network policies be enabled at the same time for the same instance**?

   * Yes. The system merges the allowlists and blocklists of all active policies and applies the combined result.

5. **How to prevent the instance\_admin from being locked out by a policy**?

   * Before creating or activating a policy, make sure the IP you’re using (visible when you create or modify the policy in the web UI) is in the allowlist. If you are accidentally blocked, an instance\_admin can modify the network policy to restore access to the service instance.

^
