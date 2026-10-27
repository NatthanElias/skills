# OpenCode skills

Ten skills for OpenCode v2: OpenCode ports of the shared `vscode/.github` skills, plus `orchestrate` and `escrita-academica`. `orchestrate` uses OpenCode's built-in `explore` and `general` subagents through the `subagent` tool.

## Install

From the repository root, preview a user-wide installation, then apply it:

```bash
python3 scripts/install_opencode.py --target ~/.config/opencode/skills --dry-run
python3 scripts/install_opencode.py --target ~/.config/opencode/skills
```

For a project installation:

```bash
python3 scripts/install_opencode.py --target /path/to/project/.opencode/skills
```

The installer needs Python 3. It copies the full collection, skips identical copies, and refuses conflicting destinations before copying anything. Back up conflicting skills outside discovery folders before retrying. Installation creates independent copies; back up an installed copy and reinstall after editing its source here.

## Keep other harnesses' skills out

OpenCode v2 also loads global skills from `~/.claude/skills/` and `~/.agents/skills/`, which hold the Claude Code and Codex collections. `~/.config/opencode/skills/` takes precedence over both, so every skill with an OpenCode version shadows its Claude Code and Codex copies. Hide the skills that exist only in the other collections with `skill` deny rules in `~/.config/opencode/opencode.json`:

```json
"permissions": [
  { "action": "skill", "resource": "finish-session", "effect": "deny" },
  { "action": "skill", "resource": "natthan-workflow", "effect": "deny" }
]
```

Add a rule whenever a Claude Code or Codex skill has no OpenCode version.

## Subagents

`orchestrate` needs the built-in `explore` and `general` agents. Leave them enabled in `opencode.json`. The `subagent` tool takes no model, so a subagent runs on its agent's configured `model` or on the parent session's model. For a reviewer on another model family, add a custom agent with its own `model` under `~/.config/opencode/agents/`.

## Invoke

The model loads skills with the `skill` tool. To ask for one by name, mention it as `@skill-id`, for example `@handoff`. `adversarial-senior-review` sets `disable-model-invocation: true`, so it loads only when named.

## Validate

The checker requires Python 3 and PyYAML:

```bash
python3 opencode/writing-for-agents/scripts/check_harness.py opencode
```

It checks names, descriptions, OpenCode frontmatter, and local Markdown links. It does not verify permissions or the availability of tools and agents.
