---
name: lakehouse-llms-index
description: |
  Generate or update the llms.txt and llms-full.txt (based on SUMMARY.md) for the Lakehouse help documentation repository,
  or verify whether the URLs in these two files are consistent with SUMMARY.md and up to date.
  Applicable to both the Singdata Chinese documentation (www.yunqi.tech) and the Singdata English documentation (singdata.com).
  Use when the user says "generate llms index", "update llms.txt/llms-full.txt", "verify document URLs", or "sync SUMMARY to llms".
---

# Lakehouse LLMs Index Generator

## Overview

`llms.txt` and `llms-full.txt` are LLM navigation index files for Lakehouse documentation, generated from `SUMMARY.md`. The files are hosted at `git@k.topthink.com:4v2dmg3x2e/k7pl9zonpy.git`, local path: `/Users/guanyangw/work/AI_CODE_COLLECTIONS/lakehouse/clickzetta-documents/`.

## Applicable Documentation Sites (Dual-Brand / Dual-Repository)

The documentation has two independent repositories and sites:

| Brand | Language | Local Repository | BASE_URL |
|------|------|----------|----------|
| Singdata (Chinese) | Chinese | `clickzetta-documents/` | `https://www.yunqi.tech/documents/` |
| Singdata | English | `singdata-documents-en/` | `https://singdata.com/documents/` |

When generating or verifying, first confirm the `BASE_URL` corresponding to the target repository. **Note: The Singdata domain is `singdata.com` (no www prefix, and not clickzetta.com).** If the user does not specify, default to the Singdata Chinese site `https://www.yunqi.tech/documents/`.

**Both sites use the same URL slug rules**: slug = filename from SUMMARY.md with `.md` removed, **preserving original case and separators** (verified via singdata.com sitemap.xml, e.g., `overview.md`→`overview`, `Ingestion.md`→`Ingestion`, `RemoteFunction-as-udf.md`→`RemoteFunction-as-udf`). The "URL Generation Rules" below apply to both sites; the only difference is the domain.

> ⚠️ Verification note: When determining the "actual live URL", **do not use the existing `llms-full.txt` in the repository as the live value** — it may itself be outdated/incorrect. To verify the real slugs, fetch the site's `sitemap.xml` (e.g., `https://singdata.com/sitemap.xml`), which is the authoritative source.

## Difference Between the Two Files

| File | Content Scope | Hierarchy |
|------|---------|------|
| `llms.txt` | Only top-level sections (`##`) and first-level sub-pages (`*` direct children, depth=0) | Flat, no indentation |
| `llms-full.txt` | All levels of pages in SUMMARY.md | 2-space indentation for hierarchy |

Both files use the same format:
```
- [Title](URL): one-sentence summary (30-50 words)
```

## URL Generation Rules

**Strictly concatenate by filename (including directory path), preserving original case:**

```
Remove .md suffix from filename → concatenate after BASE_URL
```

Examples (using Singdata English site; Chinese site only replaces domain with www.yunqi.tech):
- `overview.md` → `https://singdata.com/documents/overview`
- `LakehouseStudio-tour.md` → `https://singdata.com/documents/LakehouseStudio-tour`
- `eco_integration/sqlworkbench-j-lakehouse.md` → `https://singdata.com/documents/eco_integration/sqlworkbench-j-lakehouse`
- `sql_functions/aggregate_functions/avg.md` → `https://singdata.com/documents/sql_functions/aggregate_functions/avg`

**Note:** Do not perform any case conversion, camelCase transformation, or path simplification. Preserve the original file path exactly.

## Summary Source

Summaries are derived by reading the content of the corresponding `.md` files, 30-50 words, describing the core content of the document. Entries with existing summaries are reused directly; summaries are only generated for new entries.

## Generation Steps

### Step 1: Parse SUMMARY.md

```python
import re

# Select domain based on target repository
BASE_URL = "https://www.yunqi.tech/documents/"   # Singdata Chinese site
# BASE_URL = "https://singdata.com/documents/"   # Singdata English site (note: no www)

with open('SUMMARY.md', 'r') as f:
    lines = f.readlines()

entries = []  # (type, title, url, filepath, depth)
for line in lines:
    # Section title
    section = re.match(r'^## (.+)', line)
    if section:
        entries.append(('section', section.group(1).strip(), None, None, -1))
        continue
    # List item: number of indent spaces / 4 = depth
    item = re.match(r'^(\s*)\* \[(.+?)\]\((.+?)\)', line)
    if item:
        depth = len(item.group(1)) // 4
        title = item.group(2).strip()
        filepath = item.group(3).strip()
        url = BASE_URL + filepath[:-3]  # remove .md, preserve original path and case
        entries.append(('item', title, url, filepath, depth))
```

### Step 2: Reuse Existing Summaries

```python
with open('llms-full.txt', 'r') as f:
    existing_txt = f.read()

existing = {}
for line in existing_txt.split('\n'):
    # Compatible with both domains
    m = re.match(r'\s*- \[.+?\]\((https://[^)]+)\): (.+)', line)
    if m:
        # Use .md path as key to reuse summaries, avoiding key mismatch due to domain changes
        path = re.sub(r'https://[^/]+/documents/', '', m.group(1))
        existing[path] = m.group(2)
```

### Step 3: Generate Summaries for New Entries

