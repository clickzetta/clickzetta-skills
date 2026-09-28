#!/usr/bin/env python3
"""Shared helpers for the clickzetta-ossie-interop scripts.

Contents:
  * YAML / JSON loading and dumping (block-style YAML, stable key order)
  * cz-cli JSON result normalisation (tolerates several output envelopes)
  * A small quote/bracket-aware scanner used to parse SHOW CREATE SEMANTIC VIEW
  * Type mapping between ClickZetta SQL types and Ossie DataType
  * The "sidecar" codec that stores Ossie-only metadata in semantic view PROPERTIES
  * Ossie plugin-style issue collection
"""
from __future__ import annotations

import base64
import json
import re
import sys
import zlib
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - reported to the user by each script
    yaml = None

OSSIE_VERSION = "0.2.0.dev0"
VENDOR = "CLICKZETTA"
SIDECAR_KEY_PREFIX = "ossie_sidecar_"
SIDECAR_MAGIC = "OSSIE1"
SIDECAR_CHUNK = 2000          # characters of base64 per property value
TEMPORAL = {"Date", "Time", "DateTime", "DateTimeTz"}
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def need_yaml() -> None:
    if yaml is None:
        sys.stderr.write("PyYAML is required: python3 -m pip install pyyaml\n")
        sys.exit(2)


class CliError(Exception):
    """Input the caller can fix: a file that cannot be read, or that is not an Ossie file.

    Raising this instead of letting an OSError / YAMLError escape gives the user one clear
    sentence rather than a Python traceback. `run_cli` turns it into exit code 2.
    """


def run_cli(main) -> None:
    """Run a script body, reporting CliError as a one-line message and exit code 2.

    Exit codes are the same across every script in this skill:
      0  ran, nothing to report
      1  ran, and found problems (invalid model, differences, error-level issues)
      2  could not run at all (unreadable input, not an Ossie file, bad usage)
    """
    try:
        main()
    except CliError as exc:
        sys.stderr.write(f"error: {exc}\n")
        sys.exit(2)
    except BrokenPipeError:          # e.g. piping into head/less
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)


# --------------------------------------------------------------------------- issues
class Issues:
    """Collects diagnostics using the Ossie CLI plugin shape {severity, message, path}."""

    def __init__(self) -> None:
        self.items: list[dict[str, str]] = []

    def add(self, severity: str, message: str, path: str = "") -> None:
        item = {"severity": severity, "message": message}
        if path:
            item["path"] = path
        self.items.append(item)

    def error(self, m: str, p: str = "") -> None:
        self.add("error", m, p)

    def warn(self, m: str, p: str = "") -> None:
        self.add("warning", m, p)

    def info(self, m: str, p: str = "") -> None:
        self.add("info", m, p)

    @property
    def has_errors(self) -> bool:
        return any(i["severity"] == "error" for i in self.items)

    def report(self, stream=sys.stderr) -> None:
        for i in self.items:
            loc = f" [{i['path']}]" if i.get("path") else ""
            stream.write(f"{i['severity'].upper():8}{loc} {i['message']}\n")

    def write_json(self, path: str | None) -> None:
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.items, fh, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- yaml io
class _Dumper(yaml.SafeDumper if yaml else object):  # type: ignore[misc]
    pass


if yaml:
    def _str_repr(dumper, data):
        style = "|" if "\n" in data else None
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)

    _Dumper.add_representer(str, _str_repr)

    def _ignore_aliases(self, data):  # never emit &anchors / *aliases
        return True

    _Dumper.ignore_aliases = _ignore_aliases


