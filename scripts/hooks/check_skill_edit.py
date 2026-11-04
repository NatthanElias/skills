#!/usr/bin/env python3
"""After-edit hook for this repository: run the owning harness's skill checker.

Claude Code and Codex call this after a file edit, with the hook event as JSON on
stdin. When the edit lands in a skill folder of this repository, the checker of
the harness folder that holds it runs on that skill, from the fixed table below,
never a checker found next to the file. Problems go back to the agent as
additional context. The hook never blocks, so a half-written skill only draws a
note, and it prints nothing when the checks pass or the edit is elsewhere.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CHECKERS = {
    "claude": "claude/writing-for-agents/scripts/check_harness.py",
    "codex": "codex/writing-for-agents/scripts/check_harness.py",
    "opencode": "opencode/writing-for-agents/scripts/check_harness.py",
    "gemini": "gemini/writing-for-agents/scripts/check_harness.py",
}
# The VS Code checker validates the whole bundle from the folder that holds `.github/`.
BUNDLE = ("vscode", "vscode/.github/skills/writing-for-agents/scripts/check_harness.py")
PATCH_PATH = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", re.M)
LIMIT = 2000


def edited_paths(event):
    tool_input = event.get("tool_input") or {}
    base = Path(event.get("cwd") or REPO)
    paths = [tool_input[key] for key in ("file_path", "path") if isinstance(tool_input.get(key), str)]
    command = tool_input.get("command")
    if isinstance(command, str):
        paths += PATCH_PATH.findall(command)
    return [(base / path).resolve() for path in paths]


def skill_folder(path, harness_root):
    for folder in [path.parent, *path.parent.parents]:
        if folder == harness_root or harness_root not in folder.parents:
            return None
        if (folder / "SKILL.md").is_file():
            return folder
    return None


def runs(paths):
    """Return {(command, cwd)} for the checks the edited paths need."""
    needed = set()
    for path in paths:
        try:
            parts = path.relative_to(REPO).parts
        except ValueError:
            continue
        if not parts:
            continue
        if parts[0] == BUNDLE[0]:
            needed.add(((sys.executable, str(REPO / BUNDLE[1])), str(REPO / BUNDLE[0])))
        elif parts[0] in CHECKERS:
            folder = skill_folder(path, REPO / parts[0])
            if folder:
                needed.add(((sys.executable, str(REPO / CHECKERS[parts[0]]), str(folder)), str(REPO)))
    return needed


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    notes = []
    for command, cwd in sorted(runs(edited_paths(event))):
        try:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as error:
            notes.append(f"{command[1]} could not run: {error}")
            continue
        if result.returncode:
            output = (result.stdout + result.stderr).strip()[-LIMIT:]
            target = command[2] if len(command) > 2 else cwd
            notes.append(f"{Path(command[1]).relative_to(REPO)} reported problems in "
                         f"{Path(target).relative_to(REPO)}:\n{output}")
    if notes:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                 "additionalContext": "\n\n".join(notes)}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
