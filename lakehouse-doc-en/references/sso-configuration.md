# Single Sign-On (Private Preview)

This document is intended to guide you step-by-step through the configuration of Single Sign-On (SSO), ensuring you can successfully enable SSO using either the OAuth 2.0/OIDC or SAML 2.0 protocol.

***

## Basic Concepts

* **Single Sign-On (SSO**): A mechanism that allows users to access multiple systems with a single authentication process, simplifying the login experience and improving security.

* **Federated Authentication**: The Lakehouse (Service Provider, SP) trusts an external Identity Provider (IdP) to perform user authentication.

* **Protocol Overview**:

  * **SAML 2.0**: An XML-based identity assertion protocol that transmits user identity information via an Assertion.
  * **OAuth 2.0 / OpenID Connect (OIDC**): OAuth provides an authorization framework, while OIDC adds an identity layer using a JWT-formatted ID Token to represent user identity.

## Relationship Between Singdata and the Customer’s IdP

* Register the Lakehouse application in the IdP (provide callback URL/ACS, Entity ID, signing or encryption certificates).
* Enter the parameters provided by the IdP into the Lakehouse platform.
* After configuration, two login flows are supported: login from Lakehouse (SP-init) or from the IdP (if IdP-init is supported).

## Limitations

Currently, Lakehouse **does not support** the following features. Please keep these in mind during configuration and use:

1. **No global logout support**. Logging out from the IdP will not affect the login state in Lakehouse. Users must log out from Lakehouse separately.

2. **No multi-IdP configuration**. Only one IdP connection is supported.

3. **SSO is supported only for web login**. JDBC, Python SDK, Java SDK, and similar methods are currently not supported for SSO login.

4. **Identity mapping field limitations**:

   * For SAML 2.0, only Email can be used as the identity mapping field.
   * For OAuth 2.0 / OpenID Connect (OIDC), only Email or Phone can be used.

5. **Identity mapping field uniqueness requirement**:
   The field used for identity mapping must be unique across all users in Lakehouse. If multiple users have duplicate Email or Phone information in the chosen mapping field, those users will be unable to log in via SSO.

***

## Protocol Configuration Guide

### Enabling SSO

By default, SSO login is disabled in a Lakehouse account. Users with the Account Administrator role can enable it.

Log in to the Lakehouse account, go to the **Account Center** page, and under the **SSO Login** option, click **Enable SSO Login**.

:-: ![](.topwrite/assets/screenshot-20250814-170309.png =678)

**Note**: Once SSO login is enabled, all users in the account can only log in using SSO, and username/password login for the web will no longer be allowed. Before enabling SSO, ensure that all users who need to log in to Lakehouse:

1. Have a user identity in the IdP.
2. Have unique identity mapping information (Email or Phone) in Lakehouse that does not duplicate any other user.

***

### OAuth 2.0 / OpenID Connect (OIDC) Protocol

**1. Select the protocol**

After enabling SSO login, select **OAuth 2.0 / OIDC Protocol** in the right-side pop-up. Once selected, you will see the protocol’s callback URL, for example:

:-: ![](.topwrite/assets/image_1755162417316.png =695)

```
https://api.clickzetta.com/clickzetta-portal/sso/oidc/consume?u={code}
```

Use this callback URL to register the Lakehouse application in your IdP service and record the Client\_ID and other configuration values for later use.

**Configure Authorization Endpoint**

:-: ![](.topwrite/assets/image_1755162515497.png =546)

**Parameters**:

* **Authorization Endpoint URL** (e.g., `https://idp.example.com/authorize`): Redirects users to the IdP for identity authorization.
* **Client ID**: Identifies the Lakehouse application in the IdP, obtained after registering the Lakehouse app in your IdP.
* **Response type**: Only supports `code` mode.
* **Scope** (e.g., `openid`, `profile`, `email`): Determines the user information that can be requested; multiple scopes are supported. For OpenID, `openid` must be selected. Additional custom scopes can be added by selecting **Other**.
* **Optional extended parameters**: Allows adding extra fields as required by the IdP (e.g., `prompt=login`).

**Configure Token Endpoint**

:-: ![](.topwrite/assets/image_1755162550809.png =515)

**Parameters**:

* **Token Endpoint URL**: Exchanges the authorization code for tokens. After Lakehouse calls the IdP authorization endpoint and receives the code, it calls this endpoint to exchange the code for tokens.
* **Client Secret (optional**): Used to verify client identity. If the IdP does not issue a secret, this can be left blank.
* **Optional extended parameters**: Add as required by the IdP.

**Configure UserInfo Endpoint**

:-: ![](.topwrite/assets/image_1755162592157.png =478)

**Parameters**:

* **UserInfo Endpoint URL**: Used by Lakehouse to retrieve detailed user information.

* **Identity mapping configuration**:

  * **UserInfo field**: The field in the UserInfo response containing the user’s identity. Options: Email, Phone, or custom field.
  * **Identity mapping field**: The Lakehouse field to match against the UserInfo field. Options: Email or Phone. If using Phone, Lakehouse supports phone numbers with country codes starting with `00`, `+`, or no country code.

* **Test user information completeness**: Checks and lists all users in the account who are missing or have duplicate values in the chosen identity mapping field. Such users will be unable to log in via SSO.

* **Optional extended parameters**: Add as required by the IdP.

**Allow account administrators to also log in with username/password**

If enabled, account administrators can still log in with username and password in case of SSO failures, allowing them to adjust account configurations.

***

### SAML 2.0 Protocol

**Select the protocol**

After enabling SSO login, select **SAML 2.0 Protocol** in the right-side pop-up. Once selected, you will see the callback URL (Assertion Consumer Service URL), for example:

:-: ![](.topwrite/assets/image_1755162706106.png =478)

```
https://api.clickzetta.com/clickzetta-portal/sso/saml/consume?u={code}
```

Use this address to register the application in the IdP, and record and save the Entity ID and X.509 certificate returned by the IdP.

:-: **Enter SSO Login URL**
![](.topwrite/assets/image_1755162752056.png =478)

**Parameters**:

* **SSO Login URL**: The IdP endpoint that receives SAML requests.
* **Entity ID**: The application identifier in the IdP, obtained after app registration.
* **X.509 Certificate (optional**): Used for signature verification and data security, obtained after app registration in the IdP.
* **Issuer (optional**): The entity issuing the SAML assertion, used for trust verification.
* **Test user information completeness**: For SAML 2.0, only Email is supported as the identity mapping field. The completeness check lists users missing or duplicating email information, who will not be able to log in after SSO is enabled.

**Allow account administrators to also log in with username/password**

If enabled, account administrators can still log in with username and password in case of SSO failures, allowing them to adjust account configurations.

***

## Frequently Asked Questions

**Q: Why does Lakehouse show “Authentication failed” after logging in from the IdP**?
A: This usually occurs when the mapping field (Email or Phone) is not unique among users, or is missing/incorrectly formatted in the IdP response. If it’s a uniqueness issue, the error message will clearly indicate it. If not, check whether the mapping field configuration is correct (e.g., returning Email but mapping it to Phone).

**Q: Why can’t I log in with username/password even though “Allow account administrators to also log in” is enabled**?
A: Once SSO is enabled and this option is selected, **only** users with the Account Administrator role can log in using username/password; all other users must log in using SSO.

**Q: Can I use SSO login via SDK (e.g., Python, JDBC**)?
A: Currently, only web login is supported. Python, JDBC, and similar SDKs only support username/password authentication.
