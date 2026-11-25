#!/usr/bin/env python3
"""
resume_note.py - state where active feature work stands when a session resumes.

A session-start hook runs this on resume and after compaction. It prints facts
only: the newest active feature folder (reading the leading metadata block of
plan.md or request.md via lean_config.py and cross-checking review.md) and
current HEAD. Legacy feature folders (holding checks.md, execution/, or old
plan-only folders without request.md/inline state lines) are read-only history
and are never picked as the active feature. Prints nothing outside a Git
repository or when no active feature is found.

Usage:
  python3 .agents/skills/feature-workflow/scripts/resume_note.py [--root PATH]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_config import parse_header_state, parse_review_state, recheck_pass_error


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _classify_run(st, review: Path, prefix=""):
    if st["review_skipped"]:
        return f"{prefix}review skipped (non-logic edit), ready to report"
    rev = parse_review_state(str(review))
    if not st["review_sent"]:
        return f"{prefix}build in progress"
    if not rev["exists"]:
        return f"{prefix}review sent at {st['review_sent']} (wait or re-dispatch if failed)"
    if st["fix_round"] == 0:
        return f"{prefix}review.md present, fix pass pending"
    if st["recheck_closed"] == "not needed":
        if rev["round1_verdict"] == "PASS" and rev["recheck_count"] == 0:
            return f"{prefix}done, ready to report"
        return f"{prefix}re-check mismatch: review.md verdict is not PASS"
    if st["recheck_closed"] == "pass":
        err = recheck_pass_error(st, rev)
        if err is None:
            return f"{prefix}done, ready to report"
        return f"{prefix}re-check mismatch: {err}"
    if st["recheck_escalated"]:
        return f"{prefix}Round 3 re-check OPEN - escalate to user (no 4th review round)"
    if rev["recheck_count"] > 2 or any(r["round"] is not None and r["round"] >= 4 for r in rev["rechecks"]):
        return f"{prefix}review cap exceeded (max 3 rounds) - escalate to user"
    if rev["recheck_count"] == 2:
        r3 = rev["rechecks"][1]
        if r3["verdict"] == "OPEN":
            return f"{prefix}Round 3 re-check OPEN in review.md - record open - escalated and escalate to user"
        if r3["verdict"] == "PASS":
            if st["fix_round"] < 2:
                return f"{prefix}Round 3 PASS mismatch: Fix pass 2 not recorded"
            return f"{prefix}Round 3 re-check PASS in review.md, record status"
        return f"{prefix}Round 3 re-check returned in review.md, record status"
    if st["recheck_sent_round"] == 3:
        return f"{prefix}Round 3 re-check sent at {st['recheck_sent']} (wait or re-dispatch if failed)"
    if rev["recheck_count"] == 1:
        r2 = rev["rechecks"][0]
        if r2["round"] not in (None, 2):
            return f"{prefix}re-check mismatch: Round {r2['round']} without Round 2"
        if r2["verdict"] == "PASS":
            return f"{prefix}Round 2 re-check PASS in review.md, record status"
        if r2["verdict"] == "OPEN":
            if st["fix_round"] < 2:
                return f"{prefix}Round 2 re-check OPEN, fix pass 2 pending"
            return f"{prefix}fix pass 2 done, Round 3 re-check pending"
        return f"{prefix}Round 2 re-check returned in review.md, record status"
    if st["recheck_round2_open"]:
        if st["fix_round"] < 2:
            return f"{prefix}Round 2 re-check OPEN, fix pass 2 pending"
        return f"{prefix}fix pass 2 done, Round 3 re-check pending"
    if st["recheck_sent_round"] == 2:
        return f"{prefix}Round 2 re-check sent at {st['recheck_sent']} (wait or re-dispatch if failed)"
    return f"{prefix}fix pass done, Round 2 re-check pending"


def feature_state(fdir: Path):
    """Return ('active', mtime, ref_file, label), ('legacy',), or None."""
    plan = fdir / "plan.md"
    request = fdir / "request.md"
    review = fdir / "review.md"
    if (fdir / "checks.md").is_file() or (fdir / "execution").is_dir():
        return ("legacy",)

    if plan.is_file():
        st = parse_header_state(plan.read_text(encoding="utf-8", errors="replace").splitlines())
        if not request.is_file() and not st["has_any_state"]:
            return ("legacy",)
        if not st["approved"]:
            label = "plan awaiting approval"
        else:
            label = _classify_run(st, review, prefix="approved, ")
        mtime = max(p.stat().st_mtime for p in (plan, request, review) if p.is_file())
        return ("active", mtime, plan, label)

    if request.is_file():
        st = parse_header_state(request.read_text(encoding="utf-8", errors="replace").splitlines())
        if not st["small_change"]:
            return ("active", request.stat().st_mtime, request, "planning, no plan.md yet")
        if not st["approved"]:
            label = "small change awaiting approval"
        else:
            label = _classify_run(st, review, prefix="small change, ")
        mtime = max(p.stat().st_mtime for p in (request, review) if p.is_file())
        return ("active", mtime, request, label)

    return None


def note(root):
    top = git(root, "rev-parse", "--show-toplevel")
    if not top:
        return ""
    features_dir = Path(top) / ".specs" / "features"
    if not features_dir.is_dir():
        return ""

    active = []
    legacy_count = 0
    for fdir in sorted(features_dir.iterdir()):
        if not fdir.is_dir():
            continue
        st = feature_state(fdir)
        if st is None:
            continue
        if st[0] == "legacy":
            legacy_count += 1
        else:
            active.append((st[1], fdir.name, st[2], st[3]))
    if not active:
        return ""

    active.sort(key=lambda item: item[0], reverse=True)
    mtime, name, ref_file, label = active[0]
    changed = datetime.fromtimestamp(mtime).isoformat(timespec="minutes")
    head = git(top, "rev-parse", "--short=12", "HEAD")
    branch = git(top, "branch", "--show-current")
    where = (
        (f"HEAD is {head} on {branch}." if branch else f"HEAD is {head}, detached.")
        if head
        else f"{branch or 'HEAD'} has no commits yet."
    )
    extras = []
    if len(active) > 1:
        extras.append(f"{len(active) - 1} other active")
    if legacy_count:
        extras.append(f"{legacy_count} legacy")
    extra_note = f" ({', '.join(extras)} feature folders also exist.)" if extras else ""
    rel = ref_file.relative_to(Path(top)).as_posix()
    return (
        f"feature-workflow: newest active feature is `{name}` ({label}; {rel}, last changed {changed}). "
        f"{where}{extra_note}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(prog="resume_note.py", description=__doc__.strip().splitlines()[0])
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "vscode-hook"), default="text")
    args = parser.parse_args(argv)
    root = args.root
    if args.format == "vscode-hook":
        payload = {}
        if not sys.stdin.isatty():
            try:
                raw = sys.stdin.read().strip()
                if raw:
                    data = json.loads(raw)
                    if isinstance(data, dict):
                        payload = data
            except (json.JSONDecodeError, OSError):
                pass
        # Skip subagents and unrelated new/startup sessions; emit on resume (or when source is omitted).
        source = payload.get("source")
        if payload.get("agentId") or payload.get("agent_id") or (isinstance(source, str) and source != "resume"):
            print("{}")
            return 0
        if root is None:
            cwd = payload.get("cwd")
            root = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
        text = note(root)
        if text:
            # Top-level additionalContext is read by the Copilot harness; hookSpecificOutput supports the legacy Local harness.
            print(json.dumps({
                "additionalContext": text,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": text,
                },
            }))
        else:
            print("{}")
        return 0
    text = note(root or Path.cwd())
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
