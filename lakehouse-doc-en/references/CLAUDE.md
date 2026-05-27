# Singdata Lakehouse Documentation — Collaboration Guidelines

## Documentation Quality Goals

Core user pain points: **content too shallow, lack of examples, slow updates, errors (typos + incorrect SQL)**.

Before delivering any document, self-check against these standards:

- After reading the first screen, the user can decide "is this feature right for my use case"
- Every SQL example has setup data + actual output, verified with cz-cli
- Critical warnings appear next to the parameter that triggers them, not only at the bottom
- No typos, no unverified SQL

---

## Content Quality Standards

### Concept Documents (Feature Introduction Pages)

The first screen must answer three questions:

1. **What is it**: One-sentence analogy using something the user already knows
2. **When to use it**: Comparison with similar features (table or brief explanation)
3. **Core mechanism**: The single most important working principle to build a mental model

Example (what a Dynamic Table first screen should contain):
> A Dynamic Table is like an "auto-refreshing query result table" — you define a SQL query, and the system incrementally computes and maintains the result. Use it to build ODS→DWD→ADS data pipelines. If you only need transparent query acceleration, use a Materialized View. If you only need logical encapsulation without storing data, use a View.

### SQL Reference Documents (Command Reference Pages)

**Purpose**: Users come here to look up uncertain syntax or parameter meanings. Organized by command structure.

**Fixed structure** (order must not change):

1. `# COMMAND NAME` — all-caps English (`MERGE INTO`)
2. `## Overview` — one sentence on purpose + positioning (when to use this command vs. alternatives)
3. `## Syntax` — code block annotated ` ```Plain `, use `<placeholder>` for parameters
4. `## Parameters` — each parameter describes behavior, format: what it does — when to use this value; critical constraints follow the parameter inline with `> ⚠️`
5. `## Examples` — three-part: setup data → core SQL → actual output
6. `## Notes` — summary of critical constraints (also inline next to parameters)
7. `## Related Documentation` — link to the corresponding usage guide

**Parameter description format**: describe behavior, not just definition.

```
# Bad:  `BUILD DEFERRED`: Boolean, controls whether to defer build
# Good: `BUILD DEFERRED`: Does not generate data at creation time; use when you want to
#        define the structure first and trigger the initial refresh manually.
#        Required when using CREATE OR REPLACE.
```

**Warnings first**: Critical constraints must appear in two places:
- Next to the parameter/feature that triggers them (`> ⚠️ Note: ...`)
- In the Notes section at the bottom (summary)

### Usage Guide Documents (SQL_*_Guide.md)

**Purpose**: Users come here when they have a clear business goal ("I need to do funnel analysis", "I need deduplication") and want complete, runnable examples. Organized by business scenario.

**Fixed structure** (order must not change):

1. `# Lakehouse X Guide` (or "X Operations Guide")
2. `## Overview` — 2-3 sentences on business context + quick navigation anchor list
3. `## SQL Commands Used` — table: Command/Function | Purpose | Use Case (for easy navigation to SQL reference pages)
4. `## Prerequisites` — CREATE TABLE + INSERT test data; all examples in the document share this one setup, do not create separate setups per scenario; test table names use `doc_` prefix (e.g., `doc_funnel_events`)
5. `## Scenario 1/2/3...` — each scenario: complete SQL → actual output (markdown table or code block) → result interpretation
6. `## Related Documentation` — link back to the corresponding SQL reference pages

**Quality standards**:
- Cover at least 2-3 real business variants (different grouping dimensions, different time granularities, etc.)
- Results must include interpretation explaining what the output means, not just numbers
- Do not repeat parameter syntax in guides; point to SQL reference pages for syntax details

### Key Difference Between the Two Document Types

| | SQL Reference | Usage Guide |
|---|---|---|
| User intent | Look up syntax/parameters | Complete a business task |
| Organized by | Command structure | Business scenario |
| Number of examples | Cover all parameter combinations | Cover typical business variants |
| Data setup | Each example has its own minimal data | Entire document shares one setup (`doc_` prefix) |
| Cross-references | Link to usage guide at the end | Link back to SQL reference at the end |

---

## SQL Validation Standards

**All SQL examples in all documents, whether command reference or usage guide, must be verified by actually running them. Guessing expected output is not allowed.** Any tool works: cz-cli, Lakehouse Studio, JDBC client — but output must come from actual execution.

### Validation Tool (cz-cli examples)

