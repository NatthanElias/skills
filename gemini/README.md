# Antigravity skills

Twelve skills for Google Antigravity: Antigravity ports of the shared `vscode/.github` skills, plus `orchestrate`, `escrita-academica`, `finish-session`, and `natthan-workflow`. The ports name Antigravity's `ask_question` tool. `orchestrate` dispatches workers to Codex and Claude Code through T3 Code; read its [T3 reference](orchestrate/references/t3-acp.md) before changing that workflow.

## Install

The app and IDE read global skills from `~/.gemini/config/skills/`, and the `agy` CLI reads them from `~/.gemini/antigravity-cli/skills/`. Install into the app folder, then link each skill into the CLI folder so both read one copy:

```bash
python3 scripts/install_antigravity.py --target ~/.gemini/config/skills
for skill in ~/.gemini/config/skills/*/; do ln -sfn "${skill%/}" ~/.gemini/antigravity-cli/skills/; done
```

Add `--dry-run` to preview the install. These are global skills; Antigravity has no project collection. In the CLI, run `/skills reload` after installing. See the [skill format guide](https://antigravity.google/docs/skills).

## Invoke

Run a skill as `/skill-name`, or name it in the prompt. Antigravity documents no explicit-only control, so `adversarial-senior-review` relies on its description and can still be selected automatically.

## Validate

The checker requires Python 3 and PyYAML:

```bash
python3 gemini/writing-for-agents/scripts/check_harness.py gemini
```
