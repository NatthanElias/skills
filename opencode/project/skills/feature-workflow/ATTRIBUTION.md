# Attribution

Parts of this skill adapt **tlc-spec-lean** version 3.2.0 by Tech Leads Club (github.com/tech-leads-club), licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). `tlc-spec-lean` derives from `tlc-spec-driven` 3.3.0 (Felipe Rodrigues), `tlc-plan`, and `tlc-implement`.

## What was adapted from tlc-spec-lean 3.2.0

| Here | From tlc-spec-lean 3.2.0 | Adaptation |
| --- | --- | --- |
| `SKILL.md` | `SKILL.md` | Keeps the 3-phase flow (Plan → Build → Review), verbatim `request.md`, inline compaction state lines, and small-change bypass. Adds `@orchestrate` cross-model delegation (diff-sized packets), sharpened semantic-cascade small-change rule, `.specs/constraints/` integration, upstream ticket/requirement ID preservation, sensitive-data guard, and multi-repo support. |
| `references/plan.md` | `references/plan.md` | Keeps unified `## Shape` with synced Mermaid diagrams, `Changes underneath`, concrete examples under criteria, gesture-per-control, binding captures (`.png` + `.aria.yml`), and verbatim approval line. Adds `Consumers` column (production callers + test fixtures/doubles/untyped files), optional `Repo` column with expand-migrate-contract slices for multi-repo contracts, `Reverse by` column in `Landing`, baseline check line, >50-file split guard, and greenfield walking-skeleton flow. |
| `references/build.md` | `references/build.md` | Keeps direct main-session slice-by-slice vertical commits (S1 tracer bullet first), browser check at capture size, and surgical diffs. Adds characterization-first legacy testing, 6 evidence-backed anti-tautology/PCI test patterns, `comments.md` reference, and `**Gates:**` recording on the final clean commit. |
| `references/review.md` | `references/review.md` | Keeps fresh-subagent review against verbatim `request.md`, `plan.md`, and `captures/`. Adds reference-search check for missing consumers/fixtures, doubt-driven focused scratch fault checking (no fixed quota), clean-tree builder gate reuse, compact PR-ready Audit Header, PCI human-review boundary note, and up to 2 targeted fresh re-checks (3 total review rounds before escalating to the user). |
| `scripts/validate_plan.py`, `scripts/lean_config.py` | `scripts/validate_plan.py`, `scripts/lean_config.py` | Adapted to check `.specs/constraints/` slugs (or explicit user approval quotes) instead of `.specs/STATE.md` `AD-NNN` rows in `## Differences from the source`, plus optional `Consumers` and `Reverse by` table validation. |
| `scripts/check_commit.py` | `scripts/check_commit.py` | Keeps Conventional Commits validation, AI-trailer rejection (`--allow-trailers`), untracked file warnings, owed workflow next-steps, and Windows UTF-8 output. Adds a staged-`.specs/features/` guard so git-ignored feature folders are never committed. |
| `scripts/selftest.py`, `scripts/fixtures/plan.md` | `scripts/selftest.py`, `scripts/fixtures/plan.md` | Rewritten to cover `validate_plan.py`, `check_commit.py`, `constraints.py`, and `resume_note.py`. |

## Ideas from harness-toolkit

The constraint records credit ideas only from **harness-toolkit** by Tech Leads Club (github.com/tech-leads-club), licensed under the Elastic License 2.0. No text or code was copied.

| Here | Idea from harness-toolkit |
| --- | --- |
| `references/constraints.md`, `scripts/constraints.py` | One file per record, four fixed headings, citing a record by link, and a gate that checks each record's shape. |
