---
name: finish-session
description: Finalize and consolidate the current Antigravity session when the user explicitly asks to finish, wrap up, end, or hand off.
---

# Finish the session

Use this only after an explicit request to finish, end, wrap up, or hand off the current session.

1. Stop new work. Complete only final steps already authorized by the user.
2. Check `ai-memory finalize-session --help` and identify this session's recorded agent kind and memory session ID from trusted current-session metadata. Run `ai-memory finalize-session --agent <recorded-agent-kind> --session-id <verified-current-session-id> --json` in the current project. Require the explicit selector even when only one session appears open; choosing the latest does not establish that it is this session. If the correct agent kind or current recorded session cannot be identified, report the gap and ask before finalizing; never default to another harness's session. Verify that the returned `session_id` matches the selected session before consolidation.
3. If a session was finalized, call the `memory_consolidate` MCP tool, if exposed, with that `session_id` using its actual schema. Use the default single-page mode. If it is unavailable, report that consolidation is incomplete.
4. Report what finished, any open work, and whether finalization and consolidation succeeded. If either command fails, say which one failed and why. Do not claim the session was fully closed when it was not.

An ended turn or ACP connection does not prove that the memory session was finalized. Report success only from the finalization and consolidation results.
