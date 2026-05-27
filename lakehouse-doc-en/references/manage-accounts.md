# Account Management Guide

This guide provides detailed instructions on how to manage your Singdata Lakehouse account, including logging into the Management Center, managing account information, and managing users.

## 1. Basic Concepts

### Account Name

In Singdata Lakehouse, each account has a unique identifier used to distinguish different accounts globally. The account name consists of an 8-character random string automatically generated when you complete registration. The account name also determines your login address and some access configurations.

The account name is your unique identifier within Singdata Lakehouse and cannot be changed once generated. You can find your account name from the prompt shown after completing registration or on the Home page of the Management Center.

:-: ![](.topwrite/assets/image_1739329828430.png =780)

^

:-: ![](.topwrite/assets/image_1739329908616.png =783)

### Login Address

In Singdata products, each account has its own dedicated login address. The format of the login address is \<your\_account\_name>.accounts.clickzetta.com.

:-: ![](.topwrite/assets/image_1739329970639.png =799)

### Service Instance Name

Singdata Lakehouse is a multi-cloud big data platform that supports creating service instances across different regions of various cloud providers. Each service instance is created within a specific region, where a logical resource area is allocated from the infrastructure to provide Lakehouse services to you. The service instance name (instance_name) is the unique identifier of the service instance, automatically generated when you create the service instance, consisting of an 8-character random string. You can find your service instance name in the service instance URL or in the top-right corner of the service instance Home page.

:-: ![](.topwrite/assets/image_1740540520113.png =807)

### Account Registration Phone Number

The account registration phone number is the mobile phone number you enter when creating your account and adding the first user. Initially, the account phone number is the same as the phone number of the first user under your account. An account administrator can change the registration phone number in the Management Center. Please keep your registration phone number safe, as in Singdata products, each registration phone number can only correspond to one account, and it is the sole credential for recovering your account.

:-: ![](.topwrite/assets/image_1739330026163.png =806)

^

^

## 2. Account Name and Identifier

### Why an Account Name is Needed

* **Global Uniqueness**: The account name uniquely identifies your account across the global Singdata Lakehouse service network.
* **Security Control**: When enabling account security policies and integrating with third-party applications, the account name is required for access and interaction.

### Common Scenarios for the Account Name

The Lakehouse account name is primarily used in the following scenarios:

**1. Logging into the Lakehouse Web Interface**

When logging into the Lakehouse Management Center or web interface, you need to enter the correct account URL in your browser (\<your\_account\_name>.accounts.clickzetta.com).

^

### Why a Service Instance Name is Needed

* **Global Uniqueness**: The instance name uniquely identifies your service instance across the global Singdata Lakehouse service network. The instance name includes region information and allows direct interaction with the Lakehouse service within that region, simplifying the access path.
* **Security Control**: When enabling network security policies and using third-party clients to access Lakehouse, the instance name is required for access and interaction.
* **Resource Linking**: When performing data sharing and similar features, you need to explicitly specify the target or source account's service instance name.

### Common Scenarios for the Service Instance Name

**1. Lakehouse CLI / Other Clients / Drivers**

When using CLI, JDBC drivers, Python/R/Java clients, or third-party tools (such as BI tools) to connect to Lakehouse, you need to specify the service instance name in the connection configuration.

**2. Third-Party Application and Service Integration**

When external applications (such as data analytics platforms, ETL tools, or cloud storage services) interact with Lakehouse, you need to provide the service instance name to identify the target Lakehouse service.

**3. Data Sharing Operations**

In Lakehouse's "Data Sharing" feature, you need to use the service instance name to define the scope of operations.

^

## Lakehouse Account URL and Login

### Login Address Format

In Singdata Lakehouse, each account has its own dedicated login address (URL). The general format is as follows:

