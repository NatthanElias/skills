# Scan the workspace

Write the workspace documents owned by [workspace-analysis](../SKILL.md). Apply [writing-for-agents](../../writing-for-agents/SKILL.md), [unslop](../../unslop/SKILL.md), and [technical-writing](../../technical-writing/SKILL.md) to page wording.

## 1. Fix the scope

List all repository folders without scanning unselected repositories. Take the selected roots from setup or `docs/harness/setup-selection.json`. If neither supplies the scope, ask with the question tool and recommend the relevant repositories.

Assign stable repository and checkout IDs. Repository IDs must match `[A-Za-z0-9][A-Za-z0-9._-]*`. Confirm identity rather than equating folder names. Record local bindings in `.local/workspace-bindings.json`, full HEADs, and remotes without credentials.

Scan the working tree the user has already checked out. Checkout IDs are identity labels, not branch names. Record the current HEAD for evidence; never switch branches or revisions, create a branch, or ask the user to choose a commit. If the checkout changes during the scan, report stale evidence instead of restoring a revision.

On a rescan, select only flagged repositories unless the user requests a full scan. Keep the other index entries and pages. Apply the selected-root exclusions from the skill to every writer.

Done when every folder has a selected or not-selected status and every selected checkout has an ID, binding, and recorded identity.

## 2. Collect repository evidence

Follow [orchestrate-vscode](../../orchestrate-vscode/SKILL.md) for size routing, agent and model selection, dispatch, and parallelism.

For `main session`, collect the evidence in the main session without dispatching a helper. For `one subagent`, delegate through orchestrate-vscode. For a split route, divide the repository's evidence gathering into bounded, non-overlapping scopes within the ceiling and size each packet before dispatch. Keep every packet within its selected repository.

Evidence helpers are read-only and return reports. Independent evidence packets may run in parallel under orchestrate-vscode's rules. The main session writes the repository pages and shared documents. Record unread modules as gaps instead of claiming full coverage. On a rescan, collect evidence only for the repositories selected in step 1.

For a delegated packet, send this complete request with its bounded scope, filling every placeholder. For the main-session route, collect the same facts locally:

```text
Scan repository <repo_id>, checkout <checkout_id> at <absolute repository root>.
Recorded HEAD: <full 40-char HEAD>. Scan date: <YYYY-MM-DD>.
Checkout ID is an identity label, not a branch to switch to.
Read the current working tree. Never switch branches or revisions, create a
branch, or restore files. If HEAD differs from the recorded evidence, stop
and report the mismatch; do not check out that HEAD or scan old Git objects.
Size result: <script output>. Read scope: <repository root and exclusions>.
Target page: <absolute workspace root>/docs/workspace/repos/<repo_id>.md.
Page format: <absolute path to references/repo-page.md>; read it before writing.
Writing rules: read <absolute paths to writing-for-agents/SKILL.md,
SKILL-MECHANICS.md, unslop/SKILL.md, and technical-writing/SKILL.md>.
Read only your bounded repository scope, the target page, and these format
and writing references. Return evidence only; do not write or edit any file.
Stop at repository boundaries. Skip Git internals, secrets, build output,
and unreviewed symlinks. Cite repository files for facts and use paths relative
to the repository root in code font. Write "Unknown" for what code does not show.
Collect facts for repo-page.md's nine headings. Report unread modules in
Unknowns. Never imply that you read them.
Find controllers, listeners, schedulers, main configuration, modules, checks,
offers, calls, task start paths, and invariants enforced by code or tests.
Report HTTP methods and full paths, including controller-level prefixes.
Resolve each client's base URL to its property or constant without exposing secrets.
Report topic names and library coordinates. Keep unknown targets explicit.
Stop after replying in exactly this format:

Repository: <repo_id>
Purpose: <one line>
Type: service | library
Role: <a few words for the repository table>
Start reading: <path relative to the repository>
Check command: <command> | none found
Routes:
- <task> -> <path relative to the repository>
Offers:
- http <METHOD> <full path> -> <file>
- topic <name> -> <file>
- library <groupId:artifactId> -> <file>
Calls:
- http <METHOD> <full path> (base URL from <property or constant>) -> <file>
- topic <name> -> <file>
- library <groupId:artifactId> -> <file>
Unknowns: <what the code didn't show, or none>
```

Check each report against its packet and merge reports for a split repository. Re-dispatch a failed helper once with a complete corrected request. If that attempt fails, record the repository and missing evidence as a gap. A gap does not waive the validator's page requirements.

