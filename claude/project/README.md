# Claude Code project collection

This folder holds the Claude Code port of the VS Code project workflow for one Git repository. Install it into a repository, never into `~/`. The global Claude Code skills sit one level up, in [`claude/`](../README.md).

## Contents

| Skill | Purpose |
| --- | --- |
| `workflow-setup` | Interviews you about the repository and writes the always-on `CLAUDE.md` and the setup records under `docs/harness/`. |
| `feature-workflow` | Takes one feature from spec through plan, build, and independent review, with records under `.specs/`. |
| `generate-roadmap` | Splits a PoC, an MVP, or the next phase of an existing project, with a fixed deadline, into parallel developer fronts before feature planning. It updates the roadmap at milestones and archives each finished phase. |

| Agent | File | Role |
| --- | --- | --- |
| `task-worker` | `agents/task-worker.md` | Builder. It edits files and runs commands on `sonnet`. |
| `spec-verifier` | `agents/spec-verifier.md` | Independent verifier. It reads and runs checks but does not edit, on `opus`. |

## Dependencies

These skills call two global Claude Code skills: `/orchestrate` to delegate work, and `/grill-me` for the setup interview. Install the global collection first, as described in the [Claude Code README](../README.md). `workflow-setup` warns when either is missing.

## Install

From the skills repository root, preview the install, then apply it:

```bash
python3 scripts/install_project.py --harness claude --root /path/to/repository --dry-run
python3 scripts/install_project.py --harness claude --root /path/to/repository
```

The installer copies the skills into `.claude/skills/` and the agents into `.claude/agents/`. It skips identical copies and refuses to overwrite a different file. It also adds a session-start hook to `.claude/settings.json` that states the newest feature handoff when a session resumes or compacts, keeping the hooks already there. Then run `/workflow-setup` in the repository. `workflow-setup` sets `disable-model-invocation: true`, so only you can start it.

Feature-workflow can also make Git run its commit checks in a clone. It asks before installing them, because they check your own commits too:

```bash
python3 .claude/skills/feature-workflow/scripts/git_hooks.py install
```

## Validate

```bash
python3 claude/writing-for-agents/scripts/check_harness.py claude/project/skills
python3 claude/project/skills/feature-workflow/scripts/selftest.py
python3 claude/project/skills/feature-workflow/scripts/test_git_hooks.py
```

The self-test must report 0 survived after any change to a `feature-workflow` script or reference.
