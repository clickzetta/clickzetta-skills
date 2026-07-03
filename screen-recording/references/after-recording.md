# Post-Recording Narration Skill

This skill is used for wrap-up after a screen recording session ends. Record normally during the session, then trigger this skill in the same conversation window when done.

**Do not reference this file before recording begins** — it will affect the AI's interaction style. Before recording, only have the AI reference `before-recording.md` to create the operation log hook.

**Scope**: This file only covers footage manifest and shot script generation rules after recording ends. It does not include project retrospectives, data query rules, customer case analysis, or one-off issue handling. Those belong in their respective business skills or project retrospective documents.

**Path convention**: `<recording-dir>` throughout this document refers to the directory where recording output is saved. The default is `./recording-output/` under the current workspace; if the user specified a different directory before recording, use that. Do not write the author's absolute local path.

## How to Trigger

Do not require the user to use a fixed ending phrase. As long as the user expresses that recording has ended or they want to wrap up or generate a script, trigger this file's workflow.

Recognized expressions include but are not limited to:
- Recording finished, we're done recording, ready to wrap up
- Start organizing the recording
- Generate footage manifest, shot script, or post-recording document
- We just recorded a demo

If the user's expression is ambiguous (e.g., "pretty much done", "let's stop here"), confirm in one sentence whether recording has ended before proceeding.

After triggering, immediately delete the recording operation log hook to prevent subsequent conversations from continuing to write to the log. If the current environment cannot delete the hook, prompt the user to disable it manually before continuing.

Time is provided verbally by the user. If they don't remember, leave the time field as "not recorded".

**Output the following files**, all saved in the `<recording-dir>/` directory:
- `footage-manifest-[date].md` — for the editor to locate footage
- `shot-script-[date].md` — for voiceover and post-production
- `recording-log.txt` — the operation log auto-generated during recording, delivered along with the documents above

Date format: `YYYYMMDD`, e.g. `footage-manifest-20260623.md`.

When this skill is triggered after recording, also read `<recording-dir>/recording-log.txt` and map its timestamps to each step in the footage manifest.

By default, generate only the footage manifest and shot script, output sequentially, separated by `---`.

### Document 1: Footage Manifest (for the editor)

**Purpose**: The editor uses this manifest to annotate the raw recording step by step, knowing what each segment is doing and which shot it belongs to.

Output a time info block at the top:

```
Recording date: YYYY-MM-DD
Recording start: HH:MM (Beijing time)
Recording end: HH:MM (Beijing time)
Total duration: approx. X minutes
Source filename: (to be filled by user)
```

Then list operations in chronological order:

```
### [#] [Operation name]
Shot: Shot N — [Shot name]
User prompt: [User's exact words]
AI action: [Commands or operations performed, written in full]
Result: [Result summary, e.g. "returned 20 rows", "error then retry succeeded", "write complete"]
Visual cue: [Key visual description for editor to locate this segment, e.g. "terminal shows 3-column table, first row is customers"]
Edit note: [speed up / keep / skip / highlight / switch to browser]
```

**Edit note guide:**
- `keep` — include at normal speed in the final cut
- `highlight` — recommend slow down or hold; this is a key moment
- `speed up` — recommend 2–3× speed; content is present but doesn't need close attention
- `skip` — recommend cutting; doesn't affect comprehension
- `switch to browser` — need to cut to browser here; specify which page

### Document 2: Shot Script (for voiceover and post-production)

**Purpose**: Maps to the final video structure. Each shot has narration, duration, and visual description. The AI reads this file when revising scripts.

**Core message for all videos (must understand before writing narration):**
> The goal of this series is not to show off technical prowess, but to tell users: the data operations you used to handle yourself can now be handed off to an agent — convenient and reliable. The focus is on "the user said one thing and the agent got it done", not on how complex the technology is. Narration should make viewers feel "wow, this is so simple now", not "wow, this technology is impressive".

Start with a one-line video summary:
> This video demonstrates [topic], for [target audience], target runtime X minutes.

Then output by shot:

```
## Shot N: [Shot name]

Source material: steps X–X (footage manifest sequence range)
Estimated duration: X seconds

Visual: [What the final video shows in this shot, 1–2 sentences]
Narration:
[Narration text, estimated at 3.5 characters/second, must fill the duration]
```

End with a duration summary table:

| Shot | Name | Source steps | Est. duration |
|------|------|-------------|---------------|
| 1    |      |             |               |
| ...  |      |             |               |
| Total |     |             | X min X sec   |

## Narration Writing Guidelines

**Target audience**: People with some data work experience who may not know technical details. They understand "data query" and "data sync" but don't need to know SQL syntax or command-line parameters. Narration should make them feel "I could use this tool and it seems pretty handy".

**Writing rules:**
- Use "the agent" or "we ask the agent" as the subject — not "AI" or "the system"
- Only describe what happens on screen; do not explain technical principles
- Match word count to duration: 3.5 characters/second; 30 seconds needs ~105 characters
- Each shot's narration must cover all "keep" and "highlight" steps within that shot
- Avoid command parameters (e.g. `--sync`, `--write`), error messages, or technical jargon pileups

**Example comparison (use this to review each narration segment):**

Wrong — focused on technical details:
> "We ran the `cz-cli table describe` command with the `--format table` parameter, which returned the DDL structure of the customers table, including 4 column definitions."

Correct — focused on user value:
> "We ask the agent to take a look at this customer table. It pulls up the field structure and sample data right away — no need to open any interface."

## Shot Boundary Rules

The AI decides shot boundaries based on the conversation, following these principles:

**Merge into the same shot:**
- Consecutive operations under the same user intent (e.g. "check table structure" involving describe + preview + stats)
- An "confirm to proceed" message immediately following a Q&A
- An error followed immediately by a successful retry counts as one operation

**Handling error-retry steps:**
- List the error step separately in the footage manifest; write "error" in the result field and "skip" in edit notes
- List the retry step separately right after; write "retry succeeded" in the result field and "keep" in edit notes
- This helps the editor understand the two steps are consecutive with an error clip in between, not two independent operations

**Handling user confirmation messages:**
- "OK", "confirm", "go ahead" messages before high-risk operations (write, delete) must be listed in the footage manifest
- Write the user's exact words; write "waiting for user confirmation before executing [operation]" in AI action; mark edit note as "highlight"
- These moments show that the agent actively waits for confirmation before critical operations — a key highlight for the final cut
- Pure chitchat (unrelated to operations) is not listed in the footage manifest

**List as a separate shot:**
- The user switches to a clearly different operation goal (from "query data" to "modify data")
- A moment requiring a switch to the browser interface
- A clear "highlight moment" that should be spotlighted (e.g. Time Travel, write-protect block)
- Opening title card and closing title card are each their own shot

**Shot count reference:**
Shot count is determined by recording duration and content density — there's no fixed number. Each shot should have a clear single theme that viewers can grasp at a glance. Typically each shot corresponds to 20–45 seconds in the final cut; too short fragments the video, too long loses focus.

## Time Source Rules

- User verbally provided the time → use it as-is, do not modify
- User did not provide time → read `<recording-dir>/recording-log.txt`, use the first entry's timestamp as start time and current system time as end time, calculate total duration
- recording-log.txt does not exist or is empty → fill "not recorded", do not infer or fabricate

