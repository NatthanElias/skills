---
name: workflow-setup
description: Interview a team and install or reconfigure their workflow. Use when setting up for selected repositories, changing team choices, adding a repository, or syncing the package from ai-core-workflow.
user-invocable: true
disable-model-invocation: true
---

# Workflow setup

## 1. Choose repositories

List the repository folders and ask which to include with the question tool. Recommend the roots relevant to the team's work. Keep unselected repositories outside the scan.

The workspace is single-repository when its root is a Git repository or the team selects exactly one repository. Ask the team to confirm it with the question tool, since someone may have opened one repository of a larger system. A single repository takes its ID from its folder name, unless the team gives another. Selecting a second repository later makes the workspace multi-repository: rerun setup with `single_repository` false and workspace-analysis selected, restoring its folder if it was deleted by running [Sync the package](#sync-the-package).

Use each repository's current checkout. The user supplies the correct branch. Never switch branches or revisions, create a branch, or ask the team to choose a commit for setup. Record the current HEAD only as scan evidence.

Done when the team has confirmed the selected roots and whether the workspace is single- or multi-repository.

## 2. Scan a multi-repository workspace once

Skip this step for a single repository. Its install leaves out workspace-analysis, and step 3 reads the repository directly.

Otherwise run workspace-analysis (`.github/skills/workspace-analysis/SKILL.md`) through its full scan procedure. Reuse its repository facts in the interview rather than scanning again. When adding a repository later, scan only that repository and retain existing evidence and pages.

Done when the workspace is single-repository, or when the workspace validator prints `Workspace OK: <n> checkouts, <m> pages` and the scan returns a brief, repository rows, task routes, and check suggestions.

## 3. Read and interview

Read the selected roots' instructions, CI files, document indexes, and `docs/harness/setup-selection.json` when present. Use the scan for repository facts and IDs. For a single repository, read its instructions, manifests, and CI yourself, and suggest the brief, repository row, task routes, and check commands from them. A new repository with no build or test command records its check as a validation gap; its first feature adds the commands. Ask only for decisions the team owns.

Discover available skills from `.github/skills/*/SKILL.md`, including the team's own skills. Recommend only those relevant to the project.

Setup uses `grill-me` for the interview and, in a multi-repository workspace, `workspace-analysis` for the scan. The scan also uses the core `orchestrate-vscode`, `writing-for-agents`, `unslop`, and `technical-writing` tools; keep these in a setup-capable bundle. Installing this bundle does not require a team to use every shipped skill. Select `feature-workflow` only when the team wants it; its dependencies apply only when selected. Defaults never add an absent skill.

Skill folder names use lowercase letters, digits, and dashes, beginning with a letter or digit.

Find the team standards skill or document and propose a Team additions line that names it. When none exists, tell the team to supply one, and offer writing-for-agents to turn their standards into a skill.

Load `grill-me` for the interview, with three changes:

- Recommend the scan's suggestions and the default where one exists.
- Offer defer or skip on every optional choice.
- End the interview when each setting is accepted, deferred, or skipped: project ID, repositories and whether the workspace is single-repository, skills, feature document location, checks or gaps per repository, delegation, authoritative documents, brief, repository rows, and task routes. Reuse an existing project ID or propose a lowercase ID from the project name. The team confirms, edits, or drops each suggested route.

Leave commit policy out of the setup interview. Preserve an existing policy; otherwise use "Local commits under an approved plan; push, force-push, deploy, and production data need explicit approval". Setup never commits.

Review routing is fixed in orchestrate-vscode, so leave it out of the interview. Team policy takes priority over a  default. When two applicable instructions conflict, show the conflict and let the team resolve it. Every setting stays within the user's own authority. Keep personal settings in `.local/`, and add them only when the user asks.

### Team choices and personal choices

Team choices govern shared work: project ID, repository scope, enabled skills, feature-document location, checks, delegation, authoritative documents, brief, repository roles, and task routes. Record accepted choices in the selection and show their exact merged preview before apply. Shared one-line additions, including the team standards line, belong in `## Team additions` outside setup's marked parts. Preserve the team's commit policy without reopening it in the interview.

Personal choices affect only the requesting developer: preferred response language, explanation length, editor habits, or model preferences within the team's delegation rules. Store them in `.local/` only when requested. Keep them out of shared generated instructions and the setup selection. Setup does not generate or automatically load a personal-preference file. Read or link that file explicitly when using it.

Machine-local facts are separate from personal preferences. The scan writes checkout paths in `.local/workspace-bindings.json`; HEADs and evidence hashes describe the checkout, not choices to interview about. Personal preferences cannot relax team checks, review requirements, or approval gates. A developer may run setup on the team's behalf only for decisions within their authority.

## 4. Write the selection

Write the accepted choices to `docs/harness/setup-selection.json`. Leave out `skills` to select all available installed skills. `feature-workflow` needs `orchestrate-vscode`, and `workflow-setup` needs `grill-me`; in a multi-repository workspace both also need `workspace-analysis`. `explain` needs `unslop`. In a multi-repository workspace, take repository IDs from the workspace index; for a single repository, use the ID confirmed in step 1. List each document as a label and a relative path.

For a single repository, add `"single_repository": true`. Setup then requires exactly one selected repository, leaves `workspace-analysis` out of the default skills, refuses it in an explicit list, and writes `Repositories: single` in the always-on repository section. Without the key, setup writes `Repositories: multi`.

Setup accepts a legacy `"domains": []` and refuses any other `domains` value. Move those rules into the team standards, then remove the key.

Add `package_source`, the HTTPS URL of ai-core-workflow. Ask the team for the URL they cloned `.github/` from on adoption, and drop any `user:token@` before the host. The selection is committed, so setup refuses a URL with a user name or token. For an SSH URL, ask the team for the HTTPS URL. Setup puts the URL in the README section and the sync line (step 5), and each sync clones the package from it. Older selections without it still validate, and both then name the package without a link.

```json
{"project": "catalog", "selected_repositories": ["catalog-api", "catalog-web"],
 "package_source": "https://git.example.com/platform/ai-core-workflow.git",
 "brief": "Catalog API stores product records.\nCatalog web displays and edits products.\nThe web app calls the API over HTTP.",
 "repositories": {"catalog-api": {"role": "Product records", "start": "catalog-api/src/"},
                  "catalog-web": {"role": "Product browsing and editing", "start": "catalog-web/src/"}},
 "routes": [{"task": "Change product intake", "start": "catalog-api/src/"}],
 "skills": ["workflow-setup", "workspace-analysis", "grill-me", "feature-workflow", "orchestrate-vscode"],
 "checks": {"catalog-api": "npm test"}, "feature_root": ".specs/features/<feature>/",
 "delegation": "Helpers allowed; parallel writes not allowed",
 "commits": "Local commits under an approved plan; push, force-push, deploy, and production data need explicit approval",
 "documents": {"Architecture": "docs/architecture/"}, "deferred": ["model preference"]}
```

Use repository IDs matching `[A-Za-z0-9][A-Za-z0-9._-]*`. Keys in `repositories` must name selected IDs. Each row has `role` and `start`; each route has `task` and `start`.

Use a lowercase project ID matching `[a-z0-9][a-z0-9-]*`. Older selections without one use the neutral fallback `project`.

Keep `brief` to 1 to 5 lines, aiming for 3 to 5. Exclude HTML comment markers from the brief, roles, and tasks. Roles and tasks are single table cells without newlines or `|`. Start paths are relative to the workspace root and must exist there. Use forward slashes and exclude absolute paths, `..`, colons, backticks, and table separators. Preview and validation fail on a missing start path.

The three new keys are optional for older selections. When absent, the entry records gaps; a selected repository without a row shows "Not scanned".

Done when the selection records only accepted choices and all start paths exist.

## 5. Preview and apply

From the workspace root, preview the changes:

```text
python3 .github/skills/workflow-setup/scripts/setup.py docs/harness/setup-selection.json
```

Show the exact merged preview to the team. After they accept it, run the same command with `--apply`. On a first install, apply before anyone edits a shipped file: the first `--apply` records every installed package file as the package baseline, so an earlier edit would count as package content. It writes `.github/copilot-instructions.md` and a package section in the root `README.md`, records hashes of its output and the selection, plus the installed skill names, in `docs/harness/setup-ownership.json`, and adds `.local/` to `.gitignore`. With feature-workflow selected it also adds the feature folder root, normally `.specs/features/`, because feature documents are working files; `.specs/constraints/`, `.specs/lessons/`, and `.specs/LESSONS.md` stay committed. When the project still holds feature-workflow's retired decisions table, setup prints a notice to convert it with feature-workflow's `constraints.py migrate`. A change the team already approved exactly as shown needs no second approval. Add `--root <workspace>` to target another workspace.

The always-on file contains the brief, repository table, task routes, checks, workspace document links, and team rules. It has no skill list and stays under 120 lines. Each generated body uses `<!-- setup:<name> -->` and `<!-- /setup:<name> -->` markers. The parts are `brief`, `repositories`, `routes`, `checks`, `documents`, and `team`, in that order. The brief sits directly under the title; the other parts have their own headings outside the markers.

The repository section starts with `Repositories: single` or `Repositories: multi`, followed by the table `Repository | Role | Start reading`. Task routes use `To | Start at`. Checks give one line per selected repository with its command or "No command established; validation gap". When workspace-analysis is selected, documents link to `../docs/workspace/overview.md` and `../docs/workspace/integrations.md` and give the page pattern `docs/workspace/repos/<repo>.md`.

Team rules include the project ID for lessons and review rounds, commits, and delegation. Keep the orchestrate-vscode pointer before dispatch, research, or review of code, configuration, dependency, build, or test changes. Include the feature document root and the rule to run feature-workflow's `constraints.py list` before changing code when feature-workflow is selected; that rule also says `docs/roadmap/DECISIONS.md` is for people, never a coding constraint. List authoritative documents in a label-and-backtick-path table. Keep the rule "Keep personal choices in `.local/`. Ask before push, publication, deployment, or production data changes." End with `## Team additions`, a comment that setup rewrites only marked parts and the team adds one-line rules there, the question-tool line, and the package sync line. The template seeds both lines on first install, and the team owns them afterwards. Setup changes the sync line in two cases. When the line is missing, setup adds it back. When it names no URL, setup inserts `The package lives at <package_source>.` after its first sentence and leaves the rest as written.

Setup owns only the marked bodies. It keeps all text outside them, including Team additions, verbatim. An edit inside a marked part conflicts when its body differs from both the proposal and the last adopted body. Setup preserves the file, shows the diff, and exits non-zero. Ownership hashes for these bodies live under `entry_parts` in the ownership file.

Every install gets a package section in the root `README.md`, written for people. It links ai-core-workflow at `package_source`, says improvements go upstream as merge requests, points to the override lines in Team additions, and says to sync with `/workflow-setup`. Its body sits in `<!-- setup:package -->` markers under a `## Copilot workflow package` heading that the team may rename or move. When the README has no markers, setup appends the heading and section, creating the file when it is missing. It keeps every other README line and the file's line endings. The ownership rules above apply inside the markers, with hashes under `readme_parts`. Unpaired markers also conflict. The preview shows the README change as a diff.

Without matching markers, an existing entry conflicts unless its whole-file hash matches the old `entry_hash` baseline. Setup can replace that unedited older entry. Preview prints the merged file; validation fails at 120 lines or more, or when marked bodies differ from the current rendering and require `--apply`. Validation also fails when the sync line is missing or lacks the `package_source` URL, or when the README package section is missing or differs from the current rendering.

Older installs also have `.github/references/team-workflow.md` and `docs/harness/setup-record.md`. Preview lists them. Apply deletes each one only while it matches what setup wrote or a shipped default, then removes `.github/references/` if it is empty. Apply keeps an edited file and reports it; the team moves its rules into Team additions or the team standards, then deletes it.

After apply, setup warns about skill folders left out of the selection. Copilot may still load them; delete a folder to retire its skill.

To sync an installed package with a newer version, follow [Sync the package](#sync-the-package) instead.

Done when the team has approved the preview and setup has applied that exact proposal without unresolved conflicts.

## 6. Validate configuration

Run the setup command with `--validate`:

```text
python3 .github/skills/workflow-setup/scripts/setup.py docs/harness/setup-selection.json --validate
```

For a multi-repository workspace, also run the workspace validator command that workspace-analysis gives under `## Files`.

Setup is done only when setup prints `Configuration OK` and, for a multi-repository workspace, the workspace validator prints `Workspace OK: <n> checkouts, <m> pages`. Configuration checks the rendered instructions; workspace validation checks the index, evidence, overview, integrations, and repository pages.

## Sync the package

The workspace pulls the latest ai-core-workflow `main` from `package_source`. Each sync clones it into a new temporary folder and deletes the folder at the end, so nobody keeps a local copy of the package. Changes flow one way, from the package into the workspace. To share an improvement with other projects, the team opens a merge request on ai-core-workflow.

A workspace edit to a package file is an **override**. Each override has one line in `## Team additions` of `.github/copilot-instructions.md`: `- Override .github/<file>: <reason>.`

1. Take the package URL from `package_source` in the selection. When the selection has none, take the URL in the sync line of `## Team additions`, and when that has none, ask the team. Drop any `user:token@` before the host and set `package_source` in the selection when it is missing. Then clone the package into a new temporary folder, `<tmp>`, which the first command prints:

   ```text
   python3 -c "import tempfile; print(tempfile.mkdtemp(prefix='ai-core-workflow-'))"
   git clone --depth 1 --branch main <package_source> <tmp>
   git -C <tmp> rev-parse --short HEAD
   ```

   Use this one clone for every run of this sync, so `--apply` writes exactly the package the team previewed. When the team names a local ai-core-workflow checkout instead, for example to test an unmerged branch, use that folder as `<tmp>` read-only, exactly as it stands. Report its branch, short HEAD, and any `git -C <tmp> status --porcelain` output with the preview. Done when `<tmp>` holds the package, the selection has `package_source`, and you have the short hash.
2. From the workspace root, preview the sync with the clone's setup script, so the new version renders the files:

   ```text
   python3 <tmp>/.github/skills/workflow-setup/scripts/setup.py docs/harness/setup-selection.json --root . --update-from <tmp>/.github
   ```

   The preview covers the selected skills with their references, the helper agents, the sync line's URL, the README package section, and legacy file removal. Omitted selections follow the installed bundle; workspace-only skills and the team standards stay as they are.

   The preview also lists package skills that are neither installed nor selected, under `Package skills not installed here`. A skill labeled `new since the last sync` was published after the last applied sync. `not offered before` means the workspace has no record of earlier offers. An unlabeled skill was offered in an earlier sync and left out. Use the question tool to ask which labeled skills to adopt, and show the `needs` note of each one. Name the unlabeled skills as available, without a question. Setup never enables a dependency itself: adopt each skill a chosen one needs, or leave the chosen one out. Record each adopted skill this way:
   - The selection lists `skills`: add the name there.
   - The selection omits `skills`: add `--add-skill <name>` to this command and to every later run of this sync. Once installed, the skill joins the installed defaults.

   When the team adopts a skill, rerun the preview so they see its files. Done when the team has answered for every labeled skill and seen the preview. When they decline it, go to step 6.
3. After the team approves, rerun with `--apply` and the same `--add-skill` flags. Apply records the package's skill list in the ownership file, so the next sync labels only skills published after it. Each package file takes one of these paths:
   - Unchanged in the package and edited here: setup keeps the workspace version without a flag.
   - Changed in the package and unedited here: setup writes the package version.
   - Missing here: setup writes the package version back. To retire a shipped skill, leave it out of the selection before you delete its folder.
   - Changed in both: a conflict. Setup leaves the file untouched, writes the other changes, and exits non-zero. Show each conflict. After the team merges it by hand, rerun with `--keep-local <file>`, repeating the flag per file. Later syncs keep that file until the package changes it again.
   - No longer shipped: the preview lists it as retired. Rerun with `--remove-retired` to delete the unedited ones, or with `--keep-local <file>` to keep one as a team file.

   Done when `--apply` exits zero.
4. Bring the override lines in `## Team additions` up to date. Apply has already restored the package sync line and its URL. Add or update an override line for each file kept with `--keep-local`, and delete the line of any override this sync replaced with the package version. When the sync line still names `../ai-core-workflow` or a clean clone, show the team a diff that replaces it with the sync line from `<tmp>/.github/skills/workflow-setup/templates/copilot-instructions.template.md`. Add `The package lives at <package_source>.` after its first sentence, keep any sentence the team added, and write the new line after they approve. Done when every file kept in this sync has an override line and the team has accepted or declined any sync line rewrite.
5. Run the setup command with `--validate`. Give the team the commit message `chore: sync ai-core-workflow <short-hash>`, which also covers the README section; setup never commits. Done when setup prints `Configuration OK`.
6. Delete the temporary folder. Git marks its object files read-only, which blocks a plain delete on Windows, so this command clears that flag first:

   ```text
   python3 -c "import os, shutil, stat, sys; [os.chmod(os.path.join(d, f), stat.S_IWRITE) for d, _, fs in os.walk(sys.argv[1]) for f in fs]; shutil.rmtree(sys.argv[1])" <tmp>
   ```

   Keep a local checkout the team named in step 1. Done when the temporary folder no longer exists.