```bash
# Query
cz-cli sql "<SQL>" --profile aliyun_shanghai_prod --sync

# DDL/DML (CREATE TABLE, INSERT, ALTER)
cz-cli sql "CREATE TABLE ..." --profile aliyun_shanghai_prod --sync --write
```

### ⚠️ Hallucination Incident Log (Critical — Must Read)

**Row-level permission SQL does not exist**: Lakehouse has no `CREATE ROW ACCESS POLICY`, `ALTER TABLE ... ADD ROW ACCESS POLICY`, or any row-level permission DDL syntax. These statements were completely fabricated and appeared in documentation causing serious misguidance. Row-level permissions **exist only in the DataGPT Studio UI configuration**, not as Lakehouse SQL objects. They must not appear in the object model section and must not have any SQL examples. Lesson: security/permission features must be verified with cz-cli before writing documentation — never infer from other databases (Snowflake/BigQuery).

### Common Pitfalls (Traps Already Encountered — Read Before Writing)

**Numeric display**: `1.0` may actually return `1`, `[3.0, 8.0]` may return `[3, 8]`. Use actual output.

**JSON serialization**: The `count` field in `approx_top_k`/`approx_histogram` is a string type (`"3"` not `3`). JSON output has no space after colon (`{"x":1}` not `{"x": 1}`).

**Non-deterministic functions**: `ANY_VALUE` may return NULL. Do not hardcode specific values in examples; note non-determinism.

**FILTER clause**: Not all aggregate functions support it. `MEDIAN` does not; `GROUP_CONCAT ... SEPARATOR ... FILTER` errors (use `WM_CONCAT` instead).

**DISTINCT semantics**: `COLLECT_LIST_ON_ARRAY(DISTINCT ...)` deduplicates entire array rows, not elements within arrays.

**APPROX_HISTOGRAM boundary values**: Floating-point precision may produce `0.6499999999999999` instead of `0.65`.

**PERCENT_RANK**: Takes no arguments. `percent_rank(col)` errors; correct form is `PERCENT_RANK()`.

**TABLE_CHANGES timestamps**: Only accepts literal constants; expressions like `NOW() - INTERVAL 1 HOUR` are not supported. `DESC HISTORY` returns UTC time; note timezone when querying (default UTC+8).

**GROUP_BITMAP series**: `GROUP_BITMAP`/`GROUP_BITMAP_AND`/`GROUP_BITMAP_OR`/`GROUP_BITMAP_XOR`/`GROUP_BITMAP_MERGE` return cardinality (INT), not a bitmap object. Use `GROUP_BITMAP_STATE` for a bitmap object.

**Unordered sets**: `COLLECT_SET` and `COLLECT_LIST(DISTINCT ...)` result order is non-deterministic. Do not hardcode order; note "result order is not guaranteed" in documentation.

**FROM_JSON case sensitivity**: Field names are forced to lowercase. Fields with different cases that would collide are silently dropped. Use `PARSE_JSON` to preserve uppercase field names.

**Context functions**: `CURRENT_SESSION_ID()`, `CURRENT_VCLUSTER()` return different values each time. Use comments in examples rather than hardcoding specific values.

**LAST_VALUE window frame**: Default frame is `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, causing `LAST_VALUE` to return the current row rather than the last row. Explicitly specify `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.

**Two-level window aggregation**: `SUM(SUM(col)) OVER (...)` is valid — the outer SUM is a window function, the inner SUM is an aggregate function, and it must be used with GROUP BY.

### Document Consistency Review (Required After SQL Verification)

**Background**: SQL verification ensures "each SQL block runs correctly in isolation" but cannot catch inconsistencies between table definitions and later usage, missing cross-section references, or undocumented implicit assumptions. These errors are not exposed by isolated testing — only a full read-through from the reader's perspective reveals them.

**After completing SQL verification for any usage guide, perform these three additional checks:**

| Check | Method | Typical Error |
|---|---|---|
| Table definition completeness | Scan all SQL in the document, extract all columns/CTEs used, compare against the `CREATE TABLE` or setup data at the top | Time-Decay attribution uses `conversion_time` column, but it's not in the table definition |
| CTE context references | Check whether each CTE referenced in a SQL block is defined in the same section or earlier; can the reader trace it back | Advanced scenario references `with_session` but doesn't say it comes from the session-splitting in Section 1 |
| Implicit assumptions made explicit | List key facts confirmed during testing but not mentioned in the document; decide whether they need to be stated | The depth formula works for both LPAD-padded and unpadded paths, but readers may wonder |

