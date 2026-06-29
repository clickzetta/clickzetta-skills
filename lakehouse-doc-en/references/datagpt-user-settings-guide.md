# Change Logo, Theme, and Chart Colors

User settings allow you to view current account information and adjust the Logo, theme color, chart color scheme, sample analytics domain, and dataset auto-analysis preferences for Analytics Agent. This entry is not in the left "Administration" menu — it is in the avatar menu at the lower left, which is why many users overlook it.

## Accessing User Settings

Click the current user avatar or username at the lower left of the page to open the user menu.

The menu includes:

| Menu Item | Description |
| --- | --- |
| Account Home | Go to the account home page. |
| Settings | Go to the user settings page. |
| Log Out | Log out of the current account. |

After clicking "Settings", the user settings page opens. In practice, the page URL format is:

```text
/dataai/userInfo
```

## Viewing Account Information

The top of the user settings page shows basic information about the current account:

| Information | Description |
| --- | --- |
| Name | Current user display name. |
| Account | Current login account. |
| Phone Number | Phone number bound to the account. |
| Tenant ID | Current tenant ID. |
| User ID | Current user ID. |

When users report "cannot see a certain analytics domain" or "permissions don't match expectations", first confirm the current login account here before troubleshooting roles, analytics domain membership, and resource permissions.

## Analytics Domain Settings

The page includes an "Analytics Domain Settings" section. In practice, the available action is:

```text
Reset Sample Analytics Domain
```

After clicking, a confirmation prompt appears:

```text
Resetting the sample will restore sample data to its initial state. Are you sure?
```

This operation restores sample data and is suitable for use after a demonstration, training, or sample environment has been modified. Do not use it as a regular refresh button in a real business analytics domain; before executing, confirm the current environment is indeed a sample environment, and verify that it won't affect other users currently using the sample domain.

## System Settings

The user settings page also includes a "System Settings" section. By default it is read-only; click "Edit" to modify it. Bottom actions are:

- Cancel
- Save

Clicking "Cancel" discards current edits; clicking "Save" submits the changes.

In practice, configurable items include:

| Configuration Item | Description |
| --- | --- |
| Logo | Supports filling in combination mark SVG and graphic mark SVG to adjust brand identity in the interface. |
| Theme Color | Supports selecting the interface theme color. In practice, dropdown options include "Blue" and "Orange". |
| Chart Color Scheme Prompt | Controls the color tendency and visual style when charts are generated. |
| Enable Dataset Auto Analysis | Controls whether to enable dataset auto analysis. Can be toggled on or off in edit mode. |

## Chart Color Scheme Prompt

The "Chart Color Scheme Prompt" affects the color and style choices Analytics Agent makes when generating charts. Default content is similar to:

```text
Use blue (#1890ff) as the primary color, complemented by green (#52c41a), orange (#faad14), red (#f5222d), purple (#722ed1), cyan (#13c2c2), pink (#eb2f96), dark orange (#fa8c16), lime (#a0d911), and indigo (#2f54eb) as secondary colors. The overall style should be modern, clean, and suitable for business scenarios.
```

If your enterprise or team wants charts to conform to a unified visual standard, you can adjust color requirements here. For example:

- Match the primary color to enterprise brand colors.
- Avoid colors that conflict with business meanings.
- Have positive, negative, and warning indicators use stable colors.
- Keep the chart style business-like, clean, and suitable for dashboard display.

It is recommended to write only color and style requirements here. Do not write metric definitions, field explanations, or business rules here — those should be configured in metrics, field semantics, knowledge, or answer builders.

## Enable Dataset Auto Analysis

"Enable Dataset Auto Analysis" is a toggle. In practice, it is confirmed to be off by default in the current environment; after clicking "Edit" it can be switched on.

Based on the feature name, it controls whether the system automatically analyzes datasets. Suitable to enable when you want the system to more proactively understand datasets, generate supplementary analysis content, or improve data preparation efficiency.

Before enabling, confirm:

- Whether datasets are ready and do not contain obvious errors or temporary test data.
- Whether you want the system to automatically trigger dataset-related analysis.
- Whether there are maintainers monitoring the results of auto-analysis or background task status.
- If import or parsing fails, whether it will be troubleshot through notifications.

If you are only temporarily uploading test data, or have not completed field semantics, metrics, and knowledge configuration, keep it off for now and enable it after data and semantic layers are stable.

## When to Use User Settings

Common scenarios include:

| Scenario | Recommended Action |
| --- | --- |
| Not sure of current login account | Check name, account, phone number, tenant ID, and user ID. |
| Training sample domain has been modified | Use "Reset Sample Analytics Domain", but confirm the confirmation prompt. |
| Generated chart colors don't match team standards | Modify theme color or chart color scheme prompt. |
| Want system to auto-understand datasets | Evaluate, then enable "Dataset Auto Analysis". |
| Changes don't match expectations | Return to the settings page to re-edit, or cancel unsaved changes. |

## Difference from Other Configurations

User settings are not analytics domain configuration, nor are they role authorization.

| Configuration | Primary Purpose |
| --- | --- |
| User Settings | Adjust the current user's or current environment's Logo, theme color, sample domain, chart preferences, and dataset auto-analysis toggle. |
| Analytics Domain Configuration | Determines which tables, files, knowledge, metrics, and answer builders the current domain can use. |
| Field Semantic Configuration | Helps the system understand field meanings and reduce field misselection. |
| Model Configuration | Determines which model the system calls and related model call settings. |
| Role Authorization | Determines which features and resources users can access. |

If Q&A results are inaccurate, user settings should not be the first place to check. First check analytics domain, field semantics, metrics, knowledge, answer builders, and permission configuration. User settings are more suitable for account confirmation, sample recovery, interface branding, chart style, and dataset auto-analysis preferences.

## Related Documentation

- [Analyst Guide](datagpt-analyst-guide.md)
- [Notifications](datagpt-notification-guide.md)
- [Configure Analytics Domain](datagpt-domain-management-guide.md)
- [Configure Field Semantics](datagpt-field-semantic-config-guide.md)
- [Metrics and Answer Builder](metrics_answer_build.md)
- [Model Selection and Configuration](datagpt-model-config.md)
