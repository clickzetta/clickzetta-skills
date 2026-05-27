# Python Task Package Installation and Import Guide

This guide explains how to install distribution packages from the official source or Tsinghua mirror in Python tasks, and import them stably for subsequent use.

## Applicable Scenarios

* Need to temporarily install third-party packages at task runtime.
* Need to install packages from the public internet official source (PyPI) or a domestic mirror (such as Tsinghua mirror).
* Need to install packages to a custom directory (e.g., `/home/system_normal`) before `import`.

## Runtime Installation Notes

* Python tasks run in temporary Pods, and the environment is destroyed after the task completes. Therefore, dependencies must be reinstalled on every run; do not rely on "previous installation results".
* You must use `--target` for installation, and you must add that directory to `sys.path` before importing. This is because the current Python runtime environment does not have root privileges and cannot install to the global site-packages directory; packages can only be installed to a user directory (e.g., `/home/system_normal`).
* Tsinghua mirror (optional when network is restricted): `https://pypi.tuna.tsinghua.edu.cn/simple`

## Standard Template (Recommended for Direct Reuse)

```python
import subprocess
import sys

TARGET_DIR = "/home/system_normal"
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "config",
    "--target", TARGET_DIR,
    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
])
sys.path.append(TARGET_DIR)

from config import *
```


## Quick Switch to Tsinghua Mirror

Simply change the `INDEX_URL` in the template to:

```python
INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

## Common Errors and Troubleshooting

### Error: `ModuleNotFoundError: No module named 'xxx'`

Check in order:

* Whether `--target` was used but that directory was not added to `sys.path`.
* Whether the path was appended after `import` (incorrect order).
* Whether the path was appended with `append` to the end, causing it to be shadowed by other paths.
* Whether the package name and module name match (some packages are `pip install A`, but `import B`).
