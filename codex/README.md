# Codex skills

## Install

Run these commands from the repository root. The installer needs Python 3 and
copies every skill, including the sibling skills referenced by other skills.

Preview a user-wide installation, then apply it:

```bash
python3 scripts/install_codex.py --target ~/.agents/skills --dry-run
python3 scripts/install_codex.py --target ~/.agents/skills
```

For a project installation, specify that project's skill folder:

```bash
python3 scripts/install_codex.py --target /path/to/project/.agents/skills
```

Codex discovers user skills in `~/.agents/skills` and project skills in
`.agents/skills`, according to the [official skill documentation](https://learn.chatgpt.com/docs/build-skills).
The `codex/` folder here stores the collection; install it into a discovery
location to use it.

The installer skips identical copies and refuses conflicting destinations
before copying anything. Back up a conflicting skill outside the discovery
folders before retrying. On a machine using both `~/.codex/skills` and
`~/.agents/skills`, keep only one installed copy of each name. This repository's
initial import leaves the existing installations in place.

Installation creates independent copies. After editing a skill in this
repository, back up its installed copy and reinstall to apply the update.
If Codex does not pick up an installed skill, restart it. Invoke a skill by its
name, for example `$grilling`. Existing explicit-only policies are preserved.

## Validate

The included checker requires Python 3 and PyYAML:

```bash
python3 codex/writing-for-agents/scripts/check_harness.py codex
```

It checks frontmatter, invocation metadata, duplicate names, and local Markdown
links. Keep relative links to supporting files intact when editing or moving a
skill. Skill-specific tools and dependencies remain documented in each
`SKILL.md`.