**How to execute**:
1. After writing all SQL and completing verification, **read the entire document from start to finish**
2. For each SQL block, ask: "If I only see up to this point, can I understand where all variables come from?"
3. For each table/CTE definition, ask: "Are all columns used later defined here?"
4. For key facts discovered during testing, ask: "Will readers have the same questions I had while testing?"

---

### Example Coverage Standards

Function documentation examples must cover:
1. Basic usage (required)
2. Optional parameters listed in the syntax (DISTINCT, FILTER, ORDER BY, limit, etc.)
3. NULL value handling (when behavior is non-obvious)
4. GROUP BY usage (aggregate functions)

Alias functions (e.g., `STD` = `STDDEV_SAMP`) may have fewer examples, but must cover at least FILTER and GROUP BY.

### Test Temporary Table Naming

When testing multiple function groups in parallel, use different prefixes to avoid conflicts:
- `test_agg_g1_`, `test_agg_g2_` … for aggregate_functions
- Run `DROP TABLE IF EXISTS` to clean up after testing

---

## Documentation Writing Standards

### Document Structure Templates

**SQL syntax documents** (e.g., `show-schemas.md`):
- `## Overview`: one sentence on purpose + positioning
- `## Syntax`: code block, annotated ` ```sql ` or ` ```Plain `
- `## Parameters`: parameter names in inline code, describe behavior not definition
- `## Examples`: three-part (setup data + SQL + output)
- `## Notes`: critical constraints, also inline next to parameters
- `## Related Guides`: link to the corresponding usage guide

**Feature concept documents** (e.g., `table_stream.md`):
- First screen: analogy + positioning + core mechanism
- `## How It Works` or `## Core Concepts`
- `## Use Cases`
- `## Notes` / `## Cost`
- `## Related Documentation`

**Usage guide documents** (`SQL_*_Guide.md`):
- `## Overview`: scenario description + quick navigation
- `## SQL Commands Used`: command reference table
- `## Prerequisites`: CREATE TABLE + INSERT test data
- Scenario sections: complete SQL + output + explanation
- `## Related Documentation`

### Heading Levels

**Each document must have exactly one `#` H1 heading, and it must be the first line of content.** This is the first element users see when opening a page and directly affects orientation.

**H1 naming rules** (by document type):

| Document type | H1 format | Example |
|---|---|---|
| SQL command | `# COMMAND NAME` (all caps) | `# INSERT`, `# ALTER TABLE`, `# SHOW SCHEMAS` |
| Concept/feature | `# Feature Name` | `# Materialized View`, `# Dynamic Table`, `# Table Stream` |
| Operations guide | `# Verb + Object` | `# Load Data from Object Storage`, `# Configure Network Policy` |
| Ecosystem integration | `# Tool Connection Guide` | `# FineBI Connection Guide`, `# PowerBI Connection Guide` |
| Best practices | `# Topic Best Practices` | `# Table Design Best Practices`, `# Index Usage Best Practices` |

**First `##` section name rules**:
- SQL command documents: `## Overview` (consistent — do not use "Description", "Introduction", etc.)
- Concept/feature documents: start with body text directly, no `## Overview` heading
- Other types: `## Overview` or start with body text directly

**Prohibited**:
- Section numbering (`## 1.`, `## 2.` Word-style)
- H1 using context-free words (`# Feature`, `# Overview`, `# Introduction`)
- Starting directly from `##` without an H1
- Emoji in headings

### Code Block Language Annotations

