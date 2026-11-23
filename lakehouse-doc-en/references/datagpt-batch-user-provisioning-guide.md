# Create Users Through the API

During a proof of concept (POC), creating accounts through the UI is usually sufficient for a small number of users. After launch, integrate the API with internal enterprise systems to provision accounts automatically as needed, centralize management, and reduce manual account creation and maintenance.

## Prerequisites

- Confirm the API endpoint for the current environment and the target tenant’s `tenantId`.
- Prepare a token for calling the user management APIs and pass it in the `x-clickzetta-token` request header.
- Prepare the username, email address, phone number, and password for each user to create. See the API descriptions for field requirements.
- Securely store the `userId` and `appSecretKey` returned by the create API in your enterprise backend. To associate accounts with employee identities, also maintain a mapping between employees and Singdata accounts.

## Procedure

The following steps are performed by enterprise administrators and developers:

> ⚠️ **Note**: Replace `{endpoint}` in the following API requests with the service URL for Alibaba Cloud Singapore:
>
> `https://ap-southeast-1-alicloud.api.singdata.com/clickzetta-campaign-data`

### Step 1: Check Account Status

Read employee identifiers and account information from the provisioning list, check whether each employee already has a corresponding Singdata account, and proceed based on account status:

- **New users**: Create a Singdata account and obtain its user ID and secret key.
- **Existing users**: Reuse the existing account and query the user ID if needed. If the existing key is usable, there is no need to generate another one.

### Step 2: Create or Reuse a Singdata Account

#### New Users: Create a User and Save the Account Mapping

#### Request

```http
POST {endpoint}/api/v1/user/create
Content-Type: application/json
x-clickzetta-token: {token}
```

#### Example Request Body

```json
{
  "email": "sales_beijing@example.com",
  "password": "{initialPassword}",
  "tenantId": 1504,
  "username": "sales_beijing_01",
  "phone": "{employeePhone}"
}
```

#### Request Parameters

| Field | Requirements |
| --- | --- |
| `email` | Required. Enter the user’s email address. |
| `password` | Enter the user’s initial password. |
| `tenantId` | Enter the target tenant ID. |
| `username` | Enter a username of 5–32 characters, starting with a letter and containing only letters, digits, and underscores. |
| `phone` | Required. Enter the user’s phone number. |

#### Example Response

Example response:

```json
{
  "code": "200",
  "message": "Operation successful",
  "data": {
    "userId": 52,
    "appSecretKey": "{appSecretKey}"
  },
  "success": true
}
```

Call the API separately for each user to create. Save successful results and record failures separately. If a request times out or its outcome is unclear, query the user by username before deciding whether to retry, to avoid duplicate account creation.

#### Existing Users: Query the User ID

If a user already has a Singdata account, query the corresponding user ID by username instead of creating another account.

```http
GET {endpoint}/api/v1/user/queryUserId?username={username}
x-clickzetta-token: {token}
```

After a successful query, `data` contains the user’s ID. This API does not return `appSecretKey`. To generate a new key, use the key generation API.

#### Existing Users: Generate a Key as Needed

To obtain a new key for an existing account, call:

```http
POST {endpoint}/api/v1/user/generateSecretKey?username={username}
x-clickzetta-token: {token}
```

> ⚠️ **Note**: A successful response contains `userId` and `appSecretKey` in `data`. Store them in your enterprise backend. The old key remains valid after a new key is generated, so this operation does not revoke the old key. To disable old credentials, separately confirm the revocation methods supported by your environment.

### Step 3: Configure Account Permissions

Creating a user does not automatically grant all required business permissions. Check user roles, the target analysis domain, resources within the domain, and row-level permissions separately. Adding a user to an analysis domain grants domain access only; it does not replace role or row-level permission configuration.

Grant the required permissions to new users. For existing users, review their current permissions and add or adjust only those needed for this integration.

### Step 4: Verify Access and Enable the Entry Point

Test the embedded analytics page with selected users. Confirm that they can access the target analysis domain and that Q&A results match their respective data scopes before enabling the entry point. See “Verify the Results” below for specific checks.

## Verify the Results

Check each employee’s Singdata user ID, account mapping, and processing status in the enterprise backend’s provisioning records. You can also verify user IDs through the user query API. Then open the embedded page as these users and check the following:


- Each employee has the correct Singdata account mapping, and rerunning the provisioning task does not create duplicate accounts for employees already mapped.
- Failed entries can be handled separately, and keys for successful entries are stored securely.
- Employees can access the target analysis domain without additional administrative privileges.
- When employees ask the same question, each employee’s results stay within their authorized data scope.

## Related Documentation

- [Embed Analytics Agent in Internal Applications](datagpt-embed-internal-app-guide.md)
- [Integrate Row-Level Permissions Through the API](datagpt-api-row-level-permission-guide.md)
- [Manage Permissions](datagpt-permission-management-guide.md)
- [Configure Role Authorization](datagpt-role-authorization-guide.md)
