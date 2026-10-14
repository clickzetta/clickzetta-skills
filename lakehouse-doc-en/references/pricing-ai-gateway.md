# AI Gateway Billing Guide

## Billing Overview

AI Gateway is foundational infrastructure designed for enterprise **data and AI workflows**, providing a seamless, stable, and highly integrated environment for unified access to AI models. With AI Gateway, you can invoke leading AI models directly within your business data workflows, without managing separate accounts and billing across multiple platforms.
AI Gateway charges based on actual model usage. Billing items, billing units, and pricing conditions may vary by model. Review the pricing information on the model details page before making a call.

## Pricing

The model details page displays **List price** and **Discounted Price**.
| Price Type | Description |
| --- | --- |
| List price | The model’s publicly listed base unit price. |
| Discounted Price | The actual settlement price after discounts. When you make a model call, the system uses this price to calculate the charge. |
> **Pricing Formula:**\
> Discounted Price = List price × Applicable discount factor.

A model may have multiple pricing configurations. When reviewing prices, check the billing item, billing unit, and applicable pricing conditions.

## Billing Items

Model calls may generate input, output, and cache usage. Each billing item is charged separately at its corresponding price.
| Billing Item | Description |
| --- | --- |
| Input Price | Charges for content submitted to the model, such as prompts, context, and other input. |
| Output Price | Charges for content generated and returned by the model. |
| Explicit Cache Creation | Charges for writing content to a cache for reuse in subsequent calls. |
| Explicit Cache Hit | Charges for reusing cached content by explicitly referencing an existing cache in a call. |
| Implicit Cache Hit | Charges for cached content automatically identified and reused by the model service during a call. |

> **Not all models support every billing item listed above.** Check the model details page for cache availability, supported cache types, and applicable pricing conditions.
>
> Billing units may also vary by model, such as tokens, image count, or audio and video duration. Check the model details page for the applicable units.

## Charge Calculation

Model call charges are calculated using actual usage and the corresponding unit prices. **Only billing items with listed prices on the model details page and actual usage are included. Items without listed prices are not included as separate billing items in the formula.**
> **Billing Formula:**\
> Model call charge = Input usage × Input Price + Output usage × Output Price + Explicit Cache Creation usage × Explicit Cache Creation price + Explicit Cache Hit usage × Explicit Cache Hit price + Implicit Cache Hit usage × Implicit Cache Hit price.

## Viewing Prices

You can view current model prices on the [AI Gateway platform](https://aitoken.singdata.com/model):
1. Open **Model Plaza** and search for or select a model.
2. Open the model details page to view its pricing information.
3. Check the billing units, pricing conditions, **List price**, and **Discounted Price** for each billing item.

:-: ![Viewing prices in Model Plaza](.topwrite/assets/ai-gateway-pricing-model-plaza-en.jpg =740)

:-: ![Pricing information on the model details page](.topwrite/assets/ai-gateway-pricing-model-details-en.jpg =740)

**Model prices may change over time.** Check the model details page for current prices. This guide does not establish unit prices for individual models.

If prices change within a billing period, usage is calculated separately according to the prices and billing rules applicable during each respective period. **Currently displayed prices are not used to recalculate historical usage charges. Actual billed usage and final settlement amounts are determined by the bill.**
