#!/usr/bin/env python3
r"""
check_commit.py - deterministic commit message check, staged feature guard, and owed next steps.

Adapted from tlc-spec-lean 3.2.0 (CC-BY-4.0). Pure standard library, zero dependencies.

What it checks:
  ERROR  - header does not match Conventional Commits 1.0.0 (`type(scope)!: description`)
  ERROR  - type is not one of the allowed Conventional Commits types
  ERROR  - description is empty, starts uppercase, or ends with a period
  ERROR  - an agent trailer (Co-Authored-By, Made-with); pass --allow-trailers when required
  ERROR  - any staged change or deletion under `.specs/features/` (handles non-ASCII / C-quoted paths)
  WARN   - header longer than 72 characters

After a passing message it prints what the run still owes (compaction reminder):
  - untracked files outside .specs/
  - per active feature (plan.md or small-change request.md): next owed step verified against review.md.

Usage:
  python3 .github/skills/feature-workflow/scripts/check_commit.py --message "feat(auth): add check (S1, criteria 1-2)" [--root DIR]
  python3 .github/skills/feature-workflow/scripts/check_commit.py <msgfile>
  echo "fix(cart): prevent negative quantity" | python3 .github/skills/feature-workflow/scripts/check_commit.py

Exit codes: 0 pass, 1 violation, 2 usage error.
"""

import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_config import parse_header_state, parse_review_state, recheck_pass_error

TYPES = ["feat", "fix", "refactor", "docs", "test", "style", "perf", "build", "ci", "chore"]
HEADER_RE = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?: (?P<desc>.+)$")
TRAILER_RE = re.compile(r"^\s*(co-authored-by|made-with)\s*:", re.IGNORECASE | re.MULTILINE)


def read_message(args):
    if args.message is not None:
        return args.message
    if args.msgfile:
        if os.path.isfile(args.msgfile):
            with open(args.msgfile, "r", encoding="utf-8") as f:
                return f.read()
        return args.msgfile
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def check(message, allow_trailers=False):
    errors, warnings = [], []
    lines = [ln for ln in message.splitlines() if not ln.lstrip().startswith("#")]
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return (["empty commit message"], warnings)

    header = lines[0].rstrip()
    if len(header) > 72:
        warnings.append(f"header is {len(header)} chars (>72): {header[:60]}...")

    m = HEADER_RE.match(header)
    if not m:
        errors.append(f"header does not match 'type(scope): description': {header!r}")
        return (errors, warnings)

    ctype, desc = m.group("type"), m.group("desc")
    if ctype not in TYPES:
        errors.append(f"type '{ctype}' is not one of: {', '.join(TYPES)}")
    if not desc.strip():
        errors.append("description is empty")
    else:
        if desc[:1].isupper():
            errors.append(f"description should start lowercase: '{desc[:30]}'")
        if desc.rstrip().endswith("."):
            errors.append("description should not end with a period")

    body = "\n".join(lines[1:])
    trailer = TRAILER_RE.search(body)
    if trailer and not allow_trailers:
        errors.append(
            f"agent trailer '{trailer.group(1)}:' - remove it, or pass --allow-trailers "
            "when the repo asks for one"
        )
    return (errors, warnings)


def staged_feature_files(root):
    """Return (staged_paths, git_error) under .specs/features/ using NUL-delimited raw paths."""
    try:
        inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ([], None)
    if inside.returncode != 0 or inside.stdout.strip().lower() != "true":
        return ([], None)
    try:
        proc = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--no-renames", "-z", "--", ".specs/features/"],
            cwd=root,
            capture_output=True,
        )
    except OSError as exc:
        return ([], f"could not inspect staged index: {exc}")
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip() or f"exit {proc.returncode}"
        return ([], f"git diff --cached failed: {err}")
    paths = [p.decode("utf-8", errors="replace") for p in proc.stdout.split(b"\0") if p]
    return (paths, None)


def untracked(root):
    """Untracked, unignored paths outside .specs/ - what no commit will carry. None without git."""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    paths = [ln[3:].strip().strip('"') for ln in proc.stdout.splitlines() if ln.startswith("?? ")]
    return [p for p in paths if not (p == ".specs/" or p.startswith(".specs/"))]