For entries where `path not in existing`, read the first 100 lines of the corresponding `.md` file and generate a 30-50 word summary.

### Step 4: Generate llms-full.txt

All entries, following the SUMMARY.md hierarchy, with sub-items indented by 2 spaces × depth:

```python
indent = "  " * depth
line = f"{indent}- [{title}]({url}): {summary}"
```

### Step 5: Generate llms.txt

Keep only:
- `##` section titles (converted to `## Section Name` format)
- Top-level pages at depth=0 (`*` direct children, no indentation)

## URL Verification

Check whether the URLs in `llms-full.txt` are consistent with the current SUMMARY.md:

```python
# Extract all valid URLs from SUMMARY.md
valid_urls = {BASE_URL + f[:-3] for _, _, _, f, _ in entries if f}

# Extract all URLs from llms-full.txt (by current brand domain)
domain = BASE_URL.split('/documents/')[0]  # https://www.yunqi.tech or https://singdata.com
used_urls = set(re.findall(re.escape(domain) + r'/documents/[^\)]+', full_txt))

# Identify issues
stale = used_urls - valid_urls      # in llms-full.txt but not in SUMMARY.md (old paths/deleted)
missing = valid_urls - used_urls    # in SUMMARY.md but not in llms-full.txt (new pages)
```

Common issues:
- Old notation for `eco_integration/` subdirectory (without path prefix) → should be updated to full path
- New pages in SUMMARY.md not synced to llms-full.txt
- Domain inconsistency: files with mixed singdata.com links → should be unified to the target site domain (Chinese site: www.yunqi.tech, English site: singdata.com)

> ⚠️ **Never treat the existing `llms-full.txt` (or `llms.txt`) as the authoritative source for "actual live URLs".**
> These files themselves may be outdated/incorrect (old slugs, wrong domains, etc.) — they are the objects being verified, not the basis for verification.
> The consistency check above only guarantees that the "llms files are self-consistent with SUMMARY.md"; **it does not guarantee that the URLs are actually accessible online**.
> If the filenames in SUMMARY.md differ from the published slugs online, the consistency check cannot detect this. To confirm URLs are truly valid, you must cross-check with the sitemap below.

### Sitemap Cross-Verification (Live URL Authority)

The site's `sitemap.xml` is the **sole authoritative source** for live URLs. Fetch it and cross-compare with URLs generated from SUMMARY.md:

```python
import re, urllib.request

# Chinese site: https://www.yunqi.tech/sitemap.xml ; English site: https://singdata.com/sitemap.xml
SITEMAP_URL = "https://singdata.com/sitemap.xml"
sitemap_xml = urllib.request.urlopen(SITEMAP_URL).read().decode("utf-8")

# Extract all /documents/ page URLs from sitemap, normalize domain (remove www. prefix differences)
def norm(u):
    return re.sub(r'https://(www\.)?', 'https://', u).rstrip('/')

sitemap_urls = {norm(u) for u in re.findall(r'<loc>(https://[^<]+/documents/[^<]+)</loc>', sitemap_xml)}
valid_norm   = {norm(u) for u in valid_urls}   # valid_urls from SUMMARY.md (see above)

# Cross-comparison
in_sitemap  = valid_norm & sitemap_urls   # published online → can verify with real URL
not_in_sitemap = valid_norm - sitemap_urls  # not online → treat as new file (not yet published)
orphan      = sitemap_urls - valid_norm    # online but not in SUMMARY → possibly missing pages

print("Published, verifiable via sitemap:", len(in_sitemap))
print("New files (not in sitemap, rule-based only):", len(not_in_sitemap))
for u in sorted(not_in_sitemap)[:30]:
    print("   NEW_FILE:", u)
```

Interpretation (key points):
- **Sitemap hit** → The URL is published online; the real URL can confirm the slug is correct. The higher the hit rate, the more reliable the slug rules.
- **Sitemap miss** → **This is a new file** (added to SUMMARY.md / git, but not yet published to the online help docs).
  - A miss **does not mean the URL is wrong**: the page simply does not exist online yet, so there is no real URL to compare against, and HTTP probing will necessarily fail (page not published). Therefore, **online verification is not applicable to new files**.
  - For new files, **fall back to slug rule judgment only** (filename minus `.md`, preserving original case and separators); live URL verification is not possible.
- Therefore: **never treat "sitemap miss" as a signal that the slug rule is wrong**. To judge whether the slug rule itself is correct, only look at the sitemap **hits** — if even many long-published pages fail to match the sitemap, then the rule is wrong.
- The sitemap may be paginated (sitemap_index.xml) or trimmed by JS-rendered sites; make sure to fetch it completely and normalize `www.` prefix differences.

## File Header Format

**llms.txt:**
```markdown
# Singdata Lakehouse Documentation (LLM Navigation)

> Singdata Lakehouse is a fully managed lakehouse architecture platform... (product introduction)
```

**llms-full.txt:**
```markdown
# Lakehouse Documentation (LLM Full Index)

> Singdata Lakehouse is a fully managed lakehouse architecture platform... (product introduction)
```

> If the target is the Singdata English site, replace brand names in titles and introductions with Singdata, use the `singdata.com` domain (no www prefix) for body URLs, and apply the same slug rules as the Chinese site (filename minus .md, preserve original case).
