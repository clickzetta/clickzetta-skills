
`BYOK` stands for Bring Your Own Key. Use it to connect your own provider API keys to AI Gateway. Once configured, AI Gateway can use your keys when routing calls to the corresponding provider models.

### Page capabilities

The BYOK page lets you:

- View the list of configurable providers.
- Search for providers.
- Check the configuration status of each provider.
- Refresh the provider list.
- Open the edit dialog from the More menu next to a provider.

### Configure a provider key

1. Go to `BYOK`.
2. Find the target provider.
3. Click the More menu to the right of the provider.
4. Click `Edit`.
5. Fill in the name and key in the dialog.
6. Toggle the enabled state on or off.
7. Select a test model.
8. Click `Test` to verify the key.
9. After a successful test, click `Save`.

Fields in the configuration dialog:

- `Name`: A custom name for this BYOK configuration.
- `Key`: The provider API key.
- `Enabled`: Controls whether this BYOK configuration is active.
- `Test Model`: The model used to verify that the key works.
- `Test`: Sends a test request.
- `Save`: Saves the configuration.

### Use with routing policy

After configuring BYOK, you must set a routing policy for the corresponding API key in `API Key Management` to control whether calls use BYOK.

Common combinations:

- `Default routing + BYOK configured`: The platform's default policy decides whether to use the relevant provider.
- `Specified provider + BYOK configured`: Calls prefer the specified provider, and within that provider, BYOK takes priority.
- `BYOK only`: All calls use your own keys; the platform's built-in capacity is not used.

### Recommendations

- Test the key before saving.
- Make sure the provider key is valid, has sufficient quota, and has permission to call the target models.
- Use clear names to distinguish keys from different providers.
- Before modifying or disabling a BYOK key, confirm that no API key routing policies depend on it.
- BYOK keys are sensitive credentials. Do not expose them or include them in public documentation.
