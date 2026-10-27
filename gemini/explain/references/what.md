# Work and changes

Use this lens for completed work, a diff, a pull request, or a session catch-up. [Explain](../SKILL.md) owns the response length and writing rules.

## Establish the change

1. Use current Git status, the relevant diff, touched records, and check output. Inspect only missing or stale evidence.
2. Trace each changed behavior to its implementation and proof. Separate fixes made during the work from work still outstanding.
3. Identify decisions, approvals, access, or irreversible actions that require the user. Keep work the agent can finish on the agent's next-step list.
4. Recompute reported counts and measurements from their sources. Name their scope, sample, limits, and uncertainty. Check whether errors, skips, caches, or unexecuted paths could explain the result. Label unexplained numbers as such.

## Explain the result

Open with the user-visible outcome and any pending user decision. Group the rest by cause and effect or execution flow, with source links beside the claims.

Make each claim's status explicit:

- **Verified** names the test, observation, or record that supports it.
- **Assumed** states the assumption and the consequence if it fails.
- **Unobserved** names behavior or a result that has not been run or measured.

Keep engineering checks separate from observed runtime, experimental, or business outcomes. Negative and inconclusive results still belong in the explanation. Attribute authors and reviewers according to the records.

End with pending user actions, when any exist. Give each action enough context to stand alone, including the decision, recommendation, supporting evidence, and risk.

Done when every changed behavior, reported number, and pending decision has a source and a status.
