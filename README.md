# Skills

Personal agent skills, grouped by harness.

```text
<harness>/         # codex/, opencode/ or gemini/
  <skill-name>/
    SKILL.md
    agents/       # Optional invocation metadata
    references/   # Optional supporting guidance
    scripts/      # Optional helpers
scripts/
  install_codex.py
  install_opencode.py
  setup_opencode.py
```

| Harness | Custom skills | Local source |
| --- | ---: | --- |
| [Codex](codex/README.md) | 18 | `~/.codex/skills/` and `~/.agents/skills/` |
| [OpenCode](opencode/README.md) | 14 | `~/.config/opencode/skills/` |

Each skill retains its instructions, metadata, supporting files, and executable
permissions. Bundled skills, plugin packages, system-managed Omarchy skills,
and private harness configuration are excluded. Custom adaptations retain their
existing attribution files.

The [Antigravity skills](gemini/README.md) folder contains skills for Google
Antigravity. Add other harnesses in sibling folders and keep their installation
instructions and harness-specific metadata inside those folders. Keep each
skill's resources together so the whole folder can be copied.

Use each collection's README for installation and validation. Skills with the
same name can contain different harness-specific instructions; install each
collection into its own harness's discovery folder.

For a complete OpenCode installation with Slim and the five-role workflow,
see [OpenCode setup](opencode/setup/README.md).
