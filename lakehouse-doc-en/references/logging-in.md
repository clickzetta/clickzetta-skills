# Account Signup and Setup

This guide will help you complete Singdata account registration, service instance activation, and instance initialization to smoothly begin your Singdata journey.

## Account Registration

Before using Singdata services, you need to register a Singdata account.

1. **Visit the Account Registration Page**: Go to [accounts.clickzetta.com](https://accounts.clickzetta.com/register) and click the "Sign Up" button. On the registration page, follow the prompts to fill in your information.

:-: ![](.topwrite/assets/image_1736314854109.png =734)

2. **Enter Phone Number**: On the Singdata registration page, enter a phone number that can receive SMS messages, then click the "Get Verification Code" button. The system will send a verification code via SMS to your phone. Enter the 4-digit verification code you receive into the "Verification Code" field and click "Next". ![](.topwrite/assets/image_1739260609977.png =762)

3. **Create User**: In this step, you need to create the first user for your account. Fill in the "Username", "Password", and "Confirm Password" fields. The username must be 5-32 characters in length, supporting letters, numbers, and underscores, and must start with a letter. The password must be 8-32 characters in length and must contain uppercase letters, lowercase letters, numbers, and special characters.

4. **Complete Registration**: After clicking the "Complete" button, you will see a registration success message along with your account login address. Please keep this address in a safe place for future login. The user created during registration will automatically become the administrator of this account. Click the "Go to Login" button in the prompt window and use the username and password set during registration to log in to your account.

## Logging into Your Account

After registering your account, you can log in using your account name, username, and password.

1. **Using Your Account-Specific Login URL**: Log in using the URL `https://<your_account_name>.accounts.clickzetta.com`. In the login prompt, enter your correct username and password, then click the "Login" button. If you have forgotten your username or password, click the "Forgot Username?" or "Forgot Password?" button and verify using the phone number registered with your account.

:-: ![](.topwrite/assets/image_1736314906745.png =776)

2. **Using the Universal Login URL**: Visit [accounts.clickzetta.com](https://accounts.clickzetta.com/login) to log in. Enter your 8-digit account name (displayed upon completing registration), click "Login", and you will be directed to your account's login page. In the login prompt, enter your correct username and password, then click the "Login" button. If you have forgotten your account name, click "Retrieve Account" on the account login page and verify using the phone number registered with your account.

## Creating a Lakehouse Service Instance

After logging in to your Singdata account, you will enter the Management Center home page. You can activate a Lakehouse service instance in the Management Center. Please follow the steps below:

* On the Management Center "Home" page, locate the Lakehouse product card and click the "Free Trial" button. ![](.topwrite/assets/20250211-191828.jpeg)
* In the pop-up window, select the cloud service provider and activation region, then click the "Confirm" button to complete the creation of the Lakehouse service instance. Currently, Singdata Lakehouse supports activating Lakehouse service instances in three regions: Alibaba Cloud Shanghai, Tencent Cloud Shanghai, and AWS (China) Beijing.

:-: ![](.topwrite/assets/create_instance.png =616)

* Please note that each account is currently limited to creating only one Lakehouse service instance.

## Instance Initialization

After creating the Lakehouse service instance, you can find and access it under "My Subscriptions" in the Management Center. The system will automatically perform initialization, including:

1. Creating the first workspace named "quick\_start".
2. Creating the first virtual compute cluster (Virtual Cluster) within the "quick\_start" workspace, which is in a stopped state by default.
3. Creating the system service users `sysservice_clickzetta` and `sysservice_auto_mv`.
4. Assigning the user who created the Lakehouse service instance the service instance administrator role as well as the workspace admin (workspace\_admin) role for the "quick\_start" workspace. At this point, you will have full operational permissions for the Lakehouse service instance and the "quick_start" workspace. Subsequently, you can add more users and assign appropriate permissions through the user and permission management features.

You have now completed the preparation for using Singdata Lakehouse. You can refer to other quick start documents to learn how to quickly get started with Lakehouse. For more detailed operational guidance, please refer to the [User Guide](studio_manual.md) chapter.

## Activating the DataGPT Service

The DataGPT service is now available in the Alibaba Cloud China East 2 (Shanghai) region. The system will automatically connect with Alibaba Cloud Lakehouse instances in the same region (China East 2 (Shanghai)). For Lakehouse instances not activated in Alibaba Cloud China East 2 (Shanghai), you can manually add them on the DataGPT data source page without any selection operations.

* On the Management Center "Home" page, locate the DataGPT product card and click the "Free Trial" button.

&#x20;      ![](.topwrite/assets/20250211-192212.jpeg =731)

* The pop-up window will default to **Cloud Service Provider**: Alibaba Cloud and **Region**: China East 2 (Shanghai). The system provides an option to "**Simultaneously activate an Alibaba Cloud - China East 2 (Shanghai) Lakehouse instance as the default data source**":
  * **Checked (recommended for new users)**: An Alibaba Cloud - China East 2 (Shanghai) Lakehouse instance will be automatically activated as the default data source, requiring no manual configuration.
  * **Unchecked**: The system will not automatically activate a Lakehouse instance in the China East 2 (Shanghai) region. You can manually add one on the data source management page after the service is activated. Please note that in this case, **DataGPT will not include preloaded sample data**.

&#x20;      ![](.topwrite/assets/20250211-192304.jpeg =618)

* Click "Activate" and wait a moment to enter the usage interface.

&#x20;      ![](.topwrite/assets/20250211-193618.jpeg =787)
