## Skill Package Capabilities Overview

Package a set of business knowledge, operational procedures, prompt rules, SQL templates, or analytical methods so that an Agent follows those rules when it encounters a matching request.

**What a Skill can do**

* Encode business processes: for example, data profiling, job failure diagnosis, table optimization governance.
* Fix output formats: for example, output a diagnostic report structured as "Conclusion, Evidence, Recommendation".
* Reuse domain knowledge: for example, table relationships, metric definitions, and modeling rules for the Olist e-commerce dataset.
* Manage complex templates: for example, store SQL templates in `references/sql_templates.md` for the Agent to use.
* Improve Agent consistency: avoid re-explaining rules each time and make the same type of task execute more reliably.

**A Skill typically contains**

* `SKILL.md`: the core description file, containing the skill name, description, trigger scenarios, and execution steps.
* `references/`: an optional directory for long documents, SQL templates, rule libraries, metric definitions, etc.
* Other supporting files: such as examples, scripts, and templates.

**A simple example**

```Plain
---name: schema-data-profilingdescription: Profile all tables in a specified schema and output a table inventory, field structure, table relationships, and fact/dimension table classification.---# Schema Data ProfilingWhen the user asks to analyze a schema, execute the following steps:1. List all tables under the schema.2. Retrieve field structure.3. Analyze relationships between tables.4. Count time ranges.5. Classify fact tables and dimension tables.6. Output the profiling report.
```

**Scenarios suited for a Skill**

* A category of tasks recurs frequently.
* There is a fixed business process.
* A stable output format is required.
* There is substantial domain knowledge or templates to reuse.
* You want the Agent to follow a standard automatically.

## Uploading a Skill

**Upload entry point**

* Open the Data Agent page.
* Click `Skills` in the left sidebar.
* Click `+` above the Skill list.
* The `Upload Skill` dialog appears.

**File requirements**

* Supports `.md`, `.zip`, or `.skill` files.

* If uploading a `.md` file:

  * The file must contain a YAML front matter block.
  * The YAML block must include `name` and `description`.

* If uploading a `.zip` or `.skill` file:

  * The archive must contain exactly one `SKILL.md`.
  * Place `SKILL.md` at the top level of the archive to avoid multi-level directory parsing failures.

**Recommended SKILL.md format**

```Plain
---name: skill-upload-smoke-testdescription: A test skill for verifying the Skill upload, display, and invocation pipeline.---# Skill Upload Smoke TestWhen the user asks to run the upload skill smoke test, reply: SKILL_UPLOAD_SMOKE_TEST_OK. Do not perform any external operations or read sensitive information.
```

**YAML rules**

* Must start with three hyphens: `---`
* Must end with three hyphens: `---`
* `name` must have a value.
* `description` must have a value.
* `description` should be written on a single line.
* Do not use `\` to break `description` across lines.
* Multi-line descriptions are not recommended.
* The body starts after the second `---` and can be written as normal Markdown.

**Discouraged formats**

```Plain
--name: bad-skilldescription: Only two hyphens at the start---
```

```Plain
---name: bad-skilldescription: First line \  Second line---
```

```Plain
---name: bad-skilldescription---
```

**Upload steps**

* In the `Upload Skill` dialog, click the upload area.

* Select the prepared `.md` / `.zip` / `.skill` file.

* In the `Prompt` input box, enter a trigger prompt, for example:

  * `Run upload skill smoke test`
  * `Use the data profiling skill`
  * `Profile all tables in the schema`

* Click `Confirm`.

* After a successful upload, the Skill appears in the left Skill list.

* Click a Skill to view its name, type, update time, owner, description, prompt, and body content.

**Using a Skill**

* Click `Use` on the Skill detail page.
* The page returns to the Agent chat box and inserts the Skill tag into the input field.
* Enter your task description and send.
* The Agent should execute or respond according to the Skill content.

**Common failure reasons**

* No `SKILL.md` inside the zip archive.
* Multiple `SKILL.md` files inside the zip archive.
* YAML does not start with `---`.
* YAML is missing the closing `---`.
* Missing `name`.
* Missing `description`.
* Line breaks in `description` cause parsing errors.
* The uploaded file is a fake zip or a corrupted zip.

**Recommendations**

* Keep `description` compressed to a single line.
* Use English letters, digits, and hyphens for file names and `name`.
* Check `SKILL.md` locally before each upload.
* When an upload fails without a clear error message, first check whether `SKILL.md` is missing or the YAML format is incorrect.

## Using a Skill

After selecting a Skill, the Agent will prioritize that Skill as its planning path when formulating a plan, and will plan and execute its current actions accordingly.
![](/.topwrite/assets/image_1785811403575.png)
