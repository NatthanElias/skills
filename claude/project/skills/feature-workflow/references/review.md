# Review

One unified sequence for every code change (no modes or tiers): **Round 1 fresh end-to-end review → Fix pass 1 → Round 2 targeted fresh re-check** (only when Round 1 reported blocking findings) **→ if `OPEN`, Fix pass 2 → Round 3 targeted fresh re-check → if still `OPEN`, escalate to the user (no 4th review round)**. Skip independent review only for pure non-logic edits (docs, comments, formatting), recording `**Review:** skipped - non-logic edit`.

## 1. Dispatch the fresh reviewer

Record `**Review:** sent at <HEAD short hash>` in the leading metadata block of `plan.md` (or `request.md` for small changes). Run `/orchestrate`'s delegation gate (with `--exception independent-verification` below floor):
- Dispatch **one fresh sub-agent** per accepted feature, never the author, from another model family when the client can dispatch one; if the only available reviewer shares the Builder's model, ask the user before proceeding.
- If the gate returns `split`, do not split `review.md` across colliding writers—return to [plan](plan.md) for an agreed sub-feature split preserving cross-slice criteria so each accepted feature keeps one end-to-end reviewer and one report owner.
- Preload only `request.md` (verbatim) + `plan.md` (when present) + the diff range(s) + `captures/`. Put the complete packet instructions in every T3 brief; add no author summary or hints about where to look.
- **Diff ranges:** pass every touched repository and its `<base>..<head>` range. In a greenfield first feature with no prior base commit, pass Git's empty-tree SHA `4b825dc642cb6eb9a060e54bf8d69288fbee4904..<head>`.

`<spec>` is:
- **With `plan.md`:** `The approved plan is .specs/features/<feature>/plan.md (and captures in .specs/features/<feature>/captures/ if present).`
- **Small change (no `plan.md`):** `There is no plan.md: the spec is .specs/features/<feature>/request.md (verbatim request under ## Request, plus planner answers and EARS criteria).`

```text
Someone else implemented a feature across the repository range(s) below. The user's request is quoted below. <spec>

Repositories and ranges:
- <repo path> (branch <branch>): `git diff <base>..<head>` (plus any uncommitted changes)

Check whether everything the request and spec ask for was implemented correctly, safely, and without unguarded regressions. Decide yourself how to check it. At least:
1. Request & spec coverage: read the user's request sentence by sentence against what was built (not only plan.md), plus every criterion, Landing door, and applicable `.specs/constraints/` record. If there is no `plan.md`, first verify small-change eligibility (at most 3 files, no one-way door/contract/schema/dependency change, and zero callers outside the changed files seeing different behavior); if ineligible, return `BLOCKED` so the feature returns to planning.
2. Cascading impact: run reference search (LSP + rg) for every changed contract symbol in the diff (shared types, service methods, events, schemas, persisted fields). When `plan.md` is present, any production caller, test fixture, double, factory, or untyped file missing from `Changes underneath` is a blocking finding. Inspect the consumers the reference search returns—no unrelated files.
3. Tests & doubt-driven fault check: inspect tests added/modified in the diff and tests of changed contracts using these six patterns as guidance (copied production constants/functions, vacuous loops or missing setup, unawaited async assertions, sanitization/logging tests without a recognizable PAN/CVV/PII/secret and absence check, status-guarded assertions, skip-on-failure or broad catch). For each criterion, judge whether its test would fail under the most plausible wrong implementation; cite assertion `path:line` for every finding or material doubt. Only where reading leaves doubt—and ONLY when you hold exclusive ownership of the target file, your harness permits edits, and `git status --porcelain --untracked-files=all` is empty before you start—make that single in-place edit, run ONLY the focused test, verify `git diff` contains only your injected edit, restore with `git checkout -- <file>`, and confirm `git status --porcelain --untracked-files=all` is empty afterwards. If the tree is dirty, edits are denied, or the focused test is unsafe to rerun (e.g., stateful E2E), record the doubt as `unproven` (blocking) instead of editing or running it. A surviving fault is blocking.
4. Gates: run the focused tests for changed code and changed contracts yourself in every touched repository. For each required full regression gate (tests, typecheck, lint, build, plus any path-triggered repo checks—or CI's exact affected-tests command, never weaker than CI): run each command individually (never hiding failures with `;`) and record its actual exit code and counts, OR reuse a required builder `**Gates:**` command ONLY when the repo matches, its recorded full SHA equals `git rev-parse HEAD`, `git status --porcelain --untracked-files=all` is empty, and you checked its counts for skips/drops (cite `reused @ <full-sha>`). Always re-run any command missing from `**Gates:**` or when code changed after that SHA. For an external consumer repo you cannot check out, require observed evidence from the verification mechanism `plan.md` named (not an unverified claim).
5. Screens (when UI changed): open the running app at each capture's viewport size—or at the target desktop/mobile viewport when no capture exists—exercise the controls, and compare captured states with `.specs/features/<feature>/captures/` (and `.aria.yml` when present). To reach a state live data lacks, stub in the browser or use a throwaway DB copy and state which.
6. Comments & standards: check changed code against `.claude/skills/feature-workflow/references/comments.md` and any team standards doc in `CLAUDE.md`.

Do not leave code edits behind, do not commit, do not push, and do not modify live app data outside the repository. Return the complete report in the Audit Header format below (and write it to `.specs/features/<feature>/review.md` if your harness permits file writes; otherwise the main session persists it unchanged).

Environment:
- Stay inside the listed repository root(s); do not switch branches or push.
- Builder: <builder model / identity>
- <how to start the app, ports, and any parallel stack overrides if applicable>

The user's request (verbatim):
<verbatim ## Request section from request.md>
```

