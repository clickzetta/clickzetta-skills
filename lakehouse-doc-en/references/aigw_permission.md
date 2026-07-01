`Permission Management` controls which users can access and manage AI Gateway.

### Page fields

The permission list contains:

- `Authorized User`: Users who have been granted AI Gateway permissions.
- `Role`: The role assigned to the user.
- `Updated At`: When the permission was last updated.
- `Actions`: Supports removing authorization.

You can filter the list by authorized user.

### Add authorization

1. Go to `Permission Management`.
2. Click `Add`.
3. Review the role permissions in the add authorization dialog.
4. Select a user in the `Grant to User` field.
5. Click `OK` to complete the authorization.

The role available in the current interface is:

- `AI_GATEWAY_ADMIN`

This role grants management access to AI Gateway.

### Remove authorization

1. Find the target user in the permission list.
2. Click `Remove`.
3. Review the confirmation prompt.
4. Click `OK` to remove the authorization.

The confirmation dialog shows:

```text
Are you sure you want to remove this user's permissions?
```

### Recommendations

- Grant the admin role only to users who need to manage AI Gateway.
- Review the authorized user list regularly.
- Remove permissions promptly when a user leaves or changes responsibilities.
- Avoid granting unrelated users access to API key, BYOK, and routing policy management.
- Before removing permissions, confirm the change does not affect ongoing operations or configuration management work.
