# Plan review

One fresh pre-approval review for every substantive `plan.md`. Small changes skip it.

## 1. When and how to dispatch

Run this review **once** after the complete `plan.md` passes `validate_plan.py` and before presenting the plan to the user.

Follow `$orchestrate`:
- Prefer another model family when reachable (for example, T3 Claude `claude-opus-5-5` when T3 mode is active); in native mode dispatch `plan_reviewer` with `fork_turns: "none"` without overriding its configured model.
- Preload only `request.md` (verbatim), `plan.md`, repository root(s), applicable `.specs/constraints/` paths, and the team standards doc named in `AGENTS.md` Team additions. Include no chat history, author summary, or hints.
- Plan review is **advisory**: if no subagent tool exists or dispatch fails, record `**Plan review:** skipped - <reason>` in `plan.md` and proceed to Risk-Ledger Approval.

```text
Someone else drafted `.specs/features/<feature>/plan.md` for the verbatim request in `.specs/features/<feature>/request.md`. You have no chat history.

Repositories:
- <repo path> (branch <branch>)

Audit `plan.md` against `request.md` and live code before the human approves it. Inspect only the modules named in `Shape` and `Changes underneath`, plus their reference-search results. Check these four areas:

1. Paraphrase and reading gaps: using only `request.md` and `plan.md`, write 2–5 sentences for **What this proposes** and 2–5 sentences for **How the existing system works, per this plan**. Then list every spot where the plan forced you to open code or would force a fresh reader to guess. Inability to paraphrase a section or an unstated prerequisite is blocking.
2. Codebase truth, consumers, and constraints: verify every `(exists)` module in `Shape` exists and already does what `Shape` assigns it. Run reference search (LSP + rg) for every changed contract in `Changes underneath` and flag any missing production caller, test fixture, double, factory, or untyped file. Verify conformance with applicable `.specs/constraints/` records. A non-existent or misdescribed `(exists)` module, a missing consumer, or an unaddressed constraint violation is blocking.
3. External contracts and failure modes: flag any external or out-of-workspace contract that neither cites `Sources` nor has an S1 criterion exercising it, and any unmitigated failure mode on a `Surface` route or `Landing` door.
4. Reuse and simplicity (non-blocking only): flag a reinvented helper only when naming an existing symbol to reuse (`path:symbol`), and a speculative abstraction only when removing it still passes every criterion. Treat `Confirmed? y` assumptions as settled unless a live code fact removes the trade-off.

Stay read-only: make no edits, run no commands, and write no report file. Return:

## Paraphrase
- **What this proposes:** <2–5 sentences from `request.md` + `plan.md` only>
- **How the existing system works, per this plan:** <2–5 sentences from `request.md` + `plan.md` only>
- **Reading gaps:** <bulleted list of spots that forced a code lookup or guess, or `None`>

## Blocking findings
<Numbered list with `section / path:line`, expected vs. observed, and evidence; or `None`.>

## Non-blocking notes
<Numbered list with `section / path:line` and concrete evidence; or `None`.>
```

## 2. Triage findings

Keep findings in chat—write no separate report file. Classify every finding into one category:

- **`FIX`**: valid gap. Edit `plan.md` directly and re-run `python3 .agents/skills/feature-workflow/scripts/validate_plan.py <feature>`.
- **`CONTEST`**: factually wrong. Cite a live code file and symbol, a `.specs/constraints/` record, a `Sources` entry, or an `Assumptions` row marked `Confirmed? y`. Never contest by citing your own `plan.md` prose, and never contest a reading or comprehension gap.
- **`ESCALATE`**: requires product or team knowledge outside the repo, or changes a user decision. Leave `plan.md` unchanged and add the item to the Risk Ledger for the user.
- **`DECLINE`**: optional nit. Leave `plan.md` unchanged and include its title in the short review summary.

Record `**Plan review:** done - <N> fixed / <M> contested / <K> escalated` in the leading metadata block of `plan.md`. Never fix user-facing decisions silently: when presenting the Risk Ledger, list individually every fix that touched `Criteria`, `Assumptions`, `Out of scope`, or `Landing`, and report counts for wording-only fixes and declined nit titles. Always show the reviewer's `## Paraphrase` verbatim.

## 3. Targeted re-check (at most once)

Allow **at most one** targeted re-check for the entire planning phase, and only when triage fixes or user changes altered `Criteria`, the `Shape` path, or a `Landing` door. Wording or assumption-only edits never trigger a re-check.

Dispatch one fresh reviewer with only the changed sections of `plan.md` and the prior open blocking findings. Check only whether those blockers are closed and whether the new `Shape`/contract edits hold against live code. Update `**Plan review:**` with the new totals; anything still open goes into the Risk Ledger for the user.
