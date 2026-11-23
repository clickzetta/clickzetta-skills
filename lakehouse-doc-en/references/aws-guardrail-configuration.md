# Connect to AWS Guardrails

Create an Amazon Bedrock guardrail and access credentials in AWS, then configure the connection under **Management → AI Guardrail → Connection** in Analytics Agent.

## Step 1 Create a Guardrail

1. Open **Amazon Bedrock** and select the AWS Region you want to use.
2. Go to **Guardrails**, create a guardrail, and configure the filters you need, such as denied topics, word filters, or sensitive information filters.
3. Save the guardrail and note its **region and guardrail ARN**.

![Guardrail filter configuration](assets/datagpt-aws-guardrail-rules-en.png)

## Step 2 Publish and Test a Version

1. Open the guardrail's details page. In the **Versions** section, click **Create version**.
2. Enter a description and confirm creation. Note the published version number, such as `1`.
3. In the **Test** panel, select the published version instead of **Working draft**. Choose a test method appropriate for your guardrail rules, and configure a model if needed.
4. Test with both allowed content and content that should be blocked. Confirm that the results match your rules before connecting the guardrail in the product.

![Create a published guardrail version](assets/datagpt-aws-guardrail-publish-version-en.png)

> **Note**: Creating a guardrail saves a working draft. Create a published version before proceeding, and use that version number in the product.

## Step 3 Grant Permission to Use the Guardrail

Create a dedicated IAM user with access to the guardrail. On the user's **Permissions** tab, create an inline policy and switch to the **JSON** editor. Enter the following policy, replace the `Resource` value with your guardrail's ARN, and save.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:ApplyGuardrail",
      "Resource": "arn:aws:bedrock:ap-southeast-2:123456789012:guardrail/abc123"
    }
  ]
}
```

![IAM policy editor](assets/datagpt-aws-guardrail-policy-editor-redacted.png)

After saving, check the user's **Permissions** tab to confirm that the policy has been added.

![IAM user permissions](assets/datagpt-aws-guardrail-user-permissions.jpeg)

> **Tip**: `2012-10-17` is the IAM policy language version. In the product's **Guardrail version** field, enter the guardrail version number, such as `1`.

## Step 4 Create Access Keys

Open the IAM user's **Security credentials → Access keys → Create access key**. Complete the process and save the AK and SK.

> ⚠️ **Note**: You can view or download the SK only when you create the access key. If you lose it, create a new access key. Use a dedicated IAM user rather than root user credentials.

## Step 5 Connect in the Product

1. In Analytics Agent, expand **Management**, select **AI Guardrail**, and open the **Connection** tab.
2. Configure the connection with your **Access Key ID (AK)**, **Secret Access Key (SK)**, **AWS region**, **Guardrail ARN**, and published **Guardrail version** (for example, `1`).
3. Test the connection and save the configuration.
4. Use the table below to check your connection settings and the status shown on the **Connection** tab:

![AI Guardrail connection details](assets/datagpt-aws-guardrail-connection-en.png)

| Item | Expected Value | Description and Where to Find It |
| --- | --- | --- |
| Name | Amazon Bedrock Guardrails | The guardrail service shown on the **Connection** tab. |
| Access Key ID (AK) | The access key ID of your dedicated IAM user. | Create it under **IAM → Users → Select your user → Security credentials → Create access key** (Step 4). |
| Secret Access Key (SK) | The secret access key paired with the AK. | Save it when you create the access key in Step 4. You can view or download it only at creation; if you lose it, create a new access key. |
| AWS region | The region code for your guardrail, such as `ap-southeast-2`. | Use the AWS Region selected when creating the guardrail in Step 1. |
| Guardrail ARN | The full ARN of your guardrail. | Copy it from the guardrail's details page under **Amazon Bedrock → Guardrails** (Step 1). |
| Guardrail version | The published version number, such as `1`. | Use the version created under **Versions → Create version** in Step 2, rather than the working draft. |
| AI Guardrail | **Enabled** when protection is enabled. | Check the protection status on the **Connection** tab. |

Use **Edit** to update the connection settings. Check the **Execution policy** tab to configure input and/or output checks, then use **Protection test** to verify allowed and blocked content.

> ⚠️ **Note**: The region, ARN, and version must refer to the same guardrail. After updating the filters, publish a new version and update the version number in the product.

In an API response, `HTTP 200` indicates a successful request, while `GUARDRAIL_INTERVENED` indicates that the guardrail detected matching content and took action.

> 💡 **Tip**: In Analytics Agent, go to **Management → AI Guardrail → Audit logs** to review guardrail check records and their handling results. Filter records by date, user, entry point, handling result, or check scope. Click the **+** icon next to a record to view its details.

![AI Guardrail audit logs](assets/datagpt-aws-guardrail-audit-logs-en-v2.png)

If the connection fails, check that the AK and SK are a matching pair, the IAM permissions are correct, and the region, ARN, and version are consistent.

## Related Documentation

- [AI Guardrail](datagpt-ai-guardrail-guide.md) — The AWS setup in this guide is specifically for the AI Guardrail feature in Analytics Agent. See this document to configure checkpoints, test protection, and review audit logs.
- [Configuration Guide](datagpt_tutorial.md) — Follow the setup workflow for data sources, models, analysis domains, and the semantic layer, with links to operations and governance guides.
- [Model Selection and Configuration](datagpt-model-config.md) — Configure the models available to your team and learn how to switch models in a conversation.
- [Analytics Agent Permission Management](datagpt-permission-management-guide.md) — Configure accounts, roles, analysis domain access, and row-level permissions to control access to features and data.
