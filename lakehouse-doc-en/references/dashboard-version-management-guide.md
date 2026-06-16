# Dashboard Version Management - User Guide

## **Feature Overview**

When using Analytics Agent, users often iterate on dashboard charts through ASK AI conversations. However, after multiple rounds of modifications, charts may deviate from expectations. Previously, the only option was to describe requirements again and have the Agent redo the work.

Now, the system automatically saves a version each time AI modifies a dashboard chart. Users can view historical versions at any time and restore with one click, completely solving the problem of "can't go back after making bad changes."

## Core Value

* **Recover from mistakes**: Not satisfied after multiple iterations? Restore to a previously satisfactory version with one click

* **Explore with confidence**: No need to worry about losing the current effect; freely try new analytical perspectives

* **Traceable collaboration**: Modifications on shared dashboards are recorded, so you know who changed what and when

## How to Use

### 1. Open the Version Panel

Click the **Version History** button in the upper right corner of the dashboard page

:-: ![](/.topwrite/assets/image_1780902105757.png =527)

### 2. View Historical Versions

Each version card in the version panel contains:

:-: ![](/.topwrite/assets/image_1780902136018.png =366)

* Version number (V1, V2, V3...)

* Modifier's avatar and name

* Modification time

* Change detail description

### 3. Preview Historical Versions

Click on a version card to view a snapshot of the dashboard at that version (read-only, not editable).

### 4. Restore a Historical Version

Hover over a version card and click the **Restore** button:

:-: ![](/.topwrite/assets/image_1780902285772.png =558)

* The system will show a confirmation prompt: "The rollback operation will create a new version based on this version"

* After clicking **Confirm**, the system will create a new version based on the selected historical version (e.g., restoring from V3 will generate V7 with the note "This version is derived from V3")

* Existing version records will not be lost

## Version Generation Rules

### What operations automatically generate versions?

* Modifying dashboard charts through ASK AI conversations (adding, modifying, or deleting charts)

### What operations do NOT generate versions?

* Pure text conversations (no chart changes produced)

### Version Retention Limit

* The system retains up to 100 recent versions

* Early versions exceeding the limit will be marked as "Expired"

## Dashboard Visibility and Version Permissions

### Private Dashboard

* All versions are visible only to the creator

### Shared Dashboard

* All versions are visible to users within the same tenant

### Private to Shared Transition

:-: ![](/.topwrite/assets/image_1780902352447.png =704)

* Versions before the sharing time point are visible only to the creator

* Versions created after sharing are visible to all users

* The version panel displays a divider at the sharing time point, marked "Dashboard was converted to shared at XX time. Versions below are visible only to you."

### Example Scenario

1\. User A creates a private dashboard, generating V1 through V3

2\. At V4, converts the dashboard to shared

3\. V5 is modified by User B, V6 is modified by User A

4\. User B opens version history: can only see V4, V5, V6 (V1 through V3 are not visible)

5\. User A opens version history: can see all V1 through V6

## Notes

1\. Only chart changes produced through ASK AI conversations automatically generate versions; manual drag-and-drop editing does not trigger version creation

2\. Restoring does not delete intermediate versions; instead, it creates a new version based on the target version

3\. The version retention limit is 100; it is recommended to periodically confirm the status of important versions

## Related Documentation

* [Chart Auto-Refresh Settings](chart-auto-refresh-guide.md) — Set automatic data updates for dashboard charts
* [Table Rendering](table_rendering.md) — Generate complex table layouts through natural language
* [Conversational Data Analytics (Analytics Agent)](datagpt_introduction.md) — Return to feature overview

^
