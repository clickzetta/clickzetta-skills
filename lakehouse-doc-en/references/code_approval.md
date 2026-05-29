When configuring a workspace, you can enable the "Mandatory Code Review" feature toggle to determine whether code submissions in the current workspace require review. Only code that has passed review can be published to the production environment.

## Prerequisites

Only users with the workspace administrator (workspace_admin) role can enable or disable the mandatory code review process.

## Steps

**1. Enable Code Review**

* Enable the code review process when creating a new workspace.
* For existing workspaces -> Click to enter the details page -> Edit, and enable the code review feature.
  ![](/.topwrite/assets/image_1775099278363.png)

**2. Configure the Code Review Approval Flow**

Click Approval -> Approval Flow -> Select the code review flow for the target workspace

Under "Approval", configure the approval roles/users for the code review flow. These roles/users will be the personnel who need to participate in code review when code is submitted in the current workspace.

> Only roles with development permissions can perform approvals
  ![](/.topwrite/assets/image_1775099287191.png)

**3. Submit Code for Review**

After enabling mandatory code review, any submission action will trigger a "Code Review" approval ticket. Once the approver approves, the code will be published to the production environment. If the approver rejects it, you need to modify and resubmit.
  ![](/.topwrite/assets/image_1775099296124.png)

**4. Approval**

After code submission, the approver needs to review it.

Click Approval -> Under the Approval tab, find the target task and perform the relevant actions.
  ![](/.topwrite/assets/image_1775099305006.png)
