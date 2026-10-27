---
name: finish-session
description: Finalize and consolidate the current Claude Code session when the user explicitly asks to finish, wrap up, end, or hand off.
---

# Finish the session

Use this only after an explicit request to finish, end, wrap up, or hand off the current session.

1. Stop new work. Complete only final steps already authorized by the user.
2. Check `ai-memory finalize-session --help` and identify the current recorded Claude Code memory session ID from trusted current-session metadata. Run `ai-memory finalize-session --agent claude-code --session-id <verified-current-session-id> --json` in the current project. Require the explicit selector even when only one session appears open; choosing the latest does not establish that it is this session. If the current recorded session cannot be identified, report the gap and ask before finalizing. Verify that the returned `session_id` matches the selected session before consolidation.
3. If a session was finalized, call the exposed `memory_consolidate` MCP tool with that `session_id`. Use the default single-page mode. If the tool is unavailable, report consolidation as incomplete.
4. Report what finished, any open work, and whether finalization and consolidation succeeded. If either command fails, say which one failed and why. Do not claim the session was fully closed when it was not.

Claude Code's `Stop` hook ends a turn, not a session. Do not treat it as a replacement for `finalize-session`.
