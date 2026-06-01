# Logging in to Singdata Lakehouse

You can log in to Singdata Lakehouse in many ways.

If you’re getting started with Singdata Lakehouse, start by using [Singdata Lakehouse Studio](studio_overview.md) or [Singdata Lakehouse  CLI](connect-with-cli.md), the command line client that you can download. After you get comfortable using Singdata Lakehouse, you can explore connecting to Singdata Lakehouse with other methods.

^

## Account Registration

Before using Singdata services, you must create an account. Currently, a registration code (invitation code) is required. After obtaining the registration code by contacting our sales team, you can visit <https://accounts.singdata.com/register> to sign up.

1. **Visit the** [registration page](https://accounts.singdata.com/register). On the registration page, follow the prompts to enter your desired username and password. The username you enter here will be the first user created under your new account and will be granted administrator privileges.
2. **Enter your** **Email address**: Please provide the email address that you used to obtain the invitation code, then click the “Get Code” button. A verification code will be sent to this email address. Enter the received verification code in the “Verification Code” field. This email address will serve both as the registered email for the account and for the first user created under this account.
3. **Enter the invitation code**: Input the invitation code sent by the Singdata sales team. Each invitation code can only be used once and **must** match the bound phone number.

:-: ![](/.topwrite/assets/image_1761728631383.png)

After completing the steps above, click “Register Now” to finalize your account registration. You will see a success message with a link to your account login page. Please keep this address in a safe place for future use. The user created during registration will automatically become the administrator of the account. Click “Go to Login” on the success message and use the username and password you set during registration to sign in.

***

## Logging into Your Account

Once you have successfully registered, you can log in with your account name, username, and password.

![](.topwrite/assets/image_1741178602186.png)

1. **Using Your Account-Specific Login URL**: Go to `https://<your_account_name>.accounts.singdata.com/login`. On the login page, enter your username and password, then click “Login.”

   * If you have forgotten your username or password, click the “Forgot Username?” or “Forgot Password?” button and use the phone number associated with that user to recover it.
   * If you have forgotten your account name, click “Forgot Account Name?” and verify using the phone number associated with the account.

2. **Using the General Login Page**: Go to [https://accounts.singdata.com/login](https://accounts.clickzetta.com/login) to log in. Enter your 8-digit account name (shown when you completed registration), then click “Login” to be directed to the account’s login page. In the login prompt, enter the correct username and password, then click “Login.”

   * If you have forgotten your account name, click “Forget Account” on the account login page and verify using the phone number you used at registration to retrieve it.

   ^

## Your Singdata Lakehouse account identifier

All access to Singdata Lakehouse is through your account identifier. See [Manage Account](manageaccounts.md) for details.

^

## Logging in using Singdata Lakehouse CLI

Singdata Lakehouse CLI is the command line client for connecting to Singdata Lakehouse to execute SQL queries and perform all DDL and DML operations, including loading data into and unloading data out of datalake files and database tables.

For more detailed instructions, see [Singdata Lakehouse  CLI](connect-with-cli.md)

^

## Connecting using other methods

In addition to the Singdata Lakehouse web interface and CLI, Singdata Lakehouse supports numerous other methods for connecting, including:

* Using 3rd-party client services and applications that support JDBC.
* Using 3rd-party client services and applications that support JDBC via MySQL JDBC driver.
* Developing applications that connect through the Singdata Lakehouse connectors/drivers for Python SQL Alchemy, Zettapark, Spark, etc.

However, connecting to Singdata Lakehouse using these other methods requires additional installation, configuration, and development tasks. For more information, see [Applications and tools for connecting to Singdata Lakehouse](tutorial_connect_to_lakehouse.md).

^

For more information about the tasks you can perform in Singdata Lakehouse  Studio, refer to [Singdata Lakehouse  Studio quick tour](lakehousestudiotour.md).

For more information about the detail manual guides of Singdata Lakehouse  Studio, refer to [Singdata Lakehouse  Studio manual guides](studio_manual.md).
