# Account & Billing

This guide covers how to manage your Singdata Lakehouse account, including logging into the Management Center, managing account information, and managing users.

## Basic Concepts

### Account Name

In Singdata Lakehouse, every account has a unique identifier used to distinguish accounts globally. The account name consists of an 8-character random string that is automatically generated when you complete registration. The account name also determines your login URL and certain access configurations.

The account name is your unique identifier within Singdata Lakehouse and cannot be changed once generated. You can find your account name in the prompt shown after registration or on the Management Center home page.

:-: ![](.topwrite/assets/image\_1739329828430.png =780)

^

:-: ![](.topwrite/assets/image\_1739329908616.png =783)

### Login URL

In Singdata products, each account has its own dedicated login URL. The login URL follows the format: `<your_account_name>.accounts.singdata.com`.

:-: ![](.topwrite/assets/image\_1739329970639.png =799)

### Service Instance Name

Singdata Lakehouse is a multi-cloud big data platform that supports creating service instances across different regions of multiple cloud providers. Each service instance provisioned generates a unique identifier within that region and carves out a logical area within the infrastructure resources to provide Lakehouse services. The service instance name (`instance_name`) is the unique identifier for a service instance. It is automatically generated when you provision the instance and consists of an 8-character random string. You can find your service instance name in the service instance URL or on the right side of the service instance home page.

:-: ![](.topwrite/assets/image\_1740540520113.png =807)

### Account Registration Phone Number

The account registration phone number is the phone number you provided when creating the account and adding the first user. The initial account phone number is the same as the phone number of the first user under the account. Account administrators can change the registration phone number in the Management Center. Keep your registration phone number safe — in Singdata products, each registration phone number corresponds to only one account, and it is the sole credential for account recovery.

:-: ![](.topwrite/assets/image\_1739330026163.png =806)

^ ^

## Account Name and Identifiers

### Why You Need an Account Name

* **Global uniqueness**: The account name uniquely identifies your account within the global service network of Singdata Lakehouse.
* **Security control**: When enabling account security policies and third-party application integrations, the account name is required for access or interaction.

### Common Use Cases for the Account Name

The Lakehouse account name is primarily used in the following scenarios:

**1. Logging into the Lakehouse Web Interface**

When logging into the Lakehouse Management Center or web interface, you need to enter the correct account URL (`<your_account_name>.accounts.singdata.com`) in your browser.

^

### Why You Need a Service Instance Name

* **Global uniqueness**: The instance name uniquely identifies your service instance within the global service network of Singdata Lakehouse. The service name includes region information, enabling direct interaction with the Lakehouse service in that region and simplifying the access path.
* **Security control**: When enabling network security policies and using third-party clients to access Lakehouse, the service name is required for access or interaction.
* **Resource linking**: When using features such as data sharing, you need to explicitly specify the service instance name of the target or source account.

### Common Use Cases for the Service Instance Name

**1. Lakehouse CLI / Other Clients / Drivers**

When connecting to Lakehouse using the CLI, JDBC driver, Python/R/Java clients, or third-party tools (such as BI tools), you need to specify the service instance name in the connection configuration.

**2. Third-Party Application and Service Integration**

When external applications (such as data analytics platforms, ETL tools, or cloud storage services) interact with Lakehouse, you need to provide the service instance name to identify the target Lakehouse service.

**3. Data Sharing Operations**

In the Lakehouse "Data Sharing" feature, the service instance name is used to define the scope of operations.

^

## Lakehouse Account URL and Login

### Login URL Format

In Singdata Lakehouse, each account has its own dedicated login URL. The general format is:

https://\<your_account_name\>.accounts.singdata.com

Example:

If your account name is `41nprq1k`, the login URL is:

41nprq1k.accounts.singdata.com

### Logging In with Your Account Name

You can navigate directly to `https://<your_account_name>.accounts.singdata.com` in your browser to reach the login page. On the login page, you need to enter or select the correct account name, along with your username and password. Your account may have one or more users, and you can log in as any of them on this page. You can also retrieve a username or reset a password by entering the user's phone number. When multiple users share the same phone number, you can retrieve all associated usernames via that phone number and select the one you want to log in as.

### Login Flow and Account Recovery

1\. Go to `https://<account_identifier>.accounts.singdata.com` or the unified entry point `https://accounts.singdata.com`.

2\. On the login page, enter or select the correct account name, then enter your **username** and **password**.

3\. If you forget your username or password, you can retrieve them via the user's phone number after entering the account name.

When multiple users share the same phone number, you can retrieve all associated usernames via that number and select the user you want to log in as.

4\. If you forget your account name, you can retrieve it on the login page using the account's registration phone number. One phone number corresponds to only one registered account.

^

## Using Account Identifiers in SQL / Config Files / Third-Party Tools

To accurately specify the target Lakehouse account across different environments, choose the appropriate identifier format based on your scenario:

### Using Identifiers in SQL Statements

When referencing another account in Lakehouse SQL (for example, for data sharing), use the service instance name (`instance_name`).

Example:

`--Specify the sharing instance for data sharing`

`ALTER SHARE share_demo ADD INSTANCE <instance_name>;`

### Using Identifiers in Config Files or Third-Party Tools

* **SQL clients, drivers, or library configurations**

In some SQL clients (such as DBeaver), JDBC drivers, or Python/Java library configuration files, you need to configure connection parameters. For example, when configuring the DBeaver driver:

:-: ![](.topwrite/assets/image\_1740549280083.png =361)

In the JDBC connection string, use the service instance name (`instance_name`), for example:

`jdbc:clickzetta://<your_instance_name>.ap-southeast-1-alicloud.api.clickzetta.com/demo_workspace?username=demo_user&password=DemoPassword&schema=public&virtualCluster=DEFAULT`

When configuring the Python SDK, use the service instance name (`instance_name`):

`from clickzetta import connect`

`# Establish connection`

`conn = connect(username='username',`

`password='password',`

`service='<region\_id>.api.clickzetta.com',`

`instance='your_instance_name',`

`workspace='quickstart_ws',`

`schema='public',`

`vcluster='default')`

^ ^

## Maintaining Account Information

### Viewing the Account Registration Phone Number

When you log in to Singdata with a user that has the account administrator role, you can manage your account in the Management Center. On the "Account Home" page, you can view basic account information and the account login URL. You can also click the "Modify" button next to the registration phone number to change it. Note that on the "Account Center" page you will see two separate phone number fields: "Registration Phone" under "Account Info" — this is the phone number bound to the account and can be used to retrieve the account name; and "Registration Phone" under "User Info" — this is the phone number bound to the currently logged-in user and can be used for MFA verification, username recovery, and password recovery for that user. Be sure to distinguish between the two.

![](.topwrite/assets/image\_1740550879753.png)


### Changing the Account Registration Phone Number

To change the account registration phone number, you must be logged in as a user with the account administrator (`account_admin`) role. In the "Account Center", click the modify button next to "Registration Phone" under "Account Info". After verifying the old phone number, you can enter and save the new phone number.

:-: ![](.topwrite/assets/image\_1740551806201.png =765)

:-: ![](.topwrite/assets/image\_1740551835302.png =438)

### Changing the Account Name or Service Instance Name

Both the account name (`account_name`) and the service instance name (`instance_name`) are globally unique identifiers and cannot be modified after they are generated.

^ ^

For further information on managing users under your account, see [Managing Users](account_user_management.md).
