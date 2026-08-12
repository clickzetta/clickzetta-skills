# Knowledge Base Guide

The knowledge base provides a central place to manage business knowledge, files, and metric definitions for Analytics Agent. It solves the problems of scattered knowledge and files, difficulty managing large volumes of content, and having to associate each item individually with an analytics domain.

Think of the knowledge base as a data-analytics reference library: organize content with folders inside a knowledge base, then associate files or folders with an analytics domain. Once associated, when a user asks a question in that domain, Analytics Agent can retrieve the content as the basis for its answers.

> ⚠️ **Note**: Knowledge base content that is not associated with an analytics domain is not retrieved by conversations in that domain. After uploading or creating content, associate it with the relevant analytics domain promptly.

## What Problems the Knowledge Base Solves

| Scenario | Example | Value |
| --- | --- | --- |
| Centralized management of knowledge and files | Previously, "knowledge" and "files" were in two separate entry points | Manage business descriptions, documents, and files in one place. |
| Organizing content by business topic | Sales definitions, finance policies, and product manuals filed separately | Use knowledge bases and folders to create a clear hierarchy. |
| Bulk association with analytics domains | All content in a folder serves the "Sales Analytics Domain" | After associating the folder, child items inherit the association automatically. |
| Improving Q&A accuracy | A user asks about "valid orders" or "KA customers" | Knowledge base content can be retrieved during conversation, reducing definition mismatches. |

The knowledge base is well suited to stable, reusable, frequently referenced business content such as metric definitions, field explanations, business terminology, data dictionaries, policy documents, product documentation, and operational rules.

## Core Concepts

| Concept | Description |
| --- | --- |
| Knowledge base | Top-level container for organizing and managing knowledge content. Multiple knowledge bases can be created under a single tenant. |
| Folder | An organizational unit within a knowledge base. Folders can contain subfolders and files. |
| File | The smallest content unit within a knowledge base. A file can be created directly or uploaded from a local source. |
| Analytics domain | The business analysis space for Analytics Agent. Knowledge base content is included in domain conversations only after it is associated with that domain. |
| Association inheritance | When a folder is associated with an analytics domain, all subfolders and files inside it automatically inherit the association. |

## Accessing the Knowledge Base

1. In the left navigation, click **Data Analytics Agent**.
2. Go to the **Semantic** page.
3. Click the **Knowledge Base** tab.
4. In the knowledge base list, view, create, or enter a knowledge base.

![](.topwrite/assets/datagpt-knowledge-base-list.png)

The Knowledge Base tab consolidates what was previously split across the **Knowledge** and **Files** tabs. Going forward, create and upload knowledge content from the knowledge base.

## Creating a Knowledge Base

1. Go to **Semantic > Knowledge Base**.
2. Click the first card **+ New Knowledge Base**.
3. Enter a name for the knowledge base.
4. Click **Confirm** to create.

![](.topwrite/assets/datagpt-knowledge-base-create.png)

After creation, the knowledge base appears as a card. Click the card to open its file management page; you can also rename or delete it.

If the knowledge base will contain image files, first enable and configure an OCR model under **Management > Model Configuration > OCR Model**. The OCR model recognizes images uploaded during conversation, files in the knowledge base, and image content within documents. If the OCR model is disabled, image content in the knowledge base cannot be parsed.

![](.topwrite/assets/datagpt-ocr-model-config.png)

## Organizing Folders and Files

After entering a knowledge base, a tree directory is displayed on the left side of the page. Use folders and files to organize knowledge content.

### Creating a Folder

1. Select the target location in the directory tree.
2. Click **New**.
3. Select **New Subfolder**.
4. Enter a folder name and save.

Folders can contain subfolders, making it easy to organize content by department, business topic, metric hierarchy, or content type.

### Creating a File

1. Select the target folder in the directory tree.
2. Click **New**.
3. Select **New File**.
4. Enter a file name and content.
5. Save the file.

Creating a file is suited to maintaining short text content such as terminology definitions, metric definitions, business rules, and FAQ explanations.

### Using the Directory Tree

The directory tree supports the following actions:

- Expand or collapse folders.
- View the hierarchy of folders and files.
- Reorder items at the same level.
- Move files or folders into other folders.
- Check association status using the status dot next to each node.