def read_text(path: str) -> str:
    """Read a UTF-8 text file, reporting anything that goes wrong as a CliError."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        raise CliError(f"file not found: {path}") from None
    except IsADirectoryError:
        raise CliError(f"not a file: {path}") from None
    except UnicodeDecodeError as exc:
        raise CliError(f"{path} is not UTF-8 text: {exc}") from None
    except OSError as exc:
        raise CliError(f"cannot read {path}: {exc.strerror or exc}") from None


def load_yaml(path: str) -> Any:
    need_yaml()
    text = read_text(path)
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise CliError(f"{path} is not valid YAML: {str(exc).splitlines()[0]}") from None
    if doc is None:
        raise CliError(f"{path} is empty")
    return doc


def load_json_file(path: str) -> Any:
    text = read_text(path)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise CliError(f"{path} is not valid JSON: {exc.msg} "
                       f"(line {exc.lineno}, column {exc.colno})") from None


def dump_yaml(obj: Any, path: str | None = None) -> str:
    need_yaml()
    text = yaml.dump(obj, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=100)
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return text


# --------------------------------------------------------------------------- cz-cli output
def _rows_from(obj: Any) -> list[dict] | None:
    """Find a list of row dicts inside an arbitrary cz-cli JSON envelope."""
    if isinstance(obj, list):
        if not obj:
            return []
        if all(isinstance(r, dict) for r in obj):
            return obj
        return None
    if isinstance(obj, dict):
        cols = None
        for ck in ("columns", "column_names", "header", "headers", "schema", "fields"):
            if isinstance(obj.get(ck), list):
                cols = [c if isinstance(c, str) else (c.get("name") if isinstance(c, dict) else str(c))
                        for c in obj[ck]]
                break
        for rk in ("rows", "data", "result", "results", "records", "items", "resultSet", "result_set"):
            if rk in obj:
                v = obj[rk]
                if isinstance(v, list) and v and isinstance(v[0], list) and cols:
                    return [dict(zip(cols, r)) for r in v]
                found = _rows_from(v)
                if found is not None:
                    return found
        if cols is not None and isinstance(obj.get("values"), list):
            return [dict(zip(cols, r)) for r in obj["values"]]
    return None


def parse_cli_rows(text: str) -> list[dict]:
    """Normalise cz-cli JSON output to a list of dicts with lower-case keys."""
    text = text.strip()
    if not text:
        return []
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # tolerate log lines before the JSON document
        start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
        if start < 0:
            raise
        obj = json.loads(text[start:])
    if isinstance(obj, dict) and isinstance(obj.get("error"), dict):
        raise ValueError("cz-cli error: " + str(obj["error"].get("message", obj["error"]))[:500])
    rows = _rows_from(obj)
    if rows is None:
        raise ValueError("unrecognised cz-cli JSON envelope: " + text[:300])
    return [{str(k).lower(): v for k, v in r.items()} for r in rows]


def as_list(value: Any) -> list[str]:
    """SHOW output list columns may be JSON arrays, '[a, b]' strings or 'a, b' strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    s = str(value).strip()
    if not s or s.lower() in ("null", "none", "[]"):
        return []
    if s.startswith("["):
        try:
            v = json.loads(s)
            if isinstance(v, list):
                return [str(x).strip() for x in v if str(x).strip()]
        except json.JSONDecodeError:
            s = s[1:-1]
    parts = [p.strip().strip("'\"`") for p in s.split(",")]
    return [p for p in parts if p]


# --------------------------------------------------------------------------- SQL scanner
def split_top(text: str, sep: str = ",") -> list[str]:
    """Split on `sep` outside quotes, parentheses and brackets."""
    out, buf, depth, q = [], [], 0, None
    i = 0
    while i < len(text):
        ch = text[i]
        if q:
            buf.append(ch)
            if ch == q:
                if i + 1 < len(text) and text[i + 1] == q and q in "'\"":
                    buf.append(text[i + 1])
                    i += 1
                else:
                    q = None
            elif ch == "\\" and q in "'\"" and i + 1 < len(text):
                buf.append(text[i + 1])
                i += 1
        elif ch in "'\"`":
            q = ch
            buf.append(ch)
        elif ch in "([{":
            depth += 1
            buf.append(ch)
        elif ch in ")]}":
            depth -= 1
            buf.append(ch)
        elif ch == sep and depth == 0:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def strip_sql_comments(text: str) -> str:
    """Remove -- line comments and /* */ block comments outside quotes."""
    out, i, q = [], 0, None
    while i < len(text):
        ch = text[i]
        if q:
            out.append(ch)
            if ch == q:
                q = None
            elif ch == "\\" and i + 1 < len(text):
                out.append(text[i + 1])
                i += 1
        elif ch in "'\"`":
            q = ch
            out.append(ch)
        elif text.startswith("--", i):
            j = text.find("\n", i)
            i = len(text) if j < 0 else j
            continue
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = len(text) if j < 0 else j + 2
            continue
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def top_level_mask(text: str) -> list[bool]:
    """mask[i] is True when text[i] is outside quotes and brackets."""
    mask, depth, q = [], 0, None
    i = 0
    while i < len(text):
        ch = text[i]
        if q:
            mask.append(False)
            if ch == q:
                if i + 1 < len(text) and text[i + 1] == q and q in "'\"":
                    mask.append(False)
                    i += 1
                else:
                    q = None
        elif ch in "'\"`":
            q = ch
            mask.append(False)
        elif ch in "([{":
            mask.append(depth == 0)
            depth += 1
        elif ch in ")]}":
            depth -= 1
            mask.append(depth == 0)
        else:
            mask.append(depth == 0)
        i += 1
    return mask


