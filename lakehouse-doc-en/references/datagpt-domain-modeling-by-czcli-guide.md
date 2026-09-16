# Driving Agent Analysis Domain Modeling with CZ-CLI

> Express your intent in natural language, and let the Agent handle the operations — a complete workflow from domain creation to ongoing governance

> **Environment requirement**: CZ-CLI >= 1.17.18. Check version: `cz-cli --version`. Below this version, features like `knowledge create` and `domain joins discover` are unavailable. Upgrade with: `cz-cli update`.

## How to Read This Guide

This guide teaches you **how to collaborate with the Agent** to work on analysis domains — not how to navigate web pages or memorize CLI commands.

Collaborating with the Agent is a conversation. You describe what you want to do — "add an alias to the customers table", "add a few metrics", "check domain completeness" — the Agent understands your intent, executes the operation, and reports back. You don't need to know which menu holds the config option, how many parameters a command takes, or what format a table name uses. What you need to know is what concepts make up an analysis domain, and what information and judgment each step requires from you.

This guide has three parts:

- **Chapter 2**: The conceptual model of an analysis domain — what it consists of, what each part does, and what questions it can answer once built
- **Chapter 3 + Chapter 4**: Two hands-on examples — deep refinement of a single domain (banking domain, from 40 to 92 points) and batch creation of four domains (logistics / insurance / healthcare / manufacturing), showing the full conversational collaboration process
- **Chapter 5**: Ongoing governance scenarios after a domain is built — common maintenance issues and corresponding conversation patterns

The CLI commands the Agent executes in the background are listed in the appendix for your reference, but you are not required to memorize them.

---

## 1. Introduction

### Pain Points

An analysis domain isn't done once it's built. Data keeps coming in, rules keep changing, user feedback keeps iterating — governance is a long-term commitment. But traditional approaches (clicking through web pages item by item) make this **feel like something you don't want to do**.

| Scenario | Actual steps | Emotional reaction |
|---|---|---|
| User reports "can't find customer name" | Might just be a missing alias on a field. But fixing it requires: open page → find the domain → find the table → find the field → click edit → enter alias → save | "Ugh, I have to click through all that again..." |
| Audit 5 domains | Check metric coverage and field description rates. Pages can only be opened one by one | "I'll get to it when I have time..." |
| Added a new table | Add table, fill aliases, define metrics, configure JOINs — same combination every time | "I'll do this later, it's not urgent" |
| Regulatory rule change | Update one line in a knowledge description. Must upload a file, create a folder, rebind | "All this just to change one line?" |

**Each individual operation isn't hard or time-consuming. But it's tedious, repetitive, and fragmented — the accumulation creates a negative emotional spiral.** Users procrastinate, skip non-urgent maintenance tasks, and the analysis domain quality degrades over time. Data Analytics Agent answers start becoming less accurate. Not because of capability issues — because it's **annoying**.

### Shifting the Burden from Operations to Decisions

Agent + CLI doesn't eliminate work — it **relocates work**.

```
Traditional web page approach ──────────────→ Agent + CLI approach
Hard part: knowing where to operate           Hard part: expressing the need precisely
           (Which schema is the table in?              (Which fields need aliases?
            Which config page is the field on?           What should the aliases be?
            How do I write the metric expression?        Is the metric expression correct?
            How do I upload and bind knowledge?)         Is the knowledge content accurate?)
            ...
```

**The center of work shifts**: from "operating the page" to "describing the need." Users no longer need to know which menu holds the config, what format a table name uses, or how many parameters a command takes — the Agent and CLI handle all of that. But users need to be able to clearly articulate: what I want to change, what it should look like, and what result I expect.

This isn't necessarily easier or harder than learning page navigation — **the type of difficulty changes**. What's required is an accurate understanding of analysis domain concepts (knowing that "field alias" is a thing) and accurate expression of business needs (knowing what this field should be called in business terms).

In practice:
- Changing an alias: no need to know which schema the table is in or where the field lives. But you need to know you're adding an "alias" rather than a "description," and the correct business name
- Adding a metric: no need to know the format of `--table-name`. But you need to understand what the metric means (COUNT or SUM? Does it need ROUND?)
- Quality audit: no need to open each domain one by one. But you need to understand what each dimension's score means and judge which missing items should be prioritized

