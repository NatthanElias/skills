# Always-on template

Fill each `<...>` from the setup interview and drop a section that would stay empty. Keep the result short; detail belongs in skills and docs.

```markdown
<Project name>
<One sentence: what this project is.>

## Guardrails

- <Project guardrail from the interview>
- Ask before adding dependencies, creating branches, committing, pushing, deploying or touching production data. Run tests and gates before a commit. Commit messages are semantic and one line.
- Put every decision to the user through the question tool, one question each, with a recommended option.
- Work estimated under 20k tokens (file bytes / 4) stays in the main session. 20k to 150k goes to one subagent. Split larger work into pieces of 150k or less.
- A behavior change gets a fresh reviewer from another model vendor than the builder.

## Commands

| Task | Command |
|---|---|
| Build | <command> |
| Test | <command> |

## Where things live

| Doc | When to read |
|---|---|
| `.specs/features/<feature>/` | Plan, checks and verification of a feature |
| `.specs/STATE.md` | Decisions that outlive a feature |
| `.specs/LESSONS.md` | Confirmed lessons, before planning |
| `docs/research/` | Saved research |

## Additions

<!-- Add a rule here when a session shows you need it. One line each. -->
```
