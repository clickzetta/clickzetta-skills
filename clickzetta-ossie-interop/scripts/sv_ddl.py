#!/usr/bin/env python3
"""Parser for ClickZetta `CREATE SEMANTIC VIEW` text (as returned by SHOW CREATE SEMANTIC VIEW).

parse_ddl(text) -> {
  "name": "schema.view", "comment": str|None,
  "tables":        [{alias, source, primary_key, foreign_keys, synonyms, comment}],
  "relationships": [{name, from, from_columns, to, to_columns}],
  "variables":     [{name, type, default, comment}],
  "facts" / "dimensions" / "metrics":
                   [{table, name, expression, private, synonyms, is_unique, is_time,
                     enum_values, comment, using (metrics only: relationship names)}],
}
"""
from __future__ import annotations

import re

from czossie_common import find_top, matching_paren, read_text, run_cli, split_top, strip_sql_comments, unquote

CLAUSES = ["TABLES", "RELATIONSHIPS", "VARIABLES", "FACTS", "DIMENSIONS", "METRICS"]
QSTR = r"'(?:[^'\\]|\\.|'')*'"
META_START = (r"\bWITH\s+SYNONYMS\b|\bis_unique\s*=|\bis_time\s*=|\benum_values\s*=|"
              r"\bCOMMENT\b")


def _name(tok: str) -> str:
    return ".".join(unquote(p) for p in split_dotted(tok.strip()))


def split_dotted(tok: str) -> list[str]:
    parts, buf, q = [], [], None
    for ch in tok:
        if q:
            buf.append(ch)
            if ch == q:
                q = None
        elif ch in "`\"":
            q = ch
            buf.append(ch)
        elif ch == ".":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return [p.strip() for p in parts]


def _paren_list(text: str, start_pat: str) -> tuple[list[str] | None, int, int]:
    m = find_top(text, start_pat)
    if not m:
        return None, -1, -1
    open_idx = text.index("(", m.end() - 1) if text[m.end() - 1] == "(" else text.index("(", m.end())
    close = matching_paren(text, open_idx)
    return [unquote(x) for x in split_top(text[open_idx + 1:close])], m.start(), close + 1


def _comment(text: str) -> str | None:
    m = re.search(rf"\bCOMMENT\s*=?\s*({QSTR})", text, re.I | re.S)
    return unquote(m.group(1)) if m else None


def parse_meta(meta: str) -> dict:
    out: dict = {}
    syn, _, _ = _paren_list(meta, r"\bWITH\s+SYNONYMS\s*=?\s*\(")
    if syn is not None:
        out["synonyms"] = syn
    for flag in ("is_unique", "is_time"):
        m = re.search(rf"\b{flag}\s*=\s*(true|false)\b", meta, re.I)
        if m:
            out[flag] = m.group(1).lower() == "true"
    m = re.search(r"\benum_values\s*=\s*\[", meta, re.I)
    if m:
        depth, i = 0, m.end() - 1
        while i < len(meta):
            if meta[i] == "[":
                depth += 1
            elif meta[i] == "]":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out["enum_values"] = [unquote(v) for v in split_top(meta[m.end():i])]
    c = _comment(meta)
    if c is not None:
        out["comment"] = c
    return out


def parse_member(item: str) -> dict:
    s = item.strip()
    private = False
    m = re.match(r"(PRIVATE|PUBLIC)\s+", s, re.I)
    if m:
        private = m.group(1).upper() == "PRIVATE"
        s = s[m.end():]
    as_m = find_top(s, r"\bAS\b")
    if not as_m:
        raise ValueError(f"cannot parse member (no AS): {item[:120]}")
    head = s[:as_m.start()]
    using = None
    um = re.search(r"\s+USING\s*\(([^)]*)\)\s*$", head, re.I)
    if um:  # metric path selection: <alias>.<metric> USING (<relationship>[, ...]) AS <expr>
        using = [unquote(x) for x in split_top(um.group(1))]
        head = head[:um.start()]
    full = _name(head)
    table, name = (full.rsplit(".", 1) if "." in full else (None, full))
    rest = s[as_m.end():]
    meta_m = find_top(rest, META_START)
    expr = rest[:meta_m.start()] if meta_m else rest
    meta = parse_meta(rest[meta_m.start():]) if meta_m else {}
    out = {"table": table, "name": name, "expression": expr.strip(), "private": private, **meta}
    if using:
        out["using"] = using
    return out


