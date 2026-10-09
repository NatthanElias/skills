# OpenCode skills

13 custom skills copied from `~/.config/opencode/skills/`. Supporting files and
existing attribution are preserved. The `oh-my-opencode-slim` skill is the
custom configuration workflow; the plugin itself and its private configuration
are not included.

## Install

For Slim installation, agent configuration, and the upgraded orchestration
workflow, use [the complete setup guide](setup/README.md). It includes
[two researched model choices per role](setup/models.md).

From the repository root, preview a user-wide installation, then apply it:

```bash
python3 scripts/install_opencode.py --target ~/.config/opencode/skills --dry-run
python3 scripts/install_opencode.py --target ~/.config/opencode/skills
```

For a project installation:

```bash
python3 scripts/install_opencode.py --target /path/to/project/.opencode/skills
```

These are OpenCode's native [skill discovery locations](https://docs.opencode.ai/docs/skills/).
Use them to keep OpenCode variants separate from same-named Codex skills in
shared `.agents/skills` folders.

The installer needs Python 3. It copies the full collection, skips identical
copies, and refuses conflicting destinations before copying anything. Back up
conflicting skills outside discovery folders before retrying. Installation
creates independent copies; back up an installed copy and reinstall after
editing its source here. The initial import leaves existing installations in
place.

OpenCode loads skill instructions with its native `skill` tool. Access is
controlled by OpenCode's skill permissions. Retained `agents/openai.yaml` files
are compatibility metadata; they do not configure OpenCode permissions.

Some workflows use the agents and tools from `oh-my-opencode-slim`; consult
their `SKILL.md` files for those requirements. The `codemap` workflow includes a
Node.js helper, and its examples use the global installation path. For a
project installation, run the helper from that skill's `scripts/` folder.

## Validate

The existing structural checker can also check this collection. It requires
Python 3 and PyYAML:

```bash
python3 codex/writing-for-agents/scripts/check_harness.py opencode
```

It checks names, descriptions, retained compatibility metadata, and local
Markdown links. It does not verify OpenCode permissions or the availability of
external tools and agents. Validate the two collections separately because
same-named variants are intentional.
