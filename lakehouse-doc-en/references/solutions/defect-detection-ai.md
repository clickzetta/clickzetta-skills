# Manufacturing Part Defect AI Detection & Classification

> **Core Capabilities**: AI_CLASSIFY · AI_EXTRACT · AI_COMPLETE · Dynamic Table · OSS/S3 Volume

---

## Business Background

Quality control in manufacturing is a core competitive differentiator. In precision manufacturing scenarios such as automotive parts, consumer electronics (PCB/PCBA), power batteries, and semiconductor packaging, each production line generates tens of thousands of quality inspection records and image data every day. This data accumulates on equipment or local file systems, disconnected from production systems, unable to support systematic quality analysis and process improvement.

Typical quality inspection data sources:

```
Production line cameras (AOI/industrial cameras) -> Defect images -> OSS/S3 storage
       +
Inspector workstations (MES terminals)          -> Defect text descriptions -> Business databases
       +
Sensors/PLCs                                    -> Process parameters -> Time-series data
```

These three types of data have long been siloed. Quality management teams can only compile reports after the fact, unable to perceive quality trends in real time during production, identify root causes, or trigger corrective actions.

---

## Industry Pain Points

### 1. Manual visual inspection efficiency bottleneck — cannot match production line pace

High-speed production lines operate extremely fast — SMT placement handles thousands of solder joints per minute, and battery electrode coating speeds exceed 50 m/min. A skilled inspector can only inspect a few hundred parts per day. **The gap between manual efficiency and production line speed cannot be solved by adding more people.**

### 2. Traditional AOI high false positive rate generates excessive secondary confirmation work

Traditional AOI equipment based on rule-based thresholds has a false positive rate of **15%–25%**. Many good parts are flagged as "suspected defects" and require inspectors to verify one by one. These false positives not only increase labor costs but also slow down the production line release cadence.

### 3. Defect data silos — cannot support root cause analysis

Images reside on AOI equipment or in OSS; defect descriptions live in MES; process parameters are in SCADA. These three types of data have never been correlated for analysis. Quality engineers cannot answer critical questions like "which shift/which machine/which supplier batch has a higher defect rate."

### 4. AI vision systems can detect, but results don't enter the system

Some factories have deployed dedicated vision inspection equipment, but the results (images + labels) from these devices remain on the device side. They are not aggregated into a data platform, making cross-line and cross-time statistical analysis impossible, and preventing linkage with quality SOPs to trigger automated corrective processes.

### 5. Inconsistent classification standards — individual variation in manual judgment

Different inspectors classify the same defect differently ("appearance defect" vs. "material issue") and assign different severity levels ("critical" vs. "minor"). This subjectivity makes historical data difficult to compare, unsuitable for model training or trend analysis.

---

## Solution Based on Singdata Lakehouse

This solution uses Lakehouse's **Volume storage + AI functions + Dynamic Table** capabilities to integrate image detection and text description analysis into a single pure SQL-driven pipeline, without deploying an independent AI inference service.

### Architecture Overview
![Solution Architecture](/.topwrite/assets/defect_detection_architecture.svg)

### Three AI Function Roles

| Function | Input | Output | Trigger Scope |
|----------|-------|--------|--------------|
| `AI_CLASSIFY` | Image URL | Defect category (appearance / dimension / functional / material / no-defect / re-inspection) | All images |
| `AI_EXTRACT` | Image URL + extraction template | JSON: defect location, area ratio, count, confidence | All images |
| `AI_COMPLETE` | Text description + image classification result | Root cause inference + action recommendation (scrap/rework/pass/re-inspect) | Severe/minor only (skips light/no-defect) |

**Image ingestion method**:
```sql
-- Images stored via USER VOLUME; GET_PRESIGNED_URL generates an HTTPS temporary access URL
AI_CLASSIFY(
    'endpoint:qwen3.5-plus',
    (GET_PRESIGNED_URL(USER VOLUME, image_path, 36000) AS image),
    ARRAY('Appearance Defect', 'Dimension Deviation', 'Functional Failure', 'Material Issue', 'No Defect', 'Requires Manual Re-inspection')
) AS defect_category
```

---

## Solution Technical Advantages

