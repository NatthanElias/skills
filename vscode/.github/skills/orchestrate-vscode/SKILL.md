---
name: orchestrate-vscode
description: "Use before any subagent dispatch, alone or in parallel, AND for any research question, saved or not. Useful when substantial and meaningful work can split into independent pieces."
---

# Orchestrate in VS Code

The main session owns scope, user questions, repository bindings, review records, and the final report. Each subagent gets a bounded packet, reports, and stops. Product decisions stay with the user.

A subagent starts without the chat history and cannot ask the user anything. Its report ends the dispatch. Follow-up work needs a new dispatch with a complete packet.

Work on the branch and revision the user has already checked out. Never switch branches, check out another revision, or create a branch. Include this restriction in every subagent packet. The user supplies the correct branch; repository and checkout IDs are identity labels, not Git instructions.

## Size the work

Before every dispatch, including Explore, run the size script on the files and folders the work will read or touch:

```
python3 .github/skills/orchestrate-vscode/scripts/estimate_size.py <path>...
```

It sums the bytes, skipping `.git`, divides by four, and prints the route with the floor and ceiling it applied. The floor is the smallest estimate worth a subagent; the ceiling is the most one subagent takes. Never dispatch without its output. If you cannot name the paths, ask the user with the question tool. Web-only research has no local paths: send it to Explore, and run the script only on any local paths it also reads.

| Route printed | Dispatch |
| --- | --- |
| `main session`, or the work waits on a user decision | None. The main session does the work |
| `one subagent` | One subagent |
| `split into at least N pieces` | Pieces within the ceiling, one subagent each. A piece that cannot fit is too coarse; revise it |

A workflow that cuts its own slices, such as feature-workflow, still keeps each builder within the ceiling.

## Pick the agent

List the agents the subagent tool offers, then take the first that fits:

1. A custom agent whose description names this work. Dispatch it by its exact name. If two fit, or the fit is doubtful, ask the user with the question tool.
2. Explore, for a read-only question.
3. A general subagent: dispatch without an agent name. It inherits the main session's tools, so the packet states its limits. For a build or a review, copy the limits from the task-worker or spec-verifier agent file.

## Pick the model

A custom agent runs on the model in its own file. Dispatch it without a model.

Pass a model when dispatching Explore or a general subagent:

| Role | Models, in order |
| --- | --- |
| Research and exploration, including Explore | `GPT-6 Luna (copilot)` only |
| Substantial code changes | `Claude Opus 5.5 (copilot)`, then `Claude Sonnet 5.5 (copilot)` |
| Review, verification, judging | `GPT-6.1 Sol (copilot)`, then `GPT-6 Sol (copilot)`. When a GPT model built the code, `Claude Opus 5.5 (copilot)` |
| Any other work | `GPT-6.1 Sol (copilot)`, then `GPT-6 Sol (copilot)` |

Opus 5.5 and both Sol models share the top tier. Sonnet 5.5 sits one tier below.

VS Code refuses a model above the main chat's cost tier, and the subagent does not start. On a refusal, dispatch again with the next model in the row. When the row runs out, ask the user. When Explore's model or a custom agent's model is refused, ask right away: switch the main chat's model, read in the main session, or wait. For a custom agent, also offer a general subagent on the table's model.

## Independent review

Skip review for typos, comments, documentation, formatting, and Markdown edits to skills, agents, or instructions. Run focused checks instead.

For a change to code, configuration, a dependency, a build, or a test, run the size script on the review packet: plan, checks, binding sources, and changed files. Route the review by the script's output:

- `main session`: never dispatch a reviewer. The main session reviews the work itself.
- `one subagent`: one independent reviewer.
- `split`: split the review into pieces within the ceiling, one independent reviewer each.

An independent reviewer is a fresh subagent, never the session or dispatch that built it. The reviewer's model comes from another vendor family than the builder's, at the same tier or higher. If the matching custom reviewer runs on the builder's family, ask the user with the question tool. The author's own review counts as feedback. From the floor up, without a qualifying reviewer, record independent review as pending and leave the feature unverified.

## Split and run in parallel

Atomize the work into the smallest pieces that each have one question or bounded slice, their own files, and no need for another piece's result. Dispatch independent pieces together, then merge their answers in the main session.

- Read-only subagents, including Explore, may always run in parallel.
- Writers run in parallel only when the always-on instructions allow parallel writes and each file has one writer. Otherwise they run in sequence.
- When unsure whether pieces may run in parallel, ask the user with the question tool before dispatching. Name the pieces, what they share or depend on, and the risk. Offer to run them in parallel, in sequence, or split differently, and mark one option as recommended.

## Prepare the packet

Unless the always-on instructions record `Repositories: single`, resolve selected repositories and their IDs through workspace-analysis. With `Repositories: single`, the packet names the repository root instead of repository IDs and bindings.

- Explore gets one question, selected roots, exclusions, a stop rule, and the answer format below.
- A builder gets the approved plan and checks, its whole feature or named outcome slices, repository IDs and local bindings, baseline commands and counts, current HEAD and diff fingerprints, confirmed lessons, the team standards skill or document named in Team additions, file ownership, and authorization limits.
- A verifier gets every check in its scope, the full plan and binding sources, the author's identity and model, selected repository IDs and local bindings, current HEAD and fingerprints, the diff, the review file list the size script measured, named proof commands, baseline counts, mutation budget, earlier surviving faults, and the team standards skill or document named in Team additions. A final verifier gets the whole feature, even when several builders worked on it. A review of only the final slice cannot complete the feature.

Dispatch a writer only after its checks and proof commands are settled and its prerequisites pass. Treat a missing packet field as a planning gap and close it before dispatch.

## Explore answer

Explore owns its web fetches. A source it still cannot read stays a gap in its answer. Give Explore this limit and format:

```
Read and search only. Stay inside selected roots. Cross a repository boundary only when both roots are selected.
Read code and project docs first, then official docs, specs, and first-party APIs, then other web sources. Trace each claim to the source that owns it; a secondhand source never outranks the owner.
Label claims [CODE], [DOC], [INFERRED], or [GAP]. Cite paths and lines. Do not include secret values.
If a fetch fails, retry it once yourself.
Report disagreement without choosing product intent. Stop at the stated question or budget.

Answer: <one or two sentences, or Not determined>
Evidence: <tag, repo_id:path#line or URL, finding; for a URL add the version or retrieval date and the exact quote>
Disagreements: <sources or none>
Not inspected: <scope>
Searched without result: <terms and paths>
Fetch failures: <URL and error after the retry, or none>
Stopped because: <stop rule or budget>
```

## Research

For a research question, read [research](references/research.md) before dispatching Explore. It covers when to save the answer under `docs/research/` and the note's shape.

## Results and gaps

Return each verifier gap to a bounded fix. A subagent that changes a file outside its packet stops and reports it. The main session fixes an incomplete packet, a stale checkout, or an environment failure itself, and asks the user about product behavior or any action outside the approved scope.
