#!/usr/bin/env python3
"""
resume_note.py - state where paused feature work stands when a session resumes.

A session-start hook runs this on resume and after compaction. It prints facts
only: the newest feature handoff and the current HEAD. The Resume section of
feature-workflow's SKILL.md still decides what is current; the newest handoff
is not necessarily the active feature. It prints nothing outside a Git
repository or when no feature folder holds a handoff.

Usage:
  python3 .opencode/skills/feature-workflow/scripts/resume_note.py [--root PATH]
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def note(root):
    top = git(root, "rev-parse", "--show-toplevel")
    if not top:
        return ""
    handoffs = sorted(Path(top).glob(".specs/features/*/execution/handoff.md"),
                      key=lambda path: path.stat().st_mtime, reverse=True)
    if not handoffs:
        return ""
    newest = handoffs[0]
    changed = datetime.fromtimestamp(newest.stat().st_mtime).isoformat(timespec="minutes")
    head = git(top, "rev-parse", "--short=12", "HEAD")
    branch = git(top, "branch", "--show-current")
    where = (f"HEAD is {head} on {branch}." if branch else f"HEAD is {head}, detached.") if head else f"{branch or 'HEAD'} has no commits yet."
    others = f" {len(handoffs) - 1} other feature folders also hold a handoff." if len(handoffs) > 1 else ""
    return (f"feature-workflow: the newest handoff is {newest.relative_to(top).as_posix()}, last changed "
            f"{changed}. {where}{others}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="resume_note.py", description=__doc__.strip().splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    text = note(args.root)
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
