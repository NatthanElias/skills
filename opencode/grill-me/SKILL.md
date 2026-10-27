---
name: grill-me
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled. You can ask those _now_ without guessing at answers you haven't heard yet.

Put the whole frontier to the user in **one call to the `question` tool**. One round is one call; the questions themselves never go in prose. If the client cannot show the `question` form, put the round as one numbered list in your reply and wait.

Before the call, write each decision's context and tradeoffs in chat, in plain language, so the user can decide without opening anything else. The form crops long text, so the background never goes in the call. One entry per decision:

- `header`: a short unique label for the decision.
- `prompt`: the decision in 40 words at most.
- `choices`: the concrete choices. Put the one you would pick first and end it with `(Recommended)`. Each choice is at most five words; its tradeoff belongs in the chat background. The tool always allows a free-form answer, so for an open-ended answer give your recommendation as the only choice and explain it in chat.
- `multiple`: only when more than one choice can be true at once.

A dismissed question is cancelled, not answered. Ask it again in the next call.

Count the words of each question before the call and tighten any that runs over. Use a clear prose and compact wording style.

Wait for the answers. Settled decisions push the frontier outward, so recompute it and ask the next round. A question that depends on another question in the same round waits for a later round.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (files, tools, config), dispatch a sub-agent to find it, following [orchestrate](../orchestrate/SKILL.md). Keep asking while it runs. Only the questions that depend on its report wait. The _decisions_ are the user's. Put each one to them and wait.

The session is done when the frontier is empty: every branch visited, nothing silently assumed. Act on it only after the user confirms you have reached a shared understanding.
