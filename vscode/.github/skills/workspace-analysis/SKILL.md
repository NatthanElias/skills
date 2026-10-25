---
name: workspace-analysis
description: "Scan or rescan a workspace, trace cross-repository impact, or refresh stale workspace evidence."
---

# Workspace analysis

Own `docs/workspace/` and `.local/workspace-bindings.json` at the team's workspace root. Keep scan output in that workspace; never commit it to the package.

Inspect only the selected roots, whether they come from a parent directory or a multi-root workspace. Stop at repository boundaries. Skip Git internals, secrets, build output, and symlinks nobody has reviewed.

Give each repository a stable `repo_id` and each checkout a `checkout_id`. Two folders with the same name are not the same repository. Bind local paths in `.local/workspace-bindings.json`.

## Documents

| Path | Contents | Limit |
| --- | --- | --- |
| `docs/workspace/overview.md` | Purpose, type, stack, and page link per selected repository; one line per unselected repository | Under 100 lines |
| `docs/workspace/integrations.md` | Matched calls and offers, file evidence on both sides, and unmatched calls and offers | No fixed line limit |
| `docs/workspace/repos/<repo_id>.md` | Repository facts, entry points, task routes, integrations, invariants, and Team notes | Under 150 lines; exact headings in [repo page](references/repo-page.md) |
| `docs/workspace/index.json` | Checkout identities, evidence hashes, and dependencies | Format below |
| `.local/workspace-bindings.json` | Local checkout paths | Local only |

## Scan

When setup requests a scan, the user requests a scan or rescan, or `docs/workspace/` is missing, read [scan](references/scan.md). Follow it to the end, including validation and suggestions.

## Impact or lookup

Run the validator before reusing workspace evidence. If it flags a repository, rescan that repository through [scan](references/scan.md). Keep other repositories' pages unless the user requests a full scan.

Read `overview.md`, `integrations.md`, and the involved repository pages. Then trace the consumers below. Recheck manifests, instructions, and CI that are not listed as evidence. Expand only the consumers the current change affects.

Done when the validator passes and each affected consumer has evidence or an explicit gap.

## Features across repositories

This skill owns feature-workflow's multi-repository rules: repository identities, bindings, per-repository fingerprints, release order, and linked packages. They live in [multi-repository features](references/multi-repo-features.md), which feature-workflow reads unless the always-on instructions record `Repositories: single`. A single-repository install leaves this skill out, so keep those rules here and out of feature-workflow.

## Consumers

A consumer is a repository that uses the one you are changing. It imports its code, calls it at runtime, or both. Look for each kind separately, since one never proves the other:

- **Code consumers.** Check build manifests for the shared library. For a shared class, run the editor's find-all-references first. It covers only repositories open in the workspace, so fall back to text search for the rest.
- **Runtime consumers.** Search HTTP and messaging clients for the service's URL paths or topics. These clients often declare their own copies of the request and response classes, so no import links them to the service. The service's API spec lists what it offers, not who calls it.

`docs/workspace/index.json` is the evidence record. Every dependency has a `kind`: `code`, `documented`, `inferred` or `unknown`. A consumer you could not find stays `unknown`. Local tests cannot show that an integration is absent.

## Files

`.local/workspace-bindings.json` maps each `repo_id:checkout_id` to a local path:

```json
{"orders-api:main": "C:/src/orders-api", "billing-worker:main": "C:/src/billing-worker"}
```

In `docs/workspace/index.json`, evidence paths are relative to their repository root, and a dependency's evidence sits in its source repository. An `unknown` dependency may target a repository that is not selected and needs no evidence.

```json
{
  "repositories": [
    {"repo_id": "orders-api", "checkout_id": "main", "head": "<sha>", "remote": "https://host/org/orders-api.git",
     "evidence": [{"path": "<manifest>", "sha256": "<hash>"}]}
  ],
  "dependencies": [
    {"source": ["billing-worker", "main"], "target": ["orders-api", "main"], "kind": "code", "type": "shared type",
     "symbol": "OrderEvent", "evidence": {"path": "<manifest>", "sha256": "<hash>"}, "observed": "<ISO time>", "confidence": "high"}
  ]
}
```

Store the remote without credentials. After every write, run:

```
python3 .github/skills/workspace-analysis/scripts/validate_workspace.py docs/workspace/index.json --bindings .local/workspace-bindings.json
```

It checks the index, evidence, and documents, the HEADs recorded in `integrations.md`, and that the pages match `selected_repositories` in `docs/harness/setup-selection.json` when present. It prints `Workspace OK: <n> checkouts, <m> pages` or exits non-zero with the first stale or missing item. A warning about uncommitted changes means the pages describe the last commit only; read the changed files directly.