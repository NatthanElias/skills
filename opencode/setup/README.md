# Install the orchestration workflow

Install Slim, the custom OpenCode skills, and the five-role workflow. You need
Python 3, OpenCode on `PATH`, and Bun with `bunx`. Authenticate to OpenCode Go
yourself with `/connect` or `opencode auth login`; this setup never reads or
exports credentials.

From the repository root, preview the setup:

```bash
python3 scripts/setup_opencode.py --install-plugin
```

Apply it while preserving existing model selections:

```bash
python3 scripts/setup_opencode.py --install-plugin --apply
```

For a fresh config, the setup selects the recommended profile. To explicitly
select the researched model profile:

```bash
python3 scripts/setup_opencode.py --install-plugin --models recommended --apply
```

Use `--models alternative` for the second choices in [the model recommendations](models.md).
These profiles are explicit selections, not automatic fallback chains. Existing
presets remain available. Use `--models preserve` (the default) to keep an
existing installation's active preset model settings.

`--config-dir /path/to/opencode` targets another installation. The default honors
`OPENCODE_CONFIG_DIR`, then `XDG_CONFIG_HOME`, then `~/.config/opencode`.
Once Slim is installed, omit `--install-plugin` to apply only the workflow.

## What changes

The setup calls Slim's native installer, pinned to `3.0.3`, with its verified
non-interactive flags. The native installer registers the plugin, adds its TUI
badge, prepares its cache, disables OpenCode's default explore/general agents,
and enables LSP when no preference exists. It preserves existing Slim config.
See [upstream installation](https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/installation.md).
The published 3.0.3 CLI no longer advertises the older `--skills` flag, so this
wrapper does not pass it.

The wrapper then copies the custom skill collection, adds managed instructions
to the five active agents, and applies their permissions across presets.
It enables orchestrator, explorer, librarian, fixer, and oracle. It disables
designer, observer, council, configured councillors, and configured custom roles
outside that set. Direct image routing uses the active model's vision capability.

Workers cannot delegate. Explorer and librarian cannot edit or use the shell.
Oracle cannot edit, but can use the shell for declared independent checks.
Its brief and role contract restrict commands and generated artifacts; this is
not an OS sandbox. Fixer receives the write ownership defined by each brief.
The orchestrator loads the orchestration skill through its normal skill tool.
Append files preserve other user instructions outside the managed block. Full
prompt replacements are retained, so review them if they contradict this workflow.

Updates use atomic file replacement and back up changed existing files under
`<config-dir>/.backups/skills-setup/<timestamp>/`, outside skill discovery.
Changed JSONC config is rewritten as formatted JSON in the same file; comments
remain in the backup. JSONC takes precedence over JSON. The setup preserves
unrelated configuration values and existing model settings by default.
It updates skill files without deleting additional local supporting files.

The upstream installer may modify files before a later step fails. The wrapper
reports its backup location; it does not claim transactional rollback of the
installer, downloaded packages, or caches. Restore the affected config/skill
files from that backup if needed.

## Launch and check

The setup creates `<config-dir>/run-opencode`. It enables background subagents
and Exa websearch for that process and selects the same config directory:

```bash
~/.config/opencode/run-opencode
```

No shell startup files are changed. Restart existing OpenCode sessions after
installation. Verify the five enabled roles in OpenCode and run a small bounded
task before using it for a larger project. A model listing confirms metadata,
not account access or successful inference. The setup itself makes no model calls.

To inspect supported models and variants on the target machine:

```bash
opencode models opencode-go --refresh --verbose
```

To check this repository's workflow and installer:

```bash
python3 codex/writing-for-agents/scripts/check_harness.py opencode
python3 -m unittest discover -s opencode/orchestrate/scripts -p 'test_*.py'
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The structural checker requires PyYAML. The scripts and their tests use Python's
standard library. Setup tests exercise an isolated fake upstream installer;
they do not launch paid agent sessions.
