# Codex project collection

This folder holds the Codex port of the VS Code project workflow for one Git repository. Install it into a repository, never into `~/`. The global Codex skills sit one level up, in [`codex/`](../README.md).

## Contents

| Skill | Purpose |
| --- | --- |
| `workflow-setup` | Interviews you about the repository and writes the always-on `AGENTS.md` and the setup records under `docs/harness/`. |
| `feature-workflow` | Takes one feature from spec through plan, build, and independent review, with records under `.specs/`. |
| `generate-roadmap` | Splits a PoC, an MVP, or the next phase of an existing project, with a fixed deadline, into parallel developer fronts before feature planning. It updates the roadmap at milestones and archives each finished phase. |

| Agent | File | Role |
| --- | --- | --- |
| `task_worker` | `agents/task_worker.toml` | Builder, on `gpt-6.1-sol` with high reasoning effort. |
| `spec_verifier` | `agents/spec_verifier.toml` | Independent verifier, on `gpt-6-astra` with medium reasoning effort. |

## Dependencies

These skills call two global Codex skills: `$orchestrate` to delegate work, and `$grill-me` for the setup interview. Install the global collection first, as described in the [Codex README](../README.md). `workflow-setup` warns when either is missing.

## Install

From the skills repository root, preview the install, then apply it:

```bash
python3 scripts/install_project.py --harness codex --root /path/to/repository --dry-run
python3 scripts/install_project.py --harness codex --root /path/to/repository
```

The installer copies the skills into `.agents/skills/` and the agents into `.codex/agents/`. It skips identical copies and refuses to overwrite a different file. Then run `$workflow-setup` in the repository. `workflow-setup` sets `policy.allow_implicit_invocation: false` in its `agents/openai.yaml`, so only you can start it. Codex and OpenCode share `AGENTS.md` and render the same text into it, so you can set up both in one repository.

## Validate

```bash
python3 codex/writing-for-agents/scripts/check_harness.py codex/project/skills
python3 codex/project/skills/feature-workflow/scripts/selftest.py
```

The self-test must report 0 survived after any change to a `feature-workflow` script or reference.
