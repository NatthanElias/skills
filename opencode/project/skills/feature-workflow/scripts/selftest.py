#!/usr/bin/env python3
"""
selftest.py - deterministic test suite for feature-workflow scripts.

Exercises validate_plan.py, check_commit.py, constraints.py, and resume_note.py
against the fixture plan and targeted negative cases (0 failed).

Usage:
  python3 .opencode/skills/feature-workflow/scripts/selftest.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
FIXTURE_PLAN = SCRIPTS / "fixtures" / "plan.md"


def run_py(script, args, cwd=None, input_text=None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=cwd,
        input=input_text,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def git(cwd, *args):
    res = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    assert res.returncode == 0, f"git {args} failed: {res.stderr}"
    return res.stdout.strip()


def make_repo(td):
    root = Path(td)
    git(root, "init", "-q")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.com")
    (root / "README.md").write_text("# test\n", encoding="utf-8")
    git(root, "add", "README.md")
    git(root, "commit", "-q", "-m", "chore: initial commit")
    return root


def run_tests():
    failures = []

    def expect(name, cond, detail=""):
        if not cond:
            failures.append(f"{name}: {detail}")

    # 1. validate_plan.py positive & negative checks.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fdir = root / ".specs" / "features" / "dunning"
        fdir.mkdir(parents=True)
        shutil.copy(FIXTURE_PLAN, fdir / "plan.md")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root), "--strict"])
        expect("fixture-plan-passes", res.returncode == 0, res.stdout + res.stderr)

        base_plan = (fdir / "plan.md").read_text(encoding="utf-8")

        # Empty ## Criteria (and criteria only inside tilde or 5-backtick fences) fail in default mode.
        head, tail = base_plan.split("## Criteria", 1)
        crit_body, rest = tail.split("## Out of scope", 1)
        no_criteria = head + "## Criteria\n\n### S1: Empty\n\n**Acceptance Criteria**\n\n## Out of scope" + rest
        (fdir / "plan.md").write_text(no_criteria, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("empty-criteria-fails-default", res.returncode == 1 and "no numbered acceptance criteria" in res.stdout, res.stdout)

        fenced_only = (
            head
            + "## Criteria\n\n### S1: Fenced\n\n~~~\n1. WHEN x THEN the system SHALL y\n~~~\n\n"
            + "`````markdown\n```\ninner\n```\n2. WHEN a THEN the system SHALL b\n`````\n\n## Out of scope"
            + rest
        )
        (fdir / "plan.md").write_text(fenced_only, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("fenced-only-criteria-fails-default", res.returncode == 1 and "no numbered acceptance criteria" in res.stdout, res.stdout)

        # Criterion without SHALL fails, even after two blank lines.
        bad = base_plan.replace(
            "4. The system SHALL never move a subscription directly from `Suspended` to `Trialing`",
            "\n\n4. The system never moves a subscription directly from `Suspended` to `Trialing`",
        )
        (fdir / "plan.md").write_text(bad, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("criterion-after-two-blanks-checked", res.returncode == 1 and "no SHALL" in res.stdout, res.stdout)

        # Module on path missing from Mermaid drawing fails.
        bad = (
            base_plan.replace("participant M as Billing::StatusMap\n", "")
            .replace("I->>M: 3. provider status\n", "")
            .replace("M->>S: 4. local status\n", "")
        )
        (fdir / "plan.md").write_text(bad, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("drawing-mismatch-fails", res.returncode == 1 and "Billing::StatusMap" in res.stdout, res.stdout)

        # Escaped pipe inside Surface cell does not shift Status/Who columns; non-HTTP event row passes without HTTP code.
        surf_ok = base_plan.replace(
            "| `POST /webhooks/provider` | provider envelope | `{}` · `{error}` | `200`, `401`, `409`, `422` | provider with valid signature; others get `401` |",
            "| `POST /webhooks/provider` | `a \\| b` | `{}` · `{error}` | `200`, `401`, `409`, `422` | provider with valid signature; others get `401` |\n"
            "| `EVENT billing.suspended` | `subscription_id` | JSON payload | emitted on transition; dead-letter on parse error | internal billing workers |",
        )
        (fdir / "plan.md").write_text(surf_ok, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root), "--strict"])
        expect("escaped-pipe-and-event-surface-pass", res.returncode == 0, res.stdout + res.stderr)

        # Landing truncated row (<4 cols) or missing Reverse by column fails.
        bad = base_plan.replace(
            "| `POST /webhooks/provider` response codes | `200` accepted/replayed, `409` concurrent duplicate, `422` missing subscription id | `204` - provider retries responses without a body | revert route handler before switching provider webhook endpoint |",
            "| `POST /webhooks/provider` response codes | `200`/`409`/`422` |",
        )
        (fdir / "plan.md").write_text(bad, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("truncated-landing-row-fails", res.returncode == 1 and "Reverse by" in res.stdout, res.stdout)

        bad = base_plan.replace("| Reverse by |", "| Notes |")
        (fdir / "plan.md").write_text(bad, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("missing-reverse-by-column-errors", res.returncode == 1 and "no `Reverse by` column" in res.stdout, res.stdout)

        # Changes underneath heading with no table and no `None - <reason>` fails.
        bad = base_plan.replace(
            "**Changes underneath**\n\n"
            "| Front | What changes | Consumers |\n"
            "| --- | --- | --- |\n"
            "| baseline | `a1b2c3d`: `npm test` exit 0 (214 passed, 0 failed, 0 skipped) | n/a |\n"
            "| domain | `Active` meant \"has a subscription row\", now means \"has a row and last charge succeeded\" | `AccessPolicy#grant?`, `AdminSubscriptionsController#index`, `test/fixtures/subscriptions.json` |\n"
            "| stored data | backfill existing rows to `active`; dedup 40k delivery rows before unique index | `AccessPolicy`, `AdminSubscriptionsController` |\n"
            "| contracts | `subscriptions.status` enum adds `suspended` (expand-only) | `AccessPolicy#grant?`, `test/support/subscription-factory.ts` |",
            "**Changes underneath**\n\nTBD",
        )
        (fdir / "plan.md").write_text(bad, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("changes-underneath-no-table-fails", res.returncode == 1 and "has no table" in res.stdout, res.stdout)

        # Repo column first with blank Consumers on contracts row fails.
        repo_first = base_plan.replace(
            "| Front | What changes | Consumers |\n"
            "| --- | --- | --- |\n"
            "| baseline | `a1b2c3d`: `npm test` exit 0 (214 passed, 0 failed, 0 skipped) | n/a |\n"
            "| domain | `Active` meant \"has a subscription row\", now means \"has a row and last charge succeeded\" | `AccessPolicy#grant?`, `AdminSubscriptionsController#index`, `test/fixtures/subscriptions.json` |\n"
            "| stored data | backfill existing rows to `active`; dedup 40k delivery rows before unique index | `AccessPolicy`, `AdminSubscriptionsController` |\n"
            "| contracts | `subscriptions.status` enum adds `suspended` (expand-only) | `AccessPolicy#grant?`, `test/support/subscription-factory.ts` |",
            "| Repo | Front | What changes | Consumers |\n"
            "| --- | --- | --- | --- |\n"
            "| billing-api | baseline | `a1b2c3d`: `npm test` exit 0 | n/a |\n"
            "| billing-api | contracts | `subscriptions.status` enum adds `suspended` |  |",
        )
        (fdir / "plan.md").write_text(repo_first, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("repo-first-blank-consumers-fails", res.returncode == 1 and "Consumers is blank" in res.stdout, res.stdout)

        # Binding backend ticket does NOT trigger visual Differences requirement.
        ticket_binding = base_plan.replace(
            "- TLC-412 - suspension rule and 11-day evidence",
            "- TLC-412 - binding - suspension rule and 11-day evidence",
        )
        (fdir / "plan.md").write_text(ticket_binding, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root), "--strict"])
        expect("binding-backend-ticket-needs-no-visual-diff", res.returncode == 0, res.stdout + res.stderr)

        # Per-source binding captures: settings.dark.png does NOT satisfy settings.light.png; non-binding inspiration allowed.
        cdir = fdir / "captures"
        cdir.mkdir()
        (cdir / "settings.dark.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (cdir / "settings.light.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (cdir / "mood.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        cons_dir = root / ".specs" / "constraints"
        cons_dir.mkdir(parents=True)
        (cons_dir / "keep-old-badge.md").write_text("# Keep old badge\n", encoding="utf-8")
        (cons_dir / "money.md").write_text("# Money\n\n- **legacy-id**: AD-007\n", encoding="utf-8")

        missing_light = (
            base_plan.replace(
                "7. IF a delivery carries no valid provider signature THEN the system SHALL return `401` and persist nothing\n   - bad HMAC header → `401`, 0 new rows",
                "7. IF a delivery carries no valid provider signature THEN the system SHALL return `401` and persist nothing\n   - bad HMAC header → `401`, 0 new rows\n"
                "8. WHEN admin opens dark settings THEN the system SHALL show `captures/settings.dark.png`",
            ).replace(
                "## Sources",
                "## Differences from the source\n\n| Source shows | Product shows | Confirmed |\n| --- | --- | --- |\n"
                "| New badge | Old badge | y - keep-old-badge |\n"
                "| Decimal price | Cents | y - money |\n"
                "| Legacy label | Migrated label | y - AD-007 |\n"
                "| Extra button | Omitted | y - user: \"drop the button\" |\n\n## Sources",
            ).replace(
                "- provider webhook reference - 9 statuses and 5 event types",
                "- provider webhook reference - 9 statuses and 5 event types\n"
                "- ![dark](captures/settings.dark.png) - binding - dark mode\n"
                "- ![light](captures/settings.light.png) - binding - light mode\n"
                "- ![mood](captures/mood.png) - non-binding - user: \"just tone inspiration\" - tone",
            )
        )
        (fdir / "plan.md").write_text(missing_light, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root)])
        expect("dark-does-not-satisfy-light-capture", res.returncode == 1 and "settings.light.png" in res.stdout, res.stdout)

        with_both = missing_light.replace(
            "8. WHEN admin opens dark settings THEN the system SHALL show `captures/settings.dark.png`",
            "8. WHEN admin opens dark settings THEN the system SHALL show `captures/settings.dark.png`\n"
            "9. WHEN admin opens light settings THEN the system SHALL show `captures/settings.light.png`",
        )
        (fdir / "plan.md").write_text(with_both, encoding="utf-8")
        res = run_py("validate_plan.py", ["dunning", "--root", str(root), "--strict"])
        expect("per-source-captures-and-nonbinding-inspiration-pass", res.returncode == 0, res.stdout + res.stderr)

    # 2. check_commit.py: Conventional Commits (incl. feat!: without footer), non-ASCII staged guard, header-only state & verdict check.
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(td)
        res = run_py("check_commit.py", ["--message", "feat!: drop support for node 6", "--root", str(root)])
        expect("commit-bang-without-footer-valid", res.returncode == 0 and "OK" in res.stdout, res.stdout + res.stderr)

        res = run_py("check_commit.py", ["--message", "feat(billing): add rule\n\nCo-Authored-By: Bot <b@x>", "--root", str(root)])
        expect("commit-rejects-trailer", res.returncode == 1 and "agent trailer" in res.stdout, res.stdout)

        # Fenced example & ## Request text cannot spoof approval/small-change/review state.
        pdir = root / ".specs" / "features" / "spoof-test"
        pdir.mkdir(parents=True)
        (pdir / "request.md").write_text(
            "## Request\n"
            "**Small change:** yes - quoted from docs\n"
            "**Approved**: 2026-11-21 - user: \"go\"\n"
            "**Review:** sent at abc1234\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "chore: unrelated", "--root", str(root)])
        expect("request-body-cannot-spoof-state", res.returncode == 0 and "spoof-test" not in res.stdout, res.stdout)

        # Invalid calendar date in Approved is rejected.
        fdir = root / ".specs" / "features" / "dunning"
        fdir.mkdir(parents=True)
        (fdir / "plan.md").write_text("# Dunning\n**Approved**: 2026-02-30 - user: \"go\"\n", encoding="utf-8")
        res = run_py("check_commit.py", ["--message", "feat(billing): slice 1", "--root", str(root)])
        expect("invalid-approval-date-rejected", res.returncode == 0 and "without a valid ISO date" in res.stdout, res.stdout)

        # Re-check: PASS cannot close a run whose review.md has no ## Re-check PASS verdict.
        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** done - fixed bug\n**Re-check:** PASS\n",
            encoding="utf-8",
        )
        (fdir / "review.md").write_text("# Review: dunning\n- **Verdict:** CHANGES_REQUIRED\n", encoding="utf-8")
        res = run_py("check_commit.py", ["--message", "chore: wrap up", "--root", str(root)])
        expect("stale-review-blocks-recheck-pass", res.returncode == 0 and "has no `## Re-check` section" in res.stdout, res.stdout)

        # Round 1 verdict in Audit Header is NOT overwritten by a tilde-fenced, tab-indented closing fence, or ## Blocking findings PASS.
        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** done - no changes needed\n**Re-check:** not needed - Round 1 PASS\n",
            encoding="utf-8",
        )
        (fdir / "review.md").write_text(
            "# Review: dunning\n- **Verdict:** CHANGES_REQUIRED\n"
            "~~~\n\t~~~\n- **Verdict:** PASS\n~~~\n\n"
            "## Blocking findings\n"
            "1. Example verdict line in findings:\n"
            "- **Verdict:** PASS\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "chore: wrap up", "--root", str(root)])
        expect("fenced-or-body-verdict-cannot-spoof-round1-pass", res.returncode == 0 and "Verdict is not PASS" in res.stdout, res.stdout)

        # Round 3 PASS without Round 2 or Fix pass 2 is rejected.
        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** done - fix 1\n**Re-check:** PASS\n",
            encoding="utf-8",
        )
        (fdir / "review.md").write_text(
            "# Review: dunning\n- **Verdict:** CHANGES_REQUIRED\n\n"
            "## Re-check (Round 3)\n- **Re-check verdict:** `PASS`\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "chore: wrap up", "--root", str(root)])
        expect("round3-without-round2-rejected", res.returncode == 0 and "without Round 2" in res.stdout, res.stdout)

        (fdir / "review.md").write_text(
            "# Review: dunning\n- **Verdict:** CHANGES_REQUIRED\n\n"
            "## Re-check (Round 2)\n- **Re-check verdict:** `OPEN`\n\n"
            "## Re-check (Round 3)\n- **Re-check verdict:** `PASS`\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "chore: wrap up", "--root", str(root)])
        expect("round3-without-fix-pass-2-rejected", res.returncode == 0 and "Fix pass 2" in res.stdout, res.stdout)

        # Round 4 PASS after Round 3 OPEN is rejected (3-round cap enforced).
        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** round 2 done - fix 2\n**Re-check:** PASS\n",
            encoding="utf-8",
        )
        (fdir / "review.md").write_text(
            "# Review: dunning\n- **Verdict:** CHANGES_REQUIRED\n\n"
            "## Re-check (Round 2)\n- **Re-check verdict:** `OPEN`\n\n"
            "## Re-check (Round 3)\n- **Re-check verdict:** `OPEN`\n\n"
            "## Re-check (Round 4)\n- **Re-check verdict:** `PASS`\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "chore: wrap up", "--root", str(root)])
        expect("round4-pass-rejected", res.returncode == 0 and "exceeds the 3-round review cap" in res.stdout, res.stdout)

        # Round 3 already OPEN with stale `round 2 open` header escalates instead of prompting another Round 3.
        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** round 2 done - fix 2\n**Re-check:** round 2 open\n",
            encoding="utf-8",
        )
        (fdir / "review.md").write_text(
            "# Review: dunning\n- **Verdict:** CHANGES_REQUIRED\n\n"
            "## Re-check (Round 2)\n- **Re-check verdict:** `OPEN`\n\n"
            "## Re-check (Round 3)\n- **Re-check verdict:** `OPEN`\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "fix(billing): stale", "--root", str(root)])
        expect("round3-open-overrides-stale-round2-header", res.returncode == 0 and "no 4th review round" in res.stdout, res.stdout)
        res = run_py("resume_note.py", ["--root", str(root)])
        expect("resume-round3-open-overrides-stale-round2-header", res.returncode == 0 and "Round 3 re-check OPEN" in res.stdout, res.stdout)

        # Round 2 OPEN allows Fix pass 2 -> Round 3 targeted re-check -> PASS closes; Round 3 OPEN escalates.
        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** done - fix 1\n**Re-check:** sent at def5678\n",
            encoding="utf-8",
        )
        (fdir / "review.md").write_text(
            "# Review: dunning\n- **Verdict:** CHANGES_REQUIRED\n\n"
            "## Re-check (Round 2)\n- **Re-check verdict:** `OPEN`\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "fix(billing): round 2", "--root", str(root)])
        expect("round2-open-prompts-fix-pass-2", res.returncode == 0 and "Fix pass 2" in res.stdout, res.stdout)

        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** round 2 done - fix 2\n**Re-check:** round 2 open\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "fix(billing): round 2", "--root", str(root)])
        expect("fix-pass-2-prompts-round3-recheck", res.returncode == 0 and "Round 3 (final) targeted re-check" in res.stdout, res.stdout)

        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** round 2 done - fix 2\n**Re-check:** open - escalated\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "chore: wrap up", "--root", str(root)])
        expect("round3-open-escalates-no-4th", res.returncode == 0 and "no 4th review round" in res.stdout, res.stdout)

        # With real Round 3 ## Re-check PASS (after Round 2 OPEN + Fix pass 2), reminders clear.
        (fdir / "plan.md").write_text(
            "# Dunning\n**Approved**: 2026-11-21 - user: \"go\"\n**Review:** sent at abc1234\n"
            "**Fix pass:** round 2 done - fix 2\n**Re-check:** PASS\n",
            encoding="utf-8",
        )
        (fdir / "review.md").write_text(
            "# Review: dunning\n- **Verdict:** CHANGES_REQUIRED\n\n"
            "## Re-check (Round 2)\n- **Re-check verdict:** `OPEN`\n\n"
            "## Re-check (Round 3)\n- **Re-check verdict:** `PASS`\n",
            encoding="utf-8",
        )
        res = run_py("check_commit.py", ["--message", "chore: wrap up", "--root", str(root)])
        expect("verified-round3-recheck-pass-clears-nag", res.returncode == 0 and "`dunning`" not in res.stdout, res.stdout)

        # Non-ASCII staged path under .specs/features/ (C-quoted by git) is caught!
        non_ascii = root / ".specs" / "features" / "probe" / "edição.md"
        non_ascii.parent.mkdir(parents=True)
        non_ascii.write_text("hi\n", encoding="utf-8")
        git(root, "add", "-f", str(non_ascii.relative_to(root)))
        res = run_py("check_commit.py", ["--message", "feat(billing): slice 1", "--root", str(root)])
        expect("commit-blocks-nonascii-staged-feature-file", res.returncode == 1 and ".specs/features/" in res.stdout, res.stdout)

    # 3. resume_note.py: ignores fenced examples & body text, handles review skipped & small-change approval.
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(td)
        fdir = root / ".specs" / "features" / "fenced"
        fdir.mkdir(parents=True)
        # Nested 5-backtick fence and tab-indented tilde fence cannot spoof approval.
        (fdir / "plan.md").write_text(
            "# Fenced\n\n`````markdown\n```text\ninner\n```\n**Approved**: 2026-11-21 - user: \"fake\"\n`````\n\n"
            "~~~\n\t~~~\n**Approved**: 2026-11-21 - user: \"tab-fake\"\n~~~\n\n## Problem\nx\n",
            encoding="utf-8",
        )
        (fdir / "request.md").write_text("## Request\nDo x.\n", encoding="utf-8")
        res = run_py("resume_note.py", ["--root", str(root)])
        expect("resume-ignores-nested-and-tab-fence-approval", res.returncode == 0 and "plan awaiting approval" in res.stdout, res.stdout)

        (fdir / "plan.md").write_text(
            "# Fenced\n\n**Plan review:** done - 2 fixed / 0 contested / 1 escalated\n\n## Problem\nx\n",
            encoding="utf-8",
        )
        res = run_py("resume_note.py", ["--root", str(root)])
        expect("resume-reports-plan-review-done", res.returncode == 0 and "plan awaiting approval (plan review done)" in res.stdout, res.stdout)

        (fdir / "plan.md").write_text(
            "# Fenced\n\n**Plan review:** done - 1 fixed / 0 contested / 0 escalated\n"
            "**Approved**: 2026-11-25 - user: \"Approve plan\" (ask_user)\n\n## Problem\nx\n",
            encoding="utf-8",
        )
        res = run_py("resume_note.py", ["--root", str(root)])
        expect("resume-accepts-ask-user-approval", res.returncode == 0 and "approved, build in progress" in res.stdout, res.stdout)

        sc_dir = root / ".specs" / "features" / "tiny-doc"
        sc_dir.mkdir(parents=True)
        (sc_dir / "request.md").write_text(
            "**Small change:** yes - 1 file\n"
            "**Approved**: 2026-11-21 - user: \"go\"\n"
            "**Review:** skipped - non-logic edit\n\n"
            "## Request\nFix typo.\n",
            encoding="utf-8",
        )
        res = run_py("resume_note.py", ["--root", str(root)])
        expect("resume-recognizes-review-skipped", res.returncode == 0 and "review skipped" in res.stdout, res.stdout)

        res = run_py("resume_note.py", ["--format", "vscode-hook"], input_text=json.dumps({"cwd": str(root), "source": "resume"}))
        parsed = json.loads(res.stdout) if res.returncode == 0 and res.stdout.strip() else {}
        hook_out = parsed.get("hookSpecificOutput", {})
        expect(
            "resume-vscode-hook-json",
            res.returncode == 0
            and "review skipped" in parsed.get("additionalContext", "")
            and hook_out.get("hookEventName") == "SessionStart"
            and "review skipped" in hook_out.get("additionalContext", ""),
            res.stdout,
        )

        res = run_py("resume_note.py", ["--format", "vscode-hook"], input_text=json.dumps({"cwd": str(root), "source": "new"}))
        expect("resume-vscode-hook-skips-new-session", res.returncode == 0 and json.loads(res.stdout) == {}, res.stdout)

        res = run_py("resume_note.py", ["--format", "vscode-hook"], input_text=json.dumps({"cwd": str(root), "source": "resume", "agentId": "sub-1"}))
        expect("resume-vscode-hook-skips-subagent", res.returncode == 0 and json.loads(res.stdout) == {}, res.stdout)

    with tempfile.TemporaryDirectory() as td:
        empty_root = make_repo(td)
        res = run_py("resume_note.py", ["--format", "vscode-hook"], input_text=json.dumps({"cwd": str(empty_root)}))
        expect("resume-vscode-hook-empty", res.returncode == 0 and json.loads(res.stdout) == {}, res.stdout)

    # 4. constraints.py: new, list, check.
    with tempfile.TemporaryDirectory() as td:
        root = make_repo(td)
        res = run_py(
            "constraints.py",
            [
                "new", "--root", str(root),
                "--slug", "money-in-cents",
                "--title", "Store money in integer cents",
                "--origin", "feature billing",
                "--scope", "billing",
                "--date", "2026-11-21",
            ],
        )
        expect("constraints-new", res.returncode == 0, res.stdout + res.stderr)
        rec = root / ".specs" / "constraints" / "money-in-cents.md"
        rec.write_text(
            "# Store money in integer cents\n\n"
            "- **origin**: feature billing\n"
            "- **scope**: billing\n"
            "- **date**: 2026-11-21\n\n"
            "## Decision\n\nStore amounts as integer cents.\n\n"
            "## Why\n\nAvoid float rounding drift.\n",
            encoding="utf-8",
        )
        res = run_py("constraints.py", ["check", "--root", str(root)])
        expect("constraints-check", res.returncode == 0, res.stdout + res.stderr)
        res = run_py("constraints.py", ["list", "--root", str(root), "--scope", "billing"])
        expect("constraints-list", res.returncode == 0 and "money-in-cents.md" in res.stdout, res.stdout)

    if failures:
        print("selftest: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("selftest: PASS (0 failed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