**The burden shifts from "operational" to "decisional."** The annoyance of operations is removed; the difficulty of decisions remains — and that's appropriate, because decisions are inherently something humans should make.

### The Solution

**Let the Agent handle the operations; humans handle only the decisions.**

```
Human: describe intent                      Agent: understand context + execute + report results
─────────────────                           ─────────────────────────────────────────────────
"Add an alias 'Customer Name'               Check domain detail → find customers table →
 to the customer_name field                 locate customer_name field → execute change →
 in the customers table"                    confirm alias is in effect
                                    
"Check metric coverage                      Check each domain → compare metric counts →
 across four domains"                       output comparison table → flag domains with gaps
```

The Agent's methodology is based on three design principles:

**Hand off the operational layer to machines.** Adding aliases to 67 fields — humans shouldn't do repetitive manual work. The Agent applies the same standard to each one, without fatigue or skipping.

**Hand off memory to the system.** Governance is fragmented: add a table today, change a rule next week. Users don't need to recall "where did I leave off last time" or "what's the table name in this domain" — the Agent starts from the current domain state, with unbroken context.

**Hand off inference to the LLM.** Seeing that a `loans` table has `principal` and `interest_rate` columns, the Agent can infer that "total loan amount" and "average interest rate" should be defined — without users specifying them one by one. But whether the expressed formula is correct remains a human judgment call.

These three things solve "operational burden" — repetition, memory, inference. The remaining "decisional burden" — judging what to change, whether it was changed correctly, how to prioritize — remains the human's responsibility.

---

## 2. What Is an Analysis Domain

An analysis domain is **a six-layer model that translates physical tables into business language**. Each layer doesn't need to be perfect before it can be used — you can build them up incrementally, and each layer takes effect immediately once built.

### Layer 1: Table Ingestion

**What it does**: Tells the Agent where data is — which schema, which tables.

**What you need to provide**: Schema location, tables to ingest.

**What it can answer once done**:
```
"How many records are in the customers table?" "What fields does it have?"
```

At this point the Agent only knows table and column names — it has no understanding of business meaning.

### Layer 2: Field Semantics

**What it does**: Adds aliases and business descriptions to fields.

**What you need to provide**: Which fields are business-critical (names, amounts, statuses, dates). The Agent can infer which fields need aliases, but business descriptions need user confirmation.

**What it can answer once done**:
```
"What customer types are there?" "Which account has the highest balance?"
```

The Agent now knows "customer type" maps to `customer_type` and "balance" maps to `balance`. The translation layer between natural language and physical column names is established.

**Bonus: virtual columns.** Some fields don't exist in the table but are needed by the business — for example "credit utilization = outstanding balance / credit limit." The Agent can help you define these derived fields.

### Layer 3: Table Relationships

**What it does**: Tells the Agent the JOIN relationships between tables.

**What you need to provide**: Describe the relationships — "customers is linked to accounts via customer_id." The Agent can auto-discover relationships between columns with the same name, but needs you to confirm.

**What it can answer once done**:
```
"Total deposits by branch?" "Loan delinquency status for this customer?"
```

The Agent can now query across tables and automatically generate correct JOIN SQL.

### Layer 4: Metrics

**What it does**: Defines the statistics the business cares about.

**What you need to provide**: Which metrics are needed — "total transaction amount, average interest rate, delinquency rate." The Agent can infer common metrics from the table structure; you confirm whether the expressions are correct.

**What it can answer once done**:
```
"What is the total transaction amount?" "Delinquency rate comparison by branch?"
```

The Agent no longer needs to reason about aggregation logic each time — metrics are predefined and values are returned directly.

### Layer 5: Knowledge

**What it does**: Tells the Agent business rules, terminology definitions, and judgment criteria.

**What you need to provide**: Industry knowledge — "delinquency over 30 days is considered serious," "risk score above 60 is high risk," "mortgage delinquency rate warning threshold is 3%." Usually provided in document form.

**What it can answer once done**:
```
"Is a 4.1% delinquency rate serious?" "What is this customer's risk level?"
```

