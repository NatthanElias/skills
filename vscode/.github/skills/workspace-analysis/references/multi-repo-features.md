# Multi-repository features

Feature-workflow reads this file when a feature runs in a multi-repository workspace. Each rule adds to the feature-workflow phase it names. A single-repository feature uses none of it.

## Identities and bindings

Every shared feature artifact names a repository by its `repo_id` from `docs/workspace/index.json` and a checkout by its `checkout_id`. These are identity labels, not Git instructions. Machine paths stay in `.local/workspace-bindings.json`, which maps each `repo_id:checkout_id` to a local Git root, for example `{"orders-api:primary": "/local/checkout"}`.

- `checks.md` names the selected checkouts on one line after `UI:`, comma-separated: `Repositories: orders-api:primary, billing-worker:main`.
- Cite code as `repo_id:path`, with symbol and approximate line. In a review round, cite implementation, assertion, and mutation location as `repo_id:path:line`.
- `review_files` entries are `repo_id:path`, `repo_id:checkout_id:path`, or a workspace-relative path.
- Each row of the round's `repositories` list carries `repo_id`, `checkout_id`, `head`, and `fingerprint`, one row per selected checkout.
- Gate records name the repository ID they ran in.
- A pause handoff lists the selected repository IDs and their fingerprints.
- When a feature spans unrelated repositories, keep repository-specific signals in a report for that repository.

## Plan

Select repositories through the workspace index, and trace consumers with the [impact procedure](../SKILL.md#impact-or-lookup). Name each consumer you did not inspect.

Run the baseline in each selected repository. Impact gets one row per repository with its repo ID.

Impact also gives the release order across repositories. A provider ships before the consumers that need its change. A package one selected repository consumes from another as a linked or path dependency is a code consumer: build and test the consumer against the changed provider before review, and release the provider first.

## Resume

Resolve each `repo_id:checkout_id` through `.local/workspace-bindings.json`, then capture each checkout's current HEAD, status, and fingerprint. A changed fingerprint in any selected checkout makes that repository's earlier proof stale.

## Complete

Run feature-workflow's complete-stage validator from the workspace root, and add `--bindings .local/workspace-bindings.json` to the command its verify reference gives. The validator fingerprints each bound checkout and requires a report row for every checkout `checks.md` names.