def parse_table(item: str) -> dict:
    s = item.strip()
    as_m = find_top(s, r"\bAS\b")
    alias = _name(s[:as_m.start()])
    rest = s[as_m.end():].strip()
    src_m = re.match(r"((?:`[^`]+`|\"[^\"]+\"|[\w$]+)(?:\s*\.\s*(?:`[^`]+`|\"[^\"]+\"|[\w$]+))*)", rest)
    source = _name(re.sub(r"\s+", "", src_m.group(1))) if src_m else rest.split()[0]
    pk, _, _ = _paren_list(rest, r"\bPRIMARY\s+KEY\s*\(")
    fks = []
    for fm in re.finditer(r"\bFOREIGN\s+KEY\s*\(([^)]*)\)\s*REFERENCES\s+([\w`\"]+)\s*(?:\(([^)]*)\))?",
                          rest, re.I):
        fks.append({"columns": [unquote(c) for c in split_top(fm.group(1))],
                    "to": _name(fm.group(2)),
                    "to_columns": [unquote(c) for c in split_top(fm.group(3) or "")]})
    syn, _, _ = _paren_list(rest, r"\bWITH\s+SYNONYMS\s*=?\s*\(")
    return {"alias": alias, "source": source, "primary_key": pk or [], "foreign_keys": fks,
            "synonyms": syn or [], "comment": _comment(rest)}


def parse_relationship(item: str) -> dict:
    s = item.strip()
    name = None
    m = re.match(r"([\w`\"]+)\s+AS\s+", s, re.I)
    if m:
        name, s = _name(m.group(1)), s[m.end():]
    m = re.match(r"([\w`\".]+)\s*\(([^)]*)\)\s*REFERENCES\s+([\w`\".]+)\s*(?:\(([^)]*)\))?", s, re.I | re.S)
    if not m:
        raise ValueError(f"cannot parse relationship: {item[:120]}")
    return {"name": name, "from": _name(m.group(1)),
            "from_columns": [unquote(c) for c in split_top(m.group(2))],
            "to": _name(m.group(3)),
            "to_columns": [unquote(c) for c in split_top(m.group(4) or "")]}


def parse_variable(item: str) -> dict:
    s = item.strip()
    comment = _comment(s)
    cm = re.search(rf"\bCOMMENT\s*=?\s*{QSTR}", s, re.I | re.S)
    if cm:
        s = s[:cm.start()].strip()
    m = re.match(r"([\w`\"]+)\s+(.*)$", s, re.S)
    name, rest = _name(m.group(1)), m.group(2).strip()
    default = None
    dm = find_top(rest, r"\bDEFAULT\b|=")
    if dm:
        default = rest[dm.end():].strip()
        rest = rest[:dm.start()].strip()
    return {"name": name, "type": rest, "default": default, "comment": comment}


def parse_ddl(text: str) -> dict:
    text = strip_sql_comments(text).strip().rstrip(";")
    head = re.search(r"SEMANTIC\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w`\".]+)", text, re.I)
    out: dict = {"name": _name(head.group(1)) if head else None}
    pos = head.end() if head else 0
    last_end = pos
    for clause in CLAUSES:
        m = find_top(text, rf"\b{clause}\s*\(", pos)
        items: list[str] = []
        if m:
            open_idx = m.end() - 1
            close = matching_paren(text, open_idx)
            items = [x for x in split_top(text[open_idx + 1:close]) if x.strip()]
            last_end = max(last_end, close + 1)
        key = clause.lower()
        if clause == "TABLES":
            out[key] = [parse_table(x) for x in items]
        elif clause == "RELATIONSHIPS":
            out[key] = [parse_relationship(x) for x in items]
        elif clause == "VARIABLES":
            out[key] = [parse_variable(x) for x in items]
        else:
            out[key] = [parse_member(x) for x in items]
    out["comment"] = _comment(text[last_end:])
    # inline FOREIGN KEY -> relationships (normalised form)
    for t in out["tables"]:
        for fk in t["foreign_keys"]:
            out["relationships"].append({"name": None, "from": t["alias"], "from_columns": fk["columns"],
                                         "to": fk["to"], "to_columns": fk["to_columns"]})
    return out


if __name__ == "__main__":
    import argparse
    import json

    def _cli() -> None:
        ap = argparse.ArgumentParser(
            description="Parse a CREATE SEMANTIC VIEW file (as returned by SHOW CREATE SEMANTIC VIEW) "
                        "and print its structure as JSON.")
        ap.add_argument("file")
        print(json.dumps(parse_ddl(read_text(ap.parse_args().file)), indent=2, ensure_ascii=False))

    run_cli(_cli)