If the reviewer is strictly read-only (e.g., OpenCode `edit: deny`), the main session writes its returned report verbatim to `.specs/features/<feature>/review.md`. Without sub-agents, run this prompt in a fresh session (or hand it to the user) and say so in the final report.

## Audit Header format for `.specs/features/<feature>/review.md`

```markdown
# Review: <feature>

- **Ticket / Feature:** <upstream ID or feature slug>
- **Commits:** `<repo>@<base>..<head>` (one entry per touched repo)
- **Builder → Reviewer:** `<builder model>` → `<reviewer model>`
- **Gates:** `<repo>@<full-sha>`: `<cmd1>` (exit `<N>`, `<P>` passed, `<F>` failed, `<S>` skipped — ran or reused), `<cmd2>` (exit `<N>`)
- **Verdict:** PASS | CHANGES_REQUIRED | BLOCKED

## Blocking findings
<Ranked list with `path:line`, expected vs. observed, and evidence; or `None`.>

## Non-blocking notes
<Optional observations, standards/comment nits not tied to criteria; or `None`.>
```

> **Governance note (e.g., PCI DSS v4.0.1):** Independent code review by someone other than the author is a *human PR control* in source control. This sub-agent review never replaces human PR approval; `review.md` + `plan.md` supply the structured evidence (reason, impact, test results, back-out path) that human review consumes.

## 2. Fix pass

Read `review.md`.
- If Round 1 returned `PASS` with zero blocking findings: record `**Fix pass:** done - no changes needed` and `**Re-check:** not needed - Round 1 PASS` in the leading metadata block of `plan.md` (or `request.md`)—no extra commit is needed—and go straight to **Report**.
- If Round 1 returned `BLOCKED` for small-change ineligibility: stop and write a full `plan.md` via [plan](plan.md).
- If Round 1 had blocking findings (or Round 2 returned `OPEN`):
  1. Fix every open blocking finding you agree with in **one pass** under [build.md](build.md) rules. A finding where a screen departs from a binding capture cannot be dismissed unilaterally—fix it, or ask the user if fixing requires a layout or shared-screen decision. Product decisions go to the user; disagreed findings stay unfixed with your explicit rationale in the report.
  2. Clean any tool artifacts (browser traces, test output) and commit the fix pass locally in each touched repo (validated with `check_commit.py`).
  3. Confirm `git status --porcelain --untracked-files=all` is empty, run affected focused tests and required regression gates on the new `HEAD` (individually or with `&&`, never `;`), and update `**Gates:**` in `plan.md` (or `request.md`) with the new full SHA(s) and actual exit codes/counts.
  4. Write `**Fix pass:** done - <what changed>` after Fix pass 1, or `**Fix pass:** round 2 done - <what changed>` after Fix pass 2, in `plan.md` (or `request.md`).

