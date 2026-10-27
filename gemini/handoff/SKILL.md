---
name: handoff
description: Compact the current conversation into a handoff so the next task starts in a fresh chat with clean context. Use between tasks, when the user wants to clear context or move to a new chat, branch or checkout.
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

If this conversation still has an unfinished task, warn the user in one line and write the handoff anyway. Record the unfinished work, its last known state, and the next step.

Save the handoff to the OS temporary directory unless the user names another place. Tell the user the path and ask them to open a new chat from it. A new chat starts with only the handoff. Continuing in this chat keeps the whole history.

Include:

- links to the artifacts the next task depends on, such as plans, research notes, issues and commits. Link by path or URL; the handoff points to them and copies nothing.
- stable repository and checkout IDs, revisions and dirty-file fingerprints. A machine path is never a repository identity.
- decisions, open questions and what the next task is.
- a "Suggested skills" section naming the skills the next agent should invoke, in Antigravity's `/skill-name` form.
- a closing resume step: reconcile HEAD, dirty files, instructions and missing repositories, and mark stale evidence before continuing.

Redact secrets and personal data, such as API keys, passwords and personally identifiable information.

If the user passed arguments, they describe what the next session will focus on. Tailor the handoff to that.

## Output

Output a meaningful to the current subject resume message, like "Read and implement", "Resume", etc. + the handoff full path inside a plaintext codeblock.