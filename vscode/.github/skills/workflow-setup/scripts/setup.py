"""Preview and apply selected team settings without overwriting local edits."""

import argparse
import difflib
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

import configuration

ROOT = Path(__file__).resolve().parents[4]
ENTRY = ROOT / ".github" / "copilot-instructions.md"
BASELINE = ROOT / "docs" / "harness" / "setup-ownership.json"
GITIGNORE = ROOT / ".gitignore"
README = ROOT / "README.md"
TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "copilot-instructions.template.md"
# Older setups generated these two files. Setup removes one only when its content matches what setup wrote,
# as recorded under its ownership key, or a team-workflow.md default the package once shipped.
LEGACY_TEAM = ".github/references/team-workflow.md"
LEGACY_RECORD = "docs/harness/setup-record.md"
LEGACY_KEYS = {LEGACY_TEAM: "adopted_hash", LEGACY_RECORD: "record_hash"}
# Context: feature-workflow retired this decisions table; setup points a project holding it to constraints.py migrate.
LEGACY_STATE = ".specs/STATE.md"
# Shipped team-workflow.md defaults after universal newline conversion: the last one, the one before the
# repository trait line, and the one before the commit default changed.
SHIPPED_TEAM_HASHES = ("cfdb4f6342db89336dba79b20acb518570325e191c29df85b2472dadbe21b982",
                       "b8a960a149a51a56beba50113ea1d6e046e9ddc482219f3cb6db5d59cd30b7a9",
                       "13635cd6db8248259606ecf43c7007a7fbbfe64cf314302c6ddd6db9db5171b4")
# Ownership keys older setups wrote that no current file needs.
RETIRED_KEYS = ("selection",) + tuple(LEGACY_KEYS.values())
COMMITS = "Local commits under an approved plan; push, force-push, deploy, and production data need explicit approval"
REPO_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
PART = re.compile(r"<!-- setup:([a-z]+) -->\n(.*?)<!-- /setup:\1 -->", re.S)
LIMIT = 120
SCAN = "Run workflow-setup to scan the workspace."
SYNC = re.compile(r"^- Package sync:.*$", re.M)
README_HEADING = "## Copilot workflow package"


def package_source(settings):
    """Return the selected package URL, or None; never echo a rejected value, since it may hold a token."""
    url = settings.get("package_source")
    if url is None:
        return None
    if not single_line(url) or any(mark in url for mark in " `|<>()[]\"'"):
        raise ValueError("Give package_source as an https clone URL")
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.query or parts.fragment:
        raise ValueError("Give package_source as an https clone URL")
    if "@" in parts.netloc:
        raise ValueError("Remove the user name and token from package_source; the selection is committed")
    return url


def with_source(text, url):
    """Add the template sync line when it is missing, and the package URL when that line names none."""
    match = SYNC.search(text)
    if match is None:
        text += ("\n" if text and not text.endswith("\n") else "") + \
            SYNC.search(TEMPLATE.read_text(encoding="utf-8"))[0] + "\n"
        match = SYNC.search(text)
    line = match[0]
    if url is None or "://" in line:
        return text
    sentence = f"The package lives at `{url}`."
    head, end, tail = line.partition(". ")
    line = f"{head}. {sentence} {tail}" if end else f"{line.rstrip()} {sentence}"
    return text[:match.start()] + line + text[match.end():]


def readme_section(url):
    package = f"[ai-core-workflow]({url})" if url else "ai-core-workflow"
    return ("<!-- setup:package -->\n"
            f"The Copilot skills and agents in `.github/` come from the {package} package. "
            "To improve a shared one, open a merge request on ai-core-workflow, not here.\n"
            "A local edit to a package file is an override. Each one has a line in `## Team additions` of "
            "[copilot-instructions.md](.github/copilot-instructions.md).\n"
            "To sync a newer version, run `/workflow-setup` in Copilot Chat and ask it to sync the package.\n"
            "<!-- /setup:package -->\n")


def read_readme(path):
    """Return the README text with \\n line ends and its own line end, or (None, "\\n") when missing."""
    if not path.exists():
        return None, "\n"
    raw = path.read_bytes().decode("utf-8")
    return raw.replace("\r\n", "\n"), "\r\n" if "\r\n" in raw else "\n"


