## Setup to use

This document will introduce how to complete Singdata account registration, instance creation, and instance initialization operations, to start your Singdata journey.

### Account Registration

Before officially using Singdata services, you need to register an account on Singdata, which requires 2 steps.

1. On the Singdata registration page, please enter a mobile number that can normally receive text messages, and click the "Get Verification Code" button. The mobile number you filled in will receive a verification code text message sent by the system, please fill in the 4-digit verification code into the "Verification Code" input box, and click "Next".

2. In this step, you need to create the first user for this account. Please fill in the "Username", "Password" and "Confirm Password" input boxes, and click the "Complete" button. The username supports 5-32 characters, only supports English, numbers, and underscores \_, and needs to start with a letter. The password length is 8-32 characters, and must include uppercase letters, lowercase letters, numbers, and special symbols.

3. After the user is created, you will see a registration success prompt and receive your account login address. Please copy and bookmark this address for future login. At this point, you have completed the creation of the Singdata account, and the user created during registration will automatically become the administrator of this account. Click the "Go to Login" button in the prompt window on the page, and you can use the username and password registered in the previous step to log in to your account.

### Account Login

* **Login from** \[**account\_name**].**accounts.singdata.com**
  After completing account registration and activating your service instance, you will receive a unique URL starting with your account name: \[account\_name].accounts.singdata.com. Use this URL to log in and share it with other users under your account for direct access without entering the account name. To log in, enter your username and password in the login prompt and click "Login."After successful verification, the page will automatically redirect to the management center page of the account. If you forget your username or password, please click the "Forgot Username?" or "Forgot Password?" button. You can retrieve it by verifying with the mobile number used during registration.
* **Login from accounts.singdata.com**
  When you log in using the URL accounts.singdata.com, you need to enter the account name you need to log in. The account name is 8 random English letters and numbers, displayed when the account is registered. After entering the correct account name, click "Login", then jump to the login page of this account, please enter the correct username and password in the login prompt box, and click the "Login" button. After successful verification, the page will automatically jump to the management center page of this account.
  If you forget the account name, please click "Retrieve Account" on the account login page, enter the mobile number when registering the account, and you can retrieve the account name after verification.

### Create Lakehouse Service Instance

After you complete the account registration and login, you can open your Lakehouse instance in the management center. Click the "Free Open" button in the Lakehouse product card on the "Home" page of the management center, select the cloud service provider and opening region in the pop-up window, and click "Confirm" to complete the creation of the Lakehouse service instance.
Currently, Singdata only allows one account to create one Lakehouse service instance.

### Instance Initialization

After creating the Lakehouse service instance, you will see the newly created Lakehouse service instance in the "My Subscription" in the management center, click to enter this service instance. During the instance creation process, the system will automatically initialize this service instance, including:

* Automatically create two system service users in the Lakehouse service instance: sysservice\_clickzetta, sysservice\_auto\_mv;
* Automatically create the first workspace in the service instance: quickstart\_ws;
* Automatically create the first computing cluster (Virtual Cluster) in the quickstart\_ws workspace, which is closed by default;
* Automatically set the user who created the Lakehouse service instance as the administrator role of this service instance and the space administrator (workspace\_admin) role of the workspace quickstart\_ws. At this time, this user has all operation permissions for the Lakehouse service instance and the quickstart\_ws workspace. Subsequent users and permissions can be added and further allocated through the user and permission management function.

***

After the above operations, you have completed the preparation for using Singdata Lakehouse. For detailed guidance on page operations, you can check the content in the "Operation Guide" section below.
