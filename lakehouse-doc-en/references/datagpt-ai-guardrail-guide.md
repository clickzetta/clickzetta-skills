# AI Guardrail

AI Guardrail checks user input, final output, external content, and tool results in Analytics Agent against safety policies to help identify and handle risky content.

> ⚠️ **Note**: Configure the guardrail connection and enable the feature before use. Protection depends on the guardrail version, execution policy, and content being checked.

## When to Use It

- **Validate protection before launch**: Confirm that normal business questions are allowed and risky content, such as instructions to ignore safety rules or disclose confidential information, is blocked.
- **Check content at different stages**: Validate user input, final output, external content, and tool results to cover content sources beyond the original question.
- **Recheck after policy changes**: Rerun the same test cases to confirm that protection meets your team's requirements without disrupting normal business Q&A.

## Before You Begin

1. Sign in to Analytics Agent with an account that can access **Management → AI Guardrail**.
2. Confirm that the Amazon Bedrock Guardrails connection is configured. Check the **AWS region**, **Guardrail ARN**, and **Guardrail version**, and confirm that **AI Guardrail** is **Enabled**. If the connection is not configured, contact the administrator responsible for guardrail integration.
3. Under **Execution policy**, review the stages to check so that the content types you validate match your requirements.
4. Define the expected handling of normal and risky content. Before running tests, review each case's **Check type** and **Expected** result to identify what should be allowed or blocked.

## Procedure

### Step 1: Open AI Guardrail

In the left navigation, open **Management → AI Guardrail**.

### Step 2: Review the Connection

Open **Connection** and review the connection settings and enabled status. To change an existing connection, click **Edit**.

![](assets/ai-guardrail-access-config.png)

| Setting or status | Description |
| --- | --- |
| Name | The connected guardrail service. |
| AWS region | The AWS Region where the guardrail is located. It must match the target guardrail's Region. |
| Guardrail ARN | The resource identifier of the guardrail to use. It determines which set of safety rules checks the content. |
| Guardrail version | The guardrail version to call. It determines which version of the rules is used for the check. |
| AI Guardrail | The feature's enabled status. Confirm that it shows **Enabled**. |

### Step 3: Configure Checkpoints

Open **Execution policy** and select the checkpoints to enable during Q&A. You can combine the four checkpoints as needed to determine what content is checked and at which stage. Each time an enabled checkpoint is triggered, the system sends the current content at that stage to the AWS `ApplyGuardrail` API for a check.

<table style="width:100%; table-layout:auto;">
<thead><tr>
<th style="width:18%; min-width:125px; word-break:normal; overflow-wrap:normal;">Checkpoint</th>
<th style="width:32%;">When and what it checks</th>
<th style="width:50%;">Purpose and limitations</th>
</tr></thead>
<tbody>
<tr>
<td style="vertical-align:top; word-break:normal; overflow-wrap:normal;">User input</td>
<td style="vertical-align:top; overflow-wrap:break-word;">Checks the current user input text before the Agent runs.</td>
<td style="vertical-align:top; overflow-wrap:break-word;">Identifies risky questions or instructions that attempt to bypass rules before processing begins. With <strong>Block on match</strong> enabled, matching content is stopped at the entry point.</td>
</tr>
<tr>
<td style="vertical-align:top; word-break:normal; overflow-wrap:normal;">Final output</td>
<td style="vertical-align:top; overflow-wrap:break-word;">Checks the Agent&#x27;s final answer before delivery.</td>
<td style="vertical-align:top; overflow-wrap:break-word;">Checks content before it is shown to you. When enabled, the final answer is displayed after the check passes or handling under the policy is complete. Tool progress messages and attachments are excluded.</td>
</tr>
<tr>
<td style="vertical-align:top; word-break:normal; overflow-wrap:normal;">External content</td>
<td style="vertical-align:top; overflow-wrap:break-word;">Checks added context and text retrieved from knowledge bases or the web before the model uses it.</td>
<td style="vertical-align:top; overflow-wrap:break-word;">Reduces the risk of unsafe content or prompt injection from external sources entering the model&#x27;s context.</td>
</tr>
<tr>
<td style="vertical-align:top; word-break:normal; overflow-wrap:normal;">Tool results</td>
<td style="vertical-align:top; overflow-wrap:break-word;">Checks tool results before the model uses them.</td>
<td style="vertical-align:top; overflow-wrap:break-word;">Prevents unsafe tool results from being used to generate answers. Operations already performed by tools cannot be undone.</td>
</tr>
</tbody>
</table>

Set **Block on match** to determine how policy matches are handled. Enable it to stop the request or answer delivery at the corresponding stage, or disable it to record matches and continue. Click **Save policy** when finished.

> ⚠️ **Note**: Failed safety checks stop the request regardless of the **Block on match** setting. Each check adds an AWS call and increases Q&A latency. User input and final output checks require separate calls.

### Step 4: Review Protection Results and Records

Use **Protection test** to validate test cases and **Audit logs** to review protection records from actual Q&A.

- **Protection test**: Click **Run all** or **Run** for an individual case. Compare the expected and detected results to see whether they match. Click **Retry** to run a completed case again.
- **Audit logs**: Filter by time, user, entry point, handling result, or check type. Review the original question, check stage, and handling result. Expand a record to see details such as the guardrail version, session ID, and duration.

> ⚠️ **Note**: **Run all** reruns cases that already have results. To compare results before and after a policy change, record the current results before rerunning the tests. Protection tests show results for test cases; review audit logs to confirm how actual Q&A was handled.

## FAQ

### Why do some test cases differ from expectations when the feature is enabled?

**Enabled** means that protection is active, not that every case will produce the expected result. Review the case's check type and expected result, then check the guardrail version and execution policy. Have the person responsible for the policy review any mismatches, and rerun the tests.

### Does Completed mean that a test passed?

No. **Completed** means that execution has finished. Check the **Verdict** to see whether the result meets expectations. If a case is expected to be blocked but is allowed, the mismatch still needs attention even though execution is complete.

### How do I rerun a single test case?

Find the case under **Protection test** and click **Retry** in that row. Use the content search or verdict filter to narrow the list.

### What should I do if a normal business question is blocked?

Record the test content, check type, expected result, and detected result, and ask the person responsible for the safety policy to review them. After an adjustment, rerun that case and recheck risky cases to confirm that normal business Q&A works and protection requirements are still met.

### Can AI Guardrail replace data permissions?

No. AI Guardrail checks whether content complies with safety policies. Role authorization, analytics domain resource permissions, and row-level permissions control access to features, resources, and data scopes. These permissions must still be configured before using the Agent.

## Related Documents

- [Connect to AWS Guardrails](aws-guardrail-configuration.md): Create AWS guardrail rules, publish a version, and configure the connection.
- [Governance Overview](datagpt-governance-overview.md): Understand the roles of permissions, data scopes, and auditing in governance.
- [Permission Management](datagpt-permission-management-guide.md): Find the configuration entry points and understand the differences between account, role, domain, and row-level permissions.
- [Configure Role Authorization](datagpt-role-authorization-guide.md): Set feature permissions and resource viewing and editing permissions for different roles.
- [Configure Row-Level Permissions](datagpt-row-level-permission-guide.md): Restrict which data rows each person can view, such as by region or store.
- [Managing Analytics Domain Resource Permissions](datagpt-domain-resource-permission-guide.md): Understand access boundaries for tables, files, knowledge, metrics, and other resources within an analytics domain.
