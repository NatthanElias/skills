#!/usr/bin/env python3
"""Copy a harness's project collection (project skills and agents) into a repository."""

import argparse
from pathlib import Path
import shutil

from install_skills import file_contents

# Project discovery folders: skills, then agents.
TARGETS = {
    'claude': ('.claude/skills', '.claude/agents'),
    'codex': ('.agents/skills', '.codex/agents'),
    'opencode': ('.opencode/skills', '.opencode/agents'),
}
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo', '.pytest_cache')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--harness', required=True, choices=sorted(TARGETS))
    parser.add_argument('--root', required=True, type=Path, help='Repository root to install into')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing files')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / args.harness / 'project'
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f'Repository root does not exist: {root}')
    skills_dir, agents_dir = (root / part for part in TARGETS[args.harness])
    pending, skipped, conflicts = [], [], []
    for skill in sorted(path.parent for path in (source / 'skills').glob('*/SKILL.md')):
        destination = skills_dir / skill.name
        if destination.exists() or destination.is_symlink():
            if destination.is_dir() and file_contents(skill) == file_contents(destination):
                skipped.append(destination)
            else:
                conflicts.append(destination)
        else:
            pending.append((skill, destination))
    for agent in sorted(path for path in (source / 'agents').iterdir() if path.is_file()):
        destination = agents_dir / agent.name
        if destination.exists() or destination.is_symlink():
            if destination.is_file() and destination.read_bytes() == agent.read_bytes():
                skipped.append(destination)
            else:
                conflicts.append(destination)
        else:
            pending.append((agent, destination))
    if conflicts:
        parser.exit(1, 'Back up conflicting destinations before installing:\n'
                    + ''.join(f'  {path}\n' for path in conflicts))
    for destination in skipped:
        print(f'Unchanged: {destination}')
    for item, destination in pending:
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if item.is_dir():
                shutil.copytree(item, destination, ignore=IGNORE)
            else:
                shutil.copy2(item, destination)
        print(f'{"Would install" if args.dry_run else "Installed"}: {destination}')


if __name__ == '__main__':
    main()
