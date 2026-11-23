"""Check the installed .github: local links, skill front matter, and bounded helpers."""

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
TEMPLATE = Path(".github/skills/workflow-setup/templates/copilot-instructions.template.md")
INLINE_LINK = re.compile(r'\[[^\]\n]+\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\s*\)')
REFERENCE_LINK = re.compile(r'^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)', re.MULTILINE)
FENCE_RE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')


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