def _raw_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def next_steps(root):
    """(feature, what follows) for each active feature whose build/review run is in progress."""
    base = os.path.join(root, ".specs", "features")
    if not os.path.isdir(base):
        return []
    out = []
    for name in sorted(os.listdir(base)):
        fdir = os.path.join(base, name)
        if not os.path.isdir(fdir):
            continue
        if os.path.isfile(os.path.join(fdir, "checks.md")) or os.path.isdir(os.path.join(fdir, "execution")):
            continue
        plan = os.path.join(fdir, "plan.md")
        request = os.path.join(fdir, "request.md")
        review = os.path.join(fdir, "review.md")

        if os.path.isfile(plan):
            st = parse_header_state(_raw_lines(plan))
            where = "plan.md"
            if not st["has_any_state"] and not os.path.isfile(request):
                continue  # legacy pre-3.2 plan-only folder
        elif os.path.isfile(request):
            st = parse_header_state(_raw_lines(request))
            where = "request.md"
            if not st["small_change"]:
                continue  # planning in progress, no plan.md yet
        else:
            continue

        if not st["approved"]:
            if st["approved_malformed"]:
                out.append(
                    (
                        name,
                        f"{where} has an `**Approved**` line without a valid ISO date and verbatim "
                        "`user: \"<their words>\"` quote - do not build until explicit user approval is recorded",
                    )
                )
            continue

        if st["review_skipped"]:
            continue

        rev = parse_review_state(review)
        if not st["review_sent"]:
            out.append(
                (
                    name,
                    f"after its last build commit, record per-command `**Gates:**` in {where} and send the "
                    "fresh review (references/review.md)",
                )
            )
        elif not rev["exists"]:
            out.append(
                (
                    name,
                    f"review was sent at {st['review_sent']}; wait if live, or re-dispatch if it failed",
                )
            )
        elif st["fix_round"] == 0:
            out.append(
                (
                    name,
                    f"run the fix pass after review.md, commit, run gates on HEAD, and record `**Fix pass:** done` in {where}",
                )
            )
        elif st["recheck_closed"] == "not needed":
            if rev["round1_verdict"] != "PASS" or rev["recheck_count"] > 0:
                out.append(
                    (
                        name,
                        f"{where} says `**Re-check:** not needed` but review.md Verdict is not PASS - "
                        "dispatch the Round 2 targeted re-check instead",
                    )
                )
        elif st["recheck_closed"] == "pass":
            err = recheck_pass_error(st, rev)
            if err:
                out.append((name, f"{where} says `**Re-check:** PASS` but {err}"))
        elif st["recheck_escalated"]:
            out.append((name, "Round 3 targeted re-check still has OPEN blockers - report them first and escalate to the user (no 4th review round)"))
        elif rev["recheck_count"] > 2 or any(r["round"] is not None and r["round"] >= 4 for r in rev["rechecks"]):
            out.append((name, "review.md exceeds the 3-round review cap - record `**Re-check:** open - escalated` and escalate to the user (no 4th review round)"))
        elif rev["recheck_count"] == 2:
            r3 = rev["rechecks"][1]
            if r3["verdict"] == "OPEN":
                out.append((name, f"Round 3 targeted re-check returned OPEN in review.md - record `**Re-check:** open - escalated` in {where} and escalate to the user (no 4th review round)"))
            elif r3["verdict"] == "PASS":
                if st["fix_round"] < 2:
                    out.append((name, f"Round 3 re-check returned PASS in review.md, but Fix pass 2 (`**Fix pass:** round 2 done`) is not recorded in {where}"))
                else:
                    out.append((name, f"Round 3 re-check returned PASS; record `**Re-check:** PASS` in {where}"))
            else:
                out.append((name, f"Round 3 `## Re-check` in review.md is missing its verdict; record `**Re-check:** PASS` or `open - escalated` in {where} matching review.md"))
        elif st["recheck_sent_round"] == 3:
            out.append(
                (
                    name,
                    f"Round 3 re-check was sent at {st['recheck_sent']}; wait for `## Re-check (Round 3)` in review.md "
                    "(or re-dispatch if it failed)",
                )
            )
        elif rev["recheck_count"] == 1:
            r2 = rev["rechecks"][0]
            if r2["round"] not in (None, 2):
                out.append((name, f"review.md has Round {r2['round']} re-check without Round 2; fix review.md sequence"))
            elif r2["verdict"] == "PASS":
                out.append((name, f"Round 2 re-check returned PASS; record `**Re-check:** PASS` in {where}"))
            elif r2["verdict"] == "OPEN":
                if st["fix_round"] < 2:
                    out.append(
                        (
                            name,
                            f"Round 2 re-check returned OPEN; run Fix pass 2, commit, run gates on HEAD, and record "
                            f"`**Fix pass:** round 2 done` in {where}",
                        )
                    )
                else:
                    out.append(
                        (
                            name,
                            f"Fix pass 2 is done; record `**Re-check:** round 3 sent at <hash>` in {where} and dispatch "
                            "the Round 3 (final) targeted re-check",
                        )
                    )
            else:
                out.append((name, f"record `**Re-check:** PASS` or `round 2 open` in {where} matching review.md"))
        elif st["recheck_round2_open"]:
            if st["fix_round"] < 2:
                out.append(
                    (
                        name,
                        f"Round 2 re-check is OPEN; run Fix pass 2, commit, run gates on HEAD, and record "
                        f"`**Fix pass:** round 2 done` in {where}",
                    )
                )
            else:
                out.append(
                    (
                        name,
                        f"Fix pass 2 is done; record `**Re-check:** round 3 sent at <hash>` in {where} and dispatch "
                        "the Round 3 (final) targeted re-check",
                    )
                )
        elif st["recheck_sent_round"] == 2:
            out.append(
                (
                    name,
                    f"Round 2 re-check was sent at {st['recheck_sent']}; wait for `## Re-check` in review.md "
                    "(or re-dispatch if it failed)",
                )
            )
        else:
            out.append(
                (
                    name,
                    f"if Round 1 had blockers, record `**Re-check:** sent at <hash>` in {where} and dispatch the "
                    "Round 2 targeted re-check; if Round 1 passed, record `**Re-check:** not needed - Round 1 PASS`",
                )
            )
    return out


