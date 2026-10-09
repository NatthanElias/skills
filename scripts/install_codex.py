#!/usr/bin/env python3
"""Copy the Codex collection to an explicit skill discovery folder."""

import argparse
from pathlib import Path
import shutil


def file_contents(directory):
    """Compare installed files without considering generated Python caches."""
    return {
        path.relative_to(directory): path.read_bytes()
        for path in directory.rglob('*')
        if path.is_file()
        and '__pycache__' not in path.parts
        and '.pytest_cache' not in path.parts
        and path.suffix not in ('.pyc', '.pyo')
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', required=True, type=Path,
                        help='Destination, e.g. ~/.agents/skills or a project .agents/skills')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing files')
    args = parser.parse_args()
    source_root = Path(__file__).resolve().parents[1] / 'codex'
    target = args.target.expanduser().resolve()
    if target == source_root or source_root in target.parents:
        parser.error('The destination must be outside the source collection.')
    sources = sorted(path.parent for path in source_root.glob('*/SKILL.md'))
    if not sources:
        parser.error('No Codex skills found next to this installer.')

    pending = []
    skipped = []
    conflicts = []
    try:
        if target.exists() and not target.is_dir():
            parser.error(f'Destination is not a directory: {target}')
        for source in sources:
            destination = target / source.name
            if destination.exists() or destination.is_symlink():
                if destination.is_dir() and file_contents(source) == file_contents(destination):
                    skipped.append(destination)
                else:
                    conflicts.append(destination)
            else:
                pending.append((source, destination))
        if conflicts:
            parser.exit(1, 'Back up conflicting destinations before installing:\n'
                        + ''.join(f'  {path}\n' for path in conflicts))
        for destination in skipped:
            print(f'Unchanged: {destination}')
        for source, destination in pending:
            if not args.dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, destination,
                                ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo', '.pytest_cache'))
            print(f'{"Would install" if args.dry_run else "Installed"}: {destination}')
    except OSError as error:
        parser.exit(1, f'Installation failed: {error}\n')


if __name__ == '__main__':
    main()
