#!/usr/bin/env python3
"""
git_hooks.py - run feature-workflow's commit checks as Git hooks in this clone.

Git runs the checks on every commit in the clone, whoever commits, so the
checks no longer depend on an agent remembering them:

  pre-commit   no file under .specs/features/ is staged; lesson files are not
               mixed with other files; the constraint records pass
               `constraints.py check` and have no unstaged or untracked changes
  commit-msg   the message passes check_commit.py; a commit holding only
               lesson files is a `chore(specs): ...` commit

Merge commits and Git's own `Merge`, `Revert`, `fixup!`, `squash!`, and
`amend!` messages are skipped, as commit linters do. For `git commit --amend`
the checks cover the whole amended commit, found from the calling Git process.
Git runs neither hook for cherry-pick or rebase.

Usage:
  python3 .opencode/skills/feature-workflow/scripts/git_hooks.py status
  python3 .opencode/skills/feature-workflow/scripts/git_hooks.py install
  python3 .opencode/skills/feature-workflow/scripts/git_hooks.py uninstall

`install` writes small shell hooks into this clone's hooks folder. It never
overwrites a hook it did not write, and when core.hooksPath hands the hooks to
a manager such as Husky or Lefthook it prints the two commands to add there.

Exit codes: 0 pass, 1 check failed, 2 usage or Git error, 3 hooks owned elsewhere.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_commit  # noqa: E402
import constraints  # noqa: E402

SCRIPT = ".opencode/skills/feature-workflow/scripts/git_hooks.py"
MARK = "# feature-workflow git hook"
HOOKS = ("pre-commit", "commit-msg")
FEATURES = ".specs/features/"
LESSONS = (".specs/lessons/", ".specs/LESSONS.md")
CONSTRAINT_PATHS = (".specs/constraints", ".specs/STATE.md")
SKIPPED_PREFIXES = ("Merge ", 'Revert "', "fixup! ", "squash! ", "amend! ")
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

SHIM = """#!/bin/sh
{mark}. Remove it with: python3 {script} uninstall
script="$(git rev-parse --show-toplevel)/{script}"
if [ ! -f "$script" ]; then
  echo "feature-workflow: $script is missing in this checkout; commit checks skipped" >&2
  exit 0
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "feature-workflow: python3 not found; install it or run: python3 {script} uninstall" >&2
  exit 1
