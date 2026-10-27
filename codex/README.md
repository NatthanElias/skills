# Codex skills

## Install

Run these commands from the repository root. The installer needs Python 3 and
copies every skill, including the sibling skills referenced by other skills.

Preview a user-wide installation, then apply it:

```bash
python3 scripts/install_codex.py --target ~/.agents/skills --dry-run
python3 scripts/install_codex.py --target ~/.agents/skills
```

These are global skills; install them only into `~/.agents/skills`.
Repositories get the [project collection](project/README.md) instead.

Codex discovers user skills in `~/.agents/skills` and project skills in
`.agents/skills`, according to the [official skill documentation](https://learn.chatgpt.com/docs/build-skills).
The `codex/` folder here stores the collection; install it into a discovery
location to use it.

The installer skips identical copies and refuses conflicting destinations
before copying anything. Back up a conflicting skill outside the discovery
folders before retrying. Codex does not merge same-named skills, so keep the
legacy `~/.codex/skills` folder free of copies of these names.

OpenCode v2 also reads `~/.agents/skills`. See
[Keep other harnesses' skills out](../opencode/README.md#keep-other-harnesses-skills-out)
when you add a skill that has no OpenCode version.

Installation creates independent copies. After editing a skill in this
repository, back up its installed copy and reinstall to apply the update.
If Codex does not pick up an installed skill, restart it. Invoke a skill by its
name, for example `$grill-me`. Existing explicit-only policies are preserved.

## Orchestrate in T3 Code

When Codex runs inside T3 Code and the session exposes `delegate_task`,
`orchestrate` switches to T3 mode. It then dispatches the Scout to OpenCode
(`gpt-6-luna`), the Builder and the Oracle to Claude Code (Sonnet 5.5 and
Opus 5.5), and the Verifier to Codex (`gpt-6.1-sol`). Outside T3 it keeps
its native Codex roster. A repository can override the T3 roster, or select
native mode, in its `AGENTS.md`. The T3 mechanics are in
[`orchestrate/references/t3.md`](orchestrate/references/t3.md).

## Validate

The included checker requires Python 3 and PyYAML:

```bash
python3 codex/writing-for-agents/scripts/check_harness.py codex
```

It checks frontmatter, invocation metadata, duplicate names, and local Markdown
links. Keep relative links to supporting files intact when editing or moving a
skill. Skill-specific tools and dependencies remain documented in each
`SKILL.md`.
