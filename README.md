# Skills

Personal agent skills, grouped by harness.

```text
codex/
  <skill-name>/
    SKILL.md
    agents/       # Optional invocation metadata
    references/   # Optional supporting guidance
    scripts/      # Optional helpers
scripts/
  install_codex.py
```

The `codex/` collection contains 17 custom skills copied from the local
`~/.codex/skills/` and `~/.agents/skills/` folders. Each skill retains its
instructions, invocation policy, supporting files, and executable permissions.
Bundled OpenAI skills and system-managed Omarchy skills are excluded.

Add other harnesses in sibling folders, such as `claude/` or `gemini/`. Keep
their installation instructions and harness-specific metadata inside those
folders. Keep each skill's resources together so the whole folder can be copied.

See [the Codex collection](codex/README.md) for installation and validation.
