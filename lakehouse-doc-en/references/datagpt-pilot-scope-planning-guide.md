# How Administrators Should Plan Analytics Agent Pilot Scenarios

Many teams first encountering Analytics Agent run into questions that are not "how do I ask a question" or "how do I configure a field," but rather:

- Which business scenario should we pilot first?
- Which tables, users, and questions should be included in the first batch?
- What kind of pilot is more likely to deliver business value?
- What kind of pilot looks broad in scope but is actually more likely to get out of control?

A well-chosen pilot scenario helps teams see real value faster and makes it easier to stabilize Q&A quality. A pilot scenario that is too large, too varied, or too sensitive often causes teams to quickly lose momentum on field ambiguity, definition conflicts, permission complexity, and validation cost.

Therefore, planning a pilot scenario is not "find a batch of tables and put them in" — it starts with deciding: which category of users, around which category of questions, within which scope, will validate the business value of Analytics Agent.

## Why Pilot Scenario Planning Matters

The value of Analytics Agent does not come from "connecting a chat interface to a database." It comes from having a large language model complete analysis within a business context that has already been prepared. Whether that context is clear is directly tied to the pilot scenario selected.

When the pilot scenario has clear boundaries:

- Analytics domains are easier to plan.
- Field semantics are easier to complete.
- Metrics and knowledge are easier to standardize.
- Permission boundaries are easier to control.
- Validation question sets are easier to build.

When the pilot scenario has blurry boundaries:

- Analytics domains quickly grow too large.
- Similar fields and similar definitions easily conflict.
- Multi-department permissions are hard to untangle in one pass.
- Administrators do not know which configuration to fix first.
- Business users encounter inconsistent answers from the start and lose confidence in the product.

Therefore, the focus of the pilot phase is not to cover more business scenarios — it is to validate a clear, valuable, and verifiable scenario end to end.

## What the Pilot Should Validate Beyond Q&A Capability

A pilot scenario's goal should not be only to prove "the system can answer a few questions." It should validate at least the following:

| What to validate | Explanation |
| --- | --- |
| Whether business users are willing to ask questions in natural language | Is the entry point natural enough; do questions match everyday business expressions? |
| Whether analytics domain boundaries are reasonable | Can the system consistently select the right data within the current domain? |
| Whether key business terms can be understood | Is semantic configuration, knowledge, and metrics sufficient to absorb real business language? |
| Whether core definitions are consistent | Does the same question get a consistent interpretation each time? |
| Whether permission boundaries are controllable | Does each role see the data range they are supposed to see? |
| Whether administrative work is verifiable | Does the team know how to use representative questions to judge whether configuration is production-ready? |

If the pilot can only prove "this system occasionally answers a few questions correctly," its value remains at the demo level. Only when the pilot validates business value, governance boundaries, and validation method together can the team more confidently move toward the production phase.

## Scenarios Well-Suited for an Early Pilot

Bigger is not better for a pilot — clearer is better. Scenarios that are better suited for an early start typically have the following characteristics.

### High-Frequency Query Scenarios

Prioritize scenarios where business users already frequently query, check, and export information.

Examples:

- The sales team checks pipeline count, signed contracts, and payment progress daily.
- The operations team checks new users, active users, and conversion rates daily.
- The customer success team regularly checks renewing customers, churned customers, and account health.

The value of these scenarios is easier for business users to perceive directly, because they replace existing real work rather than creating an entirely new way of working.

### Scenarios With Relatively Clear Definitions

The pilot phase is better suited for scenarios where key metrics already have basic consensus, rather than jumping immediately into the domain with the most contested definitions.

Examples:

- Account count, active account count, new account count
- Signed contract count, renewing customers count
- Comparisons by channel, region, product, or subscription plan

If the most common questions in a scenario still have no unified definition, the pilot easily turns into "spending most of the time debating definitions" — delaying judgment of the product's actual value.

### Scenarios With a Relatively Contained Data Scope

The pilot phase is better suited for scenarios that can build Q&A around a small number of core tables, rather than depending from the start on a large number of cross-department, multi-topic, multi-tier tables.

Examples:

- Customer health analysis within a single thematic domain
- Business analysis for a single business line
- Operations analysis for a specific channel or product line

This makes it easier to build out semantics, metrics, Answer Builders, and the validation question set solidly.

