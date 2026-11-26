"""Check the installed .github: local links, skill front matter, and bounded helpers."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
TEMPLATE = Path(".github/skills/workflow-setup/templates/copilot-instructions.template.md")
INLINE_LINK = re.compile(r'\[[^\]\n]+\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\s*\)')
REFERENCE_LINK = re.compile(r'^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)', re.MULTILINE)
FENCE_RE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
HOOK_SCRIPT = re.compile(r'\.github[/\\]skills[/\\][\w-]+[/\\]scripts[/\\][\w.-]+\.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prose(text):
    lines, fence = [], None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match:
            marker, tail = match.groups()
            if fence is None:
                if marker[0] != '`' or '`' not in tail:
                    fence = marker
                    continue
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not tail.strip():
                fence = None
                continue
        if fence is None:
            lines.append(re.sub(r'(`+).*?\1', '', line))
    return '\n'.join(lines)


def harness(root):
    github = root / ".github"
    template = root / TEMPLATE
    require(template.is_file(), "Missing entry template")
    # The template renders to .github/copilot-instructions.md, so its links resolve from .github.
    documents = [(template, github)] + [(path, path.parent) for path in sorted(github.rglob("*.md"))
                                        if path != template]
    for path, base in documents:
        text = prose(path.read_text(encoding="utf-8"))
        for pattern in (INLINE_LINK, REFERENCE_LINK):
            for match in pattern.finditer(text):
                target = match.group(1).strip("<>")
                parts = urlsplit(target)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                require((base / unquote(parts.path)).resolve().is_file(), f"Broken link in {path}: {target}")
    skills = list((github / "skills").glob("*/SKILL.md"))
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        require(text.startswith("---\n") and f"name: {skill.parent.name}\n" in text
                and "description:" in text.split("---", 2)[1], f"Invalid skill: {skill}")
    # VS Code registers every .md directly in .github/agents/ except README.md as an agent.
    for agent in (github / "agents").glob("*.md"):
        if agent.name == "README.md":
            continue
        text = agent.read_text(encoding="utf-8")
        require("user-invocable: false" in text and "agents: []" in text,
                f"Unbounded helper: {agent}")
    hooks_dir = github / "hooks"
    if hooks_dir.is_dir():
        for hook_path in sorted(hooks_dir.glob("*.json")):
            try:
                data = json.loads(hook_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid hook JSON in {hook_path}: {error}") from error
            require(isinstance(data, dict) and data.get("version") == 1
                    and isinstance(data.get("hooks"), dict) and data["hooks"],
                    f"Invalid hook config in {hook_path}: expected version 1 and non-empty hooks map")
            require((github / "skills" / hook_path.stem / "SKILL.md").is_file(),
                    f"Hook has no matching installed skill: {hook_path}")
            for event, entries in data["hooks"].items():
                require(isinstance(entries, list) and entries,
                        f"Invalid hook entries for {event} in {hook_path}")
                for entry in entries:
                    require(isinstance(entry, dict), f"Invalid hook entry for {event} in {hook_path}")
                    if entry.get("type", "command") == "command":
                        bash = entry.get("bash")
                        pwsh = entry.get("powershell")
                        require(isinstance(bash, str) and bash.strip()
                                and isinstance(pwsh, str) and pwsh.strip(),
                                f"Command hook in {hook_path} must define both bash and powershell")
                        for cmd in (bash, pwsh):
                            for match in HOOK_SCRIPT.findall(cmd):
                                target = root / Path(match.replace("\\", "/"))
                                require(target.is_file(), f"Missing hook script in {hook_path}: {match}")
    print(f"Harness OK: {len(skills)} skills and local links")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=ROOT, help="Workspace root that holds .github/")
    args = parser.parse_args()
    try:
        harness(args.root)
    except (ValueError, FileNotFoundError, OSError) as error:
        parser.exit(1, f"Validation failed: {error}\n")


if __name__ == "__main__":
    main()
