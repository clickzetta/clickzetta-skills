# Pre-Recording Initialization

This skill only handles initialization before the recording starts: confirm the working directory and create a user message operation log hook. Do not read `after-recording.md` before recording begins, to avoid affecting the style of interactions during the session.

## Recording Directory

Confirm the recording working directory first. The default is `./recording-output/` under the current workspace; if the user specifies a different directory, use that instead. The placeholder `<recording-dir>` is used throughout this document — do not write the author's absolute local path.

Before creating the hook, replace `<recording-dir>` with the actual path. Do not leave angle-bracket placeholders. If using a relative path, resolve it against the current workspace and tell the user the actual directory in your reply.

## Hook Creation

Create the following hook, then tell the user "Hook created, you can start recording anytime" and note that the log will be written to `<recording-dir>/recording-log.txt`.

```
Name: Recording Operation Log
Trigger event: promptSubmit
Action type: runCommand
Command: mkdir -p "<recording-dir>" && printf '[%s] %s\n' "$(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S')" "$KIRO_USER_MESSAGE" >> "<recording-dir>/recording-log.txt"
```

Once the hook is created, every user message during the recording session will be automatically logged with a Beijing timestamp — no manual action needed.

If the current environment does not support hooks, `promptSubmit`, or `$KIRO_USER_MESSAGE`, do not pretend the hook was created successfully. Explicitly tell the user "This environment cannot automatically log user messages" and ask them to manually provide the start/end times and a summary of key operations after recording ends.
