---
name: handoff
description: Write a handoff document so the next task starts in a fresh chat with clean context. Use at a meaningful work boundary (such as approved planning to implementation), when switching chats, branches, or checkouts, or when the user asks; prefer in-thread compaction for mid-task context pressure.
argument-hint: "[what the next session will be used for]"
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Prefer in-thread compaction when a task is still underway rather than treating a token count such as 150K as an automatic handoff threshold; a fresh thread fits a clean work boundary (such as moving from approved planning to implementation). If the user explicitly asks for a handoff while a task is unfinished, mention compaction as an option in one line and write the handoff anyway—never block an explicit request. Record the unfinished work, its last known state, and the next step.

Save the handoff to the OS temporary directory unless the user names another place. Tell the user the path and ask them to open a new chat from it. A new chat starts with only the handoff. Continuing in this chat keeps the whole history.

Include:

- links to the artifacts the next task depends on, such as plans, research notes, issues and commits. Link by path or URL; the handoff points to them and copies nothing.
- stable repository and checkout IDs, revisions and dirty-file fingerprints. A machine path is never a repository identity.
- decisions, open questions and what the next task is.
- a "Suggested skills" section naming the skills the next agent should invoke, in Claude Code's `/skill-name` form.
- a closing resume step: reconcile HEAD, dirty files, instructions and missing repositories, and mark stale evidence before continuing.

Redact secrets and personal data, such as API keys, passwords and personally identifiable information.

If the user passed arguments, they describe what the next session will focus on. Tailor the handoff to that.

## Output

Output a meaningful to the current subject resume message, like "Read and implement", "Resume", etc. + the handoff full path inside a plaintext codeblock.