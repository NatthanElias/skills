# Repository page format

Write `docs/workspace/repos/<repo_id>.md` under 150 lines. Use this header, then the nine `##` headings below in exactly this order. The workspace validator reads the headings from this block, so a heading renamed here is the one every page needs. Replace placeholders with evidence from the repository. Keep repository-root-relative paths in code font and cite the files that support each claim. Write "Unknown" where code does not show the answer.

```markdown
# <repo_id>

Commit scanned: `<full 40-char HEAD>` on <YYYY-MM-DD>.

## What it does

Describe the repository's purpose in 2 to 3 lines from its implementation.

## Type and stack

State service or library, language, and framework versions from manifests. Give declared versions where the manifest pins them.

## Build and test

Give the build and test commands supported by manifests or CI. Record a gap when no command is established.

## Entry points

List controllers, listeners, schedulers, and main configuration with file citations.

## Modules

State what each inspected module owns. List unread modules when the scan cannot cover the repository.

## Where to start

Use a To / Start at table for common tasks. Each start path must name an existing file or folder.

| To | Start at |
| --- | --- |
| <task> | `<repository-relative path>` |

## Offers and calls

Separate offers from calls. Give HTTP method and full path, topic names, and library coordinates with files; for calls, include base-URL properties.

## Rules that must not break

List invariants enforced by code or tests and cite the enforcing files. Keep undocumented intent as Unknown.

## Team notes

None yet.
```

On first scan, use `None yet.` for Team notes. On rescan, copy that section's existing contents unchanged.