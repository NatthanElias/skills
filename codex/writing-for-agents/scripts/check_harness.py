#!/usr/bin/env python3
"""Validate selected local Codex skills, invocation metadata, and local links."""
import argparse
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    sys.exit('Validation failed: PyYAML is required in this Python environment.')

ALLOWED = {'name', 'description', 'license', 'allowed-tools', 'metadata'}
INLINE_LINK = re.compile(r'\[[^\]\n]+\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\s*\)')
REFERENCE_LINK = re.compile(r'^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)', re.MULTILINE)

def require(condition, message):
    if not condition:
        raise ValueError(message)

def mapping(text, label):
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ValueError(f'{label}: invalid YAML: {error}') from error
    require(isinstance(data, dict), f'{label}: YAML must be a mapping')
    return data

def prose(text):
    lines, fence = [], None
    for line in text.splitlines():
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if match:
            marker, tail = match.groups()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not tail.strip():
                fence = None
            continue
        if fence is None:
            lines.append(re.sub(r'(`+).*?\1', '', line))
    return '\n'.join(lines)

def check_links(path):
    text = prose(path.read_text(encoding='utf-8'))
    for pattern in (INLINE_LINK, REFERENCE_LINK):
        for match in pattern.finditer(text):
            target = match.group(1).strip('<>')
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            require((path.parent / unquote(parts.path)).exists(), f'{path}: broken local link: {target}')

def check_metadata(directory):
    path = directory / 'agents/openai.yaml'
    if not path.exists():
        return
    data = mapping(path.read_text(encoding='utf-8'), str(path))
    require(not (set(data) - {'interface', 'policy', 'dependencies'}), f'{path}: unsupported metadata keys')
    interface = data.get('interface')
    require(isinstance(interface, dict), f'{path}: interface must be a mapping')
    for key in ('display_name', 'short_description'):
        value = interface.get(key)
        require(isinstance(value, str) and value.strip(), f'{path}: missing or invalid {key}')
    if 'default_prompt' in interface:
        require(isinstance(interface['default_prompt'], str) and interface['default_prompt'].strip(),
                f'{path}: default_prompt must be a nonempty string')
    for key in ('icon_small', 'icon_large'):
        if key in interface:
            value = interface[key]
            require(isinstance(value, str) and value.strip(), f'{path}: invalid {key}')
            icon = Path(value)
            require(not icon.is_absolute() and '..' not in icon.parts, f'{path}: unsafe icon path')
            require((directory / icon).is_file(), f'{path}: missing {key}: {value}')
    if 'policy' in data:
        policy = data['policy']
        require(isinstance(policy, dict), f'{path}: policy must be a mapping')
        require(not (set(policy) - {'allow_implicit_invocation', 'products'}), f'{path}: unsupported policy fields')
        if 'allow_implicit_invocation' in policy:
            require(type(policy['allow_implicit_invocation']) is bool,
                    f'{path}: allow_implicit_invocation must be a boolean')
        if 'products' in policy:
            value = policy['products']
            require(isinstance(value, list) and bool(value) and all(v in ('CHAT', 'CODEX') for v in value),
                    f'{path}: products must list CHAT, CODEX, or both')
    if 'dependencies' in data:
        dependencies = data['dependencies']
        require(isinstance(dependencies, dict) and not (set(dependencies) - {'tools'}),
                f'{path}: dependencies supports only tools')
        tools = dependencies.get('tools', [])
        require(isinstance(tools, list), f'{path}: dependencies.tools must be a list')
        for tool in tools:
            require(isinstance(tool, dict) and tool.get('type') == 'mcp'
                    and isinstance(tool.get('value'), str) and tool['value'].strip(),
                    f'{path}: invalid MCP dependency')

def validate_skill(directory):
    path = directory / 'SKILL.md'
    require(path.is_file(), f'{directory}: missing SKILL.md')
    text = path.read_text(encoding='utf-8')
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.DOTALL)
    require(match is not None, f'{path}: missing or unclosed YAML frontmatter')
    data = mapping(match.group(1), str(path))
    require(not (set(data) - ALLOWED), f'{path}: unsupported frontmatter keys: {sorted(set(data) - ALLOWED)}')
    name = data.get('name')
    require(isinstance(name, str) and len(name) <= 64 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name),
            f'{path}: invalid skill name')
    require(name == directory.name, f'{path}: skill name differs from directory name')
    description = data.get('description')
    require(isinstance(description, str) and bool(description.strip()) and len(description) <= 1024,
            f'{path}: description must contain 1 to 1024 characters')
    require('<' not in description and '>' not in description, f'{path}: angle brackets in description')
    body = text[match.end():]
    require(bool(body.strip()), f'{path}: empty skill body')
    require(not re.search(r'(?m)^\s*\[TODO:[^\n]*\]\s*$', prose(body)), f'{path}: unfinished scaffold placeholder')
    check_metadata(directory)
    for document in sorted(directory.rglob('*.md')):
        check_links(document)
    return name

def collect(paths):
    directories = []
    for path in paths:
        path = path.expanduser().absolute()
        require(path.is_dir(), f'{path}: skill directory or root does not exist')
        if (path / 'SKILL.md').is_file():
            directories.append(path)
        else:
            directories.extend(p for p in sorted(path.iterdir()) if p.is_dir()
                               and not p.name.startswith('.') and (p / 'SKILL.md').is_file())
    return list(dict.fromkeys(directories))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', type=Path, nargs='*', help='Skill folders or roots containing skills')
    parser.add_argument('--global', dest='global_scope', action='store_true', help='Include existing user skill roots')
    parser.add_argument('--names', nargs='+', help='Select only these installed skill names')
    args = parser.parse_args()
    paths = list(args.paths)
    if args.global_scope:
        codex = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
        paths.extend(p for p in (codex / 'skills', Path.home() / '.agents/skills') if p.is_dir())
    if not paths:
        paths = [Path(__file__).resolve().parents[1]]
    try:
        directories = collect(paths)
        if args.names:
            wanted = set(args.names)
            directories = [p for p in directories if p.name in wanted]
            missing = wanted - {p.name for p in directories}
            require(not missing, f'Skills not found: {sorted(missing)}')
        require(bool(directories), 'No skills selected; nothing was validated')
        names = {}
        for directory in directories:
            name = validate_skill(directory)
            require(name not in names, f'Duplicate skill name {name}: {names.get(name)} and {directory}')
            names[name] = directory
    except (ValueError, OSError, UnicodeError) as error:
        parser.exit(1, f'Validation failed: {error}\n')
    print(f'Harness OK: {len(names)} skills, Codex metadata, and local links')

if __name__ == '__main__':
    main()
