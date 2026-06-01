---
name: dt-creator
description: |
  Reference index for creating Dynamic Tables. Covers declaration strategies for static partition DT
  vs dynamic partition DT, SQL patterns supported by incremental computation, incremental refresh
  configuration options, and how to query refresh history.
---

# DT Creator — Reference Index

## references/

- **dt-declaration-strategy.md** — DT declaration strategy (creation syntax and selection between static partition DT and dynamic partition DT)
- **sql-limitations.md** — SQL support matrix (support status for JOIN, aggregation, window functions, non-deterministic functions, etc.)
- **incremental-config-reference.md** — Incremental computation configuration reference (refresh strategy, source table characteristic declarations, state table management, etc.)
- **refresh-history-guide.md** — Incremental refresh history queries (SHOW REFRESH HISTORY / DESC HISTORY / information_schema)