### 1. Image detection and text analysis fused in SQL — no independent AI service

Traditional solutions require separately deploying and maintaining Python inference services (Flask/FastAPI), model version management, and GPU resource scheduling. This solution calls multimodal large models directly in SQL via `AI_CLASSIFY`, `AI_EXTRACT`, and `AI_COMPLETE`, with images accessed through USER VOLUME + `GET_PRESIGNED_URL`. **The entire pipeline has no Python, no standalone services, and no GPU resource management.**

### 2. Dynamic Table enables true incremental processing — eliminates repeated inference

Production lines add inspection records daily. Dynamic Table's `change_tracking` mechanism only processes incremental data; already-analyzed records are not re-inferred. **Each image calls AI exactly once — token consumption is precise and predictable.**

### 3. Tiered AI call triggering — optimal cost

```
AI_CLASSIFY  -> All images (low cost, dedicated classification function)
AI_EXTRACT   -> All images (dedicated extraction function, low cost)
AI_COMPLETE  -> Only severity IN ('Critical', 'Minor') (approximately 40–60% of images)
              Skips 'Light' and 'No Defect' -> saves approximately 40% of AI_COMPLETE calls
```

### 4. Dual-channel image + text fusion — improves judgment reliability

Relying solely on images may miss edge cases (e.g., material issues that are hard to distinguish visually). Relying solely on text descriptions depends on inspector subjective judgment. This solution uses both the AI image classification result and the text description as context inputs to `AI_COMPLETE`. **Two streams of information corroborate each other, improving root cause inference accuracy.**

### 5. ODS layer retains full raw data — supports traceability and model iteration

`defect_inspection_records` retains `raw_category` (initial human judgment) and `defect_image` (image path). `defect_analysis_dt` stores the complete AI inference results. Both coexist to support:
- AI classification vs. human classification consistency analysis (identifying classification bias)
- Routing AI-mislabeled samples back for annotation to continuously improve prompts or fine-tune models

### 6. Integration with MES/ERP — action recommendations directly applied

The `action` field (scrap/rework/pass/re-inspect) can be pushed directly to MES systems via Studio Task scheduling, enabling quality inspection results to automatically drive corrective processes — no more manual ticket transcription.

---

## Customer Value

**Quality Management Team**

Real-time visibility into defect rates and defect type distribution across production lines, shifts, and SKUs — shifting from after-the-fact report compilation to real-time alerts. When the critical defect rate on a production line exceeds a threshold, a `PAUSE_LINE` signal can be triggered to prevent batches of defective products from being released.

**Quality Engineers**

Frequent clustering of the `root_cause` field directly points to process problem root causes (e.g., "reflow soldering temperature curve instability" appearing repeatedly). Root cause analysis that previously took days is now available as real-time structured data, accelerating the CAPA (Corrective and Preventive Action) development cycle.

**Production Management Team**

Rework tickets are automatically generated for `action = 'Rework'` records, and `action = 'Scrap'` records directly drive material write-offs — reducing manual ticket entry by inspectors while lowering the risk of defective products circulating due to missing entries.

**IT / Digitalization Team**

No need to purchase and maintain additional AI inference platforms, GPU servers, or model version management systems. The quality inspection AI pipeline and data warehouse analytics layer are on the same platform, with unified permission management, unified monitoring, and unified SLAs. **Operational complexity is significantly reduced.**

**Senior Management**

Quality cost (Quality Cost) is quantifiable: defect rate × unit rework/scrap cost, trackable by production line and over time to measure improvement effectiveness — supporting ROI calculations for quality improvement projects.

---

## Important Notes

**Image Ingestion**
- Images must be uploaded to the Lakehouse USER VOLUME first; external HTTP URLs cannot be used directly. Images in OSS/S3 must be synced to a Volume or configured as an External Volume mount.
- `AI_CLASSIFY` / `AI_EXTRACT` / `AI_COMPLETE` image mode **must use a multimodal model** (e.g., `doubao-seed-2-0-pro`, `qwen-vl` series). Text-only models receiving image parameters will not error but will silently ignore the image, making classification results unreliable.
- Temporary URLs generated by `GET_PRESIGNED_URL` have an expiration time (36000 seconds = 10 hours recommended). Dynamic Table REFRESH must occur within this window.

**Data Scale and Cost**
- High-frequency inspection scenarios (hundreds of images per minute per line) require evaluating AI inference concurrency and token throughput. Use the `task.concurrency` parameter in `COPY_JOB_HINT` to control concurrency.
- Image AI calls (multimodal) cost significantly more than pure text. Tiered triggering (AI_CLASSIFY first, then deciding whether to invoke AI_COMPLETE based on result) is the key to cost control.

**Dynamic Table Usage Guidelines**
- Partitioned table PRIMARY KEY must include the partition key (`inspect_time`); otherwise table creation will fail.
- `change_tracking = true` must be set separately via `ALTER TABLE SET TBLPROPERTIES` after table creation — it cannot be inlined in the CREATE TABLE statement.
- Dynamic Tables do not support DML; historical data corrections can only be made on the source table.

**Image Quality Requirements**
- AI classification accuracy depends heavily on image quality: low resolution, uneven lighting, and occlusion all degrade detection effectiveness.
- Pre-processing at the production line camera side is recommended (crop ROI, normalize exposure) before uploading to Volume.

---

## Extension Directions

- **SPC Statistical Process Control**: Combine defect rate time-series data with Dynamic Table to compute control limits (UCL/LCL) for automated production line out-of-control alerts
- **Integration with Predictive Maintenance** ([04-predictive-maintenance](../04-predictive-maintenance/)): Correlate high-defect-rate time periods with equipment sensor anomaly data to help determine whether equipment performance degradation is the cause
- **Supplier Quality Management**: Aggregate defect rates by `supplier_id` to automatically generate monthly supplier quality reports
- **Model iteration closed loop**: Automatically flag AI mislabeled records (AI classification ≠ human review result) and aggregate into training datasets to support continuous improvement through prompt optimization or model fine-tuning

---

## Related Documents

### AI Functions

| Document | Description |
|----------|-------------|
| [AI Functions Overview](../ai_functions_overview.md) | Overview of AI functions, model selection, invocation methods, and billing |
| [AI_CLASSIFY](../ai_classify.md) | Image/text classification function supporting custom category labels; used in this solution for defect category determination |
| [AI_EXTRACT](../ai_extract.md) | Structured information extraction function; used in this solution to extract defect location, area ratio, and count from images |
| [AI_COMPLETE](../ai_complete.md) | General LLM completion function; used in this solution for root cause inference and action recommendation generation |

### Dynamic Table

| Document | Description |
|----------|-------------|
| [Dynamic Table Summary](../dynamic_table_summary.md) | Core concepts, incremental refresh mechanism, and comparison with materialized views |
| [Dynamic Table Development Guide](../sql_dynamic_table_guide.md) | End-to-end examples for table creation, refresh, and history review |
| [CREATE DYNAMIC TABLE](../create-dynamic-table.md) | Table creation syntax reference, including `change_tracking`, refresh scheduling, and other parameters |
| [View Dynamic Table Refresh Mode](../dynamic-table-incre.md) | Incremental vs. full refresh mode explanation and how to determine the current refresh strategy |
| [Dynamic Table Refresh Scheduling](../dynamic-table-scheduling.md) | Scheduled refresh configuration to control pipeline refresh frequency |

### Volume File Storage

| Document | Description |
|----------|-------------|
| [File Storage Overview](../volume-overview.md) | Volume type descriptions (internal/external/user) and use cases |
| [Internal Volume](../om-internal-volume.md) | Creating and managing Internal Volumes, suitable for storing inspection images |
| [External Volume (OSS)](../oss_volume_creation.md) | Mounting Alibaba Cloud OSS buckets as External Volumes |
| [External Volume (COS)](../cos_volume_creation.md) | Mounting Tencent Cloud COS buckets as External Volumes |
| [External Volume (S3)](../s3_volume_creation.md) | Mounting AWS S3 buckets as External Volumes |
| [Volume File Management](../sql_volume_guide.md) | PUT/GET/LIST/REMOVE operation guide |
| [GET_PRESIGNED_URL](../sql_functions/scalar_functions/file_functions/get_presigned_url.md) | Generating temporary access URLs — a required step for AI function image input |
