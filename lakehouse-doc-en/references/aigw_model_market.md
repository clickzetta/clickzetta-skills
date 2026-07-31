`Model Market` is where you browse the models that AI Gateway currently supports, along with their descriptions, provider sources, endpoints, and call examples.

### Page capabilities

Model Market lets you:

- View all available models.
- Switch between grid view and table view.
- Filter models by provider.
- Check whether a model has platform built-in support.
- Check whether a model supports BYOK.
- Open the model detail page to see how to call it.

### Model cards

A model card typically contains:

- `Model Name`: The display name of the model in AI Gateway.
- `Built-in`: Indicates whether you can call this model directly using the platform's built-in provider.
- `BYOK`: Indicates whether you can call this model with your own key.
- `Model Description`: Explains the model's capabilities, recommended use cases, and characteristics.
- `View`: Opens the model detail page.

Use the model description to determine which use case the model is best suited for: text generation, code generation, visual understanding, image generation, video generation, embedding, and so on.

### Model detail page

Click `View` on a model card to open the detail page.

The detail page contains:

- `Basic Info`: Shows the model name and description.
- `Endpoint Management`: Lists endpoint names, service providers, billing rates, status, and actions.
- `View Billing`: Shows billing information for the endpoint.
- `Monitoring`: Shows call monitoring for the model or endpoint.
- `Call Examples`: Provides REST API or cURL examples.

### Call a model

To call a model, you generally need:

1. Use the AI Gateway endpoint URL.
2. Set the request header `Content-Type: application/json`.
3. Set the request header `Authorization: Bearer $API_KEY`.
4. Use the `model` name shown on the model detail page in the request body.
5. Fill in text, image, video, or other parameters based on the model type.

Example structure:

```bash
curl -X POST <AI_GATEWAY_ENDPOINT> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "<MODEL_NAME>",
    "input": "<REQUEST_CONTENT>"
  }'
```

Request body structure varies by model. Use the examples on the model detail page as the authoritative reference.

### Recommendations

- Before integrating, open the model detail page to confirm the model name and call examples.
- Compare multiple models for the same task, weighing output quality, cost, and latency.
- If you need to use your own key, check whether the model supports BYOK.
- For production workloads, monitor the endpoint status and usage metrics on the model detail page.
