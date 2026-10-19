# What: work and deltas

Read this reference when explaining work just completed, reviewing a diff or PR, or catching the user up on session changes. Style rules live in [../SKILL.md](../SKILL.md).

## Gather

1. Re-read current state before reporting it. Check `git status`, the diff, check output and every record the work touched. Your memory of the session is a lead to confirm.
2. Collect every item waiting on the user. An item is a call only the user can make, such as a product choice, an approval, an irreversible action or access you lack. Work you can still do yourself is a next step for you.
3. Explain every number before you report it. For each count, metric, timing or result:
   - Re-derive it from its source, and say so when you correct one.
   - Name what bounds it, such as the run count, the spread, a resource limit or the sample.
   - List what else it could be measuring, such as errors, skipped or cached work, code that never ran, or noise. Rule each one out with evidence, or state it as open.
   - When you cannot name the bound, call the number unexplained.

## Write

1. Open with one sentence that names the user-visible outcome and what waits on the user. When nothing waits, say so.
2. Group changes by logical flow, such as cause, change and effect, or request and steps. Cite files as anchors inside that flow, in place of a file-by-file list.
3. Name every bug found and fixed along the way.
4. Give each claim a status:
   - **Verified.** Name the check, test or observation that verified it.
   - **Assumed.** Name the assumption and what breaks if it fails.
   - **Unobserved.** Name what has not run or been measured yet.
5. List action items last. For each one, give the call, your pick, the evidence behind your pick and its risk, even when the risk is low. Each item must stand alone when read out of context.

## Morfe boundaries

- Passing engineering verification is separate from an observed transfer comparison. Report "tests pass" and "the pilot observed X" as different claims.
- A no-transfer or all-withheld result is valid evidence about the mechanism. Report it as a finding, with the same weight as a positive one.
- Name the actual author and reviewer of each decision or result, as the records attribute them.

## Done when

Every changed behavior, every reported number and every waiting item appears with its anchor and its status.
