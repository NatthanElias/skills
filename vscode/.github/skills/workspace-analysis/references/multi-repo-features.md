# Multi-repository features

Feature-workflow reads this file when a feature runs in a multi-repository workspace. Each rule adds to the feature-workflow phase it names. A single-repository feature uses none of it.

## Identities and bindings

Every shared feature artifact names a repository by its `repo_id` from `docs/workspace/index.json` and a checkout by its `checkout_id`. These are identity labels, not Git instructions. Machine paths stay in `.local/workspace-bindings.json`, which maps each `repo_id:checkout_id` to a local Git root, for example `{"orders-api:primary": "/local/checkout"}`.

- In `plan.md`, `## Changes underneath` includes the `Repo` column with each row's `repo_id`.
- Cite code as `repo_id:path`, with symbol and approximate line. In `review.md`, cite every finding as `repo_id:path:line`.
- Record one entry per touched repository on `**Gates:**` (e.g., `orders-api: npm test @ <full-sha> (exit 0, 42 passed, 0 failed)`).
- Pass each touched repository's diff range (`<repo_id> (<checkout_id>): <base>..<head>`) to the fresh reviewer, and list every touched repository's commit range in `review.md`'s Audit Header (`Commits`).
- When a feature spans unrelated repositories, keep repository-specific signals clearly attributed to their `repo_id`.

## Plan

Select repositories through the workspace index, and trace consumers with the [impact procedure](../SKILL.md#impact-or-lookup). Name each consumer you did not inspect.

Run the baseline in each selected repository. `## Changes underneath` and `## Release order` list each affected repository by `repo_id`.

`## Release order` records the rollout sequence across repositories. A provider ships before the consumers that need its change. A package one selected repository consumes from another as a linked or path dependency is a code consumer: build and test the consumer against the changed provider before review, and release the provider first.

## Resume

Resolve each `repo_id:checkout_id` through `.local/workspace-bindings.json`, then check each checkout's `git log`, `git rev-parse HEAD`, and `git status --porcelain --untracked-files=all` against `**Gates:**` and `**Review:**`. Any commit or uncommitted edit after the recorded SHA invalidates that repository's gate record and requires re-running its gates before review.

## Review and completion

Each touched repository must have a clean tree (`git status --porcelain --untracked-files=all` empty), recorded `**Gates:**` matching its current `HEAD`, and its diff range included in the fresh reviewer packet before `review.md` can close the feature.
