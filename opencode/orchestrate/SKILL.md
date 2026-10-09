---
name: orchestrate
description: Delegate substantial, bounded work and research through oh-my-opencode-slim. Use when specialist execution, evidence gathering, or independent review justifies briefing and reconciling workers.
---

# Orchestrate

Own framing, architecture, task decomposition, interpretation, and integration.
Resolve routine implementation details. Leave consequential choices to the user
unless they delegated the decision. Workers execute a chosen plan or gather
specified evidence. Every specialist is a leaf; route requests for additional
research through the root.

## Place the work

Before execution, identify the deliverable, required context, acceptance
criteria, dependencies, and useful work that can proceed alongside it.
Run [scripts/delegation_gate.py](scripts/delegation_gate.py) on the relevant
text inputs, including required context once:

```bash
python3 <skill-dir>/scripts/delegation_gate.py --scope "bounded task" path/to/input ...
```

The defaults match the Codex workflow: below 25,000 estimated tokens, work
locally; from 25,000 through 150,000, delegate; above 150,000, split and rerun
each slice. Invalid scope exits 2; oversized scope exits 3. Neither permits
execution. An indivisible oversized scope requires the user's mechanism choice.
These thresholds are policy defaults. Bytes divided by four approximate input
size, not actual tokens, output size, difficulty, or remaining context capacity.
Use narrower scopes when the selected model or session needs them.

Use `--planned-bytes N --reason "basis"` for new work or external evidence
without local inputs. Avoid unrelated files and binary sizes. Explicit user
delegation and required independent assessment may bypass the floor using
`--exception user-request` or `--exception independent-verification`, with a
reason citing the instruction. Exceptions never bypass the ceiling. Override
`--floor-tokens` and `--ceiling-tokens` only for an explicit project/user policy.
Record the JSON result in the brief or existing task state. Rerun after scope changes.

## Choose a specialist

| Role | Assignment |
| --- | --- |
| explorer | Read-only repository evidence, paths, excerpts, and coverage gaps. |
| librarian | Read-only external research from primary sources, with versioned evidence. |
| fixer | Bounded implementation of the root's chosen approach and assigned checks. |
| oracle | Consequential judgment or fresh independent verification. |

Before briefing workers, read [the role contracts](references/roles.md).
Give each worker its applicable contract. Oracle advice and independent
verification are different assignments, even when both use `oracle`.

Models, effort variants, tools, and permissions belong in the plugin's active
preset. Select the configured role suited to the assignment's difficulty.
If its model, tools, or capacity cannot meet the brief, narrow the task or
report the limitation and request the needed configuration choice. Announce
the task, role, configured model/variant when known, and objective before
dispatch. Distinguish configured selection from runtime-reported identity.

Call Oracle when independent judgment is warranted by the stakes or unresolved
trade-offs: major architecture, security, data integrity, reliability, difficult
debugging, or consequential user behavior. Routine mechanical changes do not
require Oracle. For required independent assessment, cite this requirement in
the gate exception. Oracle recommends with evidence; the root evaluates it.
When the user has delegated the decision, proceed within that scope. Otherwise
present the recommendation, rationale, and alternatives through the available
question tool and wait for the decision before dependent work.

## Brief and dispatch

Every brief includes:

- One objective, relevant context, and the exact evidence question or chosen approach.
- Read/write scope, file ownership, permitted side effects, and explicit exclusions.
- Applicable user/repository constraints, skill references, and settled decisions.
- Acceptance criteria, assigned checks, and expected evidence and results format.
- Role contract, leaf spawning restriction, and the sizing result.

Use a new worker session with a self-contained brief by default. Reuse a session
only when its context directly benefits the next assignment and still fits the
role. Independent verification always uses a fresh session without the author's
discussion history. Supply the plan, relevant sources, diff/revision, checks,
and review criteria instead.

Assign every file to one active writer, including the root. A worker needing
another file requests a handoff. Transfer ownership only after the previous
writer has stopped. Parallelize independent assignments within runtime limits;
wait for prerequisites before dispatching dependent work.

For tool discovery, completion events, steering, reuse, cancellation, and
partial-state recovery, follow [the OpenCode lifecycle](references/lifecycle.md).
For large, risky, phased work, read [deepwork](../deepwork/SKILL.md) for
persistent state and bounded phase reviews. Use
[verification-planning](../verification-planning/SKILL.md) when the evidence
path itself needs design. Keep their state and review budgets authoritative.

## Accept evidence

Open the sources supporting research claims you will rely on. Resolve material
contradictions or label them unresolved. Worker summaries and search snippets
alone do not establish claims. For reusable research, follow
[research preservation](references/research.md); routine lookups stay in the conversation.

Fixer runs its assigned checks. Use a fresh Oracle verification assignment when
the user or applicable workflow requires independence; otherwise its cost must
be justified. Inspect the diff and returned evidence against the brief.
Reuse valid checks. Rerun decisive checks when changes, failures, stale state,
or missing evidence justify them. A phase gate does not replace final review
of the completed scope.

Return one integrated result with changes, validation, skipped checks, and
remaining limitations. Workers finishing is not proof the user's goal is met.
Delegation never expands authorization to install, spend, contact others,
commit, push, or deploy.
