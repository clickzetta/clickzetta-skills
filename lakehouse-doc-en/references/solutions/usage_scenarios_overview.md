# Industry Solutions Overview

Singdata Lakehouse consolidates business scenarios that traditionally required multiple independent systems (stream processing clusters + AI inference services + data warehouses + BI + vector databases) into a single platform implemented with pure SQL, through core capabilities including **Dynamic Table · AI Functions · Volume · PIPE · MERGE INTO · Window Functions · Full-text/Vector Search**.

This page summarizes all currently published industry solutions to help you quickly locate the solution documentation that best matches your scenario.

![](/.topwrite/assets/solutions-flywheel.svg)

---

## Solution Landscape

| Solution | Industry | Core Requirement | Key Technologies |
|----------|----------|-----------------|-----------------|
| [Manufacturing Part Defect AI Detection & Classification](defect-detection-ai.md) | Manufacturing | Dual-channel defect detection via production line images + text descriptions, with tiered AI inference triggering | `AI_CLASSIFY` · `AI_EXTRACT` · `AI_COMPLETE` · Dynamic Table · Volume |
| [Equipment Predictive Maintenance](predictive-maintenance.md) | Discrete/Process Manufacturing | IoT sensor rolling-average anomaly detection + automated AI maintenance recommendation generation | `AI_COMPLETE` · Dynamic Table · BloomFilter Index · API Connection |
| [Supply Chain Inventory Optimization](supply-chain-inventory.md) | Manufacturing / Retail / E-commerce | Dynamic replenishment decisions + real-time supplier lead time integration, replacing static ERP models | Window Functions · Dynamic Table · `MERGE INTO` · `AI_EXTRACT` |
| [Smart Mine Safety Alert](smart-mine.md) | Mining / Heavy Industry | Cross-system correlation alerts across six subsystems + AI action recommendations + RAG historical knowledge retrieval | `AI_CLASSIFY` · `AI_COMPLETE` · `AI_EMBEDDING` · Dynamic Table · Full-text/Vector/Hybrid Search |
| [Customer Complaint Intelligent Labeling](complaint-labeling.md) | E-commerce / Retail / Local Services | Automatic customer service ticket classification, replacing manual labeling, end-to-end latency ≤5 minutes | `AI_COMPLETE` · Dynamic Table · API Connection |
| [Email Customer Support Auto-Triage](email-customer-support.md) | E-commerce / 3C / Cross-border | Single AI call completes intent classification + entity extraction + reply draft, latency ≤10 minutes | `AI_COMPLETE` · Dynamic Table · `REGEXP_EXTRACT` · `GET_JSON_OBJECT` |
| [Product Review Sentiment Analysis](product-review-sentiment.md) | E-commerce Platforms | Real-time sentiment classification of Kafka review streams + structured summary extraction | `AI_SENTIMENT` · `AI_COMPLETE` · `CREATE PIPE` · Dynamic Table |
| [User Behavior Funnel Analysis](user-behavior-funnel.md) | E-commerce / Local Services / Cross-border | Multi-channel funnel conversion rate auto-aggregation, latency ≤1 hour, pinpointing largest drop-off stages | Dynamic Table · `MERGE INTO` · `COUNT DISTINCT` · Window Functions |
| [Autonomous Driving Full-Loop Data Platform](autonomous-driving-full-loop.md) | Autonomous Driving | Full loop from road test data collection → labeling → training set → model iteration | Dynamic Table · Volume · `AI_COMPLETE` · Table Stream |

---

## Select by Technical Capability

Starting from "I want to use a specific Lakehouse feature" — find the corresponding reference solution:

| Technical Capability | Reference Solutions |
|---------------------|-------------------|
| `AI_CLASSIFY` (classification function) | [Defect AI Detection](defect-detection-ai.md) · [Smart Mine](smart-mine.md) (disaster type rapid classification) · [Supply Chain Inventory Optimization](supply-chain-inventory.md) (SKU ABC classification extension) |
| `AI_EXTRACT` (structured extraction) | [Defect AI Detection](defect-detection-ai.md) · [Supply Chain Inventory Optimization](supply-chain-inventory.md) (supplier notification parsing) |
| `AI_COMPLETE` (LLM inference) | [Predictive Maintenance](predictive-maintenance.md) · [Smart Mine](smart-mine.md) · [Complaint Labeling](complaint-labeling.md) · [Email Customer Support](email-customer-support.md) · [Product Reviews](product-review-sentiment.md) · [Defect Detection](defect-detection-ai.md) · [Autonomous Driving](autonomous-driving-full-loop.md) |
| `AI_SENTIMENT` (sentiment classification) | [Product Review Sentiment Analysis](product-review-sentiment.md) |
| `AI_EMBEDDING` (text vectorization) | [Smart Mine](smart-mine.md) (historical incident semantic retrieval + RAG) |
| Dynamic Table (incremental computation) | All solutions use this |
| `MERGE INTO` (idempotent archiving / UPSERT) | [Supply Chain Inventory Optimization](supply-chain-inventory.md) · [User Behavior Funnel](user-behavior-funnel.md) |
| Window Functions (multi-window / sliding averages) | [Supply Chain Inventory Optimization](supply-chain-inventory.md) · [Smart Mine](smart-mine.md) (gas trend prediction) · [User Behavior Funnel](user-behavior-funnel.md) |
| `CREATE PIPE` (Kafka ingestion) | [Product Review Sentiment Analysis](product-review-sentiment.md) |
| Volume / `GET_PRESIGNED_URL` (image ingestion) | [Defect AI Detection](defect-detection-ai.md) · [Autonomous Driving](autonomous-driving-full-loop.md) |
| `REGEXP_EXTRACT` + `GET_JSON_OBJECT` (LLM output parsing) | [Email Customer Support Auto-Triage](email-customer-support.md) · [Predictive Maintenance](predictive-maintenance.md) · [Smart Mine](smart-mine.md) |
| BloomFilter Index (high-cardinality column equality query acceleration) | [Predictive Maintenance](predictive-maintenance.md) · [Smart Mine](smart-mine.md) (zone_id / sensor_type point queries) |
| Full-text Search + Inverted Index (Chinese keyword search) | [Smart Mine](smart-mine.md) (incident reports, action record retrieval) |
| Vector Index + `AI_EMBEDDING` (semantic similarity / RAG) | [Smart Mine](smart-mine.md) (historical incident experience semantic retrieval injected into Prompt) |
| Full-text + Vector Hybrid Search (Hybrid Search) | [Smart Mine](smart-mine.md) (dual-optimized precision + recall) |
| API Connection (AI model credential management) | [Predictive Maintenance](predictive-maintenance.md) · [Smart Mine](smart-mine.md) · [Complaint Labeling](complaint-labeling.md) · [Email Customer Support](email-customer-support.md) |
| Table Stream (change capture) | [Autonomous Driving Full-Loop](autonomous-driving-full-loop.md) |

---

## Select by Business Need

### I want to use AI to analyze unstructured data

**Images / Video**: See [Defect AI Detection](defect-detection-ai.md) to learn how to connect images to AI functions via Volume + `GET_PRESIGNED_URL`.

**Text classification (single label)**: See [Complaint Intelligent Labeling](complaint-labeling.md) for the most streamlined LLM classification pipeline — only three layers of Dynamic Tables from source to labeled result.

**Text multi-task (classification + extraction + draft generation)**: See [Email Customer Support Auto-Triage](email-customer-support.md), which demonstrates a single `AI_COMPLETE` call completing five tasks simultaneously through a structured JSON prompt, plus the pattern of stable LLM output parsing using `REGEXP_EXTRACT` + `GET_JSON_OBJECT`.

**Text sentiment + structured summary extraction**: See [Product Review Sentiment Analysis](product-review-sentiment.md), which shows dual-function division of labor between `AI_SENTIMENT` and `AI_COMPLETE`, plus tiered triggering cost control that skips AI for neutral reviews.

**Extracting fields from unstructured notifications**: See [Supply Chain Inventory Optimization](supply-chain-inventory.md) for supplier lead time parsing — `AI_EXTRACT` converts email/notification text into structured fields that directly drive business logic.

**Historical document knowledge base + RAG enhancement**: See [Smart Mine](smart-mine.md), which shows how to build a searchable knowledge base from historical incident reports using `AI_EMBEDDING` + vector index, then inject retrieval results into AI_COMPLETE prompts — no standalone vector database (Milvus/Pinecone) required.

### I want to build near-real-time data pipelines

All solutions use Dynamic Table for incremental refresh without external schedulers. Complexity from low to high:

- **Simplest (row-by-row AI inference)**: [Complaint Labeling](complaint-labeling.md) · [Email Customer Support](email-customer-support.md) — three layers of Dynamic Tables, new data completes AI classification within ≤10 minutes of write
- **Medium (aggregation + threshold filtering)**: [Predictive Maintenance](predictive-maintenance.md) · [User Behavior Funnel](user-behavior-funnel.md) — aggregation for noise reduction/UV statistics, then filtering/MERGE into summary tables
- **Multi-level multi-frequency (industrial safety)**: [Smart Mine](smart-mine.md) — real-time pipeline (1-minute Studio Cron) + aggregation layer DT (5 minutes) + cross-system correlation DT (5 minutes) + trend prediction DT (5 minutes), four complementary refresh intervals
- **Complex (stream ingestion + multi-layer AI)**: [Product Review Sentiment Analysis](product-review-sentiment.md) — Kafka PIPE ingestion + four-layer Dynamic Tables + dual AI functions + aggregated views

### I want to do e-commerce operations data analysis

