# Data Source IP Whitelist Configuration Guide

## Application Scenarios

When the data source is deployed in an intranet environment or has strict security control requirements, it is necessary to configure IP whitelists on the **source database/server**:

1. Allow only the IP segments of the data synchronization service to access the source data.
2. Prevent unauthorized network access.
3. Meet the enterprise's network security audit requirements.

## Prerequisites

* Confirm that the target data source supports the IP whitelist mechanism.
* Obtain the public IP address of the server where the data synchronization service is located.
* Ensure that you have the necessary permissions to manage the data source.

## Configuration Process

If you encounter errors due to whitelist restrictions while testing data source connectivity or running synchronization tasks, follow the steps outlined in this document.

### Step 1: Obtain the Data Synchronization Service Export IP Address

Based on the cloud service and region where your service is located, obtain the corresponding IP address:

| Service Region          | IP Address                                   |
| ----------------------- | -------------------------------------------- |
| Alibaba Cloud·Shanghai  | 47.100.176.72                                |
| Alibaba Cloud·Singapore | 47.237.31.114                                |
| Tencent Cloud·Shanghai  | 110.40.220.6, 124.220.91.8, 101.34.216.184   |
| Tencent Cloud·Beijing   | 101.42.151.242, 101.42.224.202, 43.138.11.31 |
| Tencent Cloud·Guangzhou | 43.138.226.127, 1.14.203.242, 175.178.164.94 |
| AWS·Beijing             | 54.223.225.56, 52.80.208.69                  |
| AWS·Singapore           | 54.251.190.22, 13.250.195.227                |

### Step 2: Configure Whitelist on the Source Database

1. **Log in to the Source Database Management Console**
   * MySQL: Through security groups or database parameter settings
   * Oracle: Through the SQLNET.ORA file configuration
   * SQL Server: Through server firewall settings

2. **Add IP Whitelist Rules**
   Taking Alibaba Cloud RDS MySQL as an example, here are the detailed steps based on the **Alibaba Cloud Console** interface:

   **Step 1: Log in to the Alibaba Cloud Console**
   Open your browser and visit the Alibaba Cloud website. Log in with your Alibaba Cloud account.

   **Step 2: Navigate to the RDS Management Console**
   After logging in, click on the top menu item “**Products & Services**,” then select “**Databases**” > “**Relational Database RDS**.”

   **Step 3: Select the Target RDS Instance**
   On the RDS console page, locate the RDS instance you want to operate on. Click the instance name to enter the instance details page.

   **Step 4: Access “Whitelist Settings**”
   On the instance details page, find the “**Security Settings**” in the left menu. Click on the “**Whitelist Settings**” option.

   **Step 5: Add a Whitelist**
   On the “Whitelist Settings” page, you will see the current whitelist configuration. Click the “**Add Whitelist Group**” button, or directly add the IP address to an existing whitelist group.

   **Step 6: Configure the Whitelist**
   In the pop-up dialog box, enter a whitelist group name (optional). In the “**Whitelist Content**” field, input the allowed IP addresses or IP segments. You can enter multiple IP addresses or segments, separated by commas. For example: `47.100.176.72`. Then click “**OK**” to complete the addition.

   **Step 7: Save the Whitelist Settings**
   After adding, click the “**Save**” button at the bottom of the page to save the whitelist settings.

### Step 3: Data Synchronization Validation

1. In the data source configuration, click on the connectivity test. If successful, this usually indicates that the configuration is normal.
2. As a precaution, create a test synchronization task and run it manually.
3. Observe whether the task log shows a successful connection.
4. In case of failure, check the synchronization task logs and database audit logs.

## Notes

The specific configuration methods may vary depending on the data source type (MySQL/Oracle, etc.), so refer to the official documentation of the corresponding data source. If you need to access cloud products, visit the help centers of each cloud product to view the precautions for adding whitelists. Whitelist settings usually take effect immediately, but may also take a few minutes.

## FAQs

### Q1: Still Cannot Connect After Adding IP Whitelist

* Verify the IP address for accuracy (it is recommended to use `curl ifconfig.me` to check the outbound IP).
* Ensure that the data source firewall has opened the corresponding port.
* Check whether the whitelist configuration has taken effect (some databases require a restart to take effect).

### Q2: Best Practices for Whitelist Maintenance

1. Create a dedicated access account for the data synchronization service.
2. Configure access scope based on the principle of least privilege.
3. Regularly audit the IP addresses in the whitelist.
4. It is recommended to enhance security by using VPN/dedicated lines.
5. Do not add `0.0.0.0/0` (allowing access from all IP addresses) to the production environment whitelist unless absolutely necessary.

^
