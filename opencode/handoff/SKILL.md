---
name: handoff
description: Write a handoff between tasks for a fresh OpenCode session. Invoke explicitly when moving to a new session, checkout, or branch.
metadata:
  opencode/slash: "true"
  opencode/autoinvoke: "false"
---

# Handoff

Write a document that gives a fresh agent enough context to begin the next task.
Use the user's handoff request to identify that task; otherwise infer it from
the conversation and mark any open question. Run only on an explicit request.

Run between tasks. If the current task is unfinished, identify the outstanding
work and yield without claiming completion. An explicit request to transfer
unfinished work overrides this restriction; label the unfinished state and
next action.

## Write the document

Save a uniquely named Markdown file to the runtime OS temporary directory,
using `tempfile.gettempdir()` or an equivalent. Use another location only when
the user names it. A remote runtime's temporary directory belongs to that
runtime, not necessarily to the user's desktop. State where the file lives.

Include:

- The next task, completed work, decisions, open questions, constraints, and
  authorization relevant to the next task.
- Paths or URLs to plans, research, issues, commits, and other artifacts.
  Reference their content rather than copying it.
- Stable repository identity and checkout state for each relevant repository.
  Prefer a credential-free remote URL and revision or root-commit identity.
  Record the branch or detached state, full HEAD revision, and checkout path.
  A path locates a checkout; it does not identify a repository.
- The dirty-file inventory, including staged, unstaged, and untracked state.
  Fingerprint changed files and, when useful, staged and unstaged patches
  without reproducing sensitive content. Label missing repositories,
  unavailable state, and unchecked evidence.
- A `Suggested skills` section naming installed OpenCode skills for the next
  task and why. Resolve paths from the current runtime's catalog. Use the
  native `skill` tool by exact name; mention `/name` only when the runtime
  exposes that skill as a command.
- A closing resume step that reconciles repository identities, HEAD,
  dirty-file fingerprints, applicable instructions, and missing repositories.
  Mark evidence stale when its revision or environment differs.

Inspect repository state with read-only commands. Writing a handoff does not
authorize committing, stashing, switching branches, or creating a session.
Redact secrets and unnecessary personal data, including credentials in remote
URLs. Keep only context needed by the next task. Read the saved file back and
check that every required item is present or explicitly marked unavailable.

## Return the resume instruction

Tell the user the full path and how to open a fresh session in the target
checkout. In the OpenCode TUI, use `/new`, then paste the resume instruction.
A saved file or `/compact` does not create a fresh session. Continuing,
forking, or importing a session carries prior history; use a new session for
this workflow. Claim a session was created only when the user requested it
and a supported runtime tool confirms it.

Return the resume instruction and full path in a plaintext code block:

```text
Read /absolute/path/to/handoff.md and resume the next task after reconciling repository state.
```

If the new runtime cannot read that path, tell the user to transfer or attach
the file there. OpenCode CLI supports attaching it with
`opencode run --file /absolute/path/to/handoff.md "Resume the next task after reconciling repository state."`
from the target checkout, without session continuation flags. Execute this
only if the user explicitly requested starting the new session.
