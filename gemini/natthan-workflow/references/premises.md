# Premises

Check whether the project's instructions, skills, agents and docs make an agent follow each premise. Judge the behavior, not the mechanism: a script, an agent file or a line of prose can each carry a premise.

- PRESENT: an always-loaded file or a skill states it.
- PARTIAL: it is stated with a gap, such as no threshold or no owner.
- MISSING: nothing states it.

| Premise | Present when the project states |
|---|---|
| Plan before code | Substantive work starts with a plan the user approves before any edit |
| Grounded plan | The plan names the flow, impacted files, changed contracts or stored shapes, hard-to-reverse choices, criteria, out of scope, assumptions and sources |
| Small-correction path | A size limit below which a fix skips the plan but still states its criterion and proof |
| Observable checks | Each check names a concrete value, state, error or payload field |
| Evidence tags | Claims carry a source tag and a citation; an inferred claim cannot pass; missing evidence is a gap |
| Baseline first | Build and tests run before changes, so new failures show |
| Proof that ran | Each check closes with a command, exit code and test counts |
| Tests stay strong | Tests are never weakened, skipped or deleted to pass a gate |
| Independent review | A fresh reviewer from another model vendor, who did not write the change, verifies it |
| Fault injection | The verifier injects plausible faults and treats a missed one as a test gap |
| Escalation | After three failed fix rounds, the work goes back to the user |
| Approval boundary | Dependencies, branches, commits, push, deploy and production data need explicit approval |
| Resume reconciliation | On resume, the agent reconciles HEAD, dirty files and instructions, and marks stale proof |
| Lessons loop | Review failures feed lessons, reused once a second feature confirms them |
| Delegation sizing | A token estimate decides main session, one subagent, or split pieces |
| Decisions through questions | Decisions reach the user through the question tool, each with a recommended option |
| Feature package location | Feature specs live in one known folder, by default `.specs/features/<feature>/` |

## Report format

| Premise or job | Verdict | Evidence | Missing |
|---|---|---|---|
| `<name>` | PRESENT, PARTIAL or MISSING | `path:line` or none | What would close it |

List MISSING premises first, the ones that guard behavior changes at the top. List missing core-job skills in a separate table.