| Content | Annotation |
|------|------|
| SQL statements | ` ```sql ` |
| Syntax structure (with placeholders) | ` ```Plain ` |
| Shell / cz-cli commands | ` ```bash ` |
| JSON | ` ```json ` |
| Agent prompt text | ` ```Plain ` |
| No specific language | no annotation |

Do not use ` ```Scala `, ` ```SQL ` (uppercase), or other non-standard annotations.

### Inline Formatting

- Command names, parameter names, field names, table names, function names: wrap in backticks, e.g., `SHOW SCHEMAS`, `ON_ERROR`
- UI buttons, menu paths: **bold**, e.g., **Development → Tasks**
- Important notes or constraints: **bold** key words
- Internal document links: relative paths, e.g., `[Real-time Sync Tasks](realtime_sync.md)`

### Code in Table Cells

Backtick code spans (`<code>`) default to `white-space: nowrap` and will not wrap in table cells, breaking the table layout when too long.

Rules:
- **Short commands or identifiers** (roughly 30 characters or fewer, e.g., `SHOW SHARES`, `instance_admin`): keep backticks
- **Long SQL commands** (GRANT, REVOKE, CREATE SCHEMA, etc. with parameters): remove backticks, use plain text to allow natural wrapping
- **Angle bracket placeholders** (`<name>`): use HTML entities `&lt;name&gt;` in table cells to prevent the platform from parsing them as HTML tags

### Language Style

- Technical terms stay in English (SCHEMA, VCLUSTER, DML, etc.)
- Sentences are concise; avoid colloquial language
- Use ordered lists for step-by-step instructions, unordered lists for notes
- Parameter descriptions use "what it does — when to use this value" format, not "what it is" format

### Pronoun Convention

- Use **"you"** consistently to address the reader
- Exception: `privacy-policy.md`, `user-aggrement.md`, and other legal agreement files may use more formal language
- Do not refer to readers as "customers" or "users" — use "you" or "your team"

### Warning Block Format

Critical warnings use blockquote + ⚠️ format:

```
> ⚠️ **Note**: warning content
```

Supplementary tips use blockquote + 💡 format:

```
> 💡 **Tip**: tip content
```

Do not use `> Note`, `> **Note**`, `> Tip`, `> **Tip**` (without emoji) variants.

### Paragraph Spacing

- Leave one blank line before and after section headings
- Leave one blank line before and after code blocks
- Generally no blank lines between list items; add blank lines when items are long

### Images

Images are uploaded by the platform and auto-generate paths:

```
![](.topwrite/assets/image_xxxxxxxxxx.png)
```

Centered display uses platform-specific syntax:

```
:-: ![](.topwrite/assets/image_xxxxxxxxxx.png =740)
```

`=740` specifies width. Add `^` before and after centered images as paragraph separators. Do not manually move or rename files under `.topwrite/assets/`.

---

## Pre-submission Checklist

Review before each submission:

- [ ] All SQL examples have been actually run with cz-cli; output matches documentation
- [ ] Examples include setup data (CREATE TABLE/INSERT) and execution output
- [ ] Critical warnings are inline next to parameters, not only at the bottom
- [ ] New files are registered in `SUMMARY.md`
- [ ] No filename typos (configration/worksapce/materialzied/informaiton/parquert/buckload)
- [ ] No emoji in headings
- [ ] New SQL function documents placed in the correct `sql_functions/` subdirectory
- [ ] Warning blocks use `> ⚠️ **Note**:` format
- [ ] Shell/cz-cli command code blocks annotated ` ```bash `, not ` ```Plain ` or ` ```Scala `

---

## Translation Rules (CN → EN)

When translating from the Chinese documentation:

| Chinese | English |
|---------|---------|
| 云器 | Singdata |
| ClickZetta / clickzetta | Singdata |
| `*.clickzetta.com` | `*.singdata.com` |

- Code blocks and SQL: preserve as-is, do not translate
- Image paths: preserve as-is
- Internal link filenames: keep consistent with the EN filename
- Files excluded from translation (use EN version directly): `pricing.md`, `user-aggrement.md`, `product-trial-agreement.md`, `billing.md`, `cost_management.md`, `account-funds.md`
- `llms.txt` and `llms-full.txt`: regenerate, do not translate

---

## File and Directory Management

### File Naming Conventions

- Separate words with hyphens `-` or underscores `_`, consistent with existing file style
- Do not use uppercase letters to start filenames (except SQL keyword documents, e.g., `ALTER-TABLE.md`)
- SQL function documents go in the appropriate `sql_functions/` subdirectory, not the root

### Complete Process for Renaming Files

1. `git mv <old> <new>` to rename
2. `grep -rl "<old-name>" --include="*.md" .` to find all documents referencing the old filename
3. Bulk replace old filename
4. Update `SUMMARY.md`
5. Grep again to confirm no remaining references
6. Commit all changes together

### macOS Case-Sensitivity Trap

macOS filesystem is case-insensitive — `CREATE-TABLE.md` and `create-table.md` appear to both exist locally, but git only has one. The Linux server (documentation publishing environment) is case-sensitive; uppercase links will 404.

**Always use `git ls-files <filename>` to confirm the actual filename in git** before acting — do not rely on macOS local `ls` results.

### SUMMARY.md

`SUMMARY.md` is the documentation table of contents. All additions, deletions, and renames must be synced here. Format:

```markdown
* [Document Title](filename.md)
```

### Image Storage

- Images are managed by the TopWrite platform, not through Git LFS
- Do not manually modify the `.topwrite/assets/` directory
- `.gitattributes` is configured to not use LFS for that directory
- `lfs.skipdownloaderrors true` is set locally; LFS prompts during pull do not affect usage

