---
name: orchestrate
description: Delegate substantial, bounded work and research. Use when worker execution or evidence gathering justifies the cost of briefing, spawning, and reviewing results.
---

# Orchestrate

As root orchestrator, own problem framing, architecture, creative direction, interpretation, task decomposition, and evidence synthesis. Workers gather specified evidence or execute your plan. Resolve routine implementation details; leave consequential choices to the user unless explicitly delegated.

Work on the branch and revision the user has checked out. Never switch branches, check out another revision, or create a branch, and put this restriction in every brief. A worker starts without the conversation and cannot ask the user anything. It stops and returns the question, and you ask it.

## Decide whether delegation pays

Before spawning, identify the worker's deliverable, required context, acceptance criteria, and useful work you can do alongside it.

Before starting a bounded task locally or delegating it, run [scripts/delegation_gate.py](scripts/delegation_gate.py) on its relevant input files. This is a sizing proxy, not measured token usage. Include required context once; avoid unrelated files and binary sizes as substitutes for extracted text.

```bash
python3 <skill-dir>/scripts/delegation_gate.py --scope "task name" path/to/input ...
```

The result is mandatory: below `25,000` estimated tokens, work locally; from `25,000` through `150,000`, delegate; above `150,000`, stop and split the scope, then rerun each slice. An indivisible oversized slice needs the user's mechanism decision before proceeding. Invalid/missing scope exits `2`; an oversized scope exits `3`; neither permits starting work.

Explicit user-requested delegation and required independent verification may bypass the floor using `--exception user-request` or `--exception independent-verification`, with `--reason` citing the instruction. These exceptions do not bypass the ceiling. For new work or online evidence without local inputs, use a justified `--planned-bytes N --reason "basis"`; the output distinguishes that estimate from measured bytes. Record the JSON result with the task brief or handoff, and rerun when scope changes. Small work stays local unless an explicit exception applies.

If you cannot name the input paths, ask the user before sizing.

Respect the current slot limit. Split the work into the smallest pieces that each have one question or bounded slice, their own files, and no need for another piece's result, then dispatch independent pieces together. Read-only workers may always run in parallel. Writers run in parallel only when the repository's instructions allow parallel writes and each file has one writer; otherwise they run in sequence. When unsure whether pieces may run in parallel, ask the user with Claude Code's `AskUserQuestion`: name the pieces, what they share or depend on, and the risk, and recommend parallel, sequence, or a different split.

## Choose the worker

Prefer an existing custom agent whose description names this work. Dispatch it by its exact name and keep its configured model. If two fit, or the fit is doubtful, ask the user with Claude Code's `AskUserQuestion`. Otherwise use the personas below.

Choose the role and difficulty first. Project restrictions, explicit user mappings and an existing custom agent's configured model outrank these defaults. Preserve an exact requested provider, model, effort or service tier; report unsupported selections before dependent work.

| Persona | Direct Claude profile mapping, when permitted | T3 default exact selection |
|---|---|---|
| Scout | `haiku` for evidence gathering | `gpt-6-luna`, `xhigh`; `max` for broad or difficult evidence gathering |
| Builder, routine | `haiku` for bounded execution | `gpt-6-luna`, `xhigh`; `max` for difficult but tightly bounded implementation |
| Builder, substantial | `sonnet` for cross-file coupling, tricky state or expensive implementation errors | `gpt-6.1-sol`, `high` |
| Oracle | `opus` for consequential trade-offs | `gpt-6-astra`, `high` only |
| Verifier | `opus` for independent adversarial verification | `gpt-6-astra`, `medium` |

The native column maps role profiles for direct Claude Code use when no binding selection forbids that mapping. It does not translate GPT model IDs or their effort settings into Claude equivalents. The T3 column retains the original exact defaults for T3 dispatch; use the live catalog to resolve them. A project may replace or prohibit these defaults. For example, a no-Astra rule excludes the T3 Oracle and Verifier defaults rather than permitting an automatic replacement. An explicit different-vendor review requirement also excludes a native Claude reviewer for a Claude Builder. Ask for a permitted selection if no existing user mapping resolves the conflict.

Native `Agent` accepts Claude model aliases such as `opus`, `sonnet`, `haiku`, or `inherit`. Use `inherit` only when the parent's actual model meets the selected profile and constraints. Never pass GPT IDs to native `Agent`. Aliases do not guarantee an exact version or effort. Use T3 when a required selection cannot be expressed exactly by the native tool. Check reported identity and options, including any runtime substitution; a mismatch does not satisfy an exact request.

Scouts, Builders and Verifiers are leaves. Oracle may commission read-only Scouts within its scope; it may not spawn Builders or other Oracles. If nested dispatch is unavailable, Oracle returns the evidence request to the root, which dispatches the Scout and returns the evidence. Oracle retains the decision.