The Agent not only returns numbers but can also make business judgments — placing data in industry context for interpretation.

### Layer 6: Answer Builder

**What it does**: Locks frequently needed analysis scenarios into preset templates.

**What you need to provide**: Which analyses are repeatedly needed — "loan delinquency monitoring," "card spending merchant analysis." The Agent helps generate SQL and analysis panel configurations.

**Once done**: Users say "loan delinquency monitoring" to open the full analysis panel, without needing to describe the analysis requirements each time.

---

## 3. Hands-On Example 1: Deep Refinement of a Single Domain

> The complete process of taking the banking domain from 40 to 92 points. This is not a "one-sentence magic" demo — it's a real iterative collaboration: build each step, validate, find issues, fix them, continue.

The banking data is in the `bnk_banking` schema with 9 tables: customers / accounts / branches / credit_cards (dimensions) + transactions / card_transactions / loans / loan_payments / audit_log (facts).

### 3.1 Check Current State

The domain is already built (ID 28), but only the most basic table ingestion has been done.

User: **"Help me check the semantic build status of the newly created banking domain"**

Agent checks domain details:
```
→ 9 tables ingested
→ 67 fields, all types auto-inferred correctly
→ Field descriptions all empty, aliases all empty
→ Metrics: 0, Knowledge: 0, Sample questions: 0
→ Score: 40/100
```

This is the starting point — tables exist, but the Agent has no understanding of business meaning. The user decides to continue building.

### 3.2 Start Filling In

After the Agent reported the domain state (9 tables / 0 metrics / 0 knowledge / 40 points):

```
User: need
```

Just two words. The Agent understood — fill in the banking domain from its current 40-point state to a usable level. The Agent lists what needs to be done: 67 field descriptions, 16 metrics, 6 knowledge items, 8 JOINs, 4 virtual columns, then starts executing item by item.

**Field descriptions and aliases.** The Agent sets business descriptions for all 67 fields one by one, and adds Chinese aliases to 27 key fields. No need for the user to confirm each one — the Agent infers suitable aliases from field names (`customer_name` → "Customer Name," `risk_score` → "Risk Score," `balance` → "Balance"), then reports results after execution.

**Metrics.** The Agent defines core aggregations on each fact table. When user judgment is needed (e.g., "Which field should be the numerator for delinquency rate?"), the Agent pauses and asks.

**Knowledge.** The Agent creates 6 business knowledge items using file paths (customer classification, loan types, delinquency rate calculation, credit card metrics, merchant categories, transaction types). After creation —

### 3.3 Knowledge Not Visible

```
User: still can't see the knowledge on the page
```

Agent checks: CLI `knowledge list --domain-id 28` returns 6 entries. But the "Data Knowledge" tab on the web page is empty.

Agent identifies root cause: knowledge has two storage paths — API text entries and knowledge space file nodes. The current method used API approach; the page only renders file nodes. Agent switches approach: writes knowledge content as Markdown files and recreates them through the file upload path (upload → create folder → move in → bind to domain).

```
User: this time it works. So it was the command that had the issue?
```

Agent confirms: yes, entries created by `knowledge create` don't appear in the page file tree. All future knowledge should go through the file upload path.

### 3.4 Table Relationship Failure

```
User: what's the issue with the table relationship command?
```

Agent tries auto-discovery: `domain joins discover`, returns FAIL. Retries 3 consecutive times, all fail. Tries switching to a different profile, still FAIL.

```
User: try a different way to discover the table join relationships, then configure the table associations
```

Agent changes approach: no longer relying on auto-discovery. Switches to the data instance and validates FK data match rates pair by pair using SQL (`SELECT COUNT(DISTINCT a.customer_id), COUNT(DISTINCT c.customer_id) FROM accounts a LEFT JOIN customers c...`). All 7 relationship pairs are 100% matched.

Confirmed: FKs exist but the auto-discovery engine has a bug. Agent's temporary workaround: write the 8 JOIN rules into the domain's custom prompt so the Agent references these rules when generating SQL. Functionally equivalent, but doesn't use the formal JOIN metadata configuration.

