# Model Selection and Configuration

Analytics Agent supports multiple large language models. Administrators can select which large language models are used for conversational analysis on behalf of the team. Once configured, users can choose from these models on the conversation page.

## Switching Models in a Conversation

Click the model icon on the left side of the input box to open a dropdown list of available models. Click to switch. Models marked as **Suggest** are system-recommended models.

:-: ![](/.topwrite/assets/image_1780906064431.png =400)

> 💡 **Tip**: The **Model Configuration List** at the bottom of the list links directly to the model configuration page.

## Configuring Available Models (Admin)

Controls which models appear in the conversation dropdown list.

**Entry point**: Left navigation bar → Admin → Model Configuration

:-: ![](/.topwrite/assets/image_1780906096468.png =746)

Toggle the switch on a model card to make that model immediately visible to all users; turning it off hides it from the list. Supports filtering by provider and searching by name.

If the model you need is not in the list (such as an enterprise self-built model), click "Go to AI Gateway to create a new model" at the bottom of the page. After configuring it in AI Gateway, return to the model configuration page and enable the model card switch.

:-: ![](/.topwrite/assets/image_1780906154059.png =531)

## Related Documentation

* [AI Gateway](AIGateway.md) — Connect self-built or third-party models
* [Data Source Management](datagpt_data_source.md) — Configure the data sources for your analytics domain
* [Improving Q\&A Accuracy](answer-accuracy-improve.md) — After completing model configuration, use the semantic layer to further improve answer quality
* [Conversational Data Analysis (Analytics Agent)](datagpt_introduction.md) — Return to the feature overview

^
