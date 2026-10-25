"""Selected package routes and safe skill-file updates."""

import hashlib
import re
from pathlib import Path


DAILY = (
    "workflow-setup", "workspace-analysis", "generate-mvp-roadmap", "feature-workflow", "diagnosing-bugs",
    "handoff", "grill-me", "explain", "unslop", "technical-writing", "writing-for-agents",
    "adversarial-senior-review", "orchestrate-vscode",
)
ALL_SKILLS = DAILY
USER_ONLY = ("adversarial-senior-review", "workflow-setup")
GITHUB = Path(__file__).resolve().parents[3]
REQUIRES = {
    "workflow-setup": ("workspace-analysis", "grill-me"),
    "feature-workflow": ("workspace-analysis", "orchestrate-vscode"),
    "explain": ("unslop",),
}
# A single repository needs no scan, so its install leaves this skill out.
MULTI_ONLY = "workspace-analysis"
# The workspace validator owns these generated pages.
WORKSPACE_LINKS = ("../docs/workspace/overview.md", "../docs/workspace/integrations.md")
CODE_CHANGES = "code, configuration, dependency, build, or test changes"
LINK = re.compile(r"\[[^]]+\]\(([^)#]+)(?:#[^)]*)?\)")
SCRIPT = re.compile(r"\b(python3?)\s+(\.github/skills/[\w-]+/scripts/[\w.-]+\.py)(?=\s|`|$)")
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")


def hash_bytes(content):
    return hashlib.sha256(content).hexdigest()


def catalog(github):
    skills = {path.parent.name for path in (github / "skills").glob("*/SKILL.md")}
    for name in sorted(skills):
        if not NAME.fullmatch(name):
            raise ValueError(f"Use a lowercase skill name with digits or dashes: {name!r}")
    return skills


def retired_domains(settings):
    """Accept an absent or empty legacy domains list; refuse any other value so no rule is lost silently."""
    if settings.get("domains", []) != []:
        raise ValueError("The domains setting is retired. Move those rules into a team standards skill or document, "
                         "name it in Team additions, then remove domains from the selection")


def single_repository(settings):
    value = settings.get("single_repository", False)
    if not isinstance(value, bool):
        raise ValueError("Set single_repository to true or false")
    return value


def ordered(names):
    return tuple(name for name in ALL_SKILLS if name in names) + tuple(sorted(set(names) - set(ALL_SKILLS)))


def selected(settings, github=None, additions=None, adding=()):
    """Return the selected skills; adding names package skills to install beside the installed defaults."""
    github = GITHUB if github is None else github
    single = single_repository(settings)
    retired_domains(settings)
    installed_skills = catalog(github)
    available = installed_skills | (catalog(additions) if additions else set())
    skill_names = ordered(available)
    for name in adding:
        if "skills" in settings:
            raise ValueError(f"The selection lists skills; add {name} there instead of using --add-skill")
        if name in installed_skills:
            raise ValueError(f"--add-skill names an installed skill: {name}")
        if name not in available:
            raise ValueError(f"--add-skill names no package skill: {name}")
    skills = settings.get("skills", [name for name in skill_names
                                     if name in installed_skills and not (single and name == MULTI_ONLY)]
                          + list(adding))
    if not isinstance(skills, list) or not skills or any(not isinstance(x, str) for x in skills):
        raise ValueError("Select at least one skill by name")
    if len(skills) != len(set(skills)):
        raise ValueError("Select unique known skill names")
    if set(skills) - available:
        raise ValueError(f"Selected skill is missing: {sorted(set(skills) - available)[0]}")
    chosen = set(skills)
    if single and MULTI_ONLY in chosen:
        raise ValueError(f"A single-repository install leaves out {MULTI_ONLY}; drop it or set single_repository "
                         "to false")
    for skill, dependencies in REQUIRES.items():
        if skill in chosen:
            for dependency in dependencies:
                if dependency not in chosen and not (single and dependency == MULTI_ONLY):
                    raise ValueError(f"{skill} requires {dependency}")
    return tuple(name for name in skill_names if name in chosen)


def delegation_line(skills):
    if "orchestrate-vscode" not in skills:
        # Without orchestrate-vscode there is no size script, so no review floor and no self-review.
        return f"Keep verification of {CODE_CHANGES} pending until a separate reviewer checks them."
    return ("Read [orchestrate-vscode](skills/orchestrate-vscode/SKILL.md) before dispatch, research, or a review of "
            f"{CODE_CHANGES}.")


def check_links(path, base):
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        if "://" not in target and not (base / target).resolve().is_file():
            raise ValueError(f"Broken selected route link in {path}: {target}")


def check_scripts(content, root, fallback=None):
    for interpreter, target in SCRIPT.findall(content):
        if interpreter != "python3":
            raise ValueError(f"Unsupported selected script invocation: use python3 for {target}")
        # A sync may cite a script the package ships but the workspace does not hold yet.
        if not (root / target).is_file() and not (fallback and (fallback.parent / target).is_file()):
            raise ValueError(f"Missing selected script: {target}")


