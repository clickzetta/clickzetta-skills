# Python Task Package Installation and Import Guide

This guide explains how to temporarily install third-party packages at Python task runtime and import them in subsequent code.

## Applicable Scenarios

* Need to temporarily install third-party packages at task runtime.
* Need to install packages from PyPI or a package mirror such as the Tsinghua mirror.
* Need to install packages to a temporary directory under `/tmp` before `import`.

## Runtime Installation Notes

* Python tasks run in temporary Pods, and the environment is destroyed after the task completes. Dependencies must be reinstalled on every run; do not rely on a previous installation.
* Python tasks run as a non-root user and cannot install dependencies into the system-level `site-packages` directory. Use `--target` to install packages into a dedicated temporary directory under `/tmp`, and add that directory to `sys.path` before importing.
* `/tmp` is available only for temporary files during the current task run. Do not use it for data that must persist after the task completes.

> ⚠️ **Note**: Do not install dependencies under `/home` or into system Python directories. Python tasks do not guarantee that these directories are writable.

## Standard Template (Recommended for Direct Reuse)

```python
import subprocess
import sys

TARGET_DIR = "/tmp/python_packages"
INDEX_URL = "https://pypi.org/simple"

subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "config",
    "--target", TARGET_DIR,
    "--index-url", INDEX_URL,
    "--no-cache-dir",
])
sys.path.insert(0, TARGET_DIR)

import config
```

## Quick Switch to Tsinghua Mirror

If access to PyPI is slow, change `INDEX_URL` in the template to the Tsinghua mirror:

```python
INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

## Common Errors and Troubleshooting

### Error: `ModuleNotFoundError: No module named 'xxx'`

Check in order:

* Whether `--target` was used but that directory was not added to `sys.path`.
* Whether the directory was added to `sys.path` only after the `import` statement.
* Whether `sys.path.append()` added the path at the end, allowing another module with the same name to shadow the installed package. Use `sys.path.insert(0, TARGET_DIR)` instead.
* Whether the package name and module name match (some packages are `pip install A`, but `import B`).

### Error: `Permission denied`

Check whether `--target` points to a directory under `/tmp`. Do not use `/home`, the system `site-packages` directory, or any other directory that is not explicitly documented as writable.