## 3. Targeted re-check (Round 2, and Round 3 if Round 2 is OPEN)

After Fix pass 1, record `**Re-check:** sent at <HEAD short hash>` in `plan.md` (or `request.md`) for Round 2. After Fix pass 2, record `**Re-check:** round 3 sent at <HEAD short hash>` for Round 3 (the final review round). Dispatch **one fresh sub-agent** (never the author) with the fixed prompt below (setting `<N>` to `2` or `3`, `<prev-round-head>` to the reviewed HEAD of Round `<N-1>`, and quoting only the open blocking findings from Round `<N-1>`). Add no author summary or commentary.

```text
Someone else ran a fix pass for the open blocking findings from Round <N-1> of `.specs/features/<feature>/review.md`.

Repositories and fix ranges:
- <repo path> (branch <branch>): `git diff <prev-round-head>..<head>`

Your ONLY job is to verify whether each open blocking finding below is now closed on HEAD:
1. Inspect the fix diff and run the focused tests for every blocking finding yourself.
2. For required full regression gates on HEAD: run each command individually (never `;`) and record actual exit codes/counts, OR reuse a qualifying post-fix builder `**Gates:**` command ONLY when the repo matches, its recorded full SHA equals `git rev-parse HEAD`, and `git status --porcelain --untracked-files=all` is empty (never reuse an earlier pre-fix gate run).
3. Do NOT re-review untouched parts of the feature and do NOT hunt for unrelated findings. Do not leave code edits, commit, or push.

Return (and append to `.specs/features/<feature>/review.md` without editing earlier rounds' sections if your harness permits file writes; otherwise the main session appends it unchanged):

## Re-check (Round <N>)
- **Commits:** `<repo>@<prev-round-head>..<head>`
- **Reviewer:** `<your model / identity>`
- **Gates:** `<repo>@<full-sha>`: `<cmd>` (exit `<N>`, `<P>` passed, `<F>` failed, `<S>` skipped — ran or reused)
- **Finding status:** one line per open blocking finding (`CLOSED` with `path:line` evidence, or `OPEN` with what remains)
- **Re-check verdict:** `PASS` | `OPEN`

Environment:
- Stay inside the listed repository root(s); do not switch branches or push.
- <how to start the app, ports, and any parallel stack overrides if applicable>

Open blocking findings from Round <N-1> (verbatim from review.md):
<verbatim open blocking findings from Round N-1>
```

After the re-check returns (and `## Re-check (Round <N>)` is in `review.md`):
- If `PASS`: update `**Re-check:** PASS` in `plan.md` (or `request.md`).
- If Round 2 returned `OPEN`: update `**Re-check:** round 2 open` in `plan.md` (or `request.md`), run **Fix pass 2** on the remaining `OPEN` blockers (step 2 above), and dispatch **Round 3** (final targeted re-check).
- If Round 3 still returned `OPEN`: update `**Re-check:** open - escalated` in `plan.md` (or `request.md`) and escalate directly to the user—**no 4th review round**.

## 4. Report

Update affected living docs (plain developer prose; leave historical discovery snapshots untouched) and lead the final response with the outcome:
1. Verdict (put any red gate, unfixed finding, or escalated `OPEN` blocker **first**).
2. What was built and local commits (`<repo>@<sha> <msg>`).
3. Review outcome, what the fix pass changed (plus re-check result if run), and any disagreed findings with rationale.
4. Remaining approvals needed (`git push`, PR creation, deploy, migrations).