Done when every selected repository has checked evidence collected locally or through size-routed helpers, with unread scope and failures recorded as gaps.

## 3. Match calls to offers

In the main session, compare the reports and verify the cited files. Resolve base-URL properties to the provider where configuration permits. Keep an unresolved provider as a gap.

- Match HTTP by method and full path. Normalize variable segments such as `{x}` and `:x` to `{}` and drop trailing slashes. A URL-path match finds a client with its own DTO copy; imports do not.
- Match messaging by topic name and verify which side publishes or consumes.
- Match libraries by the artifact a selected repository builds, using `groupId:artifactId` where available.

Use the index kinds: `code` for implementation evidence, `documented` for a claim supported only by documents, `inferred` for an indirect match, and `unknown` for an unresolved dependency. Record uncertainty instead of proving absence from local tests. Keep source evidence in the source repository.

Done when every reported call and offer has a match with evidence on both sides or an explicit unmatched entry.

## 4. Write the shared documents

Write each selected repository's page under 150 lines using [repo page](repo-page.md), its header, and its nine headings. Cite the checked repository files and name unread modules under Modules. On first scan, use "None yet." under Team notes. On rescan, preserve Team notes unchanged.

Write `docs/workspace/overview.md` under 100 lines. Give each selected repository its purpose, type, stack, and a `repos/<repo_id>.md` link. Give each unselected repository one line marked "not selected", with no page.

```text
| Repository | Purpose | Type | Stack | Page |
| --- | --- | --- | --- | --- |
| id-service | Generate ID sequences | service | <language>, <framework> | <page link> |

legacy-reports: not selected.
```

Replace `<page link>` with a relative Markdown link to `repos/id-service.md` in the generated overview.

Write `docs/workspace/integrations.md` with matched links, calls with no provider found, and offers with no caller found. Name each side of a match by its repo ID and record that side's HEAD from the index in its commit column. The validator fails a matched row when either side has moved since, so on a rescan recheck every row that involves a rescanned repository and update both commit columns. Cite repository-relative files on both sides of each match. Use normalized paths for comparison and retain the observed full paths in evidence.

```text
| Caller | Caller commit | Provider | Provider commit | Contract | Kind | Caller evidence | Provider evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| orders-api | `34f2a42` | id-service | `aae21d1` | HTTP GET /api/v1/generator/{}/next | code | `orders-api:src/id_client` | `id-service:src/generator_routes` |

| Unmatched call | Evidence | Gap |
| --- | --- | --- |
| topic order.created | `orders-api:src/publisher` | No provider found |

| Unmatched offer | Evidence | Gap |
| --- | --- | --- |
| HTTP GET /health | `id-service:src/health_routes` | No caller found |
```

These rows illustrate the format; write facts from the scan, not these example paths.

Write `index.json` in the [existing format](../SKILL.md#files). Hash the evidence files with SHA-256 and include checkout identities, HEADs, sanitized remotes, and dependencies. Each non-unknown dependency has a source-file citation and hash, an observation time, and confidence. Preserve untouched entries on a partial rescan and recompute affected matches using retained evidence.

Done when overview links cover every indexed repository, integrations cover every match and gap, and index hashes describe the evidence just read.

## 5. Validate the workspace

Run from the team workspace root:

```text
python3 .github/skills/workspace-analysis/scripts/validate_workspace.py docs/workspace/index.json --bindings .local/workspace-bindings.json
```

Fix each stale or missing item within scope and rerun. If a gap prevents validation, report the blocker and leave the scan incomplete.

Done when the validator prints `Workspace OK: <n> checkouts, <m> pages`.

## 6. Return setup suggestions

Return a brief draft of 3 to 5 lines, repository rows with role and start path, task routes, and check commands or gaps. Prefix repository-relative start paths with the repository folder so they resolve from the workspace root. Suggest routes from controllers, listeners, schedulers, and configuration. Confirm each suggested path exists.

During setup, hand these suggestions to the interview. On a rescan outside setup, if `docs/harness/setup-selection.json` exists, compare suggestions with its `brief`, `repositories`, and `routes`. Show the differences and ask with the question tool which values to take. Recommend evidence-backed changes. Write only accepted values and preserve every other setting.

Run the setup preview and show the exact merged instructions:

```text
python3 .github/skills/workflow-setup/scripts/setup.py docs/harness/setup-selection.json
```

Apply with `--apply` only after approval. Only the accepted marked brief, repository, and route parts may change. Team rules are never touched. If the preview includes another change, stop before applying and resolve that difference.

Done when setup has the suggestions, or the standalone rescan has returned them and completed any approved preview and apply.