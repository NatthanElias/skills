---
name: natthan-workflow
description: Use only when the user explicitly asks. Natthan's way of working with
  coding agents. Run at the start of a project to apply his rules, audit the harness,
  and set the project up.
---

Use only when the user explicitly asks for this skill or its named workflow.

# Natthan's workflow

The rules below hold in every harness and every project. Subagent dispatch and model names differ between harnesses; adapt those mechanics and keep the rules. Follow the rules for the rest of the session.

If the user only asks you to follow the rules, skip the setup.

## Setup

1. Read the project. Read the always-on file the harness loads (the active workspace rules and any applicable `AGENTS.md` instructions supplied by the client), skill and agent folders, build manifests, CI files and the docs index. Note the harness, its models, and whether it can dispatch subagents. Done when you can name the build and test commands or mark them unknown.
2. Audit. Check the project against every premise in [premises](references/premises.md), and look for a skill that does each [core job](#core-jobs), matching by behavior, not by name. Done when every premise and every job has a verdict and the file that proves it.
3. Report gaps. Show the audit in the report format from [premises](references/premises.md). List missing skills; installing them is the user's call.
4. Interview. Use [grill-me](../grill-me/SKILL.md) to settle what the files could not answer: build and test commands, where feature specs and research live, parallel writes, commit and push policy, project guardrails, and which gaps to close now. Recommend a default for each.
5. Write the always-on file. Fill [the template](references/always-on-template.md) for the file this harness loads. Preview the exact change and write it after the user approves. Keep the user's existing text; where the template conflicts with it, show both and keep theirs until the user picks.
6. Close. Report what you wrote and which gaps remain open.

## Rules

### Talking to the user

- Put every decision through the question tool: one question per decision, a recommended option, and enough plain-language context to decide without opening anything. Leave out internal item IDs. Without a question tool, use one numbered list.
- Find facts yourself, with subagents when it helps. Decisions belong to the user.

Use a question tool only if it is exposed and permitted in this session, and follow its actual schema. Otherwise ask in the final response and yield for an answer. Do not infer an answer from a default selection, elapsed time, or an unanswered question.

- Keep replies short. When the user is confused, explain as you would to a junior developer, in a few lines. Stop after each solved issue so the user can review.
- In multi-step work, open each update or question with the current item and what is left.
- Work through obstacles yourself. Stop only for a product decision, an action that needs approval, or a clear policy block.
- Give file paths as text or links.

### Approvals

- An approved plan authorizes its local edits and checks.
- Ask before adding dependencies, creating branches, committing, pushing, deploying, or touching production data.
- Before a commit, run the required tests and gates, and commit only when they pass. Commit messages are semantic and one line.

### Delegation

Use [orchestrate](../orchestrate/SKILL.md) before dispatch. Run its deterministic delegation gate on the relevant inputs; the estimate is file bytes divided by four, rounded up. Its explicit floor exceptions and ceiling rules apply.

| Estimate | Route |
|---|---|
| Under 25k, or waiting on a user decision | Main session |
| 25k to 150k | One subagent |
| Over 150k | Pieces of 150k or less, one subagent each. Revise a piece that cannot fit |

- The main session owns scope, decisions, opinions, user questions, review records and the final report. A subagent gets a delimited task and a complete packet (goal, files, limits, proof commands, answer format), reports, and stops. A missing packet field is a planning gap; close it before dispatch.
- Pick the agent in this order: a custom agent whose description names the work, a read-only explorer for questions, then a general subagent with its limits written in the packet.
- Read-only subagents run in parallel whenever the pieces are independent. Writers run in parallel only when each file has one writer. When unsure, ask.
- Keep one agent per job. Two agents that do the same job get merged.
- Skills in the normal session come first. Custom agents cover fixed roles such as builder and verifier, and no coordinator agent is mandatory.

Dispatch through [orchestrate](../orchestrate/SKILL.md), using its T3 Orchestrate v2 transport, exact selected harness/model/options, stable request IDs, identity checks, and task tracking. Pass only the complete task packet. Respect available slots and queue excess independent pieces. Read-only limits in a packet constrain behavior; they do not create an OS sandbox.

### Models

Use orchestrate's selected Scout, Builder, Oracle, and Verifier mappings unless the user or applicable project rules explicitly override them. Select models from the live T3 catalog with their provider instances and supported options. Keep the selected harness, model, and options; if any are unavailable, ask before substituting. Each review round is a new `delegate_task` with fresh context and the previous findings and responses. A different-vendor reviewer means a different model vendor family, not a different model from the same vendor. If the required independent reviewer is unavailable, ask and keep the work unverified.

A custom agent requested for a task keeps its configured model. Report any conflict with the selected mapping before dispatch; do not create separate agent definitions or change configuration to implement this workflow.


### Feature work

- Research in one chat, then implement in a fresh chat that gets only the plan.
- Research reads code and project docs first, then library docs, then the web, and states what stays uncertain.
- Substantive work goes plan, checks, build, verify. A small correction (one behavior, at most three files, no contract, schema or persisted-field change) states its criterion and proof inline.
- Reuse existing specs, requirements and their IDs. Feature packages live in `.specs/features/<feature>/` and get committed; `docs/` holds research and living docs.
- Tag claims `[CODE]`, `[INTERPRETED]`, `[INFERRED]` or `[GAP]` and cite `path:line`. An `[INFERRED]` claim never supports a PASS. Missing evidence stays a `[GAP]` until the user makes the product decision.
- Each check names a concrete value, state, error or payload field. Its proof is a command that ran, recorded with exit code and test counts.
- Make the smallest change that passes the proof and follows current patterns. Keep the user's uncommitted changes intact. Tests stay at least as strong as you found them.
- A behavior change needs an independent reviewer: fresh context, a different vendor family from the builder, same tier or higher. The author's own review counts as feedback. Without such a reviewer, the work stays unverified.
- The verifier injects 1 to 3 plausible faults, up to 5 on critical paths such as persisted data or shared contracts. A fault the tests miss is a test gap.
- After three failed fix rounds, escalate to the user.
- On resume, reconcile HEAD, dirty files and instructions before editing. A changed checkout makes earlier proof stale.
- A review failure that shows a reusable mechanism becomes a candidate lesson, confirmed when a second feature hits it. Load confirmed lessons before planning.

### Writing

- The always-on file is an index, like a book's table of contents: project guardrails plus a table of docs with a short "when to read" column. Skills are found through their own descriptions, and procedures live in skills.
- Write an instruction only where it changes what a capable model would do anyway. Use a table where it summarizes better than prose.
- Keep one source of truth per rule, and link instead of copying. A skill carries only what it needs to run, with no notes on where it came from.
- Skill support files go in `references/`, scripts in `scripts/`.
- Before a major rewrite of an installed skill, back up the old version outside every skill discovery root.
- After changing harness files, walk through a full workflow (setup, research, feature, verify) and fix the gaps it shows. When setup scripts change, also install into a scratch copy: preview, apply, then a rerun that changes nothing.
- Check UI flows in the harness's built-in browser, and only when the task touches the frontend.

## Core jobs

Match skills by behavior; names vary between harnesses.

| Job | When | Usual name |
|---|---|---|
| Grill | Stress-test a plan, or settle ambiguity before changing anything | [grill-me](../grill-me/SKILL.md) |
| Unslop | Every piece of prose. It wins where it overlaps a writing skill | `unslop` |
| Write for agents | Skills, agent files, instruction files | `writing-for-agents` |
| Write for people | READMEs, how-tos, runbooks, PR descriptions | `technical-writing` |
| Adversarial review | Challenge a spec, plan, design, code or doc and propose deleting, replacing, shrinking or restructuring it. Read-only | `adversarial-senior-review` |
| Research | Scout evidence gathering, with user approval before saving reusable findings under `docs/research/`. A quick lookup stays in the main session | `orchestrate` |
| Handoff | The user wants a fresh chat between tasks; a paused feature uses the feature workflow's own handoff. Save to the OS temp folder, list what is done and what is left, and name the skills the next agent needs | `handoff` |
| Orchestrate | Before any subagent dispatch. Harness-specific | `orchestrate` |
| Feature lifecycle | Plan, build, verify or resume a feature | `feature-workflow` |
| Troubleshoot | Diagnose a failure before fixing it | `troubleshooting` |
