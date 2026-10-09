---
name: handoff
description: Write a handoff between completed tasks so the next task can begin in a fresh Codex chat. Use when the user asks to move to a new chat, checkout, or branch.
---

# Handoff

Write a document that gives a fresh agent enough context to begin the next task. Arguments to `$handoff` describe that task; otherwise infer it from the conversation and mark any open question.

Run between tasks. If the current task is unfinished, identify the outstanding work and yield without claiming completion. An explicit request to transfer unfinished work overrides this restriction; label the unfinished state and next action.

## Write the document

Save a uniquely named Markdown file to the runtime OS temporary directory, using `tempfile.gettempdir()` or an equivalent. Use another location only when the user names it. A remote runtime's temporary directory belongs to that runtime, not necessarily to the user's desktop. State where the file lives.

Include:

- The next task, completed work, decisions, open questions, constraints, and authorization relevant to the next task.
- Paths or URLs to plans, research, issues, commits, and other artifacts. Reference their content rather than copying it.
- Stable repository identity and checkout state for each relevant repository. Prefer a credential-free remote URL and revision or root-commit identity. Record the branch or detached state, full HEAD revision, and checkout path. A path locates a checkout; it does not identify a repository.
- The dirty-file inventory, including staged, unstaged, and untracked state. Fingerprint changed files and, when useful, staged and unstaged patches without reproducing sensitive content. Label missing repositories, unavailable state, and unchecked evidence.
- A `Suggested skills` section naming installed skills for the next task and why. Use Codex's `$skill-name` invocation form and resolve paths from the current catalog.
- A closing resume step that reconciles repository identities, HEAD, dirty-file fingerprints, applicable instructions, and missing repositories. Mark evidence stale when its revision or environment differs.

Inspect repository state with read-only commands. Writing a handoff does not authorize committing, stashing, switching branches, or starting a new thread. Redact secrets and unnecessary personal data, including credentials in remote URLs. Keep only context needed by the next task.

## Return the resume instruction

Tell the user the path and that a fresh chat must be opened from it. A saved file does not clear this chat's history. Claim a new chat exists only if the user requested it and a supported thread tool confirms it.

Return the resume instruction and full path in a plaintext code block:

```text
Read /absolute/path/to/handoff.md and resume the next task after reconciling repository state.
```