A green status dot means the item is associated with an analytics domain; a grey dot means it is not associated. When you select a node, the right-side detail panel shows the association details and guidance.

![](.topwrite/assets/datagpt-knowledge-base-detail.png)

## Uploading Local Files

1. Enter the target knowledge base.
2. Select the folder to upload into.
3. Click **New**.
4. Select **Upload File**.
5. Select a local file and upload it.
6. After the upload completes, confirm the file appears in the directory tree.

Supported file formats:

- PDF
- Word (`.docx`)
- Excel (`.xlsx`, `.xls`)
- Images (PNG, JPG, JPEG, GIF, WebP)
- CSV
- TXT
- Markdown

The maximum size per file is 200 MB. Selecting multiple local files for bulk upload at once is not supported in this release.

> ⚠️ **Note**: Uploading a file keeps the original file as-is; it is not converted to another format. Whether a file can be effectively cited in Q&A depends on the file format, content quality, and the data extraction model's capability.

## Cloud Storage Import Not Yet Supported

The current version does not support importing knowledge base content from cloud storage. Use **New File** or **Upload File** to maintain knowledge base content for now.

If your content is already stored in S3, OSS, COS, OBS, or similar object storage, download it locally first, then add it to the knowledge base via **Upload File**.

> ⚠️ **Note**: Do not treat cloud storage import as an available operation. Entry points, parameters, and steps will be added once that capability is released.

## Associating with an Analytics Domain

Knowledge base content must be associated with an analytics domain before it is retrieved in conversations in that domain. Both files and folders can be associated with an analytics domain, and a file or folder can be associated with multiple domains.

### Associate a Single File or Folder

1. Find the target file or folder in the knowledge base directory tree.
2. Hover over the node.
3. Click the **⋮** more-options button.
4. Select **Associate Analytics Domain**.
5. Search for and select the analytics domain in the dialog.
6. Click **Confirm**.

You can also click **+ Add** in the **Analytics Domain Association** section of the right-side detail panel to complete the association.

### Bulk Associate with an Analytics Domain

1. Click the multi-select button at the top of the directory tree to enter bulk selection mode.
2. Select multiple files or folders.
3. Click **Associate Analytics Domain** in the bulk action bar.
4. Select the analytics domains to associate.
5. Click **Confirm**.

Bulk mode can also be used for bulk delete, copy, or move. Exiting bulk mode returns the directory tree to normal browsing.

## Understanding Association Inheritance

When a folder is associated with an analytics domain, all subfolders and files inside it automatically inherit the association.

| Action | Result |
| --- | --- |
| Associate a folder with an analytics domain | Subfolders and files inherit the domain automatically. |
| Add a file under an already-associated folder | The new file inherits the parent folder's analytics domain. |
| Move a file into an already-associated folder | The file inherits the target folder's domain; any prior standalone association is overwritten. |
| Remove association from a parent folder | Child items no longer inherit that domain and may become unassociated. |
| Child inherits parent's association | The child cannot modify that inherited association independently; changes must be made at the parent level. |

To assign a separate analytics domain to a specific child file, first remove the association from the parent folder, then configure the child file independently.

> ⚠️ **Note**: When you move a file that already has its own standalone analytics domain association into a folder that is also associated with an analytics domain, the file's association changes to inherit the target folder's. Confirm the new association scope is correct before moving.

## Viewing Association Status

Both the directory tree and the right-side detail panel show analytics domain association status.

| Status | Display | Meaning |
| --- | --- | --- |
| Associated | A green status dot appears next to the directory tree node; the detail panel shows the associated analytics domain tags. | The file or folder is associated with an analytics domain and can be retrieved in conversations in that domain. |
| Not associated | A grey status dot appears next to the directory tree node; the detail panel shows an **Associate** entry or an unassociated prompt. | The content is not yet associated with an analytics domain and will not be retrieved in domain conversations. |

The right-side detail panel shows a contextual prompt based on the current node's status. An associated folder shows the message "All files in this folder will automatically inherit the above analytics domain associations." When unassociated, you can click **Associate** in the detail panel to add the association.

![](.topwrite/assets/datagpt-knowledge-base-association-status.png)

## Viewing File and Folder Details

Click a folder or file in the directory tree to display its details on the right side.

