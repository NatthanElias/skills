# Skills

Personal agent skills, grouped by harness.

```text
<harness>/         # codex/ or opencode/
  <skill-name>/
    SKILL.md
    agents/       # Optional invocation metadata
    references/   # Optional supporting guidance
    scripts/      # Optional helpers
scripts/
  install_codex.py
  install_opencode.py
```

| Harness | Custom skills | Local source |
| --- | ---: | --- |
| [Codex](codex/README.md) | 17 | `~/.codex/skills/` and `~/.agents/skills/` |
| [OpenCode](opencode/README.md) | 13 | `~/.config/opencode/skills/` |

Each skill retains its instructions, metadata, supporting files, and executable
permissions. Bundled skills, plugin packages, system-managed Omarchy skills,
and private harness configuration are excluded. Custom adaptations retain their
existing attribution files.

Add other harnesses in sibling folders, such as `claude/` or `gemini/`. Keep
their installation instructions and harness-specific metadata inside those
folders. Keep each skill's resources together so the whole folder can be copied.

Use each collection's README for installation and validation. Skills with the
same name can contain different harness-specific instructions; install each
collection into its own harness's discovery folder.
