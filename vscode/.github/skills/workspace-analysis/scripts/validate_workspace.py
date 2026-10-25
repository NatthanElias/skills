"""Validate the workspace index, its fingerprinted evidence, and the workspace pages."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

PAGE_FORMAT = Path(__file__).resolve().parents[1] / "references" / "repo-page.md"
COMMIT = re.compile(r"^Commit scanned: `([0-9a-f]{7,40})`", re.M)
REPO_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
SIDES = ("Caller", "Provider")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def headings():
    """Read the page headings from the repo-page.md template, so a team edit there changes what pages need."""
    block = re.search(r"^```markdown\n(.*?)^```", PAGE_FORMAT.read_text(encoding="utf-8"), re.M | re.S)
    found = re.findall(r"^## (.+?)\s*$", block[1], re.M) if block else []
    require(found, f"No page template with ## headings in {PAGE_FORMAT}")
    return found


def inside(root, relative):
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute(),
            f"Invalid relative path: {relative!r}")
    path = (root / relative).resolve()
    require(path == root.resolve() or root.resolve() in path.parents,
            f"Path escapes root: {relative}")
    return path


def sanitized_remote(remote):
    if "://" in remote:
        parts = urlsplit(remote)
        require(parts.hostname is not None, "Invalid Git remote")
        host = parts.hostname + (f":{parts.port}" if parts.port else "")
        return urlunsplit((parts.scheme, host, parts.path, parts.query, parts.fragment))
    if re.match(r"^[^@/]+@[^:/]+:", remote):
        return remote.split("@", 1)[1]
    return remote


def workspace(index_path, bindings_path):
    index = json.loads(index_path.read_text(encoding="utf-8"))
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    repositories = index["repositories"]
    identities = [(item["repo_id"], item["checkout_id"]) for item in repositories]
    require(len(identities) == len(set(identities)), "Duplicate repository checkout identity")
    for item in repositories:
        identity = f'{item["repo_id"]}:{item["checkout_id"]}'
        root = Path(bindings[identity]).resolve()
        require(root.is_dir(), f"Missing selected root: {identity}")
        if item.get("synthetic") is not True:
            require(item.get("head") and item.get("remote"), f"Missing Git identity: {identity}")
            def git(*arguments):
                result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True,
                                        text=True, check=False)
                require(result.returncode == 0, f"Git identity unavailable: {identity}")
                return result.stdout.strip()
            require(Path(git("rev-parse", "--show-toplevel")).resolve() == root,
                    f"Root is not selected checkout: {identity}")
            require(git("rev-parse", "HEAD") == item["head"], f"Stale HEAD: {identity}")
            remote = git("config", "--get", "remote.origin.url")
            require(sanitized_remote(remote) == item["remote"] and sanitized_remote(item["remote"]) == item["remote"],
                    f"Remote identity differs or stores credentials: {identity}")
            status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True,
                                    text=True, check=False)
            require(status.returncode == 0, f"Git status unavailable: {identity}")
            changed = [line[3:] for line in status.stdout.splitlines() if line.strip()]
            if changed:
                print(f"Warning: {identity} has uncommitted changes the pages do not describe: "
                      + ", ".join(changed[:5]) + (f" and {len(changed) - 5} more" if len(changed) > 5 else ""))
        for evidence in item.get("evidence", []):
            path = inside(root, evidence["path"])
            require(path.is_file(), f"Missing evidence: {identity} {path}")
            require(evidence.get("sha256"), f"Missing evidence fingerprint: {path}")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"],
                    f"Stale evidence: {path}")
    for edge in index.get("dependencies", []):
        source = tuple(edge["source"])
        require(source in identities, "Dependency source not selected")
        require(edge["kind"] in ("code", "documented", "inferred", "unknown"),
                "Dependency evidence kind unknown")
        if edge["kind"] != "unknown":
            require(tuple(edge["target"]) in identities, "Dependency target not selected")
            evidence = edge["evidence"]
            require(evidence.get("path") and evidence.get("sha256"), "Missing dependency citation")
            source_root = Path(bindings[f"{source[0]}:{source[1]}"]).resolve()
            citation = inside(source_root, evidence["path"])
            require(citation.is_file() and hashlib.sha256(citation.read_bytes()).hexdigest() == evidence["sha256"],
                    "Stale dependency evidence")
    return len(identities)


def lines(path, limit):
    require(path.is_file(), f"Missing workspace page: {path}")
    text = path.read_text(encoding="utf-8")
    count = len(text.splitlines())
    require(count < limit, f"{path} has {count} lines; keep it under {limit}")
    return text


def selection(folder):
    """Return the repositories in setup's selection, or None outside a docs/workspace folder or before setup."""
    if folder.name != "workspace" or folder.parent.name != "docs":
        return None
    path = folder.parent / "harness" / "setup-selection.json"
    if not path.is_file():
        return None
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Setup selection is not valid JSON: {path}: {error}") from error
    selected = settings.get("selected_repositories") if isinstance(settings, dict) else None
    require(isinstance(selected, list) and selected and all(isinstance(repo, str) for repo in selected),
            f"Setup selection needs selected_repositories as a list of repository IDs: {path}")
    require(len(selected) == len(set(selected)), f"Setup selection repeats a repository: {path}")
    for repo in selected:
        require(REPO_ID.fullmatch(repo), f"Invalid repository ID in setup selection: {repo!r}")
    return selected