### Scenarios With Identified Business Users and Maintainers

A pilot that can be sustained typically requires two types of people simultaneously:

- People who will genuinely use it: business owners, business analysts, operations or sales staff
- People who can maintain it: data maintainers, BI analysts, administrators

Without genuine users, the pilot easily becomes internal self-testing. Without maintainers, even when problems surface they are hard to fix and verify promptly.

## Scenarios Not Suited for an Early Pilot

Some scenarios look important but are not suitable as the first pilot batch.

### Large, All-Encompassing Scenarios That Cross Many Departments and Definitions

For example, starting with "a company-wide business overview domain" that includes questions about sales, finance, operations, customer success, and HR all in one pilot.

The problem is not whether the system can accommodate this — it is that:

- Field and knowledge ambiguity accumulates quickly.
- Metric definitions are more likely to conflict.
- Permission boundaries become complex.
- After a pilot failure, it is hard to determine which layer the problem originated from.

A more reliable approach is to start from one department domain or thematic domain and expand incrementally to an overview domain.

### Scenarios Where Core Definitions Have Long Been Unresolved

If a business domain still has no basic consensus on core terms like "revenue," "active customers," or "conversion rate," it is not suited as a first-priority pilot scenario.

This does not mean it cannot be done — it means it is better suited as a second-phase objective: first validate a relatively clear scenario end to end, then tackle the domain with more contested definitions.

### Scenarios With High Sensitivity and Insufficient Governance Preparation

For example, high-sensitivity data scenarios involving compensation, financial vouchers, or customer privacy — if role configuration, field hiding, row-level permissions, and audit are not yet sufficiently prepared, these are not suited for early business-side access.

These scenarios have high governance requirements and are better brought in after the team has mastered analytics domain planning, permission control, and validation methodology.

### Scenarios Entirely Dependent on Complex Multi-Table Reasoning From Day One

If a question scenario depends heavily from day one on multi-table JOINs, complex derived definitions, and fixed analytical logic, and the team has not yet prepared Answer Builders and standard definitions, the pilot is likely to be inconsistent.

These scenarios are not impossible to do — but they are better suited as "the second layer of capability validation" in a pilot, rather than the first set of launch scenarios.

## How to Define the Scope of a Pilot Scenario

A pilot scenario must first clarify four scopes.

### Define the Business Scope

First answer: what category of business questions does this pilot aim to address?

For example:

- Not "what can sales ask about," but "how the sales team views pipeline progress and contract results"
- Not "what can operations ask about," but "user growth and active user analysis"

The more specific the scope, the easier the pilot is to execute.

### Define the Data Scope

Then answer: to answer these questions, which tables are needed in the first batch?

The principle here is not "add everything that might be needed" — it is "include only the core tables that current high-frequency questions genuinely require."

A better approach:

- Start by listing high-frequency questions.
- Then work backwards from the questions to identify which tables are needed.
- Finally, include only those tables in the analytics domain.

This makes it easier to control analytics domain size and avoid irrelevant fields and tables interfering with Q&A.

### Define the User Scope

The pilot phase should not open to all business users at once.

A more suitable user scope typically consists of:

- A small group of business users who will genuinely use the system.
- One or a few BI analysts who can review SQL and records.
- One administrator or maintainer who can handle permissions, domains, and governance issues.

This combination makes it easier to form a feedback loop.

### Define the Question Scope

The most dangerous thing in a pilot is having no fixed question scope. Without scope, the team cannot tell "whether this pilot succeeded."

Prepare a representative set of questions before the pilot begins, typically including:

- 5 to 10 high-frequency questions
- 2 to 3 questions prone to ambiguity
- 2 to 3 complex questions
- 1 to 2 permission verification questions

This gives the pilot a clear acceptance target from the start.

## An Actionable Pilot Planning Method

For administrators who need a more direct method, follow these steps in order.

### Step 1: Define the pilot objectives first

Write clearly what this pilot is meant to prove.

For example:

- Can business users query account health using natural language?
- Can core metrics be answered consistently?
- Can complex account health overviews be handled through Answer Builders?
- Can permission scope be controlled by role?

If the pilot objectives cannot be written clearly, no amount of configuration later will make it easy to judge success.

### Step 2: List representative business questions

Do not start from tables — start from questions.

Examples:

- `How many active accounts are currently on the Basic plan?`
- `Show account count, active account count, and active rate by plan.`
- `For the Google channel only, show active rate and active seats by plan.`
- `Do an ordinary business user and a regional manager see the same data range?`

These questions will determine which tables to add, which semantics to fill in, and which metrics and Answer Builders to build.

### Step 3: Work backwards from questions to data and configuration

Use the questions to determine:

- Which tables are needed
- Which field semantics are needed
- Which terms need knowledge to explain
- Which definitions are suitable for building metrics
- Which complex questions need Answer Builders
- Whether role or row-level permissions are needed

This way configuration work is no longer abstract "building a semantic layer" — it directly serves a set of questions to be solved.

### Step 4: Limit the scope of the first batch

In the pilot phase, actively limit scope:

- Cover only one thematic domain
- Include only one set of core tables
- Open access to only a small group of business users
- Cover only one defined set of questions

This is not reducing product value — it is making value visible earlier and making problems easier to locate.

### Step 5: Define acceptance criteria in advance

Do not wait until configuration is complete to think about how to verify it. A more reliable approach is to confirm at the start of the pilot:

- Which questions must pass
- Which questions allow manual review
- Which evidence to look at — answers, charts, SQL, records, and permission results
- Who will confirm pass or fail

This prevents the pilot from devolving into "it feels like it's good enough to use."

## How to Tell Whether a Pilot Scenario Was Well-Chosen

A well-chosen pilot scenario will typically show these signals:

- Business users quickly understand "what this domain can help me do."
- Maintainers have a fairly clear sense of which field semantics, knowledge, and metrics to fill in.
- Although complex questions are few, each configuration addition produces a clear improvement in Q&A quality.
- The validation question set can gradually stabilize.
- Permission boundaries are relatively clear without a large number of exception rules.

Conversely, if a pilot scenario shows these symptoms from the start, it usually means the scope needs to be reduced:

- Business questions span multiple unrelated topics.
- Many tables must be added at once to barely cover the questions.
- Key terms have very different meanings to different people.
- Business users immediately encounter frequent permission conflicts.
- The team cannot clearly state "what this pilot is meant to prove."

In these cases, continuing to pile on configuration often has limited effect. Reducing scope first is the better path.

## What to Expand After a Successful Pilot

After validating a pilot, it is not recommended to immediately bring in all business scenarios. Instead, expand gradually in the following directions:

- From a single thematic domain to adjacent thematic domains within the same department
- From a few core questions to more high-frequency questions
- From simple metrics to more complex Answer Builders
- From a single role to more roles and permission boundaries
- From pilot users to a broader business user base

The order of expansion should still follow the same principle: expand along already-validated value paths rather than expanding all scope at once.

## Common Pilot Planning Mistakes

### Trying to cover all business from the start

This is the most likely way to make the analytics domain quickly get out of control, and to turn the pilot into "everywhere is almost good enough."

### Adding tables first, then figuring out the questions

This order lets the analytics domain be driven by data structure rather than business questions, and later it is very easy for large numbers of irrelevant fields and tables to appear.

### Chasing complex questions first to look more advanced

Complex questions certainly matter, but in the pilot phase it is more important to first validate high-frequency questions, baseline definitions, and the validation method.

### Making business users carry too much of the clarification burden

If business users must constantly supply field names, underlying conditions, and technical expressions, this usually means back-end semantics and definition absorption are insufficient — the problem should not be attributed simply to "users not knowing how to ask."

### Unclear pilot success criteria

If the team has not defined in advance "which questions must pass, which evidence to review, and who confirms the result," the pilot easily stays at the level of subjective impressions.

## Related Documentation

- [From PoC to Production: Analytics Agent Adoption Guide](datagpt-production-adoption-guide.md) — the overall path from pilot to production
- [How Administrators Validate That Analytics Agent Configuration Is Production-Ready](datagpt-management-validation-guide.md) — how to use representative business questions for acceptance
- [Analytics Domain Planning Guide](datagpt-domain-planning-guide.md) — how to plan analytics domains by business topic, definition, and permissions
- [Configure an Analytics Domain](datagpt-domain-management-guide.md) — create a domain, add tables, and manage permissions
- [Launch an Analytics Domain](datagpt-domain-health-check-and-launch-checklist.md) — pre-launch health check and manual inspection