def find_top(text: str, pattern: str, start: int = 0, flags=re.I) -> re.Match | None:
    """First regex match that starts at a top-level position."""
    mask = top_level_mask(text)
    for m in re.compile(pattern, flags).finditer(text, start):
        if mask[m.start()]:
            return m
    return None


def matching_paren(text: str, open_idx: int) -> int:
    depth, q = 0, None
    i = open_idx
    while i < len(text):
        ch = text[i]
        if q:
            if ch == q:
                if i + 1 < len(text) and text[i + 1] == q and q in "'\"":
                    i += 1
                else:
                    q = None
        elif ch in "'\"`":
            q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced parentheses")


def unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        # ClickZetta escapes with backslash ('it\'s'); a doubled quote is NOT an escape there
        # ('it''s' is two adjacent literals and reads back as "its").
        out, i, body = [], 0, s[1:-1]
        while i < len(body):
            if body[i] == "\\" and i + 1 < len(body):
                out.append({"n": "\n", "t": "\t", "r": "\r"}.get(body[i + 1], body[i + 1]))
                i += 2
            else:
                out.append(body[i])
                i += 1
        return "".join(out)
    if len(s) >= 2 and s[0] == s[-1] == "`":
        return s[1:-1]
    return s


def sql_str(s: str) -> str:
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


def _pipes_to_concat(e: str) -> str:
    """a || b || c -> concat(concat(a,b),c), at every parenthesis level (ClickZetta stores it that way)."""
    out, i, q = [], 0, None
    while i < len(e):  # recurse into parentheses first
        ch = e[i]
        if q:
            out.append(ch)
            if ch == q:
                q = None
            elif ch == "\\" and i + 1 < len(e):
                out.append(e[i + 1])
                i += 1
        elif ch in "'\"":
            q = ch
            out.append(ch)
        elif ch == "(":
            close = matching_paren(e, i)
            out.append("(" + _pipes_to_concat(e[i + 1:close]) + ")")
            i = close
        else:
            out.append(ch)
        i += 1
    text = "".join(out)
    parts, buf, depth, q, j = [], [], 0, None, 0
    while j < len(text):  # split on || outside quotes and parentheses
        ch = text[j]
        if q:
            if ch == q:
                q = None
            elif ch == "\\" and j + 1 < len(text):
                buf.append(ch)
                j += 1
                ch = text[j]
        elif ch in "'\"":
            q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "|" and depth == 0 and text[j:j + 2] == "||":
            parts.append("".join(buf).strip())
            buf, j = [], j + 2
            continue
        buf.append(ch)
        j += 1
    parts.append("".join(buf).strip())
    if len(parts) < 2:
        return text
    acc = parts[0]
    for p in parts[1:]:
        acc = f"concat({acc},{p})"
    return acc


def norm_expr(e: str | None) -> str:
    """Whitespace/case/backtick-insensitive form used to compare expressions. Also folds the
    rewrites ClickZetta applies when it stores a view: `||` -> concat(), ORDER BY ... ASC."""
    if e is None:
        return ""
    e = e.replace("`", "")
    if "||" in e:
        try:
            e = _pipes_to_concat(e)
        except (ValueError, IndexError):
            pass
    e = re.sub(r"\s+", " ", e).strip()
    e = re.sub(r"\s+asc\b", "", e, flags=re.I)
    e = re.sub(r"\s*([(),.*/+\-=<>])\s*", r"\1", e)
    return e.lower()