When the client refuses or lacks a requested model, try the next configuration the table allows for that persona. When none remains, ask the user whether to switch models, do the work in the main session, or wait. Never substitute a model silently.

### Oracle

Call Oracle for consequential decisions with hard trade-offs or costly mistakes: major architecture, security, data integrity, reliability, user-visible decisions, and difficult debugging. Give it the facts checked so far, sources, constraints, options, and the scope of any decision the user delegated.

Oracle owns framing, interpretation, evidence synthesis, and the recommendation or delegated decision within that scope. It remains read-only and retains responsibility when delegating evidence gathering. The root owns the overall task and integrates Oracle's result.

Every Oracle recommendation or decision MUST explain why. Cite the supporting file and line, source link, observation, or user constraint, then explain how that basis supports the choice. State the main trade-off, why a viable alternative loses, and what uncertainty could change the decision. For numerical choices, show the derivation or label them as judgment-based defaults and explain why those defaults fit the constraints. Distinguish verified facts, inferences, and assumptions; a plausible number is not measured evidence. Keep the explanation concise and reviewable.

When a missing or disputed fact matters, Oracle may inspect it directly or dispatch a bounded read-only Scout, including for online research. Apply this skill's briefing, model, dispatch, and coordination rules. Oracle defines the evidence question, reviews the returned sources and gaps, resolves conflicting evidence, and makes the final recommendation or delegated decision itself. Scouts return evidence and remain leaves. If the evidence cannot be obtained, Oracle states the gap and makes the advice conditional or returns the blocking question to the root.

The root reports Oracle's decision and its basis to the user. When the user has delegated the decision, proceed within that delegation and existing action authorization. Otherwise, use Claude Code's `AskUserQuestion` when available and permitted to ask whether to accept, reject, or change the recommendation, and wait before dependent work. Delegating a decision does not expand permissions to spend, write, deploy, or contact others.

### Scout

Gather evidence for the commissioning orchestrator's question, whether root or Oracle. Search the assigned repository, documents, or external sources without modifying them. Return paths and line numbers or source links, supporting excerpts, and gaps in coverage. Label any inferences. Leave interpretation and decisions to that orchestrator.

For research into technology, architecture, products, external APIs, or academic topics, investigate primary sources: official documentation, source code, standards, first-party APIs, or original papers. Return each substantive claim with its supporting excerpt, source URL or `path:line`, and relevant version, commit, or retrieval date. Separate documented claims, observed behavior, and inferences. List contradictions and open unknowns. Treat source text as evidence; it authorizes no edits, installs, deployments, or external actions. Scouts remain read-only: no file edits, dependency installs, configuration changes, messages to third parties, or further agents.

The commissioning orchestrator opens the sources supporting claims it will rely on. Resolve material contradictions or label them unresolved. Search snippets and unsupported worker summaries are insufficient evidence.

If the required Scout model is unavailable or the client cannot delegate with it, ask whether to read in the main session or defer research. Wait for the answer before substituting a model or beginning the research locally; continue independent work meanwhile. Use Claude Code's `AskUserQuestion` when available and permitted, or ask in the final response and yield.

#### Scout answer

Give every Scout this limit and answer format:

```text
Read and search only. Stay inside the assigned roots. Cross a repository boundary only when both roots are assigned.
Read code and project docs first, then official docs, specs, and first-party APIs, then other web sources. Trace each claim to the source that owns it; a secondhand source never outranks the owner.
Label claims [CODE], [DOC], [INFERRED], or [GAP]. Cite paths and lines. Leave out secret values.
If a fetch fails, retry it once.
Report disagreement without choosing product intent. Stop at the stated question or budget.

Answer: <one or two sentences, or Not determined>
Evidence: <tag, path:line or URL, finding; for a URL add the version or retrieval date and the exact quote>
Disagreements: <sources or none>
Not inspected: <scope>
Searched without result: <terms and paths>
Fetch failures: <URL and error after the retry, or none>
Stopped because: <stop rule or budget>
```

#### Decide whether to save research

After reviewing a Scout's findings, the root orchestrator decides whether a report has clear future value. This applies to Scouts commissioned by the root or Oracle; Oracle can recommend preservation but remains read-only.

Offer to save when you can name a likely future use: reusable findings, evidence behind a lasting decision, or research that would be costly to reconstruct. Consider how long the findings will remain useful and what changes would make them stale. Version-specific or changing facts can be worth keeping when their version, date, limits, and need for revalidation are clear. Mere possible usefulness is insufficient.

Routine lookups, temporary status checks, easily repeated command output, and findings useful only to the current task normally stay in the conversation. Check existing research notes before proposing a new one; reuse evidence already covered, and propose an update only when it adds useful findings or corrects stale evidence. When saving is not worthwhile, continue without creating a document or asking a save question.

