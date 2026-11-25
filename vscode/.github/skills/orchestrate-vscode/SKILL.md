---
name: orchestrate-vscode
description: "Use before any subagent dispatch, alone or in parallel, AND for any research question, saved or not. Useful when substantial and meaningful work can split into independent pieces."
---

# Orchestrate in VS Code

The main session owns scope, user questions, repository bindings, review records, and the final report. Each subagent gets a bounded packet, reports, and stops. Product decisions stay with the user.

A subagent starts without the chat history and cannot ask the user anything. Follow-up work needs a new dispatch with a complete packet.

Work on the branch and revision the user has already checked out. Never switch branches, check out another revision, or create a branch, and put this restriction in every subagent packet. Repository and checkout IDs are identity labels, not Git instructions.

## When to delegate and split

Use judgment to decide when work stays in the main session vs. goes to a subagent. Actively split independent read-only research or codebase discovery across multiple small parallel `Explore` subagents when questions separate cleanly.

When a slice or review packet looks large, use [scripts/estimate_size.py](scripts/estimate_size.py) as an **advisory** sizing helper (`bytes / 4`, skipping `.git`) to check whether it approaches the ~150k estimated-token ceiling:

```text
python3 .github/skills/orchestrate-vscode/scripts/estimate_size.py <path>...
```

Keep each subagent's scope within ~150k estimated tokens; split oversized work into independent pieces or whole vertical slices (`feature-workflow` builds directly in the main session and keeps each feature within the ceiling for one fresh reviewer).

- Read-only subagents, including `Explore`, may always run in parallel.
- Writers run in parallel only when the always-on instructions allow parallel writes and each file has one active writer; otherwise they run in sequence.
- When unsure whether pieces may run in parallel, ask the user with the question tool: name the pieces, what they share or depend on, and the risk, and recommend parallel, sequence, or a different split.

## Pick the agent and model

List the agents the subagent tool offers, then take the first that fits:

1. A custom agent whose description names this work. Dispatch it by its exact name without overriding its model. If two fit, or the fit is doubtful, ask the user with the question tool.
2. `Explore`, for a read-only question.
3. A general subagent (no agent name): it inherits the main session's tools, so the packet states its limits (for a review, copy the limits from the `spec-verifier` agent file).

Pass a model when dispatching `Explore` or a general subagent:

| Role | Models, in order |
| --- | --- |
| Research and exploration, including `Explore` | `GPT-6 Luna (copilot)` only |
| Substantial code changes | `Claude Opus 5.5 (copilot)`, then `Claude Sonnet 5.5 (copilot)` |
| Review, verification, judging | `GPT-6.1 Sol (copilot)`, then `GPT-6 Sol (copilot)`. When a GPT model built the code, `Claude Opus 5.5 (copilot)` |
| Any other work | `GPT-6.1 Sol (copilot)`, then `GPT-6 Sol (copilot)` |

Opus 5.5 and both Sol models share the top tier; Sonnet 5.5 sits one tier below.

VS Code refuses a model above the main chat's cost tier and the subagent does not start. On a refusal, retry with the next model in the row; when none remains, ask the user. When `Explore`'s model or a custom agent's model is refused, ask right away: switch the main chat's model, read in the main session, or wait (for a custom agent, also offer a general subagent on the table's model). Never substitute silently.

## Independent review

Skip independent review for typos, comments, documentation, formatting, and Markdown edits to skills, agents, or instructions; run focused checks instead.

For changes to code, configuration, dependencies, builds, or tests, dispatch one fresh independent reviewer when the workflow (such as `feature-workflow`) or user requires it, or when the change warrants independent verification. For `feature-workflow`, follow its `references/review.md` and split oversized features at planning time rather than splitting `review.md` across colliding writers.

An independent reviewer is a fresh subagent, never the session or dispatch that built the work. Its model comes from another vendor family than the builder's, at the same tier or higher. If the matching custom reviewer runs on the builder's family, ask the user with the question tool. The author's own review counts as feedback; without a qualifying reviewer when independent review is required, record independent review as pending and leave the feature unverified.

## Prepare the packet

Unless the always-on instructions record `Repositories: single`, resolve selected repositories and their IDs through `workspace-analysis`. With `Repositories: single`, name the repository root instead of repository IDs and bindings.

- `Explore` gets one bounded question, selected roots, exclusions, a stop rule, and the evidence limits below.
- A builder gets the approved `plan.md` (or small-change `request.md`), its feature or named vertical slices, applicable `.specs/constraints/` records, repository IDs and local bindings, baseline commands and counts, current HEAD, the team standards doc named in Team additions, file ownership, and authorization limits.
- A reviewer gets `request.md` (verbatim), `plan.md` (when present), binding captures, the author's identity and model, repository IDs and local bindings, repo diff range(s) (`<base>..<head>`), recorded `**Gates:**`, applicable `.specs/constraints/` records, and the team standards doc—with no author summary or hints. A targeted re-check gets the prior round's open blocking findings and fix diff range instead. A final reviewer covers the whole feature, even when several builders worked on it.

Dispatch a writer only after its spec and acceptance criteria are approved and prerequisites pass.

## Explore answer and research

`Explore` owns its web fetches; a source it still cannot read stays a gap in its answer. Brief `Explore` with these limits:

- Read and search only inside assigned roots; cross a repository boundary only when both roots are assigned.
- Prefer primary sources: code and project docs first, then official docs, specs, and first-party APIs, then other web sources.
- Cite `repo_id:path#line` or URL (with version or retrieval date and exact quote), distinguish verified facts from inferences and gaps, leave out secrets, and report disagreements without choosing product intent.

For a research question, read [research](references/research.md) before dispatching `Explore` to decide whether and how to save lasting notes under `docs/research/`.

## Results and gaps

Return each verifier gap to a bounded fix. A subagent that changes a file outside its packet stops and reports it. The main session fixes an incomplete packet, a stale checkout, or an environment failure itself, and asks the user about product behavior or any action outside the approved scope.
