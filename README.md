# Skills

Personal agent skills, grouped by harness.

```text
<harness>/         # codex/, opencode/, claude/ or gemini/
  <skill-name>/    # Global skill
    SKILL.md
    agents/       # Optional Codex invocation metadata
    references/   # Optional supporting guidance
    scripts/      # Optional helpers
  project/        # Project collection: skills/, agents/ and README.md
vscode/.github/   # VS Code Copilot team workflow package
scripts/
  install_codex.py
  install_opencode.py
  install_claude.py
  install_antigravity.py
  install_project.py
```

Each harness folder holds two scopes. A skill directly under `<harness>/` is global: install it into the harness's user discovery folder. `<harness>/project/` is the project collection: install it into a repository with `install_project.py`. Never install one scope into the other's location.

| Harness | Global skills | User discovery folder | Project collection |
| --- | ---: | --- | --- |
| [Codex](codex/README.md) | 12 | `~/.agents/skills/` | [`codex/project/`](codex/project/README.md) |
| [OpenCode](opencode/README.md) | 10 | `~/.config/opencode/skills/` | [`opencode/project/`](opencode/project/README.md) |
| [Claude Code](claude/README.md) | 12 | `~/.claude/skills/` | [`claude/project/`](claude/project/README.md) |
| [Antigravity](gemini/README.md) | 12 | `~/.gemini/config/skills/`, linked into `~/.gemini/antigravity-cli/skills/` | None |

The `vscode/.github/` bundle is the source of the shared skills. Each harness folder holds a port of them that names only that harness's tools, invocation syntax, and file locations. When a shared skill changes, change it in `vscode/.github/skills/` first, then port the change to each harness. Harness-native skills, such as each harness's `orchestrate`, are written for that harness and are not copied between folders. The VS Code bundle stays whole: install it by copying `vscode/.github/` into a repository.

## Skill scopes

| Skill | Scope | Harnesses | Source |
| --- | --- | --- | --- |
| `adversarial-senior-review` | Global | All | Bundle port |
| `diagnosing-bugs` | Global | All | Bundle port |
| `explain` | Global | All | Bundle port |
| `grill-me` | Global | All | Bundle port |
| `handoff` | Global | All | Bundle port |
| `technical-writing` | Global | All | Bundle port |
| `unslop` | Global | All | Bundle port |
| `writing-for-agents` | Global | All | Bundle port |
| `orchestrate` | Global | Codex, OpenCode, Claude Code, Antigravity | Harness-native, with additions from `orchestrate-vscode` |
| `escrita-academica` | Global | Codex, OpenCode, Claude Code, Antigravity | Harness-native |
| `finish-session` | Global | Codex, Claude Code, Antigravity | Harness-native |
| `natthan-workflow` | Global | Codex, Claude Code, Antigravity | Harness-native |
| `workflow-setup` | Project | VS Code, Codex, OpenCode, Claude Code | Bundle port |
| `feature-workflow` | Project | VS Code, Codex, OpenCode, Claude Code | Bundle port |
| `generate-roadmap` | Project | VS Code, Codex, OpenCode, Claude Code | Bundle port |
| `workspace-analysis` | Project | VS Code | Bundle only |
| `orchestrate-vscode` | Project | VS Code | Bundle only |

"All" means VS Code and the four harness folders. In VS Code, every skill is project-local, because the bundle installs into a repository's `.github/`. The project collections also hold two agents, a task worker and a spec verifier, ported from `vscode/.github/agents/`.

## Project collections

Each project collection ports the VS Code project workflow for one Git repository. Its README lists the skills and agents it contains and the global skills it depends on. Install one into a repository:

```bash
python3 scripts/install_project.py --harness <codex|claude|opencode> --root /path/to/repository
```

| Harness | Skills | Agents | Always-on file |
| --- | --- | --- | --- |
| Codex | `.agents/skills/` | `.codex/agents/*.toml` | `AGENTS.md` |
| Claude Code | `.claude/skills/` | `.claude/agents/*.md` | `CLAUDE.md` |
| OpenCode | `.opencode/skills/` | `.opencode/agents/*.md` | `AGENTS.md` |

Codex and OpenCode both read `AGENTS.md`. Their `workflow-setup` ports render the same harness-neutral text from the shared `docs/harness/setup-selection.json`, so either setup produces the same file. OpenCode also reads project `.claude/skills/` and `.agents/skills/`, but `.opencode/skills/` shadows the same names. Which copy wins when a project skill and a global skill share a name depends on the harness, so keep project skill names distinct from global ones. Multi-repository workspaces still need the VS Code bundle's `workspace-analysis`.

Skills with the same name contain different harness-specific instructions. Install each collection into its own harness's discovery folder, and validate each one with its own checker:

```bash
python3 <harness>/writing-for-agents/scripts/check_harness.py <harness>
python3 <harness>/writing-for-agents/scripts/check_harness.py <harness>/project/skills
```

Bundled skills, system-managed Omarchy skills, and private harness configuration are excluded. Ported skills keep their attribution files.
