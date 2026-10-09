# Skill mechanics

Read this reference when writing a skill's packaging, discovery policy, or routing. Shared writing rules live in [SKILL.md](SKILL.md).

## Codex packaging

Each skill directory contains `SKILL.md` with YAML frontmatter between `---` lines. Keep nonempty `name` and `description` fields for both invocation modes. Match the directory name with lowercase letters, digits, and hyphens. The body carries instructions; supporting files hold conditional references and helpers.

Resolve installed paths through the catalog. This setup uses `~/.codex/skills/` and `~/.agents/skills/` globally; project skills use `.agents/skills/`. Keep one active copy of a name across user roots. Explicit invocation uses `$skill-name`.

## Invocation

Automatic discovery is the default. The description explains the workflow and its trigger branches. The body and supporting references load when needed. Keep descriptions short because they can occupy discovery context even when the body is not needed.

For explicit-only invocation, keep the required description and put the policy in `agents/openai.yaml`:

```yaml
interface:
  display_name: "Skill label"
  short_description: "Brief description of the skill"
policy:
  allow_implicit_invocation: false
```

This policy defaults to `true`. Set it to `false` only at the user's request or to preserve an existing explicit-only policy. Preserve unrelated interface and dependency fields. Copilot's `disable-model-invocation`, `user-invocable`, and agent-file conventions are not Codex invocation controls. Do not transfer them into new frontmatter.

Explicit-only controls automatic selection. It does not authorize actions, enforce a sandbox, or establish zero runtime context cost. Do not assume another skill can automatically trigger an explicit-only skill. Shared rules needing automatic reach should remain normally discoverable or live in a plain reference reached by a supported pointer.

## Splitting and routing

Split by invocation when a distinct workflow needs its own trigger or another workflow must discover it. The new description spends discovery context, so its independent reach must justify it. Use the sequence-cut rules in [SKILL.md](SKILL.md) when later steps distract from a current gate.

A router can explain which skill fits each task and help the user choose an invocation. It cannot change another skill's policy or bypass a required decision. Store shared reference once and link it from the workflows that need it.

Check the installed client and [official skill documentation](https://learn.chatgpt.com/docs/build-skills) when packaging or discovery is uncertain. New sessions pick up the updated catalog; restart Codex if a change does not appear.
