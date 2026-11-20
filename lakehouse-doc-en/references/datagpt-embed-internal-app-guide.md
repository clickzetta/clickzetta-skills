# Embed Analytics Agent in Internal Applications

Embed Analytics Agent in your enterprise software portal to quickly provide data Q&A and analytics. Users can ask questions and view results within a familiar portal without switching to the Singdata platform or signing in separately.

Reuse the existing analytics interface through an `iframe` to reduce development effort.

![Analytics Agent embedded in an internal enterprise application](.topwrite/assets/internal-app-workspace.png)

Embedding example: the menu on the left belongs to the enterprise application, and the panel on the right displays the embedded analytics page.

## Prerequisites

Enterprise administrators and developers should complete the following preparations:

- Configure usable analysis domains, data resources, and business definitions on the Singdata platform.
- Obtain the embedded page URL and API endpoint for the target environment. These addresses may differ.
- Generate and securely store an `appSecretKey` for the Singdata account used for integration, and grant the required roles and analysis domain access.
- If row-level permissions are required, define the data each user can access and prepare the permission rules to pass when generating tokens.
- To open the conversation page for a specific analysis domain directly, obtain its `domainId`.

## Procedure

The following steps are performed by enterprise administrators and developers:

> ⚠️ **Note**: Replace `{endpoint}` in the following API requests with the service URL for Alibaba Cloud Singapore:
>
> `https://ap-southeast-1-alicloud.api.singdata.com/clickzetta-campaign-data`

### Step 1: Obtain an appSecretKey and Provide a Credential Endpoint

Sign in to the Singdata platform with an administrator account. On the user management page, create a user for embedded access, assign the required roles and analysis domain permissions, and generate an `appSecretKey` for that user. Store the `appSecretKey` securely in your enterprise backend. Provide a credential endpoint that only signed-in employees can call. The backend uses the current employee’s identity to look up the corresponding Singdata user’s `appSecretKey` and obtain the token required by the frontend to access the analytics page.

![Generate and copy an appSecretKey on the user management page](.topwrite/assets/app-secret-key-generation.png)

### Step 2: Obtain a Token in the Enterprise Backend

#### Request

```http
GET {endpoint}/open/api/v1/appSecretKey/generateAuthToken?appSecretKey={appSecretKey}
```

#### Example Response

Example response:

```json
{
  "code": "200",
  "message": "Operation successful",
  "data": {
    "token": "{token}",
    "tenantId": "1504",
    "userId": 1,
    "expireMillisecond": "1721974345031"
  },
  "success": true
}
```

> ⚠️ **Note**: Store `appSecretKey` only in your enterprise backend, never in frontend code. The backend must determine the Singdata identity from the currently signed-in employee and must not directly trust another user ID submitted by the frontend.

### Step 3: Load the Page in the Enterprise Frontend

The following example shows the URL structure for opening a specific analysis domain’s conversation page directly. Replace the page domain, analysis domain ID, and access token with your actual configuration or backend response values. URL-encode parameter values when constructing the URL.

```html
<iframe
  title="AI Data Analytics"
  sandbox="allow-scripts allow-same-origin allow-downloads allow-popups"
  src="https://{pageDomain}/dataai/dataGPT/new?domainId={domainId}&X-ClickZetta-Token={token}&lang=en-US"
  style="width: 100%; height: 100vh; border: 0;"
></iframe>
```

#### Page Paths

| Path | Description |
| --- | --- |
| `/dataai/dataGPT` | Open the standard DataGPT page |
| `/dataai/dataGPT/new` | Use with `domainId` to open a specific analysis domain’s conversation page directly |

#### Request Parameters

<div style="overflow-x:auto;">
<table style="width:100%; table-layout:auto;">
<thead>
<tr>
<th style="white-space:nowrap; padding:12px 16px;">Parameter</th>
<th style="white-space:nowrap; padding:12px 16px;">Location</th>
<th style="white-space:nowrap; padding:12px 16px;">Type</th>
<th style="white-space:nowrap; padding:12px 16px;">Required</th>
<th style="width:100%; min-width:240px; padding:12px 16px;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;"><code>domainId</code></td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">Query</td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">String</td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">Conditional</td>
<td style="vertical-align:top; padding:12px 16px; overflow-wrap:break-word;">Required when opening a specific analysis domain’s conversation page directly. Enter the analysis domain ID obtained earlier.</td>
</tr>
<tr>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;"><code>X-ClickZetta-Token</code></td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">Query</td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">String</td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">Yes</td>
<td style="vertical-align:top; padding:12px 16px; overflow-wrap:break-word;">Pass the access token obtained by your enterprise backend.</td>
</tr>
<tr>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;"><code>lang</code></td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">Query</td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">String</td>
<td style="white-space:nowrap; vertical-align:top; padding:12px 16px;">No</td>
<td style="vertical-align:top; padding:12px 16px; overflow-wrap:break-word;">Use <code>zh-CN</code> or <code>en-US</code> to specify the page language.</td>
</tr>
</tbody>
</table>
</div>

For direct access to a specific domain, keep `domainId` valid. Deleting the corresponding analysis domain affects this entry point.

> ⚠️ **Note**: Mobile devices use a separate page URL:
>
> `https://datagpt-mobile-app.singdata.com/login?X-ClickZetta-Token={token}`

### Step 4: Configure the Enterprise Application Entry Point

Add an analytics menu item to your enterprise application and link it to the page containing the `iframe`. Size the page to fit your application layout, specify the language with `lang`, and configure the iframe’s download and pop-up capabilities as needed.

## Verify the Results

After signing in to the enterprise system, employees open the page from the analytics menu, enter business questions in the Q&A box, and view the results. Verify the integration against the following criteria:

- Signed-in employees can open the analytics page from the internal menu. After signing out of the enterprise system, they can no longer obtain new credentials from the enterprise backend.
- Employees use their corresponding Singdata identities and can access their authorized analysis domains.
- Questions submitted as a restricted employee return only data within that employee’s authorized scope. Specifying another region does not bypass these restrictions.

## Related Documentation

- [Configure Analysis Domains](datagpt-domain-management-guide.md)
- [Manage Permissions](datagpt-permission-management-guide.md)
- [Create Users Through the API](datagpt-batch-user-provisioning-guide.md)
