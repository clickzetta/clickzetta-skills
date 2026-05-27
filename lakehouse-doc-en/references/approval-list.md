# Approving Work Orders

Based on the approval flow settings for each resource, as an object permission owner, workspace or catalog owner, or instance administrator, you may receive relevant permission approval notifications and need to approve work orders. This document describes how to manually approve work orders.

## Constraints and Limitations

* Only the approvers designated as approval nodes in the approval flow can approve work orders.
* Only instance administrators can access and modify approval flows.

## Approval

### My Pending Tasks

When a user applies for permissions, the system automatically creates an approval work order based on the target object's approval flow for review. The applicant can view their application information and approval status under **Approval > Application**.

![](.topwrite/assets/image_1736245807432.png)

When an approver receives an approval notification, they can see pending work orders under **Approval > Approval**. Specific operations are as follows:

* Click **Approval > Approval** in the left menu to enter the "Pending My Approval" tab.

* The approval page supports both card view and list view.
  ![](.topwrite/assets/image_1736245843874.png)

* Filter conditions: Set keywords or work order ID, applicant, data object type, application time, sort order, and other search criteria to query pending approval work orders that meet the conditions. When multiple search conditions are set, the intersection of all conditions is used for the query.

**1. View Work Order**

*   **Card view**: Click a specific work order card on the left to view its application details on the right.
*   **List view**: Click the ID column in the list to open a pop-up with the current approval work order details.

Details include:

* Application object, requested permission points, authorized user, authorization time, application reason, approval history

**2. Approve Work Order**

On the "Pending My Approval" page, approvers can perform the following approval operations:

*   **Approve**
    *   Click the **Approve** button in the **Operation** column of a work order in the list, or the **Approve** button on the work order details page, or the **Approve** button in the upper right corner of the card view. In the pop-up window, click **Confirm** to approve the application.
    *   Select one or more items, then click the **Approve** button at the bottom of the list. In the pop-up window, click **Confirm** to approve applications in bulk.

*   **Reject**
    *   Click the **Reject** button in the **Operation** column of a work order in the list, or the **Reject** button on the work order details page, or the **Reject** button in the upper right corner of the card view. In the pop-up window, enter the rejection reason and click **Confirm** to reject the application.
    *   Select one or more items, then click the **Reject** button at the bottom of the list. In the pop-up window, click **Confirm** to reject applications in bulk.

*   **Add Signer**: Indicates that after the current approver approves, additional signers are still needed to participate in approval.
    *   Click the **Add Signer** button in the **Operation** column of a work order in the list, or the **Add Signer** button on the work order details page, or the **Add Signer** button in the upper right corner of the card view. In the **Add Signer** pop-up window, configure the signer information and click **Confirm** to complete the add-signer approval for the application.
    *   Select one or more items, then click the **Add Signer** button at the bottom of the list. In the pop-up window, configure the signer information and click **Confirm** to complete batch add-signer.

**Note:**

*   When the approver clicks the add-signer operation, the system automatically treats the current approver as having performed the approval;
*   When a work order contains multiple approval items, the approval operation applies to all items, meaning you can only approve all or reject all at once.

### Completed

Click the "Completed" tab under the Approval function to view all approval work orders that you have processed and those awaiting your action within the current instance.

![](https://tq2pllvokz.feishu.cn/space/api/box/stream/download/asynccode/?code=YmU2MjVkZTA4OWU3NDlkYWZmOGI1ZTZlOTFlZmY4MWVfZHAwaE94eWpkUzB2S2NWSGppcFd3NWsxekw3QmlFN3ZfVG9rZW46UWl5QWJ1SmZnb0pkZ1h4NDJUWmNGMUpJbjZmXzE3Mjk4MjU3MDQ6MTcyOTgyOTMwNF9WNA)
