---
name: screen-recording
description: |
  Skill for screen-recording-assisted narration workflow. Covers two phases: pre-recording setup (create a promptSubmit hook to auto-log user messages with Beijing timestamps) and post-recording script generation (produce a footage manifest and shot script from the operation log).

  Trigger when the user says: "start recording", "initialize recording session", "create recording hook", "recording done", "recording finished", "generate footage manifest", "generate shot script", "wrap up recording", "generate script from recording log".

  Keywords: screen recording, narration, footage manifest, shot script, recording hook, promptSubmit, operation log, before recording, after recording
---

# Screen Recording Narration Workflow

This skill has two phases. **Read only the reference file for the current phase — never load both at once.**

## Phase routing

| User intent | Phase | Reference to load |
|---|---|---|
| "start recording", "initialize recording session", "prepare to record" | Phase 1 — Before | `references/before-recording.md` only |
| "recording done", "recording finished", "generate footage manifest", "generate shot script", "wrap up recording" | Phase 2 — After | `references/after-recording.md` only |

## Phase 1 — Before Recording

Triggered when the user says they are about to start or wants to initialize a recording session.

Read [`references/before-recording.md`](./references/before-recording.md) and follow its instructions.

**Do NOT load `references/after-recording.md` during Phase 1.** Loading it before recording ends will change the AI's response style and break the recording experience.

Stay in Phase 1 until the user explicitly signals that recording has ended (see Phase 2 trigger below). Do not switch phases on your own.

## Phase 2 — After Recording

Triggered **only when the user explicitly tells you the recording has ended** — for example: "recording done", "we just recorded a demo", "start wrapping up the recording", "generate footage manifest or shot script".

Do not enter Phase 2 on your own. Wait for the user's signal.

Once triggered, read [`references/after-recording.md`](./references/after-recording.md) and follow its instructions to generate:
- `footage-manifest-[date].md` — footage manifest for the editor
- `shot-script-[date].md` — shot script for voiceover and post-production

## Out of Scope

This skill only handles recording setup and post-recording script generation. It does not cover:
- Business-specific data query rules or customer case analysis
- One-off troubleshooting or project retrospectives
- Video editing or export (see video production skills)
