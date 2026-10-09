---
name: interview-me
description: Interview the user about a plan, decision, or idea through an exhaustive decision-tree interview. Use when the user asks to stress-test their thinking or invokes interview-me.
---

# Interview me

Interview the user until every relevant decision is settled and they confirm the shared understanding. Map the design as a tree. A decision's children become available only after its prerequisites are settled.

## Rounds

The frontier contains decisions whose prerequisites are already settled. Ask all of that frontier in a round, using the current client's question tool. Split it into batches only when the tool or client limits a call. Questions depending on an unsettled decision wait for the next round.

Each question names one decision, gives the context and tradeoff, and presents concrete choices with your recommendation. The user must be able to decide without opening another artifact. For an open answer, state your recommendation and leave choices out.

Use only the tools exposed and permitted in this session:

- Prefer `request_user_input_async` when available. Each item has `title` for the complete question, context, and tradeoff, and optional `options` as strings. Put the recommendation first and label it `(Recommended)`. The tool returns immediately. Continue independent evidence gathering, then wait for the reply before resolving the decision.
- In Plan mode, use `request_user_input` when available and permitted. Each item has a unique `id`, a short `header`, a self-contained `question`, and the required option objects with `label` and `description`. Follow the actual schema and limits, including at most three questions per call and its option-count rules.
- These tools do not accept Copilot's `message`, `recommended`, or `multiSelect` fields. Put context in the supported question field. For multiple selections, ask the user to list all applicable choices in a free-text answer.
- If no permitted question tool exists, present the round as one numbered list in the final response and yield for answers. Each entry carries a decision, context, choices, and recommendation.

A preselected option, elapsed time, or an unanswered question is not a decision. Keep unresolved decisions pending. Record answers, recompute the frontier, and ask the next round. If the user delegates a decision, record the delegation and your chosen answer.

## Evidence

Find facts yourself. Do not ask the user for facts you can inspect in files, tools, configuration, or documentation. For substantial evidence gathering, dispatch a read-only Scout with the exposed `spawn_agent` tool. Request `model: "gpt-6-luna"`, `reasoning_effort: "xhigh"`, and `fork_turns: "none"`; use `max` for broad or difficult research. Give it the evidence question, exact sources, file and command limits, citations to return, and instructions to spawn no agents.

Respect the current dispatch schema and available agent slots. A tool list or read-only instruction does not create an OS sandbox. Handle small lookups locally. If delegation is unavailable, gather facts locally and leave only dependent decisions pending. Ask the independent frontier while the Scout runs. Review its evidence before relying on it.

## Completion

Finish when the frontier is empty, every relevant branch has an answer or explicit delegation, and no assumptions are hidden. Present the decisions and ask the user to confirm the shared understanding through the permitted question tool or numbered-list fallback. Implement only after that confirmation, within the user's authorized scope.