fi
exec python3 "$script" {hook} "$@"
"""


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def git_lines(*args):
    result = git(*args, "-z")
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return [line for line in result.stdout.split("\0") if line]


def merging():
    return git("rev-parse", "-q", "--verify", "MERGE_HEAD").returncode == 0


def command_line(pid):
    """Return (parent pid, argument list) of a process, or None where neither /proc nor ps can tell."""
    proc = Path(f"/proc/{pid}")
    try:
        args = (proc / "cmdline").read_bytes().split(b"\0")
        parent = int((proc / "stat").read_text().rsplit(")", 1)[1].split()[1])
        return parent, [arg.decode(errors="replace") for arg in args if arg]
    except (OSError, ValueError, IndexError):
        pass
    try:
        out = subprocess.run(["ps", "-o", "ppid=", "-o", "args=", "-p", str(pid)],
                             capture_output=True, text=True).stdout.strip()
    except OSError:
        return None
    parent, _, args = out.partition(" ")
    return (int(parent), args.split()) if parent.isdigit() else None


def amending():
    """True when the `git commit` that runs this hook was given --amend; hook managers may sit in between."""
    pid = os.getppid()
    for _ in range(4):
        found = command_line(pid)
        if not found:
            return False
        pid, args = found
        if args and Path(args[0]).name in ("git", "git.exe") and "commit" in args:
            return "--amend" in args
    return False


def staged():
    """Paths the new commit changes against its parent.

    Git exports GIT_INDEX_FILE to hooks, so `git commit -a` and pathspec commits show their real
    contents. An amended commit replaces HEAD, so its changes are measured from HEAD's parent;
    a commit without a parent is measured from the empty tree.
    """
    base = "HEAD^" if amending() else "HEAD"
    if git("rev-parse", "-q", "--verify", base).returncode:
        base = EMPTY_TREE  # the first commit, or amending it, has no parent to compare against
    return git_lines("diff", "--cached", "--name-only", "--no-renames", base)


def is_lesson(path):
    return path.startswith(LESSONS[0]) or path == LESSONS[1]


def pre_commit():
    if merging():
        return 0
    files = staged()
    errors = []
    features = [path for path in files if path.startswith(FEATURES)]
    if features:
        errors.append("feature folders are git-ignored working files; unstage " + ", ".join(features[:5]))
    lessons = [path for path in files if is_lesson(path)]
    others = [path for path in files if not is_lesson(path)]
    if lessons and others:
        errors.append("lesson changes go in their own `chore(specs): ...` commit; unstage either the lesson "
                      "files or " + ", ".join(others[:5]))
    # The check reads the working tree, so the working tree must equal what is committed.
    unstaged = git_lines("diff", "--name-only", "--", *CONSTRAINT_PATHS)
    untracked = git_lines("ls-files", "--others", "--exclude-standard", "--", *CONSTRAINT_PATHS)
    if unstaged or untracked:
        errors.append("stage or discard every constraint change before committing: "
                      + ", ".join((unstaged + untracked)[:5]))
    elif (Path(".specs/constraints").is_dir() or Path(".specs/STATE.md").exists()) and constraints.check(Path.cwd()):
        errors.append("constraint records fail `constraints.py check`; fix them, stage the fix, and commit again")
    return report("pre-commit", errors)


def commit_msg(message_file):
    message = Path(message_file).read_text(encoding="utf-8", errors="replace")
    header = next((line for line in message.splitlines() if line.strip() and not line.startswith("#")), "")
    if merging() or header.startswith(SKIPPED_PREFIXES):
        return 0
    errors, warnings = check_commit.check(message)
    for warning in warnings:
        print(f"  WARN  {warning}")
    files = staged()
    if files and all(is_lesson(path) for path in files) and not header.startswith("chore(specs)"):
        errors.append("a commit holding only lesson files must be `chore(specs): ...`")
    return report("commit-msg", errors)


def report(hook, errors):
    for error in errors:
        print(f"  ERROR {error}", file=sys.stderr)
    if errors:
        print(f"feature-workflow {hook}: commit blocked; fix the errors above and commit again", file=sys.stderr)
        return 1
    return 0


def hooks_folder():
    managed = git("config", "--get", "core.hooksPath").stdout.strip()
    folder = git("rev-parse", "--path-format=absolute", "--git-path", "hooks")
    if folder.returncode:
        raise RuntimeError("not inside a Git repository")
    return Path(folder.stdout.strip()), managed


def states(folder):
    found = {}
    for hook in HOOKS:
        path = folder / hook
        if path.is_symlink():
            found[hook] = "foreign"  # install never writes links, and writing through one edits its target
        elif not path.exists():
            found[hook] = "missing"
        elif MARK not in path.read_text(encoding="utf-8", errors="replace"):
            found[hook] = "foreign"
        else:
            found[hook] = "ours" if os.access(path, os.X_OK) else "not executable"
    return found


def manual_steps():
    return (f"Call these from your hook manager's hooks:\n"
            f"  pre-commit:  python3 {SCRIPT} pre-commit\n"
            f"  commit-msg:  python3 {SCRIPT} commit-msg \"$1\"")


def status():
    folder, managed = hooks_folder()
    if managed:
        print(f"managed: core.hooksPath is {managed}; check that its hooks call git_hooks.py")
        return 0
    found = states(folder)
    if all(state == "ours" for state in found.values()):
        print("installed")
    elif all(state == "missing" for state in found.values()):
        print("not installed")
    else:
        print("partly installed: " + ", ".join(f"{hook} {state}" for hook, state in found.items()))
    return 0


def install():
    folder, managed = hooks_folder()
    if managed:
        print(f"core.hooksPath is {managed}, so a hook manager owns this clone's hooks.\n{manual_steps()}")
        return 3
    found = states(folder)
    foreign = [hook for hook, state in found.items() if state == "foreign"]
    if foreign:
        print(f"{', '.join(foreign)} already exist in {folder} and were not written by feature-workflow.\n"
              f"{manual_steps()}")
        return 3
    folder.mkdir(parents=True, exist_ok=True)
    for hook in HOOKS:
        path = folder / hook
        path.write_text(SHIM.format(mark=MARK, script=SCRIPT, hook=hook), encoding="utf-8", newline="\n")
        path.chmod(0o755)
        print(f"Installed {path}")
    return 0


def uninstall():
    folder, _ = hooks_folder()
    for hook, state in states(folder).items():
        if state in ("ours", "not executable"):
            (folder / hook).unlink()
            print(f"Removed {folder / hook}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="git_hooks.py", description="feature-workflow commit checks as Git hooks.")
    parser.add_argument("action", choices=["status", "install", "uninstall", "pre-commit", "commit-msg"])
    parser.add_argument("message_file", nargs="?", help="commit-msg only: the file Git passes")
    args = parser.parse_args(argv)
    try:
        if args.action == "commit-msg":
            if not args.message_file:
                parser.error("commit-msg needs the message file Git passes")
            return commit_msg(args.message_file)
        if args.action == "pre-commit":
            return pre_commit()
        return {"status": status, "install": install, "uninstall": uninstall}[args.action]()
    except (RuntimeError, OSError) as error:
        print(f"git_hooks: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    sys.exit(main())
