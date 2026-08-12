# Release Notes 2026-07-31

This release introduces new features, enhancements, and fixes. Updates will roll out gradually to the regions below and are expected to complete within one to two weeks of the release date, depending on your region.

* **China Region**

  * Alibaba Cloud (Shanghai)

* **International Region**

  * Alibaba Cloud (Singapore)

## New Features

* [Effect Evaluation](datagpt-evaluation-guide.md):
  * Added evaluation sets, evaluation rules, evaluation tasks, and experiment comparison. Use a fixed question set to validate the quality of analytics-domain responses, review pass rates, result distributions, issue reasons, and case details, and compare the results of two evaluation tasks.
  * Evaluation sets support Excel and CSV imports. When creating an evaluation task, you can set concurrency from 1 to 8.
* [Knowledge Base](datagpt-knowledge-base-guide.md):
  * The Knowledge Base has been upgraded to organize business materials in folders and associate files or folders with analytics domains. After association, Analytics Agent can retrieve and cite the content when answering questions in the corresponding analytics domain.
  * PDF and Office-file previews, as well as citation-source previews, are supported. To recognize image content, configure an OCR model in Model Configuration.
* [Model Selection and Configuration](datagpt-model-config.md):
  * Administrators can manage available models, designate recommended models, and adjust the display order of models. If no model is configured, the page displays an empty-state prompt to guide administrators through configuration.
* [File Upload and Multimodal Q&A](datagpt-file-upload-multimodal-guide.md):
  * Upload temporary files or images in a conversation, view the conversation's file list, preview images, or cancel uploads. This is useful for temporarily adding screenshots, spreadsheets, reference documents, and other materials so that Agent can answer using the current attachments.
* [Sharing and Collaboration](datagpt-share-collaboration-guide.md):
  * Share multiple consecutive Q&A turns with others in a single action. Public share pages support pagination, mobile adaptation, and multilingual display.
* [Personal Preferences and Memory Settings](datagpt-personal-preference-memory-guide.md):
  * Added a Personal Preferences and Memory Settings page where you can view the preferences and context remembered by Agent. It supports memory search, management of unarchived items, bulk deletion, and onboarding guidance.

## Improvements

* **Q&A Performance Improvements**:
  * Optimized parallel execution of read tools, context compression, memory compression, and the return of chart and table results to improve response speed and stability in long conversations for some scenarios.
* **Web Search Experience**:
  * Added a Web Search switch so you can decide whether to enable online search for each scenario.
* **Dashboard Ask Conversation Continuity**:
  * Dashboard Ask now supports conversation continuity. After reopening a page, you can continue viewing unfinished Q&A and reconnect the stop-button state.
* **Permission Management**:
  * Analytics-domain and dashboard permission management is more granular, and authorization dialogs load faster. The visitor role is now supported, and the legacy permission-settings entry point has been retired.
* **Dashboard and Analytics-Domain Copying**:
  * Dashboard-copying and analytics-domain-copying capabilities have been enhanced, making it easier to reuse analysis results across your team.
* **Feedback Center**:
  * The Feedback Center has been redesigned with assignee management, image upload and preview, sorting and search, bulk deletion, and status marking.
* **Theme and Menu Customization**:
  * Supports tenant-level menu customization and light, dark, and user-level themes, as well as Logo and share-page style adaptation.
* **Subscription and Trial Reminders**:
  * Improved subscription and trial-period checks and notifications to help administrators stay informed about service status.

## Bug Fixes

* Fixed an issue that could cause Chinese or specially encoded content to display incorrectly in CSV-file previews.

* Fixed a permission-consistency issue for scheduled tasks in column-level permission snapshot scenarios.

* Fixed issues related to submitting and encrypting credentials for some data sources.

* Fixed exceptions in some dashboard-copying, analytics-domain-copying, and sharing scenarios.

* Fixed issues related to some model calls and subscription checks.

* Fixed exceptions when updating associations between datasets and business domains.
