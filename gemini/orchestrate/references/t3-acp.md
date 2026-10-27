# T3 Code ACP delegation

Use this reference before dispatching a worker from Antigravity through T3 Code. Read the role mapping and bounded sizing gate in [../SKILL.md](../SKILL.md) first.

## Discover capabilities

Find the exposed `orchestrator_capabilities`, `delegate_task`, `task_status`, and `task_cancel` tools. Harnesses may normalize names with an MCP prefix such as `mcp__t3_code__`. Call `orchestrator_capabilities({})` and inspect the live provider instances, model IDs, option descriptors, child-task capability, and constraints. Confirm the selected harness and model, then confirm each requested option and value. Use `target.options` to set them; unsupported settings require a decision, not a silent downgrade.

Antigravity may expose T3 as lazy MCP tools through `call_mcp_tool`. When that wrapper is available, select `ServerName: "t3-code"` and `ToolName: "orchestrator_capabilities"`, passing `{}` through the wrapper's actual argument field. Use the same server and the corresponding tool name for `delegate_task`, `task_status`, and `task_cancel`, with their argument objects below. Read the exposed schemas when needed. This native lazy route worked in the ACP runtime test while both terminal-bridge variables were unset.

If a catalog scan misses T3 tools, try the exposed lazy wrapper when available, or make one bounded direct attempt with the known `mcp__t3_code__orchestrator_capabilities` name. If native MCP access remains unavailable and `T3_ACP_MCP_NODE` is present, use the supported terminal bridge:

```bash
ELECTRON_RUN_AS_NODE=1 "$T3_ACP_MCP_NODE" ${T3_ACP_MCP_ENTRYPOINT:+"$T3_ACP_MCP_ENTRYPOINT"} acp-mcp-call orchestrator_capabilities '{}'
```

`T3_ACP_MCP_ENTRYPOINT` is optional and unset for standalone executable builds. Do not change MCP settings or install a server to make delegation work. If no supported transport works, report the missing capability and leave dependent work pending.

## Dispatch

A Builder dispatch has this argument shape. Replace the example ID and brief with a stable request ID and the complete task packet. Use the persona's exact selection from the skill for other roles.

```json
{
  "task": "Complete bounded task packet, persona, ownership, constraints, proofs, and required evidence.",
  "target": {
    "providerInstanceId": "claudeAgent",
    "model": "claude-sonnet-5-5",
    "options": {"effort": "high"}
  },
  "role": "implementation",
  "mode": "async",
  "clientRequestId": "unique-task-and-round-id"
}
```

`role` describes task purpose, not persona or model selection. Use `research` for a Scout, `review` for a Verifier, and `design` or `general` for an Oracle as appropriate. The required task packet includes the persona behavior from the skill. Omitted isolation shares the parent's checkout. Use `isolation: "worktree"` only when a separate checkout is needed and authorized; it starts from the parent local commit, runs project setup, and omits uncommitted edits. Choose the workspace in the delegation call, never by asking a worker to create its own worktree.

The same argument object works through the bridge. Pass one safely quoted JSON argument after the tool name:

```bash
ELECTRON_RUN_AS_NODE=1 "$T3_ACP_MCP_NODE" ${T3_ACP_MCP_ENTRYPOINT:+"$T3_ACP_MCP_ENTRYPOINT"} acp-mcp-call delegate_task '<single safely shell-quoted JSON argument>'
```

For generated arguments, use `shlex.quote(json.dumps(payload))` or equivalent shell quoting. JSON serialization alone is not shell quoting; backticks, `$()` and quotes in a brief must remain literal. This bridge calls T3 MCP tools. It does not launch an external model CLI directly.

Check the returned `providerInstanceId`, `model`, and `options` against the requested selection, normalizing option arrays by their `id` and `value`. A mismatch is a failed configuration check, not a usable substitute. Cancel a mismatched live task, retain its task ID and partial-state evidence, and resolve the mismatch before continuing.

## Track tasks and reviews

Retain each `taskId`, stable `clientRequestId`, requested and returned identity/options, assignment scope, status, and final evidence. Direct MCP, its lazy wrapper, and the terminal bridge pass this argument object:

```json
{"taskId":"returned-task-id"}
```

Pass this object to `task_status` or `task_cancel` through the available transport. A `mode: "wait"` timeout ends the parent's wait, not the child; do not create a duplicate task. Prefer async work and completion notifications. Check status only when useful and bound retries.

For every review round or follow-on assignment, call `delegate_task` again with a fresh round ID and the original brief, previous findings, responses, and unresolved objections. A fresh independent Verifier gets no author conversation. Never use `t3_thread_send` on `childThreadId` to start another round, or `create_threads` / `t3_thread_launch` for delegated work. Those create or address top-level conversations and are outside this workflow.

Children remain leaves except an Oracle explicitly permitted to dispatch read-only Scouts. A pending question or approval remains with its existing decision holder. Report it through the supported pending-request tools or ask the user; delegation does not confer approval authority.
