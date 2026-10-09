# OpenCode worker lifecycle

Use the running client's tool schemas. Slim's tool names vary by release and
host. On v1, delegation uses `task`, `subagent_type`, and `task_id`; on v2 it
uses `subagent`, `agent`, and `sessionID`. Never copy Codex's spawn or history
arguments into OpenCode. Discover the exposed schema before calling a tool.

1. Dispatch independent assignments in the background when supported. Record
   task/session IDs, objective, role, ownership, dependencies, and state in the
   existing task tracking. Respect runtime concurrency limits.
2. Continue useful work outside active writers' ownership. Dependent work waits
   for terminal results. Background launch acknowledgement is not completion.
3. Prefer completion events. Use exposed status/result tools for missing or
   ambiguous state; avoid unchanged polls. An accepted steering message does
   not prove that the worker consumed it. Reconcile it against the final result.
4. Review returned evidence and the actual changes. A runtime's reconciled
   status is not proof that the root used the result or met acceptance criteria.
5. Reuse a retained session for context-dependent follow-up through the exposed
   continuation tool. Give it a new bounded brief. Start fresh for a different
   role or independent review. Check existing assignments before duplicating work.
6. After cancellation or failure, inspect partial changes and running state.
   Cancellation does not undo edits. Settle ownership before replacement work.
   After a restart, verify retained state instead of treating history as live status.

Current upstream names include `task_status`, `task_result`, `task_message`,
`task_cancel`, and `task_revive`. Installed versions may expose `task_reply`
or a different continuation mechanism. Tool availability and accepted arguments
take precedence over these examples. If background support is unavailable,
use the client's supported sequential delegation and state the limitation.

Model and effort settings come from the active plugin preset and runtime.
Never infer that a fallback actually ran from the configured priority list.
Report runtime identity only when the host provides it. Keep automatic model
fallbacks explicit in config; request a choice when meeting the brief requires
an unconfigured model, provider, or increased spending authorization.

The installer disables designer, observer, and council for this workflow.
Route visual interpretation to a configured vision-capable active model. If
none can inspect the input, report the gap instead of interpreting unseen images.
Keep workers as leaves even when the host technically permits nested delegation.

Reference: [upstream background orchestration](https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/background-orchestration.md)
and [configuration](https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/configuration.md).
Checked 2026-10-09 against published Slim 3.0.3 and local 2.2.25.
