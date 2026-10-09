---
name: finish-session
description: Finalize and consolidate the current Codex session when the user explicitly asks to finish, wrap up, end, or hand off.
---

# Finish the session

Use this only after an explicit request to finish, end, wrap up, or hand off the current session.

1. Stop new work. Complete only final steps already authorized by the user.
2. Run `ai-memory finalize-session --agent codex --json` in the current project and read its `session_id`.
3. If a session was finalized, call the `memory_consolidate` MCP tool with that `session_id`. Use the default single-page mode.
4. Report what finished, any open work, and whether finalization and consolidation succeeded. If either command fails, say which one failed and why. Do not claim the session was fully closed when it was not.

Codex's `Stop` hook ends a turn, not a session. Do not treat it as a replacement for `finalize-session`.