def readme_merge(current, section, adopted, project):
    """Return the README with the current package section and whether it conflicts; keep all other text."""
    if current is None:
        return f"# {project}\n\n{README_HEADING}\n\n{section}", False
    if "<!-- setup:" not in current and "<!-- /setup:" not in current:
        separator = "" if not current or current.endswith("\n\n") else ("\n" if current.endswith("\n") else "\n\n")
        return f"{current}{separator}{README_HEADING}\n\n{section}", False
    merged, edited = merge(current, section, adopted)
    if merged is None:
        return current.rstrip("\n") + f"\n\n{README_HEADING}\n\n{section}", True
    return merged, bool(edited)


def missing_ignores(path, settings, skills):
    """Return the .gitignore entries setup still needs: `.local/`, and the feature folder root when selected."""
    entries = [".local/"]
    if "feature-workflow" in skills:
        root = portable(settings.get("feature_root", ".specs/features/<feature>/")).split("<feature>")[0]
        entries.append(root.rstrip("/") + "/")
    present = {line.strip().strip("/") for line in path.read_text(encoding="utf-8").splitlines()} \
        if path.exists() else set()
    return [entry for entry in entries if entry.strip("/") not in present]


def digest(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def single_line(value):
    # splitlines also breaks on \r, \x85, \u2028, and other separators.
    return isinstance(value, str) and value.splitlines() == [value]


def portable(path):
    if (not single_line(path) or "\\" in path or ":" in path or "|" in path or "`" in path or "<!--" in path
            or "-->" in path or path.startswith("/") or ".." in path.split("/")):
        raise ValueError(f"Use a relative workspace path: {path!r}")
    return path


def one_line(value, what, banned=()):
    if (not single_line(value) or not value.strip()
            or any(text in value for text in ("<!--", "-->") + banned)):
        raise ValueError(f"Invalid {what}: {value!r}")
    return value.strip()


def rows(items, first):
    for item in items:
        if not isinstance(item, dict) or set(item) != {first, "start"}:
            raise ValueError(f"Give each row only {first} and start: {item!r}")
        yield one_line(item[first], first, ("|",)), portable(one_line(item["start"], "start path"))


def check_length(text, name):
    count = len(text.splitlines())
    if count >= LIMIT:
        raise ValueError(f"{name} has {count} lines; keep it under {LIMIT}")


def entry_text(settings, selected, skills, single, project, feature_root):
    brief = settings.get("brief")
    if brief is None:
        brief = "No project brief yet. " + SCAN
    elif (not isinstance(brief, str) or not 1 <= len(brief.strip().splitlines()) <= 5
          or "<!--" in brief or "-->" in brief):
        raise ValueError("Write the brief in 1 to 5 lines without HTML comment markers")
    parts = {"brief": "\n".join(line.rstrip() for line in brief.strip().splitlines())}
    table = settings.get("repositories")
    if table is not None and (not isinstance(table, dict) or set(table) - set(selected)):
        raise ValueError("Repository rows must name selected repositories")
    mode = "Repositories: " + ("single" if single else "multi") + ".\n\n"
    if table:
        found = dict(zip(table, rows(table.values(), "role")))
        parts["repositories"] = mode + "\n".join(
            ["| Repository | Role | Start reading |", "| --- | --- | --- |"] +
            [f"| {repo} | {found[repo][0]} | `{found[repo][1]}` |" if repo in found
             else f"| {repo} | Not scanned | Not scanned |" for repo in selected])
    else:
        parts["repositories"] = mode + "No repository rows yet. " + SCAN
    routes = settings.get("routes")
    if routes is not None and not isinstance(routes, list):
        raise ValueError("List routes as task and start pairs")
    if routes:
        parts["routes"] = "\n".join(["| To | Start at |", "| --- | --- |"] +
                                    [f"| {task} | `{start}` |" for task, start in rows(routes, "task")])
    else:
        parts["routes"] = "No task routes yet. " + SCAN
    checks = settings.get("checks", {})
    parts["checks"] = "\n".join(
        f"- {repo}: `{one_line(checks[repo], 'check command', ('`',))}`" if repo in checks
        else f"- {repo}: No command established; validation gap" for repo in selected)
    parts["documents"] = (
        "Read the [workspace overview](../docs/workspace/overview.md) first to pick a repository. "
        "Each selected repository has a page at `docs/workspace/repos/<repo>.md`.\n"
        "Read [integrations](../docs/workspace/integrations.md) before changing an HTTP path, topic, or shared library.")
    team = [f"- Project ID for lessons and review rounds: {project}.",
            f"- Commits: {one_line(settings.get('commits', COMMITS), 'commit policy').rstrip('.')}.",
            f"- Delegation: {one_line(settings.get('delegation', 'Helpers allowed; parallel writes not allowed'), 'delegation').rstrip('.')}. "
            + configuration.delegation_line(skills)]
    if "feature-workflow" in skills:
        team.append(f"- Feature documents: `{feature_root}`.")
        team.append("- Constraints: before changing code, run "
                    "`python3 .github/skills/feature-workflow/scripts/constraints.py list` for the areas and paths "
                    "you touch, and conform to each record or ask to supersede it. `docs/roadmap/DECISIONS.md` is "
                    "for people, never a coding constraint.")
    documents = settings.get("documents", {})
    for label in documents:
        one_line(label, "document label", (":", "|"))
    if documents:
        team += ["", "| Document | Path |", "| --- | --- |"]
        team += [f"| {label} | `{portable(path)}` |" for label, path in documents.items()]
    team += ["", "Follow each repository's own instructions too. Keep personal choices in `.local/`. "
             "Ask before push, publication, deployment, or production data changes."]
    parts["team"] = "\n".join(team)
    template = TEMPLATE.read_text(encoding="utf-8")
    if "workspace-analysis" not in skills:
        template = re.sub(r"## Workspace documents\n\n<!-- setup:documents -->\n.*?<!-- /setup:documents -->\n\n",
                          "", template, flags=re.S)
    entry = re.sub(r"\{\{(\w+)\}\}", lambda match: parts[match[1]], template)
    check_length(entry, "The always-on file")
    return entry


def marked(text):
    """Return the marked parts in order, or None when a marker is unpaired or nested."""
    found = PART.findall(text)
    if text.count("<!-- setup:") + text.count("<!-- /setup:") != 2 * len(found):
        return None
    return found


def merge(current, entry, adopted):
    """Put new bodies into the current file; return None without the same markers, plus edited part names."""
    new = dict(PART.findall(entry))
    found = marked(current)
    if found is None or [name for name, _ in found] != list(new):
        return None, []
    edited = [name for name, body in found if body != new[name] and digest(body) != adopted.get(name)]
    return PART.sub(lambda match: f"<!-- setup:{match[1]} -->\n{new[match[1]]}<!-- /setup:{match[1]} -->",
                    current), edited


def check_starts(root, settings):
    top = root.resolve()
    for item in list((settings.get("repositories") or {}).values()) + list(settings.get("routes") or []):
        path = (root / item["start"]).resolve()
        if not path.exists():
            raise ValueError(f"Start path not found under the workspace root: {item['start']}")
        if path != top and top not in path.parents:
            raise ValueError(f"Start path leads outside the workspace root: {item['start']}")


def proposed(settings, github=None, additions=None, adding=()):
    selected = settings["selected_repositories"]
    if not isinstance(selected, list) or not selected or any(not isinstance(x, str) for x in selected):
        raise ValueError("Select repository IDs")
    if len(selected) != len(set(selected)):
        raise ValueError("Select unique repository IDs")
    for repo in selected:
        if not REPO_ID.fullmatch(repo):
            raise ValueError(f"Use a repository ID of letters, digits, dots, dashes, or underscores: {repo!r}")
    skills = configuration.selected(settings, github, additions, adding)
    single = configuration.single_repository(settings)
    if single and len(selected) != 1:
        raise ValueError("A single-repository install selects exactly one repository; set single_repository to "
                         "false for more")
    checks = settings.get("checks", {})
    if set(checks) - set(selected):
        raise ValueError("Checks reference unselected repositories")
    feature_root = portable(settings.get("feature_root", ".specs/features/<feature>/").rstrip("."))
    project = settings.get("project", "project")
    if not isinstance(project, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", project):
        raise ValueError(f"Use a lowercase project ID: {project!r}")
    package_source(settings)
    return entry_text(settings, selected, skills, single, project, feature_root)


def validate_configuration(root, settings):
    skills = configuration.selected(settings, root / ".github")
    return configuration.validate(root, skills, proposed(settings, root / ".github"))


def selection_hash(settings):
    """Fingerprint the accepted selection, which stays in setup-selection.json, so a change reruns setup."""
    return digest(json.dumps(settings, sort_keys=True, ensure_ascii=False))


def unlinked(root, relative):
    """Whether root/relative reaches its own place with no symlink or junction on the way from the root."""
    path = root / relative
    expected = root.resolve().joinpath(*relative.split("/"))
    return not path.is_symlink() and os.path.normcase(path.resolve()) == os.path.normcase(expected)


def legacy_files(root, previous):
    """Sort the older generated files present into removable and kept lists of (relative path, path).

    A file is removable only as a regular file at its own path inside the root, never through a link, and only
    when its content matches what setup recorded writing or a shipped default; anything else stays."""
    removable, kept = [], []
    for relative, key in LEGACY_KEYS.items():
        path = root / relative
        if not path.exists() and not path.is_symlink():
            continue
        known = {previous.get(key)} | (set(SHIPPED_TEAM_HASHES) if relative == LEGACY_TEAM else set())
        if (unlinked(root, relative) and path.is_file()
                and digest(path.read_text(encoding="utf-8", errors="replace")) in known):
            removable.append((relative, path))
        else:
            kept.append((relative, path))
    return removable, kept


def remove_legacy(root, removable):
    """Delete the removable files, then their references folder only when nothing else is left in it."""
    for _, path in removable:
        path.unlink()
    folder = root / ".github" / "references"
    if removable and unlinked(root, ".github/references") and folder.is_dir() and not any(folder.iterdir()):
        folder.rmdir()


def report_preserved(preserved):
    if preserved:
        print("Older files kept because they differ from what setup wrote, or are links. Move their rules into "
              "Team additions or the team standards, then delete them:\n" +
              "".join(f"- {relative}\n" for relative, _ in preserved))


def package_record(previous, baseline_path):
    """Return the package skill names the last applied setup recorded, or None for an older ownership file."""
    known = previous.get("package_skills")
    if known is not None and (not isinstance(known, list) or any(not isinstance(name, str) for name in known)):
        raise ValueError(f"Invalid setup ownership file: {baseline_path}")
    return known


def report_candidates(found, explicit):
    """Print the package skills a sync leaves out; the workflow asks the team which ones to adopt."""
    if not found:
        return
    print("Package skills not installed here:")
    for name, label, needs in found:
        notes = ([label] if label else []) + ([f"needs {', '.join(needs)}"] if needs else [])
        print(f"- {name}" + (f" ({'; '.join(notes)})" if notes else ""))
    how = "add its name to skills in the selection" if explicit else "rerun with --add-skill <name>"
    print(f"To adopt one, {how}, together with each skill it needs. Others stay out.\n")


def show_diff(path, current, proposed_content):
    if isinstance(current, bytes):
        current = current.decode("utf-8", errors="replace")
    if isinstance(proposed_content, bytes):
        proposed_content = proposed_content.decode("utf-8", errors="replace")
    print("".join(difflib.unified_diff(current.splitlines(keepends=True),
                                   proposed_content.splitlines(keepends=True),
                                   fromfile=str(path), tofile=f"{path} (proposed)")), end="")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("selection", type=Path, help="Reviewed JSON choices; never run untrusted commands from it")
    parser.add_argument("--root", type=Path, help="Adopting workspace root; defaults to this installed package")
    parser.add_argument("--update-from", type=Path, help="New package .github directory for selected skill updates")
    parser.add_argument("--keep-local", action="append", default=[], metavar="FILE",
                        help="With --update-from, keep this file's local version; repeat for more files")
    parser.add_argument("--remove-retired", action="store_true",
                        help="With --update-from, delete unedited files the new package no longer ships")
    parser.add_argument("--add-skill", action="append", default=[], metavar="NAME",
                        help="With --update-from and no skills list, install this package skill; repeat for more")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true", help="Apply the reviewed proposal")
    action.add_argument("--validate", action="store_true", help="Validate selected routes without writing")
    args = parser.parse_args()
    try:
        root = args.root.resolve() if args.root else ROOT
        github = root / ".github"
        entry_path = root / ".github" / "copilot-instructions.md" if args.root else ENTRY
        baseline_path = root / "docs" / "harness" / "setup-ownership.json" if args.root else BASELINE
        gitignore_path = root / ".gitignore" if args.root else GITIGNORE
        readme_path = root / "README.md" if args.root else README
        selection_path = args.selection if args.selection.is_absolute() else root / args.selection
        settings = json.loads(selection_path.read_text(encoding="utf-8"))
        if not isinstance(settings, dict):
            raise ValueError("Give the selection as a JSON object")
        source_github = args.update_from.resolve() if args.update_from else None
        if source_github:
            if source_github.name != ".github" or not source_github.is_dir():
                raise ValueError("--update-from must name a package .github directory")
            if args.validate:
                raise ValueError("Use --validate without --update-from to check the installed configuration")
        elif args.keep_local or args.remove_retired or args.add_skill:
            raise ValueError("Use --keep-local, --remove-retired, and --add-skill with --update-from")
        keep = set()
        for name in args.keep_local:
            path = (Path(name) if Path(name).is_absolute() else root / name).resolve()
            if github.resolve() not in path.parents:
                raise ValueError(f"--keep-local must name a file under .github: {name}")
            keep.add(path.relative_to(github.resolve()).as_posix())
        entry = proposed(settings, github, source_github, args.add_skill)
        skills = configuration.selected(settings, github, source_github, args.add_skill)
        if "feature-workflow" in skills and (root / LEGACY_STATE).is_file():
            print(f"Notice: {LEGACY_STATE} holds the retired decisions table. Coding agents now follow "
                  "records under .specs/constraints/. Run `python3 .github/skills/feature-workflow/scripts/"
                  f"constraints.py migrate`, review the records with the team, then delete {LEGACY_STATE}.\n")
        check_starts(root, settings)
        source_url = package_source(settings)
        section = readme_section(source_url)
        previous = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() else {}
        if not isinstance(previous, dict):
            raise ValueError(f"Invalid setup ownership file: {baseline_path}")
        known = package_record(previous, baseline_path)
        legacy, preserved = legacy_files(root, previous)
        if args.validate:
            count = configuration.validate(root, skills, entry)
            if entry_path.exists():
                current = entry_path.read_text(encoding="utf-8")
                if marked(current) != PART.findall(entry):
                    raise ValueError("The always-on file is out of date; run setup with --apply")
                if with_source(current, source_url) != current:
                    raise ValueError("The package sync line in Team additions is missing or lacks the package "
                                     "URL; run setup with --apply")
                check_length(current, "The always-on file")
            if marked(read_readme(readme_path)[0] or "") != PART.findall(section):
                raise ValueError("README.md lacks the current package section; run setup with --apply")
            if legacy:
                raise ValueError("Older generated files remain: " + ", ".join(relative for relative, _ in legacy) +
                                 "; run setup with --apply to remove them")
            report_preserved(preserved)
            print(f"Configuration OK: {count} selected skills")
            return
        if source_github:
            source_skills = configuration.catalog(source_github)
            configuration.validate(source_github.parent, tuple(name for name in skills if name in source_skills), "")
            configuration.validate(root, tuple(name for name in skills if name not in source_skills), entry,
                                   entry_fallback=source_github)
        else:
            configuration.validate(root, skills, entry)
        conflicts = []
        merged = entry
        if entry_path.exists():
            current = entry_path.read_text(encoding="utf-8")
            merged, edited = merge(current, entry, previous.get("entry_parts", {}))
            if merged is None:
                merged = entry
                # An older setup wrote the file without markers; replace it only if nobody edited it.
                if digest(current) != previous.get("entry_hash"):
                    conflicts.append((entry_path, current, entry))
            elif edited:
                conflicts.append((entry_path, current, merged))
        merged = with_source(merged, source_url)
        readme_current, readme_end = read_readme(readme_path)
        readme, readme_conflict = readme_merge(readme_current, section, previous.get("readme_parts", {}),
                                               settings.get("project", "project"))
        if readme_conflict:
            conflicts.append((readme_path, readme_current, readme))
        skill_updates, kept, retired = [], [], []
        if source_github:
            skill_updates, skill_conflicts, kept, retired = configuration.plan_updates(
                github, source_github, skills, previous.get("skill_files", {}), keep)
            conflicts.extend(skill_conflicts)
        removals = [relative for relative, edited in retired if args.remove_retired and not edited]
        unignored = missing_ignores(gitignore_path, settings, skills)
        unchanged = (entry_path.exists() and entry_path.read_text(encoding="utf-8") == merged
                     and readme == readme_current)
        # Keep the hash of a preserved older file, so a later run can still tell whether a team edited it.
        kept_keys = {LEGACY_KEYS[relative]: previous[LEGACY_KEYS[relative]]
                     for relative, _ in preserved if LEGACY_KEYS[relative] in previous}
        stale = (set(RETIRED_KEYS) & set(previous)) - set(kept_keys) or any(
            not configuration.package_owned(relative) for relative in previous.get("skill_files", {}))
        # A sync records the package's skills so the next one can tell newly published skills apart.
        record = sorted(configuration.catalog(source_github)) if source_github else (
            known if known is not None else sorted(configuration.catalog(github)))
        new_record = bool(source_github) and known != record
        found = configuration.candidates(github, source_github, skills, configuration.single_repository(settings),
                                         None if known is None else set(known)) if source_github else []
        if (not conflicts and not skill_updates and not kept and not retired and not unignored and unchanged
                and not legacy and not stale and not new_record and baseline_path.exists()
                and previous.get("selection_hash") == selection_hash(settings)):
            check_length(merged, "The always-on file")
            report_preserved(preserved)
            print("No changes")
            report_candidates(found, "skills" in settings)
            return
        print("Proposed always-on instructions:\n" + merged)
        if readme != readme_current and not readme_conflict:
            print("Proposed README.md package section:")
            show_diff(readme_path, readme_current or "", readme)
        if unignored:
            print("Proposed .gitignore addition: " + " ".join(unignored) + "\n")
        if legacy:
            print("Older generated files setup no longer writes, to remove:\n" +
                  "".join(f"- {relative}\n" for relative, _ in legacy))
        report_preserved(preserved)
        if skill_updates:
            print("Proposed package updates:")
            for path, current, content in skill_updates:
                show_diff(path, current or b"", content)
        if kept:
            print("Local versions kept: " + ", ".join(f".github/{relative}" for relative in kept) + "\n")
        if retired:
            print("Files the new package no longer ships:")
            for relative, edited in retired:
                state = "edited here, kept" if edited else ("removed" if args.remove_retired else "unedited")
                print(f"- .github/{relative} ({state})")
            if not args.remove_retired:
                print("Pass --remove-retired to delete the unedited ones, or --keep-local <file> to keep one.")
            print()
        unselected = configuration.unselected_skills(github, skills)
        if unselected:
            print("Warning: these skill folders are not selected but stay installed, so Copilot may still load "
                  "them: " + ", ".join(unselected) + ". Delete a folder to retire its skill.\n")
        report_candidates(found, "skills" in settings)
        if new_record:
            print("Proposed record of the package skill list in setup-ownership.json, so the next sync marks only "
                  "newer skills as new.\n")

        def apply_package():
            for path, _, content in skill_updates:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            for relative in removals:
                (github / relative).unlink()
            return configuration.adopted_hashes(github, source_github, skills,
                                                previous.get("skill_files", {}), kept, removals)
        if conflicts:
            print("Conflicts (current files preserved):")
            for path, current, content in conflicts:
                show_diff(path, current, content)
            hint = " or rerun with --keep-local <file> to keep yours" if source_github else ""
            if args.apply and (skill_updates or kept or removals):
                adopted_files = apply_package()
                baseline_path.parent.mkdir(parents=True, exist_ok=True)
                baseline_path.write_text(json.dumps({**previous, "skill_files": adopted_files}, indent=2) + "\n",
                                         encoding="utf-8")
                raise ValueError(f"Applied {len(skill_updates) + len(kept) + len(removals)} package changes "
                                 f"without conflicts; resolve the conflicts{hint}, then rerun")
            raise ValueError(f"Resolve the conflicts{hint} before applying the proposed settings")
        check_length(merged, "The always-on file")
        if not args.apply:
            print("Preview only; pass --apply after approval")
            return
        entry_path.parent.mkdir(parents=True, exist_ok=True)
        entry_path.write_text(merged, encoding="utf-8")
        if readme != readme_current:
            # Keep the project's own line ends so the rest of its README shows no change.
            readme_path.write_bytes(readme.replace("\n", readme_end).encode("utf-8"))
        adopted_files = apply_package()
        remove_legacy(root, legacy)
        if unignored:
            existing = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
            separator = "" if not existing or existing.endswith("\n") else "\n"
            gitignore_path.write_text(existing + separator + "".join(f"{entry}\n" for entry in unignored),
                                      encoding="utf-8")
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps({"entry_hash": digest(merged),
                                             "entry_parts": {name: digest(body) for name, body in PART.findall(entry)},
                                             "readme_parts": {name: digest(body)
                                                              for name, body in PART.findall(section)},
                                             "selection_hash": selection_hash(settings),
                                             **kept_keys,
                                             "package_skills": record,
                                             "skill_files": adopted_files}, indent=2) + "\n", encoding="utf-8")
        print("Applied accepted team choices")
    except (ValueError, KeyError, FileNotFoundError, json.JSONDecodeError) as error:
        parser.exit(1, f"Setup failed: {error}\n")


if __name__ == "__main__":
    main()