def cells(line):
    line = line.strip()
    return [cell.strip() for cell in line.strip("|").split("|")] if line.startswith("|") else None


def integrations(text, heads):
    """Check each matched integration row against the HEADs the index records for both sides."""
    lines = text.splitlines()
    for number, line in enumerate(lines):
        header = cells(line)
        if not header or header[0] != "Caller" or "Provider" not in header:
            continue
        require(all(f"{side} commit" in header for side in SIDES),
                "integrations.md needs Caller commit and Provider commit columns in the matched table")
        for row in lines[number + 2:]:
            values = cells(row)
            if values is None:
                break
            require(len(values) == len(header), f"integrations.md row does not match its header: {row}")
            found = dict(zip(header, values))
            for side in SIDES:
                repo, commit = found[side], found[f"{side} commit"].strip("`")
                require(repo in heads, f"integrations.md names a repository missing from the index: {repo}")
                require(not heads[repo] or (re.fullmatch(r"[0-9a-f]{7,40}", commit)
                                            and any(head.startswith(commit) for head in heads[repo])),
                        f"Stale integration: {repo} moved since this row was matched; recheck both sides: {row}")


def documents(index_path, index):
    folder = index_path.parent
    overview = lines(folder / "overview.md", 100)
    require((folder / "integrations.md").is_file(), f"Missing workspace page: {folder / 'integrations.md'}")
    expected = headings()
    heads = {}
    for item in index["repositories"]:
        commits = heads.setdefault(item["repo_id"], [])
        if item.get("synthetic") is not True:
            commits.append(item["head"])
    selected = selection(folder.resolve())
    if selected is not None:
        for repo_id in selected:
            require(repo_id in heads, f"Selected repository has no index row or page; scan it: {repo_id}")
        pages = [path.stem for path in (folder / "repos").glob("*.md")]
        for repo_id in sorted(set(heads) | set(pages)):
            require(repo_id in selected, f"Repository is not selected but keeps its index row or page; remove them "
                                         f"and its overview link: {repo_id}")
    for repo_id, commits in heads.items():
        require(isinstance(repo_id, str) and REPO_ID.fullmatch(repo_id), f"Invalid repository ID: {repo_id!r}")
        page = folder / "repos" / f"{repo_id}.md"
        require((folder / "repos").resolve() in page.resolve().parents, f"Page leads outside repos/: {page}")
        require(f"repos/{repo_id}.md" in overview, f"Overview does not link repos/{repo_id}.md")
        text = lines(page, 150)
        found = [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]
        require(found == expected, f"{page} needs these headings in order: {', '.join(expected)}")
        commit = COMMIT.search(text)
        require(commit, f"Missing 'Commit scanned' line: {page}")
        require(not commits or any(head.startswith(commit[1]) for head in commits), f"Stale page: {page}")
    integrations((folder / "integrations.md").read_text(encoding="utf-8"), heads)
    return len(heads)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=Path)
    parser.add_argument("--bindings", type=Path, required=True)
    args = parser.parse_args()
    try:
        checkouts = workspace(args.index, args.bindings)
        pages = documents(args.index, json.loads(args.index.read_text(encoding="utf-8")))
        print(f"Workspace OK: {checkouts} checkouts, {pages} pages")
    except (ValueError, KeyError, FileNotFoundError, json.JSONDecodeError, OSError) as error:
        parser.exit(1, f"Validation failed: {error}\n")


if __name__ == "__main__":
    main()
