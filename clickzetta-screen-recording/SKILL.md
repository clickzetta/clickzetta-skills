---
name: clickzetta-screen-recording
description: |
  Skill for screen-recording-assisted narration workflow. Covers two phases: pre-recording setup (create a promptSubmit hook to auto-log user messages with Beijing timestamps) and post-recording script generation (produce a footage manifest and shot script from the operation log).

  Trigger when the user says: "开始录屏", "录屏前初始化", "创建录屏 Hook", "录完了", "录屏结束", "生成素材清单", "生成镜头脚本", "录屏后整理", "根据录屏后 md 生成脚本", "start screen recording", "generate shot script".

  Keywords: screen recording, narration, footage manifest, shot script, recording hook, promptSubmit, operation log, 录屏, 素材清单, 镜头脚本, 旁白生成, before recording, after recording
---

# Screen Recording Narration Workflow

This skill has two phases. **Read only the reference file for the current phase — never load both at once.**

## Phase routing

| User intent | Phase | Reference to load |
|---|---|---|
| "开始录屏", "录屏前初始化", "准备录屏", "start recording" | Phase 1 — Before | `references/before-recording.md` only |
| "录完了", "录屏结束", "生成素材清单", "生成镜头脚本", "录屏后整理" | Phase 2 — After | `references/after-recording.md` only |

## Phase 1 — Before Recording

Triggered when the user says they are about to start or wants to initialize a recording session.

Read [`references/before-recording.md`](./references/before-recording.md) and follow its instructions.

**Do NOT load `references/after-recording.md` during Phase 1.** Loading it before recording ends will change the AI's response style and break the recording experience.

Stay in Phase 1 until the user explicitly signals that recording has ended (see Phase 2 trigger below). Do not switch phases on your own.

## Phase 2 — After Recording

Triggered **only when the user explicitly tells you the recording has ended** — for example: "录完了", "我们刚才录了一段视频", "开始整理录屏", "生成素材清单或镜头脚本".

Do not enter Phase 2 on your own. Wait for the user's signal.

Once triggered, read [`references/after-recording.md`](./references/after-recording.md) and follow its instructions to generate:
- `素材清单-[date].md` — footage manifest for the editor
- `镜头脚本-[date].md` — shot script for voiceover and post-production

## Out of Scope

This skill only handles recording setup and post-recording script generation. It does not cover:
- Business-specific data query rules or customer case analysis
- One-off troubleshooting or project retrospectives
- Video editing or export (see video production skills)