- **Funnel conversion rate**: [User Behavior Funnel Analysis](user-behavior-funnel.md) — multi-channel UV statistics, three-segment drop-off breakdown, `MERGE INTO` idempotent write to summary tables, latency ≤1 hour
- **Negative review alerts**: [Product Review Sentiment Analysis](product-review-sentiment.md) — real-time tagging of negative reviews, aggregated positive review rate by SKU, driving quality control and proactive follow-up
- **Customer service ticket efficiency**: [Complaint Intelligent Labeling](complaint-labeling.md) + [Email Customer Support Auto-Triage](email-customer-support.md) — automatic ticket classification routing, high-priority alerts, AI reply drafts — all three in one

### I want to replace static decision models in MES/ERP

See [Supply Chain Inventory Optimization](supply-chain-inventory.md). The solution demonstrates dynamic replenishment calculation with Dynamic Table, automatic switching between supplier real-time lead times and ERP static values using `COALESCE`, and idempotent archiving with `MERGE INTO` — all without modifying existing systems.

### I want to deploy AI in industrial scenarios

- **Quality inspection**: [Defect AI Detection](defect-detection-ai.md) — dual image + text channels, `AI_CLASSIFY` full-volume classification followed by tiered `AI_COMPLETE` triggering, cost-controlled
- **Equipment O&M**: [Predictive Maintenance](predictive-maintenance.md) — after sensor data lands in the Lakehouse, Dynamic Table automatically completes rolling-average aggregation, multi-dimensional threshold filtering, and AI recommendation generation in three pipeline layers, no additional AI service needed
- **Safety production**: [Smart Mine](smart-mine.md) — cross-system JOIN correlation alerts across six subsystems, `AI_CLASSIFY` + `AI_COMPLETE` CTE chaining, RAG injection of historical incident experience, PoC launch in 6 weeks

### I have large-scale multimodal data to manage

See [Autonomous Driving Full-Loop](autonomous-driving-full-loop.md). This solution covers unified management of structured time-series data, semi-structured JSON events, and large files (Parquet annotation packages), as well as the complete closed-loop architecture from data collection to model iteration — a reference blueprint for other data-intensive industries (precision agriculture, medical imaging, satellite remote sensing).

---

## Key Metrics by Solution

| Solution | Typical Data Scale | End-to-End Latency | AI Cost Control Strategy |
|----------|-------------------|-------------------|--------------------------|
| Defect AI Detection | Tens of thousands of images per production line per day | Dynamic Table refresh interval | `AI_CLASSIFY` first, then decide whether to invoke `AI_COMPLETE` based on result, saving ~40% of calls |
| Predictive Maintenance | Multi-dimensional sensor data per device per second | ≤10 minutes | Two-level threshold filtering, AI triggered only for medium/high risk, reducing call volume by 90%+ |
| Supply Chain Inventory Optimization | Multiple warehouses × hundreds of SKUs × daily snapshots | Hourly refresh | `AI_EXTRACT` only processes supplier notification text; `AI_COMPLETE` only triggered for anomalous-demand SKUs |
| Smart Mine Safety Alert | Single mine: 500–2,000 sensors; group-level: millions of points | ≤90 seconds (real-time pipeline) / 5 minutes (DT aggregation) | Two-level threshold pre-filtering, only HIGH/CRITICAL triggers AI; BoolFilter narrows candidate set before vector search |
| Customer Complaint Labeling | Daily average 5,000–50,000 tickets | ≤5 minutes | Incremental refresh, each ticket calls AI only once |
| Email Customer Support Auto-Triage | Continuous incoming customer service emails | ≤10 minutes | Single call completes five tasks, ~60% fewer token consumption vs. three separate calls |
| Product Review Sentiment Analysis | Continuous Kafka stream | ≤10 minutes | Neutral reviews skip `AI_COMPLETE`, saving ~35% tokens |
| User Behavior Funnel | Daily tens of millions of events, multi-channel | ≤1 hour | Pure SQL aggregation, no AI call cost; scalable to BITMAP approach for very large scale |
| Autonomous Driving Full-Loop | Fleet of millions of vehicles, peak 1M msg/s | Minutes to hours (by pipeline layer) | Long-tail scenarios trigger labeling; non-critical data bypasses AI pipeline |

---

## Related Documents

- [AI Functions Overview](../ai_functions_overview.md)
- [Dynamic Table Summary](../dynamic_table_summary.md)
- [File Storage Overview](../volume-overview.md)
- [CREATE PIPE](../create-pipe.md)
- [MERGE INTO](../merge.md)
- [Window Functions Overview](../windowfunction.md)
- [Vector Search and RAG Applications Guide](../sql_vector_search_guide.md)
- [Full-text + Vector Hybrid Search Best Practices with RRF](../rrf-fulltext-vector-hybrid-search-best-practices.md)