---

## Git Workflow

### Daily Development

Each collaborator maintains their own long-lived personal branch (e.g., `qiliang`); do not work directly on `master`.

**Before starting work**, sync the latest from master:

```bash
git checkout qiliang
GIT_LFS_SKIP_SMUDGE=1 git pull origin master --rebase
```

**Before merging to master**, rebase again to ensure no conflicts:

```bash
GIT_LFS_SKIP_SMUDGE=1 git pull origin master --rebase

git checkout master
GIT_LFS_SKIP_SMUDGE=1 git pull
git merge --ff-only qiliang
git push
git checkout qiliang
```

`--ff-only` errors immediately if rebase is incomplete, forcing you to finish the rebase before merging and avoiding merge commits.

### SUMMARY.md Conflict Resolution

Multiple people modifying SUMMARY.md simultaneously is the most common conflict scenario. When a conflict occurs during rebase, after manually resolving:

```bash
git add SUMMARY.md
git rebase --continue
```

If push is rejected (non-fast-forward), master has new commits — go back to your personal branch and rebase again:

```bash
git checkout qiliang
GIT_LFS_SKIP_SMUDGE=1 git pull origin master --rebase
```

### Before Pulling

- Run `git stash` if you have uncommitted changes
- Move untracked new files out of the way if they block rebase

### Files to Leave Alone

- `.topwrite/` directory: platform resource directory, do not modify manually

---

## Repository Information

- Remote: `git@k.topthink.com:4v2dmg3x2e/k7pl9zonpy.git`
- Main branch: `master`
- Frontend editor: https://4v2dmg3x2e.k.topthink.com/-/book/k7pl9zonpy/edit

---

## Architecture Diagram Standards

Architecture diagrams in product documentation are drawn as SVGs, stored in `/Users/liangmo/Desktop/lakehouse-diagrams/`, named `NN-description.svg` (e.g., `05-object-hierarchy.svg`). Convert to PNG with `rsvg-convert` when uploading to the documentation platform:

```bash
rsvg-convert -z 2 file.svg -o file.png
```

### Visual Standards

**Canvas and Background**

- Background gradient: `#EEF4FF` → `#E8F0FE` (left to right)
- Standard width: 900px or 960px; height adjusts to content, ensure content is not cramped
- Font: `'Inter','PingFang SC','Helvetica Neue',Arial,sans-serif`

**Cards and Containers**

- White card with shadow: `filter: feDropShadow dx=0 dy=2 stdDeviation=4 flood-color=#2563EB flood-opacity=0.09`
- Primary blue header: `#2563EB` → `#1D4ED8` (gradient)
- Deep blue header (instance level): `#1D4ED8` solid
- Light blue content area background: `#F0F6FF`, border `#BFDBFE`
- Chip/tag background: `#EFF6FF`, border `#BFDBFE`, text `#1E40AF`
- Corner radius: container `rx=14`, card `rx=10`, chip `rx=6~8`

**Text**

- Title (page level): `font-size=14~15`, `font-weight=700`, `fill=#1E3A8A`
- Card header text: `font-size=11~12`, `font-weight=700`, `fill=white`
- Body chip text: `font-size=9.5~10`, `fill=#1E40AF`
- Caption text: `font-size=9~9.5`, `fill=#64748B`

**Arrows**

Use solid-filled polygon markers, not stroke-only paths (which are invisible):

```xml
<marker id="arr" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
  <polygon points="0,0 10,3.5 0,7" fill="#2563EB"/>
</marker>
```

**Language**

All text in diagrams uses **English**.

### Object Hierarchy Color Conventions

| Level | Color |
|------|------|
| Instance header | `#1D4ED8` |
| Workspace header | `#2563EB` |
| Schema header | `#60A5FA` |
| GP VCluster | `#2563EB` → `#1D4ED8` |
| AP VCluster | `#059669` → `#047857` |
| Integration VCluster | `#7C3AED` → `#6D28D9` |
| Alibaba Cloud | `#FF6A00` |
| Tencent Cloud | `#0052D9` |
| AWS | `#F59E0B` |

### Layout Principles

- Elements in the same row have uniform width and consistent spacing; calculate coordinates mathematically
- Header bar rounded corners use two stacked rects: top one with rx, bottom one covering the lower straight corners
- Bottom caption bar: `fill=white opacity=0.7`, `rx=6~8`
- No redundant text inside diagrams; explanations go in the document body

