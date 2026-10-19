---
name: explain
description: Explain completed agent work, a codebase subsystem, or a project decision so a person can understand and check it. Use when the user asks what you just did, how something works, why something is built a certain way, or to catch them up.
---

# Explain

Give the reader a checkable mental model. They should know what changed or what the thing is, how it works, why it exists, and what the evidence does and does not establish.

## Pass 1: the first reply

Gather only the evidences the immediate question needs. Read the diff, code, records or check output that the answer rests on. Then answer in two or three sentences:

1. **Outcome or plain definition.** State what changed, or what the thing is, and link the primary `file:line` or artifact anchor.
2. **Mechanism or cited reason.** State how it works in concrete terms, or cite the recorded reason (`AD-NNN`, commit, PR, `plan.md`, `DECISIONS.md`).
3. **Evidence and boundary.** State what the checks establish and what remains unchecked, assumed or unobserved. A passing engineering check is a different claim from an observed runtime or scientific outcome. Report each one separately.

Close with one short offer to go deeper, shaped to the subject. Always provide the user with at least one option for different modes of explanation, also shaped by the subject, like: a step-by-step diagram, or an interactive HTML explainer, etc. Then stop.

Pass 1 is done when each of the three sentences carries an anchor or citation, and the boundary sentence names at least one thing the evidence leaves open, or says nothing is left open and why.

## Pass 2 and later: going deeper

When the user asks to go deeper, or asks for a lens or medium up front, read every matching reference below. Investigate further where the reference requires it, then produce the deeper explanation. A "teach me" request usually needs `how`, `why` and `visuals` together.

| Lens | Read when | Reference |
| --- | --- | --- |
| Work and deltas (`what`) | Explaining work just completed, reviewing a diff or PR, or catching the user up on session changes | [references/what.md](references/what.md) |
| Mechanism and structure (`how`) | Explaining how a subsystem, workflow, algorithm, protocol or project rule operates | [references/how.md](references/how.md) |
| Rationale and history (`why`) | Explaining why code, a constraint, an architecture or a project decision exists | [references/why.md](references/why.md) |
| Visuals and teaching (`visuals`) | Teaching a topic in depth, or producing diagrams, images or interactive HTML | [references/visuals.md](references/visuals.md) |

The lenses apply to code, architecture, specs, data and research alike.

## Writing style

Write in 80% ASD-STE100, the Simplified Technical English of aerospace maintenance manuals, and pass all text through `unslop` skill. Take its discipline. Claim no formal compliance with the standard.

1. **One claim or action per sentence.** Aim for 20 to 25 words or fewer. Split clause chains with periods.
2. **One name per concept.** Use the real codebase name for each type, record or artifact, and keep that name throughout.
3. **Active voice.** Name the actor, the verb and the target: "`Coordinator` calls `SubscriptionProxy.acquire()`".
4. **Explicit epistemic and causal links.** Write "because", "so", "the test shows" or "unverified" where the evidence supports them. Keep project domain terms and natural spoken flow. Open with the content itself, in place of framing labels such as "TL;DR", "At its core" or "The key insight".

The reply is the explanation itself, in place of a report about what you explained.
