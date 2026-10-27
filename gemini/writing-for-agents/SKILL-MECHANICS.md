# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Every Antigravity skill is model-invoked. The agent reads each skill's name and `description` at conversation start, reads the full `SKILL.md` when the description fits the request, and follows it. The user can also run a skill as `/skill-name` or name it in the prompt. The description is the skill's top-level context pointer, forced to stay loaded at all times: permanent context load in exchange for discoverability. A skill whose content is all reference is also one home for shared reference: another skill can point at it, so reference needed by several skills lives in one place.

Antigravity documents no explicit-only control. A skill meant to fire only by hand still costs its description and can still be selected. Write that description narrowly: say what the skill does, and name the slash command as its trigger. When a procedure must never fire on its own, keep it in a plain file outside the skill system and point at it from the rule or skill that needs it.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one skill that names the others and when to reach for each, so the human has one skill to remember instead of many.

## Antigravity packaging

Each skill directory contains `SKILL.md` with YAML frontmatter between `---` lines, holding `name` and `description`. Use a lowercase, hyphenated `name` that matches the directory. Write the description in the third person, stating what the skill does and when to use it. Other frontmatter fields are not documented; leave out Codex's `agents/openai.yaml` and Claude Code's invocation fields.

Optional folders are `scripts/` for executable helpers, `examples/` for reference implementations, `resources/` for templates and data, and `references/` for detailed documentation. Link each one relatively from `SKILL.md`. Tell the agent to run a script with `--help` before reading its source.

Check the [official skill documentation](https://antigravity.google/docs/skills) when packaging or discovery is uncertain.