---

## Animated Diagram (Animated SVG) Standards

Animated diagrams illustrate incremental computation, data flow, and other time-sequenced concepts. Filename prefix: `anim-NN-description.svg`, stored in the same directory. Animated diagrams are **not converted to PNG** — open directly in a browser to verify.

### Dark Theme Design System

Animated diagrams use a dark background to distinguish them from static diagrams with light blue backgrounds:

**Canvas**
- Background gradient: `#0D1117` → `#161B26` (top-left to bottom-right)
- Standard width: **960px** (consistent across all three diagrams)
- Height by content, typically 480–520px
- Canvas corner radius: `rx=16`
- Font: `'Inter','SF Pro Display','Helvetica Neue',Arial,sans-serif` (not SF Mono)

**Title and Subtitle (must be consistent across all three diagrams)**
- Title: `font-size=17`, `font-weight=700`, `fill=#F9FAFB`, `y=32`
- Subtitle: `font-size=10.5`, `fill=#4B5563`, `y=50`
- Title centered: `x=480 text-anchor=middle`

**Node Color Semantics**
| Purpose | Fill | Border |
|------|--------|--------|
| Data source / static node | `#1E293B` | `#374151` |
| Dynamic Table (compute layer) | `#2563EB`→`#1D4ED8` | `#3B82F6` |
| Output / consumption layer | `#059669`→`#047857` | `#059669` |
| Warning / problem | `#1F2937` | `#DC2626` |
| Advantage / benefit | `#0F172A` | `#059669` |
| Caption text (dark) | `#6B7280` | — |
| Caption text (light) | `#94A3B8` | — |

**SPOT Four-Principle Colors**
- S (Standard SQL): `#2563EB` / `#93C5FD`
- P (Performance): `#059669` / `#34D399`
- O (Open Format): `#7C3AED` / `#A78BFA`
- T (Trade-off): `#D97706` / `#FBBF24`

### CSS Animation Standards

**Flowing arrows (pipeline data flow)**
```css
@keyframes flow { 0%{stroke-dashoffset:40} 100%{stroke-dashoffset:0} }
.pipe { stroke-dasharray:8 4; animation:flow 1.2s linear infinite; }
```

**Node heartbeat glow**
```css
@keyframes glow {
  0%,100% { filter:drop-shadow(0 0 4px #2563EB); opacity:0.88; }
  50%     { filter:drop-shadow(0 0 14px #60A5FA); opacity:1; }
}
.node { animation:glow 2s ease-in-out infinite; transform-origin:center; }
```

**Elements flying in one by one**
```css
@keyframes fly-in {
  from { opacity:0; transform:translateX(-14px); }
  to   { opacity:1; transform:translateX(0); }
}
.item1 { animation:fly-in 0.4s 0.3s both; }
.item2 { animation:fly-in 0.4s 0.7s both; }
```

**Progress bar animation**
```css
@keyframes bar-grow { from{width:0} to{width:Xpx} }
.bar { animation:bar-grow 1.8s 0.5s ease-out forwards; width:0; }
```
> ⚠️ Do not use `width:100%` — use a fixed pixel value, otherwise it calculates relative to the parent container and overflows.

**Scan line (moving up and down within a container)**

CSS `transform:translateY` escapes `clipPath` bounds — use **SMIL `<animate>`** to drive the `y` attribute instead:
```xml
<clipPath id="cp"><rect x="20" y="86" width="258" height="212"/></clipPath>
<g clip-path="url(#cp)">
  <rect x="20" y="86" width="258" height="10" fill="#60A5FA" opacity="0.4">
    <animate attributeName="y" from="86" to="298" dur="2.4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;0.4;0.4;0" keyTimes="0;0.05;0.92;1" dur="2.4s" repeatCount="indefinite"/>
  </rect>
</g>
```

### Multi-Diagram Consistency Checklist

Before publishing a set of animated diagrams, verify:

- [ ] Canvas width consistent (960px)
- [ ] Title font-size 17, color `#F9FAFB`, y=32
- [ ] Subtitle font-size 10.5, color `#4B5563`, y=50
- [ ] Font is `SF Pro Display` (not SF Mono)
- [ ] Background gradient IDs differ but colors are consistent (`#0D1117`→`#161B26`)
- [ ] Progress bar animation uses fixed px width, not `100%`
- [ ] Scan line uses SMIL `<animate>`, not CSS `transform:translateY`
- [ ] All text uses English
- [ ] Actually open in a browser to verify animation; do not rely on static screenshots