### Folder Details

Folder details typically include:

- Folder name
- Number of files
- Created by and creation time
- Last modified by and modification time
- Analytics domain association tags
- Inheritance or unassociated prompt

If a folder is associated with an analytics domain, all content inside it inherits that association.

### File Details

File details typically include:

- File name
- File type and size
- Download entry
- Created by and creation time
- Last modified by and modification time
- Analytics domain association tags
- File content preview

For image or text files, a content preview is available in the detail panel.

## Using the Knowledge Base in an Analytics Domain

In the analytics domain detail page, the previous **Knowledge** and **Files** tabs are merged into a **Knowledge Base** tab. This entry point is primarily for viewing and managing which knowledge base content is associated with the current analytics domain.

### Viewing Associated Content

1. Enter the target analytics domain.
2. Open the **Knowledge Base** tab.
3. View the folders and files associated with the current analytics domain.
4. Click the arrow to the left of a folder to expand and view its child content.

The list shows name, type, modification time, and actions. Folders display a file count; files display file size.

![](.topwrite/assets/datagpt-domain-view-knowledge-base.png)

### Associating Knowledge Base Content from the Analytics Domain

1. In the analytics domain's **Knowledge Base** tab, click **Associate Knowledge**.
2. In the dialog, select files or folders from the global knowledge base.
3. Select the content to associate.
4. Click **Confirm**.

When you select a folder, all content inside it is associated with the current analytics domain. A **Go to Knowledge Base** link is also available at the bottom of the dialog for when you cannot find the content you need.

### Removing an Analytics Domain Association

1. Find the file or folder to remove in the analytics domain's **Knowledge Base** tab.
2. Click **Remove** in the action column.
3. Read the confirmation prompt.
4. Click **Confirm**.

After removing a file, conversations in the current domain can no longer retrieve that file's content. After removing a folder, all files in that folder lose their association with the current analytics domain.

> ⚠️ **Note**: Removing in the analytics domain tab removes the association only — it does not delete the original file from the knowledge base. The file remains in the knowledge base.

## Recommended Organization

To make the knowledge base easier to maintain and retrieve, organize content by business topic.

Recommended structure:

```text
Sales Knowledge Base
├── Metric Definitions
│   ├── Valid Orders.md
│   └── Revenue Definition.md
├── Customer Segmentation
│   ├── KA Customer Definition.md
│   └── Customer Tier Description.xlsx
└── Operational Rules
    └── Channel Source Description.pdf
```

Avoid putting all files in the root directory, and avoid names like "Data1," "Description," or "Test File" that are hard to retrieve.

## FAQ

### What is the difference between the knowledge base and the old "Knowledge" and "Files" tabs?

The knowledge base consolidates what was previously in the "Knowledge" and "Files" tabs into a single entry point, with support for knowledge base, folder, and file hierarchy management. You no longer need to maintain short-text knowledge and file content in two separate tabs.

### What is the difference between creating a file and uploading a file?

Creating a file is suited to maintaining short text content directly, such as terminology explanations and metric definitions. Uploading a file is suited to existing PDF, Word, Excel, image, CSV, TXT, or Markdown content.

### After a folder is associated with an analytics domain, can child files still have their associations changed individually?

No. Child files inherit the parent folder's association. To configure a child file separately, first remove the parent folder's association.

### Are files that are not associated with an analytics domain cited in Q&A?

No. Files not associated with an analytics domain are not retrieved in conversations in that domain.

### Does deleting a knowledge base card affect Q&A?

Yes. Deleting a knowledge base affects the associations between its content and analytics domains, as well as future retrieval. Before deleting, confirm that no production analytics domains depend on that knowledge base content.

## Related Documentation

- [Configure Analytics Domain](datagpt-domain-management-guide.md) — data, knowledge base, and permission configuration in the analytics domain
- [Configure Knowledge](datagpt-knowledge-config-best-practices.md) — original knowledge configuration and metric maintenance recommendations
- [File and Document Q&A](datagpt-file-knowledge-qa-guide.md) — how file content participates in Q&A
- [Question Asking Guide](datagpt-question-asking-guide.md) — how to ask clearer questions using business language
- [Reading Analysis Results](datagpt-answer-reading-guide.md) — how to determine whether an answer cited the correct evidence
