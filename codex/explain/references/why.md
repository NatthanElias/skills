# Why: rationale and history

Read this reference when explaining why code, a constraint, an architecture or a project decision exists. Style rules live in [../SKILL.md](../SKILL.md).

Code shows what it does. The reason it exists lives in records, and records are incomplete. Treat every explanation of intent as a claim that needs a source.

## Search the record first

Search the whole project record before inferring intent. Note each source you searched and the terms you used.

1. `.specs/STATE.md`, the `AD-NNN` decision table. Read the status column. A superseded decision is history, and the decision that superseded it is the current reason.
2. Feature folders under `.specs/features/`. Read `plan.md` `Landing` rows (one-way doors with their rejected alternatives), checks, verification reports and phase reports.
3. `.specs/LESSONS.md` and the research notes under `docs/`.
4. Git history. Use `git log --follow -- <file>`, `git log -S '<literal>'`, and `git blame -L <start>,<end> <file>`, then read the full commit bodies.
5. PRs, issues and review threads, when the repository has a remote.
6. The research, proposal and primary-paper folders listed in `AGENTS.md`, for study-design questions.

Trace past the latest commit. The current shape often comes from several earlier decisions.

## Confidence tiers

Place every claim in one tier. The tier sets its phrasing.

1. **Direct.** An author wrote the reason, in a decision row, commit body, comment, plan or review. Write "This exists because X," with the citation beside it.
2. **Supported.** Several indirect sources point to one conclusion. Write "The evidence points to X," and cite each source.
3. **Inferred.** A reasonable reading that no record states. Write "Given A and B, X seems likely because C."
4. **Speculative.** A plausible guess on thin evidence, where other explanations fit equally well. Write "One possibility is X. No record supports it." List it beside the alternatives.
5. **Unknown.** You searched and found nothing. Write "I searched A, B and C for D and found no stated reason." This is a valid and useful answer.

## Phrasing

- Confidence words need a Direct or Supported citation beside them. These include "because", "the reason is", "was designed to", "fixes", and "Nate decided".
- Hedges mark interpretation. Use "appears", "likely", "suggests" and "is consistent with" for Inferred claims.
- State evidence plainly, without "obviously", "clearly", "of course" or "just".
- Attribute each decision to its recorded author. Morfe records separate Nate's decisions, Root's autonomous decisions under AD-027, and reviewer provenance. Keep that attribution.

## Rationalization and sycophancy

- Code is not evidence of its own intent.
- A tidy rationale fitted onto messy history is Inferred or Speculative. Reclassify it.
- A consistent pattern may be copy-paste.
- A missing mention is a gap in the record. It does not show the concern was absent.
- When sources contradict, present both with citations and let the user judge.
- Treat a guess embedded in the user's question ("I assume it's for performance?") as one hypothesis among others. Test it against the record. Confirm it with citations, or say what the evidence supports instead.

## Before replying

- Every claim has a citation, or sits in Inferred or Speculative.
- Each claim's phrasing matches its tier.
- Each gap names the question, the sources searched, the search terms and the result. A reply with no gaps needs a second look.
- When the question precedes a change, end with constraints for the change, grouped as Preserve, Change, Avoid and Risk.

## Done when

Every claim about intent carries a tier and a citation or a recorded search, and the reply names what remains unknown.
