# From Requirements to the Semantic Layer: DataAgent Best Practices for Metric Definition Management

> Submit a requirement once, and DataAgent delivers two things at the same time: a **standardized metric requirements document** and a **Semantic View**. The document gives your metric definitions a unified standard going forward; the Semantic View collapses the maintenance cost from "keeping two things in sync" to "change one place, take effect everywhere."

## Why Metric Platforms Are Always "Built But Unused"

During a post-mortem, three teams each built a "repeat purchase rate" dashboard, and the numbers disagreed. After tracing the issue, the problem was not a SQL error — it was an unresolved definition conflict that nobody had surfaced: one team counted by "one ID per order," another counted by "the same real person," and a third mixed both. All three SQL statements were individually "correct," but the definitions were scattered across their own queries, and nobody had captured them centrally — the same term, three meanings, three dashboards.

This is not an isolated case; it is the problem enterprises routinely encounter with metric platforms. Breaking the metric lifecycle into phases, the pain points fall in five places:

* **High setup cost; no path to migrate existing metrics.** Building a solid metric platform or semantic layer is a large project — modeling, entity definition, definition alignment, join configuration, months of architect-led effort. Worse, enterprises are never starting from a blank slate: they already have thousands of metrics scattered across BI, SQL, and spreadsheets. The platform starts empty, and manual migration can never keep pace with new business metrics being added. **The platform is incomplete from day one.**
* **Ingestion is manual; standards depend on individual discipline.** In mainstream platforms, "define a metric" and "register it in the platform" are two separate actions — people register when they remember to, and bypass the platform with direct SQL when they don't. Standards are governance documents parked on a wiki. **Standards that depend on discipline are no standards at all.** New team members still improvise. The result: only "official metrics" live in the platform; everything else runs wild, with definition silos and duplicate definitions.
* **Consumers recompute independently; two sets of things drift apart.** Even when a metric enters the platform, BI, Notebooks, and ad-hoc SQL all recompute the definition independently — "single source of truth" never lands at the consumption layer. Meanwhile the physical layer keeps changing, and the semantic definitions in the platform are a post-hoc translation layer that **perpetually drifts** from reality. Daily work becomes maintaining alignment between these two things.
* **Change impact is guessed after the fact; changing one place means not knowing who else breaks.** Most platform lineage is derived after the fact by parsing SQL — incomplete and always lagging. When an upstream field changes, there is no way to know which metrics and dashboards will break until it is too late. "Changing one definition" becomes a high-risk operation involving a global grep, cross-team meetings, and reactive firefighting — the largest single cost in "expensive metric governance."
* **In the AI era, there is no reliable definition anchor; an Agent can only guess.** For NL2SQL or data agents to work reliably, they need a machine-readable, authoritative definition source to anchor on. The reality is definitions are still scattered, the platform is still incomplete, and the Agent has no anchor — it guesses the definition at query time. When it guesses right, that is luck; when it guesses wrong, that is an incident.

The root cause of all these problems is that **the metric platform is treated as a downstream translation layer chasing the physical layer after data is built, rather than as the first stop where business intent enters the system.** That is why it is inherently incomplete (ingestion depends on discipline), inherently drifting (two things to keep aligned), and inherently blind (lineage is guessed after the fact).

Using the Data Engineering Agent moves the semantic layer from "post-hoc translation" to "governance source."

> **When a business stakeholder submits a metric requirement, DataAgent, in the same step that generates the "metric requirements document," also converts it into a corresponding Semantic View — the document and the semantic layer are bound together from that moment. They are no longer two things to keep in sync; they are two views of the same source.**

## DataAgent: Governance at the Source — Metric Requirements and Semantic View in Lockstep

^

:-: ![](/.topwrite/assets/dataagent-4layer-architecture.svg =680)

DataAgent's approach can be stated in one sentence: **make the act of "submitting a requirement" lock together the definition, the document, the implementation, and the lineage at the source; then, when any one of them changes, the others automatically follow.** Break it into three steps.

