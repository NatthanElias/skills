# OpenCode project collection

This folder holds the OpenCode port of the VS Code project workflow for one Git repository. Install it into a repository, never into `~/`. The global OpenCode skills sit one level up, in [`opencode/`](../README.md).

## Contents

| Skill | Purpose |
| --- | --- |
| `workflow-setup` | Interviews you about the repository and writes the always-on `AGENTS.md` and the setup records under `docs/harness/`. |
| `feature-workflow` | Takes one feature from spec through plan, build, and independent review, with records under `.specs/`. |
| `generate-roadmap` | Splits a PoC, an MVP, or the next phase of an existing project, with a fixed deadline, into parallel developer fronts before feature planning. It updates the roadmap at milestones and archives each finished phase. |

| Agent | File | Role |
| --- | --- | --- |
| `task-worker` | `agents/task-worker.md` | Builder subagent on `opencode/claude-opus-5-5`. It cannot start subagents. |
| `spec-verifier` | `agents/spec-verifier.md` | Independent verifier subagent on `opencode/gpt-6.1-sol`. It cannot edit files or start subagents. |

## Dependencies

These skills call two global OpenCode skills: `@orchestrate` to delegate work, and `@grill-me` for the setup interview. Install the global collection first, as described in the [OpenCode README](../README.md). `workflow-setup` warns when either is missing.

## Install

From the skills repository root, preview the install, then apply it:

```bash
python3 scripts/install_project.py --harness opencode --root /path/to/repository --dry-run
python3 scripts/install_project.py --harness opencode --root /path/to/repository
```

The installer copies the skills into `.opencode/skills/` and the agents into `.opencode/agents/`. It skips identical copies and refuses to overwrite a different file. Then run `@workflow-setup` in the repository. `workflow-setup` sets `disable-model-invocation: true`, so it loads only when you name it. Codex and OpenCode share `AGENTS.md` and render the same text into it, so you can set up both in one repository.

## Validate

```bash
python3 opencode/writing-for-agents/scripts/check_harness.py opencode/project/skills
python3 opencode/project/skills/feature-workflow/scripts/selftest.py
```

The self-test must report 0 survived after any change to a `feature-workflow` script or reference.