After upgrading to v1.17.18, the `domain join create` command becomes available. The Agent uses the new command to rebuild all 8 JOINs, replacing the prompt workaround.

### 3.5 Continued Additions

```
User: add aliases to key fields
```

Agent adds Chinese aliases to 27 fields (Customer Name, Risk Score, Balance, Loan Type, Principal, Annual Interest Rate...).

```
User: help me create some knowledge items
```

Agent adds 6 business knowledge items.

```
User: can continue adding more
```

Agent interprets this as adding Answer Builders and virtual columns. Creates 3 ABs (loan delinquency monitoring, card spending merchant analysis, customer deposit overview) and 4 virtual columns (credit utilization, transaction month, delinquency flag, card transaction month).

### 3.6 Final Check

User: **"Check the complete state of the banking domain"**

```
Tables: 9    Field descriptions: 67    Aliases: 27
Metrics: 16    Complex metrics (AB): 3
Knowledge: 6    JOINs: 8    Virtual columns: 4
Score: 92/100
```

### 3.7 The Real Pattern of This Process

Looking back at the entire conversation, it's not a straight line of "one command → perfect result." It's:

```
Check current state → Start building → Discover issue → Diagnose root cause → Fix → Continue building → Discover new issue → ...
    ↑                                                                                                           ↓
    └──────────────────── Each round loops back to "check current state" ─────────────────────────────────────┘
```

This is the normal pattern of analysis domain governance — **build and validate in parallel, solve problems as they come, then keep going**. The Agent's value isn't in doing everything right the first time — it's in each iteration: humans only need to describe the problem and the need; the Agent handles diagnosis, execution, and reporting results.

---

## 4. Hands-On Example 2: Batch Industrial-Scale Replication

> Centralized build of four domains: logistics, insurance, healthcare, manufacturing. The methodology from the banking domain is reused directly, but each domain still requires its own "discover → build → validate → fix" iteration.

### 4.1 Explore the Data First

After the banking domain was complete, the user systematically searched for other buildable data across 62 schemas.

```
User: can you check what schemas I have?
```

Agent switches instances and lists all 62 schemas.

```
User: logistics_dw ins_insurance hrc_healthcare mfg_manufacturing
      what tables are in each of these schemas?
```

Agent lists the tables under all four schemas one by one. Each is a standard star model. After filtering, the four domains have 9 / 8 / 10 / 8 usable tables respectively.

### 4.2 Start Batch Build

```
User: create four corresponding domains
```

Agent creates four domains in parallel (IDs 29–32). Each is configured with a name, description, and 3–5 sample questions. Then tables are added in batch — lessons from the banking domain mean the parameter format is already known, and all four domains add tables smoothly.

```
User: need
```

Agent understood — same as the banking domain, all four domains need to be filled in from their current skeleton state to a usable level. Agent starts adding metrics (5–8 per domain), JOINs (4–5 per domain), and knowledge (4 items per domain) for all four.

### 4.3 Issues Found During Build

**Missing tables.** The Agent discovers data inconsistency during the final check:

Insurance domain targetCounts.dataset = 7, but should be 8 (policies table missing). Manufacturing domain similarly — quality_inspections wasn't added. Both tables silently failed during batch table addition — returning success but not actually taking effect. Agent immediately adds them.

**Column name mismatch.** When creating the "shipping trend analysis" Answer Builder for the logistics domain, SQL reports a column name error. Agent checks `table columns` and finds: the physical table's `shipment_date` was renamed to `stat_date` in the v_gpt view. After correcting the column name, the creation succeeds.

**Dataset ID mapping confusion.** When creating JOINs for the insurance domain, the Agent used the numeric ID of `policyholders` for `reinsurance_treaties`, causing "column not found." Agent switches to its own method: first runs `domain detail` to list all 8 tables' ID mappings, then creates each JOIN one by one — no more relying on memory.

### 4.4 Continue Filling In

```
User: can continue adding more
```

Agent adds Answer Builders (2 per domain) and virtual columns (9 across all domains) to the four domains. The "quality inspection pass rate analysis" for the manufacturing domain fails the first time — `CASE WHEN result='PASS'` has a string constant conflicting with JSON quotes. Agent wraps it in a virtual column and recreates it.