[https://\<your\_account\_name>.accounts.clickzetta.com](https://\<your\_account\_name>.accounts.clickzetta.com)

Example:

If your account name is 41nprq1k, then the login address is:

41nprq1k.accounts.clickzetta.com

### Logging in with the Account Name

You can directly enter `https://\<your\_account\_name>.accounts.clickzetta.com` in your browser to open the login page. On the login page, you need to enter or select the correct account name, along with your username and password. Your account may have one or more users, and you can log in as any user on the above page. You can also recover your username or reset your user password by entering the user's mobile phone number. When multiple users share the same phone number, you can recover all associated usernames through that phone number and choose the one you want to log in with.

### Login Flow and Recovery Methods

1. Visit `https://\<account\_identifier>.accounts.clickzetta.com` or the unified entry `https://accounts.clickzetta.com`.

2. On the login page, enter or select the correct account name, and enter your **username** and **password**.

3. If you forget your username or password, after entering the account name, you can recover them using the user's phone number.

When multiple users share the same phone number, you can recover all associated usernames through that number and select the desired user to log in.

4. If you forget your account name, you can recover it on the login page using the account's registration phone number. Each phone number corresponds to only one registered account.

^

## Using Account Identifiers in SQL / Configuration Files / Third-Party Tools

To correctly specify the target Lakehouse account in various environments, you need to choose the appropriate account identifier format based on the specific scenario:

### Using in SQL Statements

When you need to reference other accounts in Lakehouse SQL (for example, for data sharing), use the service instance name (instance_name).

For example:

`-- Specify the sharing instance for data sharing`

`ALTER SHARE share_demo ADD INSTANCE <instance_name>;`

### Using in Configuration Files or Third-Party Tools

* **SQL Clients, Drivers, or Library Configuration**

In configuration files for certain SQL clients (such as DBeaver), JDBC drivers, or Python/Java libraries, you need to configure connection parameters. For example, when configuring a DBeaver driver:

:-: ![](.topwrite/assets/image_1740549280083.png =361)

In JDBC connection strings, you need to use the service instance name (instance_name), such as:

`jdbc:clickzetta://<your_instance_name>.ap-southeast-1-alicloud.api.clickzetta.com/demo_workspace?username=demo_user&password=DemoPassword&schema=public&virtualCluster=DEFAULT`

For example, when configuring the Python SDK, you need to use the service instance name (instance\_name):

`from clickzetta import connect`

`# Establish a connection`

`conn = connect(username='username',`

`               password='password',`

`               service='<region\_id>.api.clickzetta.com',`

`               instance='your_instance_name',`

`               workspace='quickstart_ws',`

`               schema='public',`

`               vcluster='default')`

^

^

## Maintaining Account Information

### Viewing the Account Registration Phone Number

When you log into Singdata with a user who has the account administrator role, you can manage your account in the Management Center. On the "Account Home" page, you can view the account's basic information and the account's login URL. You can also click the "Edit" button next to the registration phone number to change the account's registered phone number.
Please note that on the "Account Center" page, you will see the "Registration Phone Number" under "Account Information" -- this is the phone number bound to the account and can be used to recover the account name; and the "Registration Phone Number" under "User Information" -- this is the phone number of the currently logged-in user, only bound to the current user's identity, and can be used for MFA verification, username recovery, password reset, etc. Please distinguish between the two.

![](.topwrite/assets/image_1740550879753.png)

### Changing the Account Registration Phone Number

If you need to change the account registration phone number, log in with a user who has the account administrator (account_admin) role. After entering the "Account Center", click the Edit button next to "Registration Phone Number" in the "Account Information" section. After verifying the old phone number, you can enter and save a new phone number.

:-: ![](.topwrite/assets/image_1740551806201.png =765)

:-: ![](.topwrite/assets/image_1740551835302.png =438)

### Changing the Account Name or Service Instance Name

The account name (account\_name) and service instance name (instance\_name) are both globally unique names and cannot be modified once generated.

^

^

For further management of users under your account, please refer to [Managing Users](account_user_management.md).
