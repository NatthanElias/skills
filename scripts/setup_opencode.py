#!/usr/bin/env python3
"""Preview or install the personal OpenCode + Slim orchestration workflow."""

import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import uuid

REPO = Path(__file__).resolve().parents[1]
SETUP = REPO / 'opencode/setup'
PLUGIN_VERSION = '3.0.3'
ROLES = ('orchestrator', 'explorer', 'librarian', 'fixer', 'oracle')
START = '<!-- skills-repo:orchestrate:start -->'
END = '<!-- skills-repo:orchestrate:end -->'


def read_jsonc(path):
    """Read JSONC without treating comment markers inside strings as comments."""
    text = path.read_text(encoding='utf-8-sig')
    decoder = json.JSONDecoder()
    parts = []
    i = 0
    while i < len(text):
        if text[i] == '"':
            _, end = decoder.raw_decode(text[i:])
            parts.append(text[i:i + end])
            i += end
        elif text.startswith('//', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
        elif text.startswith('/*', i):
            end = text.find('*/', i + 2)
            if end < 0:
                raise ValueError(f'Unclosed JSONC comment in {path}')
            parts.append(' ')
            i = end + 2
        else:
            parts.append(text[i])
            i += 1
    text = ''.join(parts)
    parts = []
    i = 0
    while i < len(text):
        if text[i] == '"':
            _, end = decoder.raw_decode(text[i:])
            parts.append(text[i:i + end])
            i += end
        elif text[i] == ',' and re.match(r'\s*[}\]]', text[i + 1:]):
            i += 1
        else:
            parts.append(text[i])
            i += 1
    result = json.loads(''.join(parts))
    if not isinstance(result, dict):
        raise ValueError(f'Configuration must be an object: {path}')
    return result


def config_path(directory, stem):
    jsonc = directory / f'{stem}.jsonc'
    return jsonc if jsonc.exists() else directory / f'{stem}.json'


def mapping(parent, key):
    result = parent.setdefault(key, {})
    if not isinstance(result, dict):
        raise ValueError(f'{key} must be an object')
    return result


def configure(original, profile):
    config = copy.deepcopy(original)
    choices = json.loads((SETUP / 'go-models.json').read_text())
    presets = mapping(config, 'presets')
    if profile == 'preserve':
        selected = config.setdefault('preset', 'opencode-go')
        if selected not in presets:
            if presets or original.get('preset'):
                raise ValueError(f'Active preset {selected!r} is missing; choose --models recommended or alternative')
            presets[selected] = copy.deepcopy(config.get('agents', {}))
    else:
        selected = f'skills-go-{profile}'
        # Keep old presets available; the selected personal preset is explicit.
        presets.setdefault(selected, {})
        for role, model in choices[profile].items():
            agent = mapping(presets[selected], role)
            for key in ('model', 'variant', 'inheritModelFrom', 'options'):
                agent.pop(key, None)
            agent.update(model)
        config['preset'] = selected

    overrides = mapping(config, 'agents')
    for name in presets:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name):
            raise ValueError(f'Preset name cannot be used as a prompt directory: {name!r}')
    blocks = [overrides, *presets.values()]
    unused = {'designer', 'observer', 'council', 'councillor'}
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError('Every preset must be an object')
        unused.update(name for name, value in block.items()
                      if name not in ROLES and not name.startswith('__') and isinstance(value, dict))
        for role in ROLES:
            agent = mapping(block, role)
            if block is presets[selected] and not agent.get('model') and not agent.get('inheritModelFrom'):
                agent.update(choices['recommended'][role])
            permissions = agent.setdefault('permission', {})
            if isinstance(permissions, str):
                permissions = agent['permission'] = {'*': permissions}
            if not isinstance(permissions, dict):
                raise ValueError(f'{role}.permission must be a string or object')
            if role != 'orchestrator':
                permissions.update({'task': 'deny', 'subagent': 'deny', 'task_*': 'deny', 'acp_run': 'deny'})
            if role in ('explorer', 'librarian', 'oracle'):
                permissions['edit'] = 'deny'
                # Oracle may execute checks declared in an independent review brief.
                permissions['bash'] = 'allow' if role == 'oracle' else 'deny'
            agent.setdefault('skills', ['*'] if role == 'orchestrator' else [])
            if role == 'orchestrator':
                skills = agent['skills']
                if not isinstance(skills, list):
                    raise ValueError('orchestrator.skills must be a list')
                if '*' not in skills and 'orchestrate' not in skills:
                    skills.append('orchestrate')
                for key in ('skills', 'skills_remove'):
                    if isinstance(agent.get(key), list):
                        agent[key] = [value for value in agent[key] if value != '!orchestrate' and
                                      not (key == 'skills_remove' and value == 'orchestrate')]
            if role == 'librarian':
                agent.setdefault('mcps', ['websearch', 'context7', 'gh_grep'])
    council = config.get('council', {})
    for preset in council.get('presets', {}).values():
        unused.update(f'councillor-{name}' for name in preset)
    disabled = config.get('disabled_agents', [])
    if not isinstance(disabled, list) or not all(isinstance(name, str) for name in disabled):
        raise ValueError('disabled_agents must be a list of names')
    config['disabled_agents'] = sorted((set(disabled) | unused) - set(ROLES))
    config['image_routing'] = 'direct'
    if isinstance(config.get('disabled_skills'), list):
        config['disabled_skills'] = [name for name in config['disabled_skills'] if name != 'orchestrate']
    return config