**Step 1 — Governance at the source: submitting a requirement creates the semantic definition, and the definition is standardized on the spot.** A business stakeholder submits a requirement. DataAgent does not rush to write SQL. Instead, it first uses a **unified definition template** (definition, calculation logic, data source, aggregation granularity — all fields required) to make inferences and surface hidden ambiguities for confirmation — for example, in "repeat purchase rate," is `customer_id` (one per order) or `customer_unique_id` (the actual person) the right identifier? Once confirmed, the output is **not a Word document that will go stale** — it is a **Semantic View** in the Lakehouse. The definition is standardized and declared in a machine-readable form the moment it is born, and the lineage is recorded at the same moment.

This is what "governance at the source" means — standards are not debt chased down after the fact; they are enforced by the process at the entry point. Metrics have no opportunity to enter the system in a non-standardized state.

**Step 2 — Continuous linkage: every subsequent metric requirement is anchored to a Semantic View.** Rather than each requirement writing its own SQL and its own definition independently, new metrics reuse already-declared entities, join relationships, and definitions, all accumulating into **one** semantic layer. The requirements document and the Semantic View are **one-to-one and bidirectionally bound** — the document is no longer a footnote left to die on a wiki; it is a human-readable view of the semantic layer itself. The drift of "document says A, production computes B" becomes structurally impossible.

**Step 3 — Bidirectional change linkage: this is where it actually solves "hard to govern."** With a bound, declarative source, the two most uncontrollable change scenarios become two manageable directions:

* **Forward direction — business definition changes propagate automatically.** "Change the repeat purchase window from 30 days to 60 days" — only **one** source is changed: the Semantic View. Every dashboard and downstream report referencing it, and even the Agent's natural language queries, automatically use the new definition. No one needs to do a global search and update one by one. Definition changes are **timely and complete**, with no missed updates or coexisting old and new definitions.
* **Reverse direction — ETL chain changes trigger impact analysis.** An intermediate table is refactored or a field's meaning changes. Because lineage was declared at generation time and is machine-readable, the system can trace **backwards** along the lineage: which metric definitions does this change affect? It lists the impact and provides a warning **before you make the change**, rather than waiting for downstream metrics to produce wrong results and users to report them. **Know who is affected before you act; catch errors before they go live.**

Forward propagation and reverse impact analysis — once both directions are connected, metric requirements are truly "governed" for the first time, rather than chased by misaligned documents and endless firefighting.

## Practical Example: Using Brazilian E-Commerce Data, Walking Through a Metric's "Birth to Change" in Five Steps

We use the Brazilian e-commerce public dataset Olist, which includes several core tables: orders, order\_items, customers, payments, and reviews.

### Step 1: Organize the business requirement into a standardized metric requirements document

The business stakeholder submits the request: "I want to build a sales GMV analysis report. Help me identify which metrics I can build and give me a metric requirements description."

DataAgent does not rush to write SQL. Instead, it produces a metric requirements document using a **unified template** (definition / calculation logic / data source / aggregation granularity — no field omitted):

:-: ![](/.topwrite/assets/image_1781592911891.png =741)

^

### Step 2: Based on the metric requirements document, create the corresponding Semantic View

Once the requirements document is confirmed, it is **not archived and forgotten** — it is immediately translated into a **Semantic View** in the Lakehouse that corresponds to it one-to-one. Entity, join\_path, dimension, and metric are defined in a single step, and **lineage is declared at this moment** (note: "declared," not parsed after the fact — this is the prerequisite for the reverse impact analysis in Step 4).

Continue with the request: "Help me save these metrics as a Semantic View, named sv\_gmv\_analysis."

> ⚠️ **A note on naming: set the rules from the start, or governance falls apart later.**
>
> A Semantic View name is not chosen casually — it is the "address" of an enterprise's semantic asset. The recommended naming pattern is `<domain>_<topic>`:
>
> * `sv_` prefix to distinguish it from physical tables and regular views at a glance.
> * **Business domain** (e.g., `ecom` for e-commerce, `fin` for finance) + **analytics topic** (e.g., `gmv`, `sales`, `fulfillment`).
>
> This example uses `sv_gmv_analysis` (sales / GMV analytics topic). The value of this pattern only becomes apparent **at scale**: when an enterprise has multiple business domains and dozens of semantic views, `sv_ecom_gmv`, `sv_ecom_fulfillment`, and `sv_fin_revenue` appear as a coherent set, **making definitions across domains immediately distinguishable while remaining manageable in one namespace** — preventing "repeat purchase rate" from having one version in domain A and another in domain B with nobody sure which to use.

