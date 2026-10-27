---
name: grill-me
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled. You can ask those _now_ without guessing at answers you haven't heard yet.

Put the whole frontier to the user in **one call to the Codex question tool**: `request_user_input_async` or `request_user_input`, whichever the current mode exposes. One round is one call; the questions themselves never go in prose. Follow the tool's schema and per-call limits; a larger frontier spans consecutive calls in the same round. If the current mode exposes neither tool, put the round as one numbered list in your reply and yield.

Before the call, write each decision's context and tradeoffs in chat, in plain language, so the user can decide without opening anything else. The tool crops long text, so the background never goes in the call. One entry per decision:

- `header`: a short unique label for the decision.
- `question`: the decision in 40 words at most.
- `options`: the concrete choices. Put the one you would pick first and end its label with `(Recommended)`. Each label is at most five words, and its description names the consequence in one line. The client adds a free-text answer, so leave out an "Other" option.
- Any other field the schema requires, such as a question `id`.

Count the words of each question before the call and tighten any that runs over. Use a clear prose and compact wording style.

Wait for the answers. Settled decisions push the frontier outward, so recompute it and ask the next round. A question that depends on another question in the same round waits for a later round.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (files, tools, config), dispatch a sub-agent to find it, following [orchestrate](../orchestrate/SKILL.md). Keep asking while it runs. Only the questions that depend on its report wait. The _decisions_ are the user's. Put each one to them and wait.

The session is done when the frontier is empty: every branch visited, nothing silently assumed. Act on it only after the user confirms you have reached a shared understanding.