def managed_prompt(existing, content):
    block = START + '\n' + content.strip() + '\n' + END
    if existing.count(START) != existing.count(END) or existing.count(START) > 1:
        raise ValueError('Malformed or duplicate managed prompt block')
    if START in existing:
        begin, end = existing.index(START), existing.index(END)
        if end < begin:
            raise ValueError('Managed prompt markers are out of order')
        return existing[:begin] + block + existing[end + len(END):]
    return (existing.rstrip() + '\n\n' if existing.strip() else '') + block + '\n'


def plan(directory, profile):
    plugin = config_path(directory, 'oh-my-opencode-slim')
    original = read_jsonc(plugin) if plugin.exists() else {}
    config = configure(original, profile)
    # Preserve an unchanged config byte-for-byte, including JSONC comments.
    updates = {}
    if config != original:
        updates[plugin] = (json.dumps(config, indent=2) + '\n').encode()
    for file in sorted((REPO / 'opencode').glob('*/SKILL.md')):
        for source in sorted(file.parent.rglob('*')):
            if source.is_file() and '__pycache__' not in source.parts and source.suffix not in ('.pyc', '.pyo'):
                updates[directory / 'skills' / source.relative_to(REPO / 'opencode')] = source.read_bytes()
    skill_dir = str(directory / 'skills/orchestrate')
    # Cover each preset-specific append, since it takes precedence over the root append.
    for folder in [directory / 'oh-my-opencode-slim', *[
        directory / 'oh-my-opencode-slim' / name for name in config['presets']
    ]]:
        for role in ROLES:
            destination = folder / f'{role}_append.md'
            existing = destination.read_text() if destination.exists() else ''
            template = (SETUP / f'prompts/{role}_append.md').read_text().replace('{{SKILL_DIR}}', skill_dir)
            updates[destination] = managed_prompt(existing, template).encode()
    return {path: data for path, data in updates.items()
            if not path.is_file() or path.read_bytes() != data}, config


def pin_plugin(directory):
    path = config_path(directory, 'opencode')
    core = read_jsonc(path)
    plugins = core.get('plugin', [])
    if not isinstance(plugins, list):
        raise ValueError('opencode.plugin must be a list')
    pinned = f'oh-my-opencode-slim@{PLUGIN_VERSION}'
    registered = []
    found = False
    for item in plugins:
        if isinstance(item, str) and re.fullmatch(r'oh-my-opencode-slim(?:@[^/]+)?', item):
            if not found:
                registered.append(pinned)
                found = True
        else:
            registered.append(item)
    if not found:
        registered.append(pinned)
    plugins = registered
    if plugins == core.get('plugin'):
        return {}
    core['plugin'] = plugins
    return {path: (json.dumps(core, indent=2) + '\n').encode()}