def main(argv=None):
    p = argparse.ArgumentParser(prog="check_commit.py", description="Validate a Conventional Commits message.")
    p.add_argument(
        "msgfile",
        nargs="?",
        default=None,
        help="a commit message file, or the message itself",
    )
    p.add_argument("--message", default=None, help="the commit message as a string")
    p.add_argument("--root", default=".", help="project root that contains .specs/ (default: current dir)")
    p.add_argument(
        "--allow-trailers",
        action="store_true",
        help="accept a Co-Authored-By or Made-with trailer when the repo asks for one",
    )
    args = p.parse_args(argv)

    message = read_message(args)
    if not message.strip():
        print("check_commit: no message provided (pass --message, a file, or pipe via stdin).", file=sys.stderr)
        return 2

    errors, warnings = check(message, args.allow_trailers)
    staged_feats, idx_err = staged_feature_files(args.root)
    if idx_err:
        errors.append(idx_err)
    elif staged_feats:
        shown = ", ".join(staged_feats[:5])
        errors.append(
            f"staged changes or deletions under .specs/features/ must stay out of commits: {shown}"
        )

    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    if errors:
        print("\ncheck_commit: FAIL - see https://www.conventionalcommits.org/en/v1.0.0/")
        return 1
    print("check_commit: OK")

    loose = untracked(args.root)
    if loose:
        shown = ", ".join(loose[:8]) + (f" and {len(loose) - 8} more" if len(loose) > 8 else "")
        print(
            f"\nUntracked, in no commit: {shown}. Leave a clean tree: commit what belongs "
            "to the work, delete tool artifacts (browser snapshots, test output), or ignore them."
        )
    for name, step in next_steps(args.root):
        print(f"\n`{name}`: {step}.")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
