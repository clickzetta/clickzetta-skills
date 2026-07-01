# Bind a Virtual MFA Device for Multi-Factor Authentication

Multi-Factor Authentication (MFA) adds an extra layer of security to your account by requiring a time-based one-time password (TOTP) in addition to your regular password when logging in or performing critical operations.

A virtual MFA device is a smartphone or desktop application that implements the TOTP standard (RFC 6238), generating a new 6-digit verification code every 30 seconds. You can use any authenticator app that supports the TOTP standard to complete MFA binding with your Singdata account. 

## Supported Authenticator Apps

Singdata is compatible with any authenticator app that follows the TOTP (Time-Based One-Time Password, RFC 6238) standard. The following are common examples (including but not limited to):

Microsoft Authenticator, Google Authenticator, Duo Mobile, Twilio Authy, Symantec VIP.

> 💡 **Tip**: You can install authenticator apps from the app store specific to your device. Some providers also offer web and desktop applications.

## Download and Install an Authenticator App

Make sure you have installed a TOTP-compatible authenticator app on your phone. You can search for and download any of the apps listed above from your device's app store.

## Log in to Your Account

Open your browser on your computer or mobile device and log in to your Singdata account.

## Add Singdata Account Dynamic Password

After logging in successfully, open your authenticator app and tap **Add Account** or the **+** symbol to add a new account.

You can choose one of the following methods:

- **Scan QR Code**: Use your authenticator app to scan the QR code displayed on the Singdata binding page.
- **Enter Setup Key**: Manually enter the key provided on the binding page. Make sure to select "Time-based" as the key type, then tap **Add** to complete the setup.

## Complete Verification

After successfully adding the account, you will see the newly added account and the corresponding 6-digit verification code on the homepage of your authenticator app. Enter the verification code in the input box on the Singdata binding page within the validity period and click **OK**. Once the verification is successful, the binding is complete.

## Reset Binding

You can reset your bound authenticator in the login verification popup or the **Account Information** window after logging in. When resetting the binding, you need to verify your identity through the email address or phone number associated with your current account. After successful verification, repeat the "Add Singdata Account Dynamic Password" and "Complete Verification" steps above to complete the re-binding.

## Frequently Asked Questions

### What if I change my phone?

You will need to re-bind your Singdata account on your new device. Some authenticator apps support cloud backup or account transfer features — check your app's documentation for details. If you are unable to transfer, you can reset your MFA binding through the steps described in the Reset Binding section.

### What if the verification code is invalid?

- Make sure the time on your device is accurate. TOTP codes are time-sensitive, and a clock drift of more than 30 seconds can cause verification failures.
- Try syncing the time settings on your device (most authenticator apps provide a time correction option in their settings).
- If the problem persists, reset your MFA binding and set it up again.

### What if I can't access my authenticator app?

If you cannot verify your identity through your authenticator app (for example, if your phone is lost or the app is uninstalled), you can reset your MFA binding by verifying your email address or phone number. If you still cannot verify normally after resetting, please contact customer support for assistance.
