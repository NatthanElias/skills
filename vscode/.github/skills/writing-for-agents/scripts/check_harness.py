"""Check the installed .github: local links, skill front matter, and bounded helpers."""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TEMPLATE = Path(".github/skills/workflow-setup/templates/copilot-instructions.template.md")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def harness(root):
    github = root / ".github"
    template = root / TEMPLATE
    require(template.is_file(), "Missing entry template")
    # The template renders to .github/copilot-instructions.md, so its links resolve from .github.
    documents = [(template, github)] + [(path, path.parent) for path in sorted(github.rglob("*.md"))
                                        if path != template]
    for path, base in documents:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\(([^)#]+)(?:#[^)]*)?\)", text):
            if "://" in target:
                continue
            require((base / target).resolve().is_file(), f"Broken link in {path}: {target}")
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
