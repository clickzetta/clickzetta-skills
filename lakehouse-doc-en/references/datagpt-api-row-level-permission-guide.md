# Integrate Row-Level Permissions Through the API

When an enterprise provides a shared analytics entry point for multiple departments in an internal system, employees typically need to query only the data they are responsible for. Row-level permissions control which rows a user can view in the same table based on their data access permissions.

## When to Use This Integration

Reuse existing employee data scopes in the integration process to reduce repetitive maintenance of individual users’ data access scopes.

## Prerequisites

- Prepare a Singdata account and its `appSecretKey` for embedded access. Multiple enterprise users can share one Singdata account while the enterprise backend passes separate row-level permission rules for each user. Alternatively, users can use their respective Singdata accounts.
- Confirm the Singdata account’s `userId` and the target analysis domain’s `domainId`, and prepare the token required to call the user management APIs.
- Identify the target tables and columns to filter, and the authorized data scope for each enterprise user.
- Define a permission point under **Management → User Management → Row-Level Permissions**, configure its target tables and columns, and record its name.

Store `appSecretKey` in your enterprise backend and use it to obtain access tokens for the corresponding user. Do not include it in frontend code.

## Procedure

The following steps are performed by enterprise administrators and developers:

> ⚠️ **Note**: Replace `{endpoint}` in the following API requests with the service URL for Alibaba Cloud Singapore:
> `https://ap-southeast-1-alicloud.api.singdata.com/clickzetta-campaign-data`

### Step 1: Add Users to the Analysis Domain

Users must have access to the target analysis domain before using its analytics features. Call the following API to grant access to users who do not yet have it. Users with existing access can skip this step.

#### Request

```http
POST {endpoint}/domian/batchAddDomainPermission
Content-Type: application/json
x-clickzetta-token: {token}
```

Example Request Body:

```json
{
  "domainId": "174",
  "targetUserIds": [45],
  "userId": 1,
  "tenantId": 1504
}
```

#### Request Parameters

<table style="width: 100%;">
  <colgroup><col style="width: 25%;"><col style="width: 75%;"></colgroup>
  <thead><tr><th>Field</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td style="white-space: nowrap;"><code>domainId</code></td><td>ID of the target analysis domain to grant access to</td></tr>
    <tr><td style="white-space: nowrap;"><code>targetUserIds</code></td><td>List of user IDs to add to the analysis domain, obtained through the user creation or query API</td></tr>
    <tr><td style="white-space: nowrap;"><code>userId</code></td><td>User ID</td></tr>
    <tr><td style="white-space: nowrap;"><code>tenantId</code></td><td>Target tenant ID</td></tr>
  </tbody>
</table>

#### Example Response

Example response:

```json
{
  "code": "204",
  "message": "Operation successful",
  "data": null,
  "success": false
}
```

### Step 2: Generate a Token with Row-Level Permission Rules

The enterprise backend accepts requests only from signed-in users, reads the current user’s authorized data scope, constructs row-level permission rules, and calls the following API. The resulting data permissions are bound to the generated token.

When multiple enterprise users share a Singdata account, use the same `appSecretKey` and generate a separate token for each user with that user’s corresponding rules.

#### Configure Permission Points

Define a permission point under **Management → User Management → Row-Level Permissions** and select the target tables and columns for row-level filtering. The request’s `name` must match the permission point name.

All table columns mapped to the same permission point use the same filter values. For example, after mapping a permission point named “Subsidiary” to the company columns in the relevant tables, pass the list of companies the current user can access when generating a token.

#### Request

```http
POST {endpoint}/open/api/v1/appSecretKey/generateAuthTokenPlus
Content-Type: application/json
```

#### Example Request Body

```json
{
  "appSecretKey": "{appSecretKey}",
  "rowLevelRule": {
    "mode": "SIMPLE",
    "ruleItems": [
      {
        "name": "Subsidiary",
        "value": ["Company A", "Company B"]
      }
    ]
  }
}
```

This example passes “Company A” and “Company B” as filter values for the current user’s “Subsidiary” permission point. Before calling the API, define a permission point with exactly this name and configure its target tables and columns.

#### Request Parameters

| Field | Type | Description |
| --- | --- | --- |
| `appSecretKey` | String | Application secret key for the Singdata account, stored in the enterprise backend and used to generate tokens |
| `rowLevelRule` | Object | Row-level permission rules bound to the token being generated |
| `rowLevelRule.mode` | String | Must be `SIMPLE` |
| `rowLevelRule.ruleItems` | Array | List of row-level permission rules |
| `ruleItems[].name` | String | Name of a defined row-level permission point |
| `ruleItems[].value` | Array | List of filter values for the permission point |

#### Use an Expression to Specify the Filter Scope

To determine filter values through a query, set `valueType` to `EXPRESSION` in the rule item and specify the expression in `value`. For example:

```json
{
  "appSecretKey": "{appSecretKey}",
  "rowLevelRule": {
    "mode": "SIMPLE",
    "ruleItems": [
      {
        "name": "bu_filter",
        "value": ["SELECT bu FROM ns1504.public.bu_alias WHERE region = 'HUA_DONG'"],
        "valueType": "EXPRESSION"
      }
    ]
  }
}
```

Replace `bu_filter` with the configured permission point name and adjust the query to match your tables and columns. Generate both permission rules and expressions in the enterprise backend using trusted user information.

#### Example Response

Example response:

```json
{
  "code": "200",
  "message": "Operation successful",
  "data": {
    "token": "{accessToken}",
    "tenantId": "107",
    "userId": 85,
    "expireMillisecond": "1755833277044"
  },
  "success": true
}
```

### Step 3: Load the Embedded Page

Return the generated user token to the frontend and load the embedded page using the `X-ClickZetta-Token` parameter. To open the target analysis domain’s conversation page directly, use the `/dataai/dataGPT/new` path and pass the `domainId` for that same target domain.


## Verify the Results

Access the target analysis domain with employee accounts that have different data scopes and verify the following:

- Users can access the target analysis domain, and the account and `domainId` used by the page match the authorization.
- Questions without filter conditions still return only data within the employee’s authorized scope.
- Questions about other regions or all data remain subject to row-level permissions.
- Charts, details, and any enabled downloads use the same data scope.

When an employee’s role or data scope changes, update the enterprise authorization mapping and verify that the permissions take effect using the credential refresh mechanism supported by your environment.

## Related Documentation

- [Embed Analytics Agent in Internal Applications](datagpt-embed-internal-app-guide.md)
- [Create Users Through the API](datagpt-batch-user-provisioning-guide.md)
- [Configure Row-Level Permissions](datagpt-row-level-permission-guide.md)
- [Manage Domain Resource Permissions](datagpt-domain-resource-permission-guide.md)
- [Bulk Download and Data Export Governance](datagpt-data-export-governance-guide.md)
