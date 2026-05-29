# Environment Setup & Project Configuration

## Environment Setup

```bash
# Option 1: venv (recommended)
python3.12 -m venv .venv
source .venv/bin/activate          # macOS/Linux
pip install clickzetta_zettapark_python clickzetta-connector-python \
    python-dotenv pandas numpy scikit-learn pyarrow jupyterlab matplotlib seaborn \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# Option 2: pyenv (when you need to switch Python versions)
pyenv install 3.12.9 && pyenv local 3.12.9
python -m venv .venv && source .venv/bin/activate
pip install clickzetta_zettapark_python clickzetta-connector-python \
    python-dotenv pandas numpy scikit-learn pyarrow jupyterlab matplotlib seaborn \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# Option 3: conda
conda create -n lakehouse-ds python=3.12 -y && conda activate lakehouse-ds
pip install clickzetta_zettapark_python clickzetta-connector-python \
    python-dotenv pandas numpy scikit-learn pyarrow jupyterlab matplotlib seaborn \
    -i https://pypi.tuna.tsinghua.edu.cn/simple
```

| Issue | Fix |
|------|------|
| Python 3.8/3.9 | `pyenv install 3.12.9` or `python3.12 -m venv .venv` |
| `pyarrow` version conflict | `pip install pyarrow==14.0.0` |
| M1/M2 Mac error | `pip install --no-binary :all:` or use conda |
| Connection timeout | VCluster not started — start it manually in Studio |

---

## Jupyter Kernel Configuration

```bash
# Register the venv as a Jupyter kernel (critical — otherwise notebook uses system Python)
source .venv/bin/activate
pip install ipykernel jupyterlab
python -m ipykernel install --user --name lakehouse-ds --display-name "Python (lakehouse-ds)"

# Start JupyterLab
jupyter lab --port=8888
```

VS Code / Cursor: open `.ipynb` → top-right "Select Kernel" → choose "Python (lakehouse-ds)"

| Issue | Fix |
|------|------|
| `ModuleNotFoundError: clickzetta` | Wrong kernel selected — switch to the registered venv kernel |
| `.env` not loading | Use `load_dotenv(dotenv_path='../.env')` with an explicit path |
| `to_pandas()` OOM | Add `TABLESAMPLE ROW(1)` or `LIMIT` |
| Charts not showing | Add `%matplotlib inline` at the top of the notebook |

---

## src/config.py Template

```python
import os, sys
from pathlib import Path
from dotenv import load_dotenv
from clickzetta.zettapark.session import Session
import clickzetta

# Search for .env in multiple locations
for _p in [
    Path(__file__).parent.parent / ".env",
    Path.home() / ".config" / "kilo" / ".env",
    Path.home() / ".czcode" / ".env",
    Path.home() / ".env",
]:
    if _p.exists():
        load_dotenv(dotenv_path=_p)
        break

def check_environment():
    """Call from 00-env-check.ipynb to print environment diagnostics."""
    ver = sys.version_info
    if ver < (3, 10):
        raise RuntimeError(
            f"Python {ver.major}.{ver.minor} does not meet requirements. ZettaPark requires Python 3.10+.\n"
            "Upgrade: brew install pyenv && pyenv install 3.12.9 && pyenv local 3.12.9"
        )
    print(f"✅ Python {ver.major}.{ver.minor}.{ver.micro}")
    for pkg, mod in [
        ("clickzetta_zettapark_python", "clickzetta.zettapark"),
        ("clickzetta-connector-python", "clickzetta"),
        ("pandas", "pandas"), ("python-dotenv", "dotenv"),
    ]:
        try:
            m = __import__(mod.split(".")[0])
            print(f"✅ {pkg}: {getattr(m, '__version__', 'ok')}")
        except ImportError:
            print(f"❌ {pkg}: not installed → pip install {pkg}")
    try:
        s = get_session()
        print(f"✅ Lakehouse: {s.sql('SELECT current_workspace(), current_user()').collect()}")
    except Exception as e:
        print(f"❌ Lakehouse connection failed: {e}")

def get_session() -> Session:
    return Session.builder.configs({
        "service":   os.environ["CLICKZETTA_SERVICE"],
        "instance":  os.environ["CLICKZETTA_INSTANCE"],
        "workspace": os.environ["CLICKZETTA_WORKSPACE"],
        "username":  os.environ["CLICKZETTA_USERNAME"],
        "password":  os.environ["CLICKZETTA_PASSWORD"],
        "vcluster":  os.environ.get("CLICKZETTA_VCLUSTER", "default_ap"),
        "schema":    os.environ.get("CLICKZETTA_SCHEMA", "public"),
    }).create()

def get_connector_connection():
    """For pd.read_sql only. Do NOT use with df.to_sql()."""
    return clickzetta.connect(
        service=os.environ["CLICKZETTA_SERVICE"],
        instance=os.environ["CLICKZETTA_INSTANCE"],
        workspace=os.environ["CLICKZETTA_WORKSPACE"],
        username=os.environ["CLICKZETTA_USERNAME"],
        password=os.environ["CLICKZETTA_PASSWORD"],
        vcluster=os.environ.get("CLICKZETTA_VCLUSTER", "default_ap"),
        schema=os.environ.get("CLICKZETTA_SCHEMA", "public"),
    )
```

---

## .env Template

```bash
CLICKZETTA_SERVICE=cn-shanghai-alicloud.api.clickzetta.com
CLICKZETTA_INSTANCE=<instance-id>
CLICKZETTA_WORKSPACE=<workspace>
CLICKZETTA_USERNAME=<username>
CLICKZETTA_PASSWORD=<password>
CLICKZETTA_VCLUSTER=default_ap
CLICKZETTA_SCHEMA=ds_workspace
```

## pyproject.toml

```toml
[project]
name = "my-lakehouse-ds-project"
requires-python = ">=3.10"
dependencies = [
    "clickzetta_zettapark_python>=0.1.2",
    "clickzetta-connector-python>=1.0.0",
    "python-dotenv>=1.0.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "pyarrow>=14.0.0",
    "jupyterlab>=4.0.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
]
```
