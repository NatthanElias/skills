# Skills

Personal agent skills, grouped by harness.

```text
<harness>/         # codex/, opencode/, claude/ or gemini/
  <skill-name>/
    SKILL.md
    agents/       # Optional Codex invocation metadata
    references/   # Optional supporting guidance
    scripts/      # Optional helpers
  project/        # Optional project collection: skills/ and agents/
vscode/.github/   # VS Code Copilot team workflow package
scripts/
  install_codex.py
  install_opencode.py
  install_claude.py
  install_antigravity.py
  install_project.py
```

| Harness | Custom skills | Global discovery folder |
| --- | ---: | --- |
| [Codex](codex/README.md) | 12 | `~/.agents/skills/` |
| [OpenCode](opencode/README.md) | 10 | `~/.config/opencode/skills/` |
| [Claude Code](claude/README.md) | 12 | `~/.claude/skills/` |
| [Antigravity](gemini/README.md) | 12 | `~/.gemini/config/skills/`, linked into `~/.gemini/antigravity-cli/skills/` |

The `vscode/.github/` bundle is the source of the shared skills: `adversarial-senior-review`, `diagnosing-bugs`, `explain`, `grill-me`, `handoff`, `technical-writing`, `unslop`, and `writing-for-agents`. Each harness folder holds a port of those skills that names only that harness's tools, invocation syntax, and file locations. When a shared skill changes, change it in `vscode/.github/skills/` first, then port the change to each harness.

Harness-specific skills, such as each harness's `orchestrate`, are written for that harness and are not copied between folders. The VS Code workflow skills (`workflow-setup`, `feature-workflow`, `workspace-analysis`, `orchestrate-vscode`, and `generate-mvp-roadmap`) and its agents stay project-local; install them by copying `vscode/.github/` into a repository.

## Project collections

`codex/project/`, `claude/project/`, and `opencode/project/` hold ports of the VS Code project workflow for one Git repository: `workflow-setup`, `feature-workflow`, `generate-mvp-roadmap`, and the builder and verifier agents. They are installed into a repository, not globally:

```bash
python3 scripts/install_project.py --harness <codex|claude|opencode> --root /path/to/repository
```

| Harness | Skills | Agents | Always-on file |
| --- | --- | --- | --- |
| Codex | `.agents/skills/` | `.codex/agents/*.toml` | `AGENTS.md` |
| Claude Code | `.claude/skills/` | `.claude/agents/*.md` | `CLAUDE.md` |
| OpenCode | `.opencode/skills/` | `.opencode/agents/*.md` | `AGENTS.md` |

Codex and OpenCode both read `AGENTS.md`. Their `workflow-setup` ports render the same harness-neutral text from the shared `docs/harness/setup-selection.json`, so either setup produces the same file. OpenCode also reads project `.claude/skills/` and `.agents/skills/`, but `.opencode/skills/` shadows the same names. Each port relies on its harness's global `orchestrate` and `grill-me`. Multi-repository workspaces still need the VS Code package's `workspace-analysis`.

Skills with the same name contain different harness-specific instructions. Install each collection into its own harness's discovery folder, and validate each one with its own checker:

```bash
python3 <harness>/writing-for-agents/scripts/check_harness.py <harness>
```

Bundled skills, system-managed Omarchy skills, and private harness configuration are excluded. Ported skills keep their attribution files.
