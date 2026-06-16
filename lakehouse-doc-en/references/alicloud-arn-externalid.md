# Obtain ARN and ExternalID

When configuring Private Link to access the Lakehouse network, to ensure that the Lakehouse can normally read the endpoint status within your cloud platform account and enhance the security of this access method, please create an independent access control role within the cloud service platform and authorize and add an external ID. The specific operations are as follows.

## Alibaba Cloud

**How to obtain ARN**:

First, go to the Alibaba Cloud Access Control page (<https://ram.console.aliyun.com/roles>) and click "Create Role", then select the feasible entity type as: Alibaba Cloud Account:


^

Enter a custom role name in the role name field;

In "Select Trusted Cloud Account", choose "Other Cloud Account", and copy the Lakehouse endpoint service's LakehouseUID content and paste it in.


^

After the role is created, click "Authorize Role", and then click "Create Authorization";


^

Search for "privatelink", and check: AliyunPrivateLinkReadOnlyAccess and AliyunPrivatelinkEndpointServiceReadOnlyAccess two policies;


^

After completing "Confirm New Authorization", switch to the "Trust Policy" tab, and click "Edit Trust Policy":


Paste the following content between "Action": "sts:AssumeRole", and "Effect": "Allow":
Sure, here is the translated content:

```
"Condition": {
        "StringEquals": {
          "sts:ExternalId": "Please replace with custom externalID"
        }
After pasting, save the trust policy.

^