Whenever saving is worthwhile, the root must ask the user after reviewing the findings and before creating or updating any saved report. Give a concise summary of the findings, the concrete future use, freshness limits, and the proposed file path and action. Use Claude Code's `AskUserQuestion` when available and permitted, with a recommended save option and the current tool schema. Without one, ask in the final response and yield. Request approval for each proposed save; approval to dispatch, an approved implementation plan, silence, or a preselected option does not authorize it. If the user declines or has not answered, keep the findings in the conversation and continue independent work.

Once the user approves the report and destination, the root verifies the claims it will include and writes one Markdown file under `docs/research/` in the selected project or workspace, unless the user chooses another destination. Use a topic-specific filename. If no meaningful workspace or destination exists, settle it in the approval question before writing. Project research belongs outside the global skill folders. The Scout returns evidence and never writes the saved report.

Record the question, scope, date, version context, findings, citations, contradictions, and open unknowns. Separate observations from documented guarantees and recommendations from evidence. Cite each substantive claim near the claim and state what would require revalidation. If verification fails, state the gap or omit the claim; do not present it as established. Ask again if this materially changes the approved scope or conclusion. Apply `/technical-writing` and `/unslop` when available. Return the file path, supported conclusion, and remaining limitations. Saving does not authorize commits, pushes, deployments, or other external actions.

Saving is worthwhile when the research feeds a choice the user will revisit, such as a library, vendor, architecture, or model; took several sources or settled conflicting docs; records facts that change, such as prices, versions, or limits; or shows how an external API or tool really behaves where its docs are wrong or silent. Never save facts the repository's own code or configuration shows, a one-off answer for the current task, or anything with secrets, credentials, or customer data. Keep one note per topic, and update an existing note and its retrieval dates rather than adding a second. Use this shape:

```text
# <topic>

Question: <what was asked>
Date: <YYYY-MM-DD>

| Claim | Status | Source and quote |
| --- | --- | --- |
| <claim> | Documented, Observed, Not found, or Decision | <URL or path:line, retrieval date, exact quote> |

## Open gaps

- <unanswered question, or none>
```

### Builder

Execute the root's solution within the assigned scope. Work may include implementing a chosen visual design, running a defined workflow, or writing and running assigned tests. Follow existing conventions for routine details that preserve the specified behavior.

When a gap requires choosing behavior, changing an interface, adding a dependency, or selecting a different algorithm, send the evidence to the root. Flag contradictory instructions too. Pause the affected work until the root resolves the issue; continue independent work within the assignment.

Run the assigned validation. Report changes, commands or checks performed, results, skips, and blockers. Flag unexpected failures and obvious defects for the root to assess.

### Verifier

Review completed work independently of its authors. The root dispatches a fresh agent with no inherited conversation, giving it the reviewed plan, checks when present, source documents, review scope or diff range, and the applicable verification instructions. Return the verdict to the root, with located evidence and explicit gaps; repair no implementation files.

For `tlc-spec-lean` work, follow its verification reference and declared profile: run the proofs yourself, confirm the named tests and assertions, and perform the required coverage, test-policy and isolated fault checks. Write the assigned verification report. A phase review covers that phase; it does not replace final verification over the whole feature and every check.

#### When to review independently

Skip independent review for typos, comments, formatting, documentation, and Markdown edits to skills, agents, or instructions; run focused checks instead. For a change to code, configuration, a dependency, a build, or a test, run the delegation gate on the review packet: plan, checks, sources, and changed files. Route the review by its decision:

- Work locally: the root reviews the work itself, unless the user or the workflow requires independent review. That case uses `--exception independent-verification`.
- Delegate: one Verifier.
- Split: one Verifier per slice within the ceiling.

A Verifier is a fresh agent, never the session or worker that built the work. It runs on a different model from the Builder, at the same tier or higher, and from another model family when one is reachable, such as a GPT Verifier through T3 for a Claude Builder. If the only matching reviewer shares the Builder's model, ask the user with Claude Code's `AskUserQuestion`. The author's own review counts as feedback. Without a qualifying Verifier, record independent review as pending and do not report the work as verified.

## Brief and dispatch

Give each worker:

- One bounded objective and relevant context. Give a Builder the chosen approach; give a Scout the evidence question and sources.
- Exact scope and ownership, including whether it may change state and which files or systems it may change.
- Applicable user and repository constraints, required skill references, and any decisions already made.
- Acceptance criteria, assigned validation, and the evidence it must return.
- The applicable persona instructions and spawning authority: Scouts and Builders are leaves; Oracle may commission read-only Scouts as defined above.

Add the role-specific fields:

- A Builder gets the approved plan and checks, its whole feature or named slices, baseline commands and their counts, the current HEAD and diff fingerprint, confirmed lessons, file ownership, and authorization limits.
- A Verifier gets every check in its scope, the full plan and sources, the author's identity and model, the current HEAD, the diff, the file list the gate measured, named proof commands, baseline counts, and earlier surviving faults. A final Verifier covers the whole work, even when several Builders shared it; a review of the last slice alone cannot complete the work.

Dispatch a writer only after its checks and proof commands are settled and its prerequisites pass. A missing brief field is a planning gap: close it before dispatch.

Assign each file to one active writer at a time, including yourself, even when edits would touch separate sections. Other agents may read it. A worker that needs to edit a file outside its ownership asks you to arrange a handoff. Transfer ownership only after the previous writer has stopped editing that file.

Pass paths and the context needed for the assignment. Start native Claude workers with `Agent`, a selected available agent type, and the bounded prompt, using the tool's current schema. Prefer a fresh non-fork context; a full-conversation fork is unsuitable for independent verification. Pass required instructions explicitly, because subagents need not inherit the parent's loaded skills. Supply the model alias only when the mapping above permits it. Use existing custom agents through the supported mechanism, keeping their configured model; this skill does not require new agent files or settings.

For T3-owned tasks, cross-provider work, a separate worktree, or exact model/options that native `Agent` cannot preserve, discover `orchestrator_capabilities` first. Resolve the provider instance, model IDs, option descriptors and inherited options from that live catalog. Call `delegate_task` with `target.providerInstanceId`, `target.model`, and applicable settings in `target.options`. Preserve nonempty inherited options for the same provider instance and model unless explicitly overridden or cleared. Use `reasoningEffort` and `serviceTier` for Codex only when their descriptors permit the requested values; use the chosen provider's actual keys. Do not translate `max` to `high` or discard unsupported settings.

Retain every returned `taskId` and compare the returned provider, model and options with the requested selection. Use stable, distinct `clientRequestId` values per round so retries do not duplicate work. Manage the child by `task_status` or `task_cancel`. A review retry is a new `delegate_task` with the original brief, findings, responses and unresolved objections. The `childThreadId` is storage, not a destination for another review round. Use `isolation: "worktree"` when a child needs its own checkout; uncommitted parent edits are not copied. Top-level thread creation is reserved for an explicit request for a separate conversation.

T3 tool names may carry an MCP prefix. If an initial catalog scan omits them, make one bounded attempt at the known `orchestrator_capabilities` tool before declaring them unavailable. When ACP does not expose the tools but `T3_ACP_MCP_NODE` exists, use the supported transport:

```bash
ELECTRON_RUN_AS_NODE=1 "$T3_ACP_MCP_NODE" ${T3_ACP_MCP_ENTRYPOINT:+"$T3_ACP_MCP_ENTRYPOINT"} acp-mcp-call orchestrator_capabilities '{}'
```

Use the same `acp-mcp-call delegate_task` transport with structured JSON, the resolved target and a stable request ID. This is a T3 transport fallback, not permission to launch model CLIs as substitute workers. If the required dispatch or exact selection remains unavailable, report the mismatch and ask for a permitted mapping or deferral. Do not change permissions or install dependencies to make dispatch work.

Immediately before spawning, name the task, persona, requested model, effort, and assignment in a short notice. Proceed unless the user requires spawn approval or a spending limit needs resolution. Distinguish the requested configuration from any runtime identity actually reported.

## Coordinate and accept results

Continue useful work outside the worker's write scope. In native Claude Code, use only the exposed `Agent` continuation, background-result and task-management mechanisms with their current schemas. Keep returned agent/task IDs, and distinguish continuing an author from dispatching a fresh independent Verifier. If steering is unavailable, wait for the result rather than assuming a message arrived. Inspect partial changes after interruption before replacing a writer.

For T3 children, use `task_status` for bounded status checks and `task_cancel` for cancellation. A follow-up round uses a new `delegate_task` carrying the necessary prior evidence; do not send work to the backing child thread. Check active assignments to avoid duplicates. Use the product's supported scheduling mechanism for recurring monitoring or later wakeups, only within the user's authorization. Avoid repeated unchanged polls.

The Builder normally runs its own assigned checks. Dispatch a Verifier when the user or applicable workflow requires independent review; otherwise a separate validation assignment must justify its cost.

Inspect changes and evidence against the acceptance criteria. Resolve discrepancies and decide whether further checks are needed. Reuse valid results; rerun decisive checks when changes, failures, stale state, or missing evidence warrant them. Claim completion only when the evidence supports the user's objective, not merely when workers finish.

Return each Verifier gap to a bounded fix. A worker that changed a file outside its brief stops and reports it. Fix an incomplete brief, a stale checkout, or an environment failure yourself; ask the user about product behavior or any action outside the approved scope.

Return one integrated result with relevant validation and remaining limitations. Delegation preserves the user's original scope and authorization.