DataAgent generates the Semantic View accordingly:

\:-:
![](/.topwrite/assets/image_1781592940964.png =680)

^

At this point, the GMV metrics have a **single, machine-readable definition**. The requirements document and `sv_gmv_analysis` are bidirectionally bound — the document is no longer a stale footnote on a wiki; it is a human-readable view of this Semantic View. The drift of "document says A, production computes B" is structurally impossible from here.

### Step 3: A definition change — change one place, take effect everywhere (forward linkage)

Metric requirements are never defined once and done. One day the business stakeholder says:

> "Help me adjust the GMV metric definition — exclude returned orders."

With the traditional approach, this is a high-risk operation: a global grep of all SQL and dashboards using the metric, one-by-one updates, and any missed instance means old and new definitions coexist with mismatched numbers.

In this practice, **only one source is changed: the Semantic View**.

**1) First submit the update request and have the Agent produce the definition description.** The Agent does not act immediately; it first clarifies "how to identify returned orders" — another "inference + confirmation" step:

:-: ![](/.topwrite/assets/image_1781593107026.png =680)

**2) After confirmation, update the corresponding Semantic View, achieving unified constraints.** Only the `gmv` metric / shared filter inside `sv_gmv_analysis` is changed — one change, everywhere takes effect:

:-: ![](/.topwrite/assets/image_1781593226519.png =680)

After the change: all **dashboards and downstream reports** referencing GMV automatically use the new definition; DataAgent's **natural language queries** (users asking "what is the GMV?") also automatically apply the new definition; **nobody needs to do a global search and update individually**. The definition change propagates timely and completely — no missed updates, no coexisting versions. This is "forward linkage": one source changes, and all consumers follow.

### Step 4: Before an ETL chain change, analyze which metrics are affected (reverse linkage)

The last type of change — and the most expensive — is when a data engineer needs to modify the physical layer (refactoring a table, changing a field's meaning). Before acting, they need to know: **which metric definitions would this change affect?**

The user simply asks:

> "Help me look at the lineage of `sv_gmv_analysis`."

Because lineage was **declared during generation** in Step 2 and is machine-readable, DataAgent can display both directions:

:-: \:-:
![](/.topwrite/assets/image_1781593304358.png =670)
![](/.topwrite/assets/image_1781496039746.png =680)

### Step 5: Use the Semantic View for analysis

The first four steps built and governed the semantic layer. The final step returns to its original purpose — **making the act of analysis consist of nothing more than asking questions**.

An analyst no longer needs to worry about which tables the GMV joins, how to filter for valid orders, or how to truncate months — all of those definitions are hardwired into `sv_gmv_analysis`. For example, to view **monthly GMV and order volume trends in 2017 to determine whether the business is growing or declining**:

:-: They only need to specify "which metrics and which dimensions" — **without rewriting "what counts as a valid order" or "how GMV is calculated"**. Compared to the bare SQL every analyst would otherwise write without a semantic layer — where definition conflicts (valid orders, GMV calculation) hide inside a tangle of joins and where clauses — now there is only one source of truth.
![](/.topwrite/assets/image_1781496048186.png =680)

## The Burden of Governance Should Not Fall on People

Metrics are hard to govern not because there are too many metrics, but because **requirements, documents, implementations, and lineage each operate independently, all depending on people to maintain their synchronization**.

What DataAgent does is bind metric requirements and Semantic View into one unit: submitting a requirement creates the semantic definition; definition changes automatically propagate to all consumers; when the physical layer moves, the affected metric definitions are identified immediately — **synchronization is no longer a daily task; it is the natural output of the system**.

The most tedious parts of data governance — aligning definitions, tracing lineage, preventing drift — are eliminated at the root. What remains is a semantic layer that grows by itself, closes the loop by itself, and alerts by itself, and a data team that no longer needs to fight fires.
