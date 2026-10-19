# How: mechanism and structure

Read this reference when explaining how a subsystem, workflow, algorithm, protocol or project rule operates. Style rules live in [../SKILL.md](../SKILL.md).

## Investigate

Scale the investigation to the question. When scope is ambiguous, state your interpretation and proceed. The user can redirect.

- **Narrow question** (one function, one rule, one small module). Read the target, its callers and the tests that pin its behavior.
- **Broad question** (a subsystem across several files, a cross-cutting feature, an architectural overview). Start at the entry point. Follow data and control flow to the outputs. Read the tests and records that pin each decision point.

When the environment supports subagents and the subsystem splits into independent slices, explore 2 to 4 slices in parallel, read-only. Follow the repository's delegation rules in `AGENTS.md`. Reconcile overlaps and resolve contradictions by checking the code yourself.

## Structure

Cover these parts in order. Drop any that do not apply. Use them as headings only when the explanation is long enough to need navigation.

1. **Overview.** One or two paragraphs. What the thing is, what it does, and why it exists. A reader can stop here and decide whether to continue.
2. **Key concepts.** The types, services or records needed to follow the rest, one line each.
3. **How it works.** The longest part. State what triggers the flow, then walk the data and control flow step by step. Anchor each step and each decision point to `file:line`. Write prose. Quote a short code excerpt only when a point depends on it.
4. **Where things live.** A short file and directory map for someone starting work here.
5. **Gotchas.** Non-obvious behavior, pitfalls and history worth knowing. Skip this part when there is nothing to say.

## Writing the mechanism

- Name concrete actors: "`UserService` calls `AuthClient.refresh()`".
- When something is complex, explain why it is complex.
- Use an analogy only when one fits exactly.
- Keep open questions and gaps visible.
- Code is evidence of present behavior. Questions of motivation go through [why.md](why.md).
- For three or more moving parts, add a diagram series from [visuals.md](visuals.md).

## Done when

The reader can predict a relevant execution path and find the code responsible for each step.