def validate(root, skills, entry, entry_fallback=None):
    github = root / ".github"
    for name in skills:
        skill = github / "skills" / name / "SKILL.md"
        if not skill.is_file():
            raise ValueError(f"Selected skill is missing: {name}")
        body = skill.read_text(encoding="utf-8")
        if not body.startswith("---\n"):
            raise ValueError(f"Selected skill has invalid frontmatter: {name}")
        header, marker, _ = body[4:].partition("\n---\n")
        if (not marker or not re.search(rf"^name:[ \t]*{re.escape(name)}[ \t]*$", header, re.M)
            or not re.search(r"^description:[ \t]*\S.*$", header, re.M)):
            raise ValueError(f"Selected skill has invalid frontmatter: {name}")
        model_disabled = re.search(r"^disable-model-invocation:\s*true\s*$", header, re.I | re.M)
        user_only = name in USER_ONLY or (name not in ALL_SKILLS and bool(model_disabled))
        if not user_only and model_disabled:
            raise ValueError(f"Unsupported selected invocation: {name} must be model-invocable")
        if user_only and (
                not model_disabled or not re.search(r"^user-invocable:\s*true\s*$", header, re.I | re.M)):
            raise ValueError(f"Unsupported selected invocation: {name} must be user-invocable")
        for path in (github / "skills" / name).rglob("*.md"):
            base = github if path.name == "copilot-instructions.template.md" else path.parent
            check_links(path, base)
            check_scripts(path.read_text(encoding="utf-8"), root)
    for target in LINK.findall(entry):
        if ("://" not in target and target not in WORKSPACE_LINKS and not (github / target).resolve().is_file()
                and not (entry_fallback and (entry_fallback / target).resolve().is_file())):
            raise ValueError(f"Broken selected entry link: {target}")
    check_scripts(entry, root, entry_fallback)
    return len(skills)


def tree_files(github, folder, files):
    for path in folder.rglob("*"):
        if "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
            continue
        if path.is_symlink():
            raise ValueError(f"Unreviewed skill symlink: {path}")
        if path.is_file():
            files[path.relative_to(github).as_posix()] = path
    return files


def skill_files(github, skills):
    files = {}
    for name in skills:
        tree_files(github, github / "skills" / name, files)
    return files


def package_files(github, skills):
    """Selected skill trees, with their skill-local references, and helper agents.

    Any other .github file, such as a team standards document, belongs to the team. The package README lives at
    the repository root, outside .github, so a sync never ships one."""
    files = skill_files(github, skills)
    tree_files(github, github / "agents", files)
    return files


def from_package(source_github, relative):
    """Whether the source still ships the skill folder that holds this file; agents always come from it."""
    parts = relative.split("/")
    return parts[0] != "skills" or (source_github / "skills" / parts[1] / "SKILL.md").is_file()


def package_owned(relative):
    """Whether a manifest entry names current package content; older setups also tracked shared references."""
    return relative.split("/")[0] in ("skills", "agents")


def plan_updates(target_github, source_github, skills, adopted, keep=()):
    """Return proposed writes, conflicts, kept files, and files the source no longer ships; change nothing."""
    if not isinstance(adopted, dict):
        raise ValueError("Invalid adopted skill manifest")
    updates, conflicts, kept = [], [], []
    source_files = package_files(source_github, skills)
    local_files = package_files(target_github, skills)
    retired = [(relative, hash_bytes(local_files[relative].read_bytes()) != adopted[relative])
               for relative in sorted(adopted) if relative in local_files and relative not in source_files
               and from_package(source_github, relative)]
    unknown = set(keep) - set(source_files) - {relative for relative, _ in retired}
    if unknown:
        raise ValueError(f"--keep-local names no package file: {sorted(unknown)[0]}")
    for relative, source in sorted(source_files.items()):
        target = target_github / relative
        proposed = source.read_bytes()
        if target.exists() and (target.is_symlink() or not target.is_file()):
            raise ValueError(f"Selected skill target is not a regular file: {target}")
        if relative in keep and target.exists():
            if target.read_bytes() != proposed and adopted.get(relative) != hash_bytes(proposed):
                kept.append(relative)
            continue
        if not target.exists():
            updates.append((target, None, proposed))
            continue
        current = target.read_bytes()
        if current == proposed:
            continue
        previous = adopted.get(relative)
        if previous is None or (hash_bytes(current) != previous and hash_bytes(proposed) != previous):
            conflicts.append((target, current, proposed))
        elif hash_bytes(current) == previous:
            updates.append((target, current, proposed))
        # A local edit with unchanged source is kept as a local choice.
    kept += [relative for relative, _ in retired if relative in keep]
    retired = [(relative, edited) for relative, edited in retired if relative not in keep]
    return updates, conflicts, kept, retired


def adopted_hashes(github, source_github, skills, adopted, kept=(), removed=()):
    """Record which installed files match the package, so a later update can tell team edits apart."""
    result = {relative: value for relative, value in adopted.items() if package_owned(relative)}
    source = package_files(source_github, skills) if source_github else {}
    for relative, path in package_files(github, skills).items():
        current = hash_bytes(path.read_bytes())
        if not source_github:
            result.setdefault(relative, current)
        elif relative in source and current == hash_bytes(source[relative].read_bytes()):
            result[relative] = current
    for relative in kept:
        if relative in source:
            result[relative] = hash_bytes(source[relative].read_bytes())
        else:
            result.pop(relative, None)
    for relative in removed:
        result.pop(relative, None)
    return result


def unselected_skills(github, skills):
    return sorted(path.parent.name for path in (github / "skills").glob("*/SKILL.md")
                  if path.parent.name not in skills)


def candidates(github, source_github, skills, single, known=None):
    """List package skills neither installed nor selected here, as (name, label, missing dependencies).

    known is the package catalog recorded at the last applied setup, or None when no record exists. A skill
    outside that record was published since then; without a record, setup has never offered any of them."""
    local = catalog(github)
    result = []
    for name in ordered(catalog(source_github)):
        if name in local or name in skills or (single and name == MULTI_ONLY):
            continue
        label = "not offered before" if known is None else ("new since the last sync" if name not in known else "")
        needs = tuple(dependency for dependency in REQUIRES.get(name, ())
                      if dependency not in skills and not (single and dependency == MULTI_ONLY))
        result.append((name, label, needs))
    return result
