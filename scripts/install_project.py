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


MANAGED_HOOK_MARKERS = ('feature-workflow/scripts/resume_note.py',)


def managed_hook_key(group):
    """Return (matcher, marker) if group runs a skill-managed hook script, else None."""
    if not isinstance(group, dict):
        return None
    hooks = group.get('hooks')
    if not isinstance(hooks, list):
        return None
    for item in hooks:
        command = item.get('command') if isinstance(item, dict) else None
        if isinstance(command, str):
            for marker in MANAGED_HOOK_MARKERS:
                if marker in command:
                    return (group.get('matcher'), marker)
    return None


def merged_hooks(source, target, upgrade=False):
    """Return the target hook file text with the collection's hook groups added/updated, or None."""
    wanted = json.loads(source.read_text(encoding='utf-8'))['hooks']
    current = json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
    if not isinstance(current, dict) or not isinstance(current.get('hooks', {}), dict):
        raise ValueError(f'{target} does not hold a JSON object with a "hooks" object')
    hooks = current.setdefault('hooks', {})
    changed = False
    for event, groups in wanted.items():
        present = hooks.setdefault(event, [])
        if not isinstance(present, list):
            raise ValueError(f'{target} holds a non-list "{event}" hook entry')
        for group in groups:
            key = managed_hook_key(group)
            matches = [i for i, existing in enumerate(present)
                       if key is not None and managed_hook_key(existing) == key]
            if matches:
                if len(matches) == 1 and present[matches[0]] == group:
                    continue
                if not upgrade:
                    raise ValueError(f'existing {event} hook for {key[1]} differs; pass --upgrade to replace')
                present[matches[0]] = group
                for index in reversed(matches[1:]):
                    present.pop(index)
                changed = True
            elif group not in present:
                present.append(group)
                changed = True
    return json.dumps(current, indent=2) + '\n' if changed else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--harness', required=True, choices=sorted(TARGETS))
    parser.add_argument('--root', required=True, type=Path, help='Repository root to install into')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing files')
    parser.add_argument('--upgrade', action='store_true',
                        help='Replace existing project skills and agents whose contents differ (reapply local overrides afterwards)')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / args.harness / 'project'
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f'Repository root does not exist: {root}')
    skills_dir, agents_dir = (root / part for part in TARGETS[args.harness])
    pending, replacements, skipped, conflicts = [], [], [], []
    for skill in sorted(path.parent for path in (source / 'skills').glob('*/SKILL.md')):
        destination = skills_dir / skill.name
        if destination.exists() or destination.is_symlink():
            if not destination.is_symlink() and destination.is_dir() and file_contents(skill) == file_contents(destination):
                skipped.append(destination)
            elif args.upgrade and not destination.is_symlink() and destination.is_dir():
                replacements.append((skill, destination))
            else:
                conflicts.append(destination)
        else:
            pending.append((skill, destination))
    for agent in sorted(path for path in (source / 'agents').iterdir() if path.is_file()):
        destination = agents_dir / agent.name
        if destination.exists() or destination.is_symlink():
            if not destination.is_symlink() and destination.is_file() and destination.read_bytes() == agent.read_bytes():
                skipped.append(destination)
            elif args.upgrade and not destination.is_symlink() and destination.is_file():
                replacements.append((agent, destination))
            else:
                conflicts.append(destination)
        else:
            pending.append((agent, destination))
    hook_change = None
    hook_source = source / 'hooks.json'
    if args.harness in HOOK_FILES and hook_source.exists():
        hook_target = root / HOOK_FILES[args.harness]
        try:
            hook_change = merged_hooks(hook_source, hook_target, upgrade=args.upgrade)
        except (ValueError, json.JSONDecodeError) as error:
            conflicts.append(f'{hook_target} ({error})')
        if hook_change is None and not conflicts:
            skipped.append(hook_target)
    if conflicts:
        parser.exit(1, 'Back up conflicting destinations (or pass --upgrade to replace project skills and agents):\n'
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
    for item, destination in replacements:
        if not args.dry_run:
            if item.is_dir():
                shutil.rmtree(destination)
                shutil.copytree(item, destination, ignore=IGNORE)
            else:
                shutil.copy2(item, destination)
        print(f'{"Would replace" if args.dry_run else "Replaced"}: {destination}')
    if hook_change is not None:
        if not args.dry_run:
            hook_target.parent.mkdir(parents=True, exist_ok=True)
            hook_target.write_text(hook_change, encoding='utf-8')
        print(f'{"Would add hooks to" if args.dry_run else "Added hooks to"}: {hook_target}')


if __name__ == '__main__':
    main()
