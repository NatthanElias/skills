---
name: feature-workflow
description: Plan, build, review, or resume an accepted feature across one or more repositories. Use for feature plans, vertical-slice implementation, independent verification, or resuming .specs/features work.
---

# Feature workflow

Freeze what must be true. Free how it is built. Have a fresh reviewer check it.

```
┌──────┐   ┌───────┐   ┌────────┐
│ PLAN │ → │ BUILD │ → │ REVIEW │
└──────┘   └───────┘   └────────┘
 human      slice by    fresh reviewer, fix pass,
 approved   slice       up to 2 targeted re-checks (3 rounds max)
```

Read the full phase reference before acting: [plan](references/plan.md) for a substantive feature, [build](references/build.md) once approved, and [review](references/review.md) after the final build commit. For advice or impact analysis without edits, run plan in read-only mode.

Load the global `$orchestrate` skill before dispatching the Reviewer or parallel Scouts. Put the complete packet instructions in every T3 worker brief; preload only `plan.md` (or `request.md`) plus the diff rather than untouched legacy files.

## Rules (hold without any reference)

1. **Ask every product decision before presenting the plan (or small-change `request.md`).** Answers update the spec and are not approval; re-present before building. Write `**Approved**: <YYYY-MM-DD> - user: "<their words>"` in the leading metadata header only from words the user actually gave—nothing is built without it. After recording approval, print the short copyable prompt for starting implementation in a fresh thread and pause unless the user asked to build in the current thread.
2. **Rules run where tests reach.** Every outcome-changing rule has a test that fails if the rule is wrong. A test changes only together with the claim it proves; never weaken, skip, or disable a test to clear a gate—stop and ask.
3. **A binding capture changes only by user decision.** Any screenshot, frame, or live site sent with the request binds unless the user called it inspiration.
4. **Build slice by slice, S1 first, each slice committed before the next.** Work is done only when committed on a clean tree, gates are green, UI screens have been exercised in a browser (at capture size, or at a named viewport when no capture exists), and review is closed by the fix pass (and targeted re-check(s) when blockers were reported, up to 3 total review rounds). An uncommitted change is not delivered.
5. **The reviewer is a fresh sub-agent, never the author**, and runs for every code change. Skip independent review only for pure non-logic edits (docs, comments, formatting), recording `**Review:** skipped - non-logic edit`.

## Small changes

A change is small when all three hold:
1. At most **3 files** change.
2. **No one-way door**: no contract (shared type, service method, event, schema, or persisted field), dependency, or migration change.
3. **No outside semantic cascade**: reference search (LSP + `rg`) finds zero callers outside the changed files that observe different behavior.

A small change skips `plan.md`. Create `.specs/features/<feature>/request.md` with a leading metadata block (above the first `## ` heading) holding `**Small change:** yes - <why it qualifies>`, `**Approved**: <YYYY-MM-DD> - user: "<their words>"`, `**Gates:**`, `**Review:**`, `**Fix pass:**`, and `**Re-check:**`. Put the user's prompt verbatim under `## Request`, and product answers plus numbered EARS criteria under `## Answers and criteria (planner)`. After explicit approval, record `**Approved**: ...` and output a short copyable plaintext prompt pointing to `.specs/features/<feature>/request.md` (pausing unless the user asked to build in the current thread). Then build, run gates once, and send one fresh reviewer on `request.md` + `git diff <base>`. If the reviewer finds the change ineligible for the small path, return to [plan](references/plan.md).

## Shared rules

- **Files hold the run; chat does not survive compaction.** Save the user's prompt verbatim under `## Request` in `.specs/features/<feature>/request.md` before asking questions or planning. Keep all workflow state lines (`**Small change:**`, `**Approved**:`, `**Settled mid-build:**`, `**Gates:**`, `**Review:**`, `**Fix pass:**`, `**Re-check:**`) in the leading metadata block above the first `## ` heading of `plan.md` (or `request.md` for small changes) so verbatim user text and fenced examples never alter state.
- **Constraints before code:** Run `python3 .agents/skills/feature-workflow/scripts/constraints.py list` for the areas and paths you touch before planning or building. Conform to every matching record or propose a superseding record ([constraints](references/constraints.md)). `docs/roadmap/DECISIONS.md` is for people, never a coding constraint.
- **Load team standards:** Load any team standards skill or document named in `AGENTS.md` Team additions before planning, building, or reviewing. Apply [comments](references/comments.md) to new or edited comments.
- **Keep upstream IDs:** Preserve accepted requirement or ticket IDs (e.g., `JIRA-123`, `REQ-12-AC1`) exactly as given beside EARS criteria.
- **Never invent:** Never fabricate an API, flag, command, or behavior. State "I could not find documentation for this" and ask before implementing behavior that depends on a missing product decision. Assumptions never support PASS. A subagent cannot ask the user: it stops and returns the question to the main session.
- **Protect sensitive data:** Keep proprietary code, customer data, payment card data (PAN/SAD), PII, and secrets out of logs and external tools.
- **Approval boundaries:** An approved plan (or approved small-change `request.md`) authorizes local edits and local commits. `git push`, force-push, deploy, production data changes, new dependencies, new branches, and breaking contract changes each require explicit approval. Never commit with `--no-verify`.
- **Language:** Section headings stay in English, prose follows the project, and identifiers are never translated.
- **Degraded path:** Skip a script only when no code-execution tool exists; perform the same checks by hand and state once in chat that you are on the degraded path.

