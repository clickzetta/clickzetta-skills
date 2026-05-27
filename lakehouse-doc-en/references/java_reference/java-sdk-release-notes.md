# Java SDK Release Notes
2023.10.20

The release notes include the following updates and changes for the Java SDK:

- Behavior Changes
- New Features
- Bug Fixes

## Version 1.1.1
### Bug Fixes
- Fixed correctness issues with igs in specific scenarios, improving program stability and reliability.
- Fixed the getColumns interface of jdbc database metadata to resolve the issue of inaccurate display of boolean type data.

### Example
If you encounter correctness issues when using igs, you can resolve this problem by upgrading to version 1.1.1. Additionally, if you experience inaccurate display of boolean type data when using the getColumns interface, you can get the fix by upgrading to this version.

## Version 1.1.2
### Bug Fixes
- Fixed the set query_tag feature, now supporting the filtering of extra quotes in the value, improving query accuracy.
- Optimized the put/get volume feature, now supporting the display of upload and download results, making it easier for users to view the operation progress.

### Example
1. When you need to set a query_tag, you might encounter issues with extra quotes in the value. Now, by upgrading to version 1.1.2, you can correctly filter these quotes, ensuring query accuracy.
2. When uploading and downloading files using volume, you might need to view the operation progress. After upgrading to version 1.1.2, you can easily view the upload and download results.

## Version 1.1.3 (Pending Implementation)
### Bug Fixes
- Fixed the issue where the igs client could not exit normally in special network failure scenarios, improving program stability.

### Expected Example
If you encounter the issue where the igs client cannot exit in special network failure scenarios, you can expect this to be resolved in version 1.1.3. This will improve program stability, ensuring normal exit in similar situations.