# Claude Code skills

Twelve skills for Claude Code: Claude Code ports of the shared `vscode/.github` skills, plus `orchestrate`, `escrita-academica`, `finish-session`, and `natthan-workflow`.

## Install

From the repository root, preview a user-wide installation, then apply it:

```bash
python3 scripts/install_claude.py --target ~/.claude/skills --dry-run
python3 scripts/install_claude.py --target ~/.claude/skills
```

These are global skills; install them only into `~/.claude/skills/`. Repositories get the [project collection](project/README.md) instead.

The installer skips identical copies and refuses conflicting destinations before copying anything. Back up a conflicting skill outside `~/.claude/skills/` before retrying. A personal skill overrides a project skill of the same name. Start a fresh session to pick up changes.

OpenCode v2 also reads `~/.claude/skills/`. See [Keep other harnesses' skills out](../opencode/README.md#keep-other-harnesses-skills-out) when you add a skill that has no OpenCode version.

## Invoke

Invoke a skill as `/skill-name`, for example `/explain`. `adversarial-senior-review` sets `disable-model-invocation: true`, so only you can start it.

## Validate

The checker requires Python 3 and PyYAML:

```bash
python3 claude/writing-for-agents/scripts/check_harness.py claude
```

It checks Claude Code frontmatter, invocation fields, duplicate names, and local Markdown links.
