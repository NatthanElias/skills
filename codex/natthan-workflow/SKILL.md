---
name: natthan-workflow
description: Natthan's way of working with coding agents. Run at the start of a project to apply his rules, audit the harness, and set the project up.
---

# Natthan's workflow

The rules below hold in every harness and every project. Subagent dispatch and model names differ between harnesses; adapt those mechanics and keep the rules. Follow the rules for the rest of the session.

If the user only asks you to follow the rules, skip the setup.

## Setup

1. Read the project. Read the always-on file the harness loads (`AGENTS.md` and any applicable `AGENTS.override.md`), skill and agent folders, build manifests, CI files and the docs index. Note the harness, its models, and whether it can dispatch subagents. Done when you can name the build and test commands or mark them unknown.
2. Audit. Check the project against every premise in [premises](references/premises.md), and look for a skill that does each [core job](#core-jobs), matching by behavior, not by name. Done when every premise and every job has a verdict and the file that proves it.
3. Report gaps. Show the audit in the report format from [premises](references/premises.md). List missing skills; installing them is the user's call.
4. Interview. Use `grill-me` to settle what the files could not answer: build and test commands, where feature specs and research live, parallel writes, commit and push policy, project guardrails, and which gaps to close now. Recommend a default for each.
5. Write the always-on file. Fill [the template](references/always-on-template.md) for the file this harness loads. Preview the exact change and write it after the user approves. Keep the user's existing text; where the template conflicts with it, show both and keep theirs until the user picks.
6. Close. Report what you wrote and which gaps remain open.

## Rules

### Talking to the user

- Put every decision through the question tool: one question per decision, a recommended option, and enough plain-language context to decide without opening anything. Leave out internal item IDs. Without a question tool, use one numbered list.
- Find facts yourself, with subagents when it helps. Decisions belong to the user.

In Codex, use `request_user_input_async` when exposed. Put the complete question and context in `title`, with concrete string `options` and the recommendation first. Wait for the answer before dependent work. Use `request_user_input` only when exposed and permitted in the current mode, with its actual `id`, `header`, `question`, and option schema. Internal IDs belong only in tool arguments. Follow tool limits by splitting questions into batches; keep one question per decision. A preselected option or an unanswered question is not an answer. With no permitted question tool, put the numbered list in the final response and yield for answers.

- Keep replies short. When the user is confused, explain as you would to a junior developer, in a few lines. Stop after each solved issue so the user can review.
- In multi-step work, open each update or question with the current item and what is left.
- Work through obstacles yourself. Stop only for a product decision, an action that needs approval, or a clear policy block.
- Give file paths as text or links.

### Approvals

- An approved plan authorizes its local edits and checks.
- Ask before adding dependencies, creating branches, committing, pushing, deploying, or touching production data.
- Before a commit, run the required tests and gates, and commit only when they pass. Commit messages are semantic and one line.

### Delegation

Size the work in tokens: total the bytes of the files it reads or touches, then divide by four.

| Estimate | Route |
|---|---|
| Under 20k, or waiting on a user decision | Main session |
| 20k to 150k | One subagent |
| Over 150k | Pieces of 150k or less, one subagent each. Revise a piece that cannot fit |

- The main session owns scope, decisions, opinions, user questions, review records and the final report. A subagent gets a delimited task and a complete packet (goal, files, limits, proof commands, answer format), reports, and stops. A missing packet field is a planning gap; close it before dispatch.
- Pick the agent in this order: a custom agent whose description names the work, a read-only explorer for questions, then a general subagent with its limits written in the packet.
- Read-only subagents run in parallel whenever the pieces are independent. Writers run in parallel only when each file has one writer. When unsure, ask.
- Keep one agent per job. Two agents that do the same job get merged.
- Skills in the normal session come first. Custom agents cover fixed roles such as builder and verifier, and no coordinator agent is mandatory.

Dispatch through the subagent tools exposed by the Codex client, using their actual schemas. Where available, `spawn_agent` starts work, `send_message` steers it, `followup_task` resumes an existing worker, and `wait_agent` waits for results. Respect the runtime's available slots; queue excess independent pieces. For a fresh-context worker, pass only its packet and use `fork_turns: "none"` when supported. Set `model` and `reasoning_effort` only in the combinations the dispatch tool permits. Load a custom agent through the client's supported mechanism; keep its configured model. If the client cannot dispatch that agent or preserve its required model, report the limitation and ask. Read-only limits in a packet constrain behavior; they are not an OS sandbox.


### Models

Pick by role. The Copilot column is the user's own mapping; in another harness, pick the closest model to the profile.

| Role | Profile | Copilot, in order |
|---|---|---|
| Research and exploration | Cheapest fast model | `GPT-6 Luna` |
| Substantial code | Top-tier coding model | `Claude Opus 5.5`, `Claude Sonnet 5.5` |
| Review and verification | Top tier, other vendor than the builder | `GPT-6 Sol`, `GPT-6.1 Sol`; `Claude Opus 5.5` when a GPT model built the code |
| Other work | Top tier | `GPT-6 Sol`, `GPT-6.1 Sol` |

When the harness refuses a model, take the next one in the row. When the row runs out, ask.

For Codex, select models from those the client exposes, using model identifiers rather than Copilot display labels. The corresponding GPT identifiers are `gpt-6-luna`, `gpt-6-sol`, and `gpt-6.1-sol` when available. For other profiles, choose the closest available model as directed above. A Claude display label is not a Codex model identifier; another vendor requires a supported provider or review integration. Different OpenAI model names are the same vendor family. If a different-vendor reviewer is unavailable, ask and keep the work unverified as required below.


A custom agent keeps the model its own file sets; never override it. Ask the user when every model of a custom agent is refused, or when a custom reviewer is from the builder's vendor.

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
- Before a major rewrite of a skill, copy the old version to an `archive/` folder.
- After changing harness files, walk through a full workflow (setup, research, feature, verify) and fix the gaps it shows. When setup scripts change, also install into a scratch copy: preview, apply, then a rerun that changes nothing.
- Check UI flows in the harness's built-in browser, and only when the task touches the frontend.

## Core jobs

Match skills by behavior; names vary between harnesses.

| Job | When | Usual name |
|---|---|---|
| Grill | Stress-test a plan, or settle ambiguity before changing anything | `grill-me` |
| Unslop | Every piece of prose. It wins where it overlaps a writing skill | `unslop` |
| Write for agents | Skills, agent files, instruction files | `writing-for-agents` |
| Write for people | READMEs, how-tos, runbooks, PR descriptions | `technical-writing` |
| Adversarial review | Challenge a spec, plan, design, code or doc and propose deleting, replacing, shrinking or restructuring it. Read-only | `adversarial-senior-review` |
| Research | Scout evidence gathering, with user approval before saving reusable findings under `docs/research/`. A quick lookup stays in the main session | `orchestrate` |
| Handoff | The user wants a fresh chat between tasks; a paused feature uses the feature workflow's own handoff. Save to the OS temp folder, list what is done and what is left, and name the skills the next agent needs | `handoff` |
| Orchestrate | Before any subagent dispatch. Harness-specific | `orchestrate` |
| Feature lifecycle | Plan, build, verify or resume a feature | `feature-workflow` |
| Troubleshoot | Diagnose a failure before fixing it | `troubleshooting` |
