# Register Account

This guide will help you complete the registration of a Singdata account, activate a service instance, and complete the instance initialization process, helping you smoothly start your journey with Singdata.

Start using Singdata

## Account Registration

Before using Singdata services, you need to register a Singdata account.

1. **Visit the account registration address**: [accounts.clickzetta.com](https://accounts.clickzetta.com/register), click the "Register" button, and follow the prompts on the registration page to fill in the information.

:-: ![](.topwrite/assets/image_1736314854109.png =734)

2. :-: **Enter your phone number**: On the Singdata registration page, please enter a phone number that can receive SMS normally, then click the "Get Verification Code" button. The system will send a verification code via SMS to your phone. Please enter the 4-digit verification code you received into the "Verification Code" input box and click "Next". ![](.topwrite/assets/image_1739260609977.png =762)

^

3. **Create a user**: In this step, you need to create the first user for your account. Please fill in "Username", "Password", and "Confirm Password". The username length must be between 5-32 characters, supporting English letters, numbers, and underscores, and must start with a letter. The password length must be between 8-32 characters and must include uppercase letters, lowercase letters, numbers, and special symbols.

4. **Complete registration**: After clicking the "Complete" button, you will see a registration success prompt and receive the account login address. Please save this address properly for future login. The user created during registration will automatically become the administrator of the account. Click the "Go to Login" button in the prompt window and log in to your account using the username and password you registered with.

## Log in to the Account

After you have registered an account, you can log in using the account and the username and password under this account.

1. **Use the account login address**: Log in using the URL of your .accounts.clickzetta.com. Enter the correct username and password in the login prompt box and click the "Login" button. If you forget your username or password, click the "Forgot Username?" or "Forgot Password?" button and use the phone number you registered with to verify and retrieve it.

:-: ![](.topwrite/assets/image_1736314906745.png =776)

2. **Use the general login address**: Visit [accounts.clickzetta.com](https://accounts.clickzetta.com/login) to log in. Enter your 8-digit account name (displayed upon registration), click "Login", and enter the account login page. Enter the correct username and password in the login prompt box and click the "Login" button. If you forget your account name, click "Retrieve Account" on the account login page and use the phone number you registered with to verify and retrieve it.

## Create a Lakehouse Service Instance

After logging into your Singdata account, you will enter the management center homepage. You can activate a Lakehouse service instance in the management center. Please follow these steps:

* Find the Lakehouse product card on the "Home" page of the management center and click the "Activate for Free" button. ![](.topwrite/assets/20250211-191828.jpeg)
* In the pop-up window, select the cloud service provider and activation region, and click the "Confirm" button to complete the creation of the Lakehouse service instance. Currently, Singdata Lakehouse supports activating Lakehouse service instances in Alibaba Cloud Shanghai, Tencent Cloud Shanghai, and Amazon Cloud (China) Beijing regions.

:-: ![](.topwrite/assets/create_instance.png =616)

* Please note that currently, each account is limited to creating one Lakehouse service instance.

## Instance Initialization

After creating a Lakehouse service instance, you can find and enter the service instance in "My Subscriptions" in the management center. The system will automatically initialize, including:

1. Creating the first workspace named "quick\_start".
2. Creating the first virtual compute cluster (Virtual Cluster) in the "quick\_start" workspace, which is in a stopped state by default.
3. Creating system service users `sysservice_clickzetta` and `sysservice_auto_mv`.
4. Setting the user who created the Lakehouse service instance as the administrator role of the service instance and the workspace administrator (workspace\_admin) role of the "quick\_start" workspace. At this point, you will have all operational permissions for the Lakehouse service instance and the "quick\_start" workspace. Subsequently, you can add more users and assign corresponding permissions through the user and permission management functions.

Now, you have completed the preparation for using Singdata Lakehouse. You can refer to other quick start documents to learn how to quickly get started with Lakehouse. For more detailed operational guidance, please refer to the "[Operation Guide](studio_manual.md)" section.

## Activate DataGPT Service

# DataGPT Service Now Available in Alibaba Cloud East China 2 (Shanghai) Region

DataGPT service is now available in the Alibaba Cloud East China 2 (Shanghai) region. The system will be integrated by default with the Lakehouse instance in the same region, East China 2 (Shanghai) Alibaba Cloud. For Lakehouse instances not activated in Alibaba Cloud - East China 2 (Shanghai), you can manually add them directly on the DataGPT data source page without needing to select any options.

* Find the DataGPT product card on the "Home" page of the management center and click the "Activate for Free" button.&#x20;

&#x20;      ![](.topwrite/assets/20250211-192212.jpeg =731)

* In the pop-up window, the **Cloud Service Provider** Alibaba Cloud and **Region** East China 2 (Shanghai) will be specified by default. The system provides the option "**Activate Alibaba Cloud - East China 2 (Shanghai) Lakehouse instance as the default data source**":
* * **Checked (Recommended for new users**): The Alibaba Cloud - East China 2 (Shanghai) Lakehouse will be automatically activated as the default data source, no manual configuration required.
  * **Unchecked**: The system will not automatically activate the Lakehouse instance in the East China 2 (Shanghai) region. You can manually add it on the data source management page after the service is activated. Please note that in this case, **DataGPT will not include preset sample data**.

&#x20;      ![](.topwrite/assets/20250211-192304.jpeg =618)

^

* Click "Activate", and after a short wait, you can enter the usage interface

&#x20;      ![](.topwrite/assets/20250211-193618.jpeg =787)

^
