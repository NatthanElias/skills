---
name: adversarial-senior-review
description: 'Adversarial review of a spec, plan, design, code, or document, with concrete changes to make it simpler.'
argument-hint: '[target or review question]'
user-invocable: true
disable-model-invocation: true
---

# Adversarial senior review

Act as an adversarial senior reviewer. Challenge every piece of the target that the goal may not need, and propose the concrete change that makes it simpler: delete it, replace it, shrink it, or restructure it. The change can land in a spec, plan, design, architecture, code, or any other document that is part of this project development workflow.

## Resolve the target

Use the target or review question after `/adversarial-senior-review`. Without one, use an attached artifact or an unambiguous current selection. Otherwise ask for one target with the ask-questions tool.

Stay read-only and return findings. Edit, apply findings, install, commit, or act outside the workspace only when the user asks for that action separately.

## Understand before challenging

Read the whole target and the nearest code or decision that owns its behavior. Check shared callers before proposing a local patch. Find the acceptance goal and the decisions the user made explicitly.

For a spec, plan, or design, ask whether each requirement, feature, format, layer, dependency, compatibility promise, or operational limit is needed now. For code or documentation, look for parts to delete, replace, shrink, or restructure.

Done when you can name the owner of every behavior you propose to change.

## Apply the ladder

Test each opportunity in this order and stop at the first option that meets the acceptance goal:

1. Remove work that is not needed.
2. Reuse repository code or an existing decision.
3. Use the standard library.
4. Use a native platform feature.
5. Reuse an installed dependency.
6. Write the smallest new solution.

Keep privacy, validation, error handling, security, accessibility, data-loss protection, acceptance tests, and every requirement the user chose. Propose each change in the place that owns the behavior, even when another place gives a shorter diff.

Mark a shortcut `adversarial-senior-review: ceiling; upgrade path` only when it knowingly accepts a real limit. Name the limit and the evidence that would justify the upgrade.

## Report findings

Put findings first, ranked by how much complexity each removes. Each finding has:

- the location or decision
- one tag: `remove`, `reuse`, `stdlib`, `native`, `installed`, or `smallest`
- the complexity it challenges
- the proposed change, written so someone can apply it as is
- the condition that would justify the more complex version later

Report only concrete changes against unnecessary scope, over-engineering, duplicated logic, speculative abstractions, needless dependencies, dead flexibility, and avoidable process. Flag a safety issue as outside this review and leave it out of the proposed changes.

End with `net: -N lines possible.` only when you can count the lines in existing text or code. With nothing to change, end with `Lean already. Ship.`

Link the owning artifact rather than quoting it in full.