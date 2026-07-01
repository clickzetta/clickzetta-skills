Git Folder is a special folder type provided by the Studio product. Creating a folder of this type allows you to associate it with a Git repository, integrating the Git repository into your own workspace. You can use Git Folders to leverage Git for version control, collaboration, and CI/CD.

## Create Git Account Association

If the address of the Git repository you need to associate is not public, you need to save the corresponding Git credentials in the product for account permission verification.

Operation entry: Left navigation menu -> More -> Associate Git

Click Add to create an account link.

Display Name: A user-defined name for the currently managed account.

Access Token: The access token created by the user in GitLab. Note that if you need to perform Git repository operations within the product, please ensure the permission configuration is correct and complete when creating the token.

> Currently, only GitLab is supported.

## Create Git Folder

On the development page, click "New" and select the "Git Folder" type to create a special folder type associated with a Git repository.

**Type**: Git Folders support two types. Only Git Folders of the same type can be created within the same workspace.

* Folder Type: Created within the workspace as a special folder type. Supports association with multiple Git repositories.
* Workspace Type: All tasks in the entire workspace are associated with a Git repository. Only one Git repository of this level can be created per workspace.

**Git Folder Name**: Customize the display name of the folder.

**Folder**: For a Folder-type Git Folder, you need to select the specific save location.

**Git Repository URL**: The URL of the Git repository you want to clone, in the format `https://example.com/organization/project.git`.

**Git Account**: Select the account information for accessing the URL. If the current URL is not public, the user needs to use an account to access and pull the content under the repository corresponding to the URL.

**Select Branch**: The branch of the Git repository to sync. After selecting this branch, the task information under the current branch will be obtained and synced. This also supports users in performing corresponding operations with the remote Git repository under the current branch, such as commit, push, branch merge, etc.

## Git Folder Operations

After creating a Git Folder, the content of the remote repository will be cloned to your workspace, and you can start using the supported Git operations.

> Singdata Studio will only clone content that complies with the Singdata task script specification. If there is content in the remote repository that does not comply with the specification, it will be automatically filtered out.

Click the "Git" button on the toolbar to open the Git operation panel. Through this panel, you can implement version control, collaboration, and CI/CD with the remote Git repository. The Git panel supports operations including: Commit and Push, Pull, Branch Merge, and visual diff comparison during commits.

1. The branch you are currently using. This is the branch you selected for cloning when creating the Git Folder. Switching to other branches is currently not supported.
2. Commit your work to the working branch and push the updated branch to the remote Git repository.
3. Each time the Git panel is opened, it automatically fetches the list of tasks that differ between the current version and the remote. When clicking on a specific task, the content differences are displayed on the right.
4. Pull the latest information from the remote.
5. Merge and Rebase. The merge function is used for `git merge` to merge the commit history of one branch into another branch. For Git beginners, it is recommended to use merge rather than rebase, because merge does not require forced push and does not rewrite commit history.

* If merge conflicts occur, resolve them in the Git Folder UI.
* If there are no conflicts, the merge operation will use `git push`.

6. Add a commit message, and optionally add a detailed description of the changes.
7. Display the current branch history.

^
