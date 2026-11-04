#!/usr/bin/env python3
"""Copy a harness's project collection (project skills and agents) into a repository.

When the collection holds hooks.json, its hook groups are merged into the harness's
project hook file; groups already present are left alone.
"""

import argparse
import json
from pathlib import Path
import shutil

from install_skills import file_contents

# Project discovery folders: skills, then agents.
TARGETS = {
    'claude': ('.claude/skills', '.claude/agents'),
    'codex': ('.agents/skills', '.codex/agents'),
    'opencode': ('.opencode/skills', '.opencode/agents'),
}
# Project hook files that receive the collection's hooks.json.
HOOK_FILES = {
    'claude': '.claude/settings.json',
    'codex': '.codex/hooks.json',
}
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo', '.pytest_cache')


def merged_hooks(source, target):
    """Return the target hook file text with the collection's missing hook groups added, or None."""
    wanted = json.loads(source.read_text(encoding='utf-8'))['hooks']
    current = json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
    if not isinstance(current, dict) or not isinstance(current.get('hooks', {}), dict):
        raise ValueError(f'{target} does not hold a JSON object with a "hooks" object')
    hooks = current.setdefault('hooks', {})
    added = False
    for event, groups in wanted.items():
        present = hooks.setdefault(event, [])
        if not isinstance(present, list):
            raise ValueError(f'{target} holds a non-list "{event}" hook entry')
        for group in groups:
            if group not in present:
                present.append(group)
                added = True
    return json.dumps(current, indent=2) + '\n' if added else None


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
    hook_change = None
    hook_source = source / 'hooks.json'
    if args.harness in HOOK_FILES and hook_source.exists():
        hook_target = root / HOOK_FILES[args.harness]
        try:
            hook_change = merged_hooks(hook_source, hook_target)
        except (ValueError, json.JSONDecodeError) as error:
            conflicts.append(f'{hook_target} ({error})')
        if hook_change is None and not conflicts:
            skipped.append(hook_target)
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
    if hook_change is not None:
        if not args.dry_run:
            hook_target.parent.mkdir(parents=True, exist_ok=True)
            hook_target.write_text(hook_change, encoding='utf-8')
        print(f'{"Would add hooks to" if args.dry_run else "Added hooks to"}: {hook_target}')


if __name__ == '__main__':
    main()