### 4.5 Final State

Agent summarizes the build results for the four domains:

```
Logistics Demo (29): 8 tables, 8+2 metrics, 4 JOINs, score 82
Insurance Demo (30): 8 tables, 6+1 metrics, 5 JOINs, score 78
Healthcare Demo (31): 9 tables, 6+2 metrics, 4 JOINs, score 82
Manufacturing Demo (32): 8 tables, 6+2 metrics, 4 JOINs, score 84
```

### 4.6 The Real Pattern of Batch Build

```
Explore data → Confirm table structure → Batch create domains + add tables → Batch configure semantics → Discover issues (missing tables, column name mismatches, ID mapping confusion)
                                                                                                          ↓
                                                                                                     Fix → Re-validate → Continue filling in
```

Lessons from the banking domain are reused (knowledge goes through file path, JOINs created manually, table addition parameters provided all at once), but each new domain still has its own issues — column name mismatches, silent table failures, ID mapping confusion. **The Agent's value is: each time an issue is discovered, users don't need to dig through pages to find the cause — the Agent checks details, diagnoses the root cause, executes the fix, and humans only need to confirm "was the fix correct."**

---

## 5. Ongoing Governance

After a domain is built, day-to-day maintenance is also handled through the Agent:

**Add a new table.** "bnk_banking added an investment_portfolio table. Add it to the banking domain and fill in field aliases and metrics."

**Update an alias.** "Change the alias for customer_type in the customers table from 'Customer Type' to 'Customer Category'."

**Update knowledge.** "Update the delinquency rate warning threshold from 3% to 2.5% in the banking domain's knowledge file."

**Quality audit.** "Check the metric coverage of five domains and list each domain's score and missing items."

After each operation, the Agent returns the execution result and the domain's latest state, so users can immediately confirm whether the expected outcome was achieved.

---

## Appendix A: Industry Domain Entity Reference

### Banking (banking)
```
Dimensions: customers / accounts / branches / credit_cards
Facts: transactions / card_transactions / loans / loan_payments + audit_log
FK: accounts→customers | credit_cards→customers/accounts | transactions→accounts
    loans→customers | loan_payments→loans | card_transactions→credit_cards | customers→branches
```

### Logistics (logistics_dw)
```
Dimensions: dim_carrier / dim_customer / dim_shipment_method / dim_warehouse
Facts: fact_shipment / fact_inventory + gld_carrier_kpi / gld_daily_shipment
```

### Insurance (ins_insurance)
```
Dimensions: policyholders / agents / insurance_products
Facts: policies / claims / claim_payments / underwriting / reinsurance_treaties
```

### Healthcare (hrc_healthcare)
```
Dimensions: patients / providers / facilities / medications
Facts: encounters / diagnoses / procedures + lab_orders / lab_results / allergies
```

### Manufacturing (mfg_manufacturing)
```
Dimensions: products / components / suppliers
Facts: bill_of_materials / work_orders / inventory / quality_inspections / supplier_components
```

---

## Appendix B: CLI Commands Behind the Agent

You don't need to run these commands in day-to-day use — the Agent handles them for you. They are listed here for reference to help you understand how the Agent works.

| Operation | Command the Agent runs |
|---|---|
| Create domain | `domain create --name "..." --datasource-id ... --description "..." --sample-question "..."` |
| Add table | `domain table add <id> --datasource-id ... --workspace ... --schema ... --table ...` |
| Field description | `table semantics set <ds> <attr> --description "..."` |
| Field alias | `table semantics set <ds> <attr> --alias "..."` |
| Virtual column | `column virtual set <ds> --name "..." --type "..." --expression "..."` |
| Metric | `metric create --domain-id ... --table-name "..." --name "..." --expression "..."` |
| JOIN | `domain join create <id> --dataset-id ... --attr-code ... --relation "n:1"` |
| Knowledge | `knowledge file upload 1 file.md` → `folder create` → `file move` → `node bind-domain` |
| Answer Builder | `answer-builder create --analysis-name "..." --content '{...}'` |
| Validate | `domain detail <id>` |
