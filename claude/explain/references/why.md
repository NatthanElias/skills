# Rationale and history

Use this lens for questions about implementation choices, constraints, and project decisions. [Explain](../SKILL.md) owns the response length and writing rules.

## Find the recorded reason

Read the project's instructions to locate its authoritative records. Search the sources that apply, and track the paths and search terms:

1. Constraint records under `.specs/constraints/`, or the decision log the project's instructions name. A record that exists is in force; follow `replaces` bullets and `git log --all -- <record>` for superseded ones before describing a reason as current.
2. Feature plans, checks, verification reports, architecture records, lessons, and research notes.
3. Git history. Use `git --no-pager log --follow -- <file>`, `git --no-pager log -S '<literal>' -- <file>`, and `git --no-pager blame -L <start>,<end> -- <file>`. Read commit bodies, not only subjects.
4. Accessible pull requests, issues, and review discussions.
5. Primary sources named by the project for research or study-design decisions.

Trace earlier decisions when the latest change does not explain the current shape. Record inaccessible sources as gaps rather than inferring their contents.

## Match certainty to evidence

| Evidence | How to phrase the claim |
| --- | --- |
| A source states the reason directly | State the reason and cite the record. |
| Several independent clues support a conclusion | Say the evidence points to it, and cite those clues. |
| The code and context suggest an interpretation | Label it as inferred and state the premises. |
| Thin evidence leaves several plausible accounts | Present the possibilities as speculation. |
| The search finds no stated reason | Name the sources and terms searched, and leave the reason unknown. |

Code establishes behavior, not its author's intention. Reserve statements such as "was designed to" for recorded intent. Attribute decisions to the author the record names.

Preserve uncertainty when simplifying prose. A consistent pattern can result from copying, and silence in a record does not prove nobody considered a concern. Test a rationale proposed in the question as a hypothesis.

When sources disagree, show their claims and citations without choosing the user's intent. For an explanation that precedes a change, finish with what to preserve, what may change, what to avoid, and the remaining risks.

Done when every intent claim has supporting evidence or an explicit uncertainty label, and every unresolved reason includes the search that left it open.
