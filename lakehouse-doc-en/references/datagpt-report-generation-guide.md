# Analysis Report Creation Guide

Describe what you need in ASK AI to generate a **PPT presentation or HTML report**, without copying charts one by one or formatting the content manually.

## **1. Generate a Report with a Single Request**

You can create a report based on the analysis results in your current conversation:

> Please turn the sales analysis we just discussed into a PPT presentation for management, highlighting overall performance, the reasons behind changes, and recommended actions.

You can also request an analysis and a report directly:

> Please analyze this quarter’s sales performance, focusing on regional differences and month-over-month changes, and generate an HTML analysis report.

Instead of entering your request directly, you can click “+” **→ “Skills**” in the message input box, select “**PPT Generation**” or “**Creative HTML Summary**”, and then enter your requirements.

💡 Specify the audience, key points, and preferred number of pages to get results that better match your expectations.

:-: ![](asset/analysis-report-creation-guide/select-report-skill.png =404)

## **2. Choose a PPT Template**

When creating a PPT presentation, you can select a template configured by your organization to match the required color scheme and layout, without uploading a template file each time.

:-: ![](/.topwrite/assets/image_1792143894797.png =388)

## **3. Preview the Results and Keep Refining**

Once generation is complete, open the report preview in the current conversation to review the content and presentation. To make changes, simply continue with a request in ASK AI:

> Please condense this to 6 pages, keeping the key charts and conclusions.
>
> Please emphasize regional differences and place that section after overall performance.
>
> Please change the final section to recommended actions, ordered by priority.

Once you are satisfied, download the file for use.

💡 Before presenting the report or sharing it externally, verify key data, metric definitions, and analytical conclusions.

## **4. Reuse Content Across Pages with Material Collections**

If your report needs content from different dashboards or conversations, save it to material collections first, then use it together in the report.

1. **Save materials**: Click “Add to Materials” below a response, or select “Add to Materials” from the “···” menu in the upper-right corner of a dashboard, and save the content to the desired material collection.
2. **Reference materials**: Return to the conversation where you are creating the report, click “+” **→ “Add Material Collection**”, and select the materials you need.
3. **Explain how to use them**: Enter your report requirements and tell AI how to use this content.

For example:

> Please combine the sales analysis in the current conversation with the selected channel analysis materials to create a business review PPT presentation, focusing on the reasons behind changes in sales.

If the current conversation already contains everything you need, you can generate the report directly; **adding materials first is not required**. To include local files, upload them through “+” **→ “Add Attachment**”.

| Add content from a conversation   | ![](/.topwrite/assets/image_1792143675185.png =255) |
| --------------------------------- | --------------------------------------------------- |
| Add content from a dashboard&#xA; | ![](/.topwrite/assets/image_1792143711402.png =236) |
| Select materials and apply        | ![](/.topwrite/assets/image_1792143745712.png =237) |

^



## **5. Administrators: Configure Organization-Wide PPT Templates**

To provide templates with a consistent organizational style, an administrator should go to “**Management” → “PPT Template Management**”, click “**Upload Template**”, and follow the on-screen instructions to upload and maintain templates for users to select when creating PPT presentations.

:-: ![](asset/analysis-report-creation-guide/manage-ppt-templates.png =425)

## Frequently Asked Questions

### Do I need to select materials before creating a report?

No. You can create a report directly from the current conversation, or request an analysis and a report through conversation. Select materials only when you need to include content saved from other dashboards or conversations.

### What is the difference between “Add to Materials” and “Add Attachment”?

“Add to Materials” saves content from dashboards or conversations to a material collection, which you can later reference in the report conversation through “+ → Add Material Collection”. “Add Attachment” uploads a local file to supplement the current conversation. Saving materials does not automatically generate a report.

### How can I make the generated content more relevant to my topic?

Specify the report’s analytical topic, audience, key points, and content order. Add relevant materials when you need information from other dashboards or conversations. Instead of simply asking for a “more professional” report, be specific: “Start with overall performance, then explain the reasons behind changes, and finish with conclusions.”

### What should I verify after generation?

Focus on the data, metric definitions, analytical conclusions, and chart presentation. For critical business decisions or external sharing, have someone familiar with the business and metric definitions review the report before use.

## Related Documentation

* [Question Asking Guide](datagpt-question-asking-guide.md)
* [DataGPT Dashboard User Guide](datagpt-dashboard-guide.md)
* [File Upload and Multimodal Q\&A](datagpt-file-upload-multimodal-guide.md)
* [Sharing and Collaboration](datagpt-share-collaboration-guide.md)

^
