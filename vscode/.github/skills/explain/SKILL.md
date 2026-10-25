---
name: explain
description: Explain completed work, how a subsystem works, or why a project decision exists. Use when the user asks what changed, how something works, why it was built that way, or to catch them up.
argument-hint: '[code, change, decision, or question]'
---

# Explain

Build an explanation the reader can check against the project. Distinguish current behavior, recorded intent, and conclusions the evidence cannot establish.

## Resolve the subject

Use the question after `/explain`, an attached file, the current editor selection, or the work just completed. Ask with the question tool when these leave several plausible subjects.

Keep investigation read-only. Create a visual artifact when requested, but change project files only with the user's approval.

## Start with a short answer

Read the code, diff, decision record, or check result needed for this question. Reuse current evidence already in the conversation. Refresh it when the checkout changed or the evidence is incomplete.

Unless the user requests depth or a medium up front, answer in two or three sentences:

1. State the outcome or define the subject. Link the code or artifact that establishes it.
2. Describe the concrete mechanism, or cite the record that states the reason.
3. Separate what the evidence verifies from assumptions and unobserved outcomes. A passing test does not establish a production or scientific result.

Offer a subject-specific way to go deeper through the available question tool, then stop. Offer only media the environment supports, such as a step-by-step walkthrough, Mermaid diagrams, or a self-contained HTML explainer.

Done when the answer's factual claims have source anchors and its evidence boundary is explicit. Say what remains unknown, or why the cited evidence settles the question.

## Go deeper on request

When the user requests detail or a medium, load each reference that matches the question. A teaching request can need several lenses.

| Question | Reference |
| --- | --- |
| What changed or what did the agent do? | [Work and changes](references/what.md) |
| How does the code, workflow, or rule operate? | [Mechanism and structure](references/how.md) |
| Why does the implementation or decision exist? | [Rationale and history](references/why.md) |
| Can you teach this with diagrams or an interactive example? | [Visual explanations](references/visuals.md) |

## Write for VS Code

- Link workspace files with Markdown links to their absolute paths. Use forward slashes in link targets and append `:line` for a source location.
- Keep repository links relative inside any document you save. Cite decisions, commits, and review records where they establish a claim.
- Write short, active sentences with one claim each. Use the same project name for a concept throughout.
- Mark inference and uncertainty where they occur. Keep domain terms the reader needs, and explain unfamiliar ones.
- Apply `unslop` to the explanation. Deliver the explanation itself rather than a report about producing it.