class Writer:
    def __init__(self, directory):
        self.directory = directory
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
        self.backup = directory / '.backups/skills-setup' / stamp
        self.saved = set()

    def save(self, path):
        if path.is_symlink():
            raise ValueError(f'Refusing to replace symlink: {path}')
        if path.exists() and path not in self.saved:
            target = self.backup / path.relative_to(self.directory)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            self.saved.add(path)

    def write(self, path, data):
        self.save(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
            temp.write(data)
            staged = Path(temp.name)
        try:
            staged.chmod(mode)
            staged.replace(path)
        finally:
            staged.unlink(missing_ok=True)


def main():
    default = os.environ.get('OPENCODE_CONFIG_DIR') or str(
        Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'opencode')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-dir', type=Path, default=Path(default))
    parser.add_argument('--models', choices=('preserve', 'recommended', 'alternative'), default='preserve')
    parser.add_argument('--install-plugin', action='store_true', help=f'Install/upgrade Slim {PLUGIN_VERSION} through bunx')
    parser.add_argument('--apply', action='store_true', help='Write changes; without this flag only preview')
    args = parser.parse_args()
    directory = args.config_dir.expanduser().resolve()
    if directory == REPO or REPO in directory.parents:
        parser.error('Choose an OpenCode config directory outside this repository.')
    writer = Writer(directory)
    try:
        existing_plugin = config_path(directory, 'oh-my-opencode-slim').exists()
        profile = 'recommended' if args.models == 'preserve' and not existing_plugin else args.models
        for stem in ('opencode', 'oh-my-opencode-slim', 'tui'):
            path = config_path(directory, stem)
            if path.exists():
                read_jsonc(path)
        updates, config = plan(directory, profile)
        if args.install_plugin:
            command = ['bunx', f'oh-my-opencode-slim@{PLUGIN_VERSION}', 'install', '--no-tui',
                       '--preset=opencode-go', '--companion=no', '--background-subagents=no']
            print('Plugin command:', ' '.join(command))
            if args.apply:
                if not shutil.which('bunx') or not shutil.which('opencode'):
                    raise ValueError('Install Bun (bunx) and OpenCode before running the plugin installer.')
                for pattern in ('opencode.json*', 'oh-my-opencode-slim.json*', 'tui.json*'):
                    for path in directory.glob(pattern):
                        if path.is_file():
                            writer.save(path)
                env = dict(os.environ, OPENCODE_CONFIG_DIR=str(directory))
                subprocess.run(command, env=env, check=True)
                updates, config = plan(directory, profile)
                updates.update(pin_plugin(directory))
        core = config_path(directory, 'opencode')
        if not args.install_plugin and not core.exists():
            raise ValueError('OpenCode is not configured here; add --install-plugin for initial setup.')
        launcher = directory / 'run-opencode'
        import shlex
        updates[launcher] = (
            '#!/bin/sh\n'
            f'export OPENCODE_CONFIG_DIR={shlex.quote(str(directory))}\n'
            'export OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true\n'
            'export OPENCODE_ENABLE_EXA=1\n'
            'exec opencode "$@"\n'
        ).encode()
        updates = {p: data for p, data in updates.items() if not p.is_file() or p.read_bytes() != data}
        for path in updates:
            if any(parent.is_symlink() for parent in path.parents if parent != directory):
                raise ValueError(f'Output has a symlinked parent: {path}')
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(f'Output is not a regular file: {path}')
        print(f'Preset: {config["preset"]}; enabled roles: {", ".join(ROLES)}')
        print('Disabled roles:', ', '.join(config['disabled_agents']))
        print(f'{"Apply" if args.apply else "Preview"}: {len(updates)} changed files under {directory}')
        if args.apply:
            for path, data in updates.items():
                writer.write(path, data)
            launcher.chmod(0o755)
            print('Backups:', writer.backup if writer.saved else 'no existing files changed')
            print('Launch:', launcher)
        else:
            print('No files changed. Add --apply to execute this setup.')
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Setup failed: {error}\nBackups, if created: {writer.backup}\n')


if __name__ == '__main__':
    main()