## Artifacts

```text
.specs/
├── constraints/                 # committed; one file per coding constraint + INDEX.md
└── features/<feature>/          # git-ignored working files (fixed path)
    ├── request.md               # leading state lines (small changes only) + ## Request (verbatim)
    ├── plan.md                  # leading state lines + approved plan
    ├── captures/                # binding visual sources (.png + optional .aria.yml)
    └── review.md                # fresh reviewer verdict, audit header, findings, and optional ## Re-check
```

Feature folders under `.specs/features/` stay git-ignored and never ride in a commit. New or superseding `.specs/constraints/` records ride in their feature commit after `constraints.py check` passes.

## Resume

Compaction keeps the task and drops the rules. Re-read this `SKILL.md` and the active phase reference, then reconcile `.specs/features/<feature>/plan.md` (or `request.md`), `review.md`, and `git log`—commits are fact; notes are intent. Older feature folders holding `checks.md` or `execution/` are read-only history; do not migrate them. In a new session, state the current position and next step before editing.

| The files show | Next step |
| --- | --- |
| `request.md` with no `**Small change:** yes` and no `plan.md` | Finish planning and write `plan.md` |
| `plan.md` (or small-change `request.md`) without valid `**Approved**: <date> - user: "..."` | Present spec and stop for approval |
| `**Review:** skipped - non-logic edit` | Update affected living docs and report outcome |
| `**Review:**` not yet `sent at <hash>` | Build the first slice not named in `git log` (read uncommitted edits first) |
| `**Review:** sent at <hash>` and no `review.md` (or dispatch failed) | Wait if live; if dispatch failed or in a new session, re-dispatch and update `sent at` |
| `review.md` with no `**Fix pass:** done` | Run Fix pass 1 |
| `**Fix pass:** done` and `**Re-check:**` still pending (Round 1 had blockers) | Dispatch the Round 2 targeted fresh re-check |
| `**Re-check:** sent at <hash>` and no `## Re-check` in `review.md` (or dispatch failed) | Wait if live; if dispatch failed or in a new session, re-dispatch and update `sent at` |
| Round 2 `## Re-check` returned `OPEN` (or `**Re-check:** round 2 open`) without `**Fix pass:** round 2 done` | Run Fix pass 2 on remaining `OPEN` blockers and record `**Fix pass:** round 2 done` |
| `**Fix pass:** round 2 done` and Round 3 not yet sent | Record `**Re-check:** round 3 sent at <hash>` and dispatch the Round 3 (final) targeted fresh re-check |
| `**Re-check:** round 3 sent at <hash>` and no `## Re-check (Round 3)` in `review.md` (or dispatch failed) | Wait if live; if dispatch failed or in a new session, re-dispatch and update `round 3 sent at` |
| Latest `## Re-check` returned in `review.md` and `**Re-check:**` still `sent at <hash>` | Record `**Re-check:** PASS`, `round 2 open`, or `open - escalated` (after Round 3) matching `review.md` |
| `**Re-check:** open - escalated` | Report open blockers first and escalate to the user (no 4th review round) |
| `**Fix pass:**` done and `**Re-check:** not needed` (with `review.md` `PASS`) or `PASS` (with latest `## Re-check` `PASS`) | Update affected living docs and report outcome |

## Scripts

Run scripts from the repository root (pass `--root DIR` if elsewhere). Run with `--help` rather than reading source; non-zero exit means stop and fix.

| When | Command |
| --- | --- |
| Before planning or building | `python3 .agents/skills/feature-workflow/scripts/constraints.py list [--scope ...] [--paths ...]` |
| Before presenting `plan.md` | `python3 .agents/skills/feature-workflow/scripts/validate_plan.py <feature>` |
| Before each commit | `python3 .agents/skills/feature-workflow/scripts/check_commit.py --message "<msg>"` |
| Before committing constraint changes | `python3 .agents/skills/feature-workflow/scripts/constraints.py check` |
| Session resume hook | `python3 .agents/skills/feature-workflow/scripts/resume_note.py` |
| After editing this skill's scripts or template | `python3 .agents/skills/feature-workflow/scripts/selftest.py` (must stay at 0 failed) |

Parts of this skill adapt `tlc-spec-lean` 3.2.0 under CC-BY-4.0; see [ATTRIBUTION.md](ATTRIBUTION.md).
