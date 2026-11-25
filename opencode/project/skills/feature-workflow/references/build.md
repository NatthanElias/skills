# Build

Deliver the approved plan slice by slice at production quality. Criteria and approved `Landing` rows are fixed (changing them goes back to the user). Decomposition inside each slice, ordering of later slices (within dependency and deployment constraints), helper placement, and reversible code details follow repository conventions.

## Before editing

1. Reconcile against [Resume](../SKILL.md#resume) if work already exists.
2. Run `constraints.py list` for touched areas and paths. Read the changed code paths, their callers, and every consumer/fixture listed in `plan.md` `Changes underneath`.
3. Build directly in the current session, slice by slice (no separate Builder subagent). If a slice looks too broad to review comfortably in one pass (~150k estimated tokens via `@orchestrate`'s advisory sizing helper), refine or split the slice first.

## Slice by slice

Build vertical slices one at a time, **S1 first** (a thin end-to-end tracer bullet through every layer—route, rule in tested layer, tests, screen); later slices may be reordered when dependency and deployment order allow. Never build one horizontal layer across all slices first. If a planned slice is really a single layer ("the API", "the screen"), cut it by demonstrable outcome before coding.

In multi-repo features, build and commit slices in deploy order (**expand first** so old consumers keep working while new consumers migrate).

For each slice:
1. **Characterize untested legacy paths first:** Before modifying brownfield code that has no tests, add a characterization test pinning its current observable behavior.
2. **Implement surgically—and completely inside scope:** Keep unrelated refactoring and formatting out of the diff, remove only what your change orphaned, and record any out-of-scope bug in the team's issue tracker (never in `.specs/`). Inside scope nothing is missing—what a control needs to work for real is the work even when no criterion names it.
3. **Apply code comments:** Follow [comments.md](comments.md) (`Why:`, `Hazard:`, `Context:`, `TODO(<ref>):`) and any team standards doc named in `AGENTS.md`.
4. **Update `plan.md` truth when needed:** Keep `Shape` and `Changes underneath` accurate if implementation discovers a better hop or new consumer. Append any newly discovered one-way door to `Landing` (never edit approved rows) and propose its `.specs/constraints/` record if it binds future features. Record mid-build user decisions on `**Settled mid-build:**` in their words.
5. **If an approved criterion or `Landing` door proves wrong or impossible, stop and ask the user** before changing it.

## Tests

Derive tests from each criterion and its concrete examples, never from the implementation you just wrote. Prove rules at the lowest layer that owns them; use integration tests for cross-boundary behavior (indexes, concurrency, migrations, route wiring, contracts). Extra tests are welcome when they protect real behavior—no quota and no dropped-test logs.

Apply one governing question to every new or modified test: **"Name the most plausible wrong implementation. Which assertion fails on it?"** Reject these six patterns:
1. **Copied production constant/function:** Pin the expected contract independently (a wrong production constant like `MAX_BODY_BYTES` or `WINDOW_MS` must fail the test; never assert `includes("")`).
2. **Vacuous loop or missing setup:** Assert the expected count/members before looping, and create prerequisite state before testing mutations or cleanup.
3. **Unawaited async assertion:** Await the RPC/promise/effect before asserting post-action state.
4. **Weak sanitization/logging check:** Feed a recognizable PAN, CVV/SAD, PII, or secret value and assert its absence/masking in the actual output or logs.
5. **Guarded assertion:** Assert the required HTTP/result status before checking its payload (`if (res.status === 200)` hides failures).
6. **Skip-on-failure or broad catch:** Fail on unexpected status codes or exceptions; assert the specific error type/code/message.

**Flakes:** Never rerun until green. Investigate nondeterminism; any quarantine follows the team's CI flake process.

## Screens

**Build against the source:** When `plan.md` marks a capture or design binding, the source is the reference, not the plan's description of it. If a criterion disagrees with a binding source, stop and ask before building that part.

When a slice touches UI, open the running app in a browser at each capture's exact viewport size (`pixel size / scale`)—or at the target desktop/mobile viewport named in the spec when no capture exists—and exercise the controls as a user. Once a captured state's slices land, compare it side by side with `.specs/features/<feature>/captures/` (and `.aria.yml` when present) and fix any difference not approved in `## Differences from the source`. Verify sibling screens sharing changed state still work. Screenshots are working checks, not saved artifacts. If no browser tool is available, hand exact verification steps to the user.

## Commit each slice and record final gates

1. Run the slice's tests green.
2. In a [greenfield first feature](plan.md#greenfield-first-feature), the final slice writes the new commands to `checks` in `docs/harness/setup-selection.json`, previews with `workflow-setup`'s `setup.py`, shows the team the preview, runs `--apply` after team approval, and includes those approved setup files in the final slice commit before recording `**Gates:**`.
3. Check any changed `.specs/constraints/` records with `python3 .opencode/skills/feature-workflow/scripts/constraints.py check`.
4. Validate the commit message (Conventional Commits 1.0.0, naming the slice and criteria, e.g., `feat(billing): suspend on failed charge (S1, criteria 1-3)`, with no AI trailers unless the repo requires them):
   ```bash
   python3 .opencode/skills/feature-workflow/scripts/check_commit.py --message "<msg>"
   ```
   Fix every error and delete/ignore untracked tool artifacts (browser traces, test reports) outside `.specs/`—never commit them. Feature folders under `.specs/features/` stay git-ignored.
5. **Before sending Review (after the final slice commit):** Confirm the tree is clean (`git status --porcelain --untracked-files=all` is empty), then run each required repo gate (tests, typecheck, lint, build, plus any path-triggered repo checks in `AGENTS.md`) individually or chained with `&&`—never `;`, which masks earlier failures. A gate already red at baseline is noted in the report, not fixed opportunistically. Record every required command's actual exit code and counts on `plan.md`'s (or `request.md`'s) `**Gates:**` line with the full repo SHA (one entry per touched repo in multi-repo work):
   ```markdown
   **Gates:** `warroom@<full-sha>` — `npm run test` (exit 0, 214 passed, 0 failed, 0 skipped), `npm run typecheck` (exit 0), `npm run lint` (exit 0)
   ```

Then dispatch [review](review.md).