# Words that must be back-quoted when used as a bare column or member name.
SQL_KEYWORDS = set("""ALL AND AS ASC BETWEEN BY CASE CAST CURRENT DATE DAY DEFAULT DESC DIMENSIONS DISTINCT ELSE END
EXISTS FACTS FALSE FILTER FROM FULL GROUP HAVING HOUR IN INTERVAL IS JOIN KEY LEFT LIKE LIMIT METRICS MINUTE MONTH
NOT NULL ON OR ORDER OUTER OVER PARTITION PRIMARY PRIVATE PUBLIC RANGE REFERENCES RELATIONSHIPS RIGHT ROW ROWS SECOND
SELECT SYNONYMS TABLE TABLES THEN TIME TIMESTAMP TRUE UNION USER VALUES VARIABLES WHEN WHERE WITH YEAR""".split())


def ident(name: str) -> str:
    if IDENT_RE.match(name) and name.upper() not in SQL_KEYWORDS:
        return name
    return "`" + name.replace("`", "``") + "`"


def quote_bare(expr: str) -> str:
    """Back-quote an expression that is only a (possibly qualified) keyword column name."""
    parts = expr.strip().split(".")
    if all(IDENT_RE.match(p) for p in parts) and any(p.upper() in SQL_KEYWORDS for p in parts):
        return ".".join(ident(p) for p in parts)
    return expr


# Words never taken as column references when qualifying a field expression.
_NON_COLUMN = SQL_KEYWORDS | set("""ANY ARRAY BIGINT BINARY BOOLEAN CHAR DECIMAL DOUBLE ESCAPE EXTRACT FIRST FLOAT
FOLLOWING IGNORE INT INTEGER LAST MAP NULLS PRECEDING RESPECT SMALLINT STRING STRUCT TIMESTAMP_LTZ TIMESTAMP_NTZ
TINYINT UNBOUNDED VARCHAR WEEK QUARTER""".split())


def qualify_columns(expr: str, alias, exclude: set[str] | frozenset = frozenset()) -> str:
    """Prefix unqualified column references in a field expression with `alias.`.

    ClickZetta resolves `<alias>.<member> AS <expr>` against every logical table, so a bare
    `distance` is ambiguous as soon as two tables have that column. Identifiers followed by `(`
    (functions), already-qualified names, keywords, type names after AS, date parts after
    INTERVAL <n> or before FROM (EXTRACT), and names in `exclude` (lower-case; e.g. VARIABLES) are left alone.
    `alias` may be a callable name -> alias|None to resolve each bare name separately.
    """
    toks = re.findall(r"'(?:[^'\\]|\\.|'')*'|\"(?:[^\"\\]|\\.)*\"|`(?:[^`]|``)+`|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|\s+|.",
                      expr)
    out: list[str] = []
    sig: list[str] = []  # significant (non-space) tokens seen so far

    def nxt(i: int) -> str:
        for t in toks[i + 1:]:
            if not t.isspace():
                return t
        return ""

    for i, t in enumerate(toks):
        is_word = bool(re.match(r"[A-Za-z_]", t)) or (t.startswith("`") and len(t) > 1)
        if is_word:
            prev = sig[-1] if sig else ""
            prev2 = sig[-2] if len(sig) > 1 else ""
            n = nxt(i)
            bare = t.strip("`").upper()
            skip = (prev == "." or n in (".", "(") or (not t.startswith("`") and bare in _NON_COLUMN)
                    or prev.upper() == "AS" or n.upper() == "FROM" and prev == "("
                    or prev2.upper() == "INTERVAL" or t.strip("`").lower() in exclude)
            if not skip:
                target = alias(t.strip("`")) if callable(alias) else alias
                if target:
                    t = f"{ident(target)}.{t}"
        out.append(t)
        if not t.isspace():
            sig.append(toks[i])
    return "".join(out)


def snake(name: str) -> str:
    s = re.sub(r"[^0-9A-Za-z]+", "_", name).strip("_")
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()
    if not s or s[0].isdigit():
        s = "f_" + s
    return s


