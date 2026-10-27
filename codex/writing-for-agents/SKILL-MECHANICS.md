# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously, and other skills can reach it. You can still type its name: model-invocation always _includes_ user reach; a description only ever adds agent discovery, never removes the human's. The description is the skill's top-level context pointer, forced to stay loaded at all times: permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place. Mechanics: leave `policy.allow_implicit_invocation` unset in `agents/openai.yaml`, since it defaults to `true`, and write a model-facing description carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full).
- A **user-invoked** skill strips the description from the agent's reach: only the human typing its name can invoke it, and no other skill can. Codex may still list its name and description, so the saving is unwanted automatic selection rather than context; it spends cognitive load: you are the index that must remember it exists. Mechanics: set `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. The `description` stays required; make it a human-facing one-line summary with the trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and keep its description short.

Shared reference that two user-invoked skills both need can live in neither: with no descriptions, neither can fire the other. Push it to a plain file outside the skill system: external reference any skill can point at.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others and when to reach for each, so the human has one skill to remember instead of many. It can only hint, never fire them: user-invoked skills have no description, so nothing but the human can reach them.

## Codex packaging

Each skill directory contains `SKILL.md` with YAML frontmatter between `---` lines. Keep nonempty `name` and `description` fields for both invocation modes. Match the directory name with lowercase letters, digits, and hyphens. Explicit invocation uses `$skill-name`.

User skills use `~/.agents/skills/`; project skills use `.agents/skills/`. Keep one copy of each name across roots.

`agents/openai.yaml` carries the display text and the invocation policy:

```yaml
interface:
  display_name: "Skill label"
  short_description: "Brief description of the skill"
policy:
  allow_implicit_invocation: false
```

Add `policy` only for an explicit-only skill. Copilot's and Claude Code's `disable-model-invocation`, `user-invocable`, and `argument-hint` are not Codex controls, so leave them out of the frontmatter. Explicit-only controls automatic selection. It does not authorize actions or enforce a sandbox.

Check the [official skill documentation](https://learn.chatgpt.com/docs/build-skills) when packaging or discovery is uncertain. New sessions pick up the updated catalog; restart Codex if a change does not appear.