def pascal(name: str) -> str:
    parts = re.split(r"[^0-9A-Za-z]+", name)
    out = "".join(p[:1].upper() + p[1:] for p in parts if p)
    return out or "Concept"


# --------------------------------------------------------------------------- types
def cz_to_ossie_type(t: str | None) -> tuple[str | None, str | None]:
    """ClickZetta SQL type -> (Ossie DataType, raw type to keep when Opaque)."""
    if not t:
        return None, None
    u = str(t).strip().upper()
    base = re.split(r"[\s(<]", u, 1)[0]
    if base in ("TINYINT", "SMALLINT", "INT", "INTEGER", "BIGINT", "LONG", "SHORT", "BYTE"):
        return "Integer", None
    if base in ("DECIMAL", "NUMERIC", "NUMBER"):
        return "Decimal", None
    if base in ("FLOAT", "DOUBLE", "REAL"):
        return "Float", None
    if base in ("STRING", "VARCHAR", "CHAR", "TEXT"):
        return "String", None
    if base in ("BOOLEAN", "BOOL"):
        return "Boolean", None
    if base == "DATE":
        return "Date", None
    if base in ("TIMESTAMP_NTZ", "DATETIME"):
        return "DateTime", None
    if base in ("TIMESTAMP", "TIMESTAMP_LTZ"):
        return "DateTimeTz", None
    if base == "TIME":
        return "Time", None
    return "Opaque", str(t).strip()


# --------------------------------------------------------------------------- extensions
def get_ext(obj: dict, vendor: str = VENDOR) -> dict:
    for ext in obj.get("custom_extensions") or []:
        if str(ext.get("vendor_name", "")).upper() == vendor:
            try:
                data = json.loads(ext.get("data") or "{}")
                return data if isinstance(data, dict) else {"value": data}
            except json.JSONDecodeError:
                return {}
    return {}


def other_exts(obj: dict, vendor: str = VENDOR) -> list[dict]:
    return [e for e in obj.get("custom_extensions") or []
            if str(e.get("vendor_name", "")).upper() != vendor]


def set_ext(obj: dict, data: dict, vendor: str = VENDOR) -> None:
    data = {k: v for k, v in data.items() if v not in (None, [], {}, "")}
    exts = other_exts(obj, vendor)
    if data:
        exts.append({"vendor_name": vendor,
                     "data": json.dumps(data, ensure_ascii=False, sort_keys=True)})
    if exts:
        obj["custom_extensions"] = exts
    else:
        obj.pop("custom_extensions", None)


# --------------------------------------------------------------------------- sidecar
def encode_sidecar(data: dict) -> list[tuple[str, str]]:
    """Return [(property_key, property_value)] chunks. Values contain only [A-Za-z0-9+/=:]."""
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    b64 = base64.b64encode(zlib.compress(raw, 9)).decode()
    chunks = [b64[i:i + SIDECAR_CHUNK] for i in range(0, len(b64), SIDECAR_CHUNK)] or [""]
    n = len(chunks)
    return [(f"{SIDECAR_KEY_PREFIX}{i}", f"{SIDECAR_MAGIC}:{i}:{n}:{c}") for i, c in enumerate(chunks)]


def decode_sidecar(text: str) -> dict | None:
    """Find sidecar chunks anywhere in `text` (e.g. raw DESC EXTENDED output)."""
    found: dict[int, str] = {}
    total = None
    for m in re.finditer(rf"{SIDECAR_MAGIC}:(\d+):(\d+):([A-Za-z0-9+/=]*)", text):
        i, n, c = int(m.group(1)), int(m.group(2)), m.group(3)
        total = n
        found.setdefault(i, c)
    if total is None:
        return None
    if sorted(found) != list(range(total)):
        raise ValueError(f"sidecar incomplete: have chunks {sorted(found)} of {total}")
    blob = "".join(found[i] for i in range(total))
    return json.loads(zlib.decompress(base64.b64decode(blob)).decode())


def iter_dialects(expr: dict | None) -> Iterable[tuple[str, str]]:
    for d in (expr or {}).get("dialects") or []:
        yield str(d.get("dialect", "")), str(d.get("expression", ""))


def ansi(expression: str) -> dict:
    return {"dialects": [{"dialect": "ANSI_SQL", "expression": expression}]}
