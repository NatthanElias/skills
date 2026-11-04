#!/usr/bin/env python3
"""Tests for git_hooks.py and resume_note.py against scratch Git repositories.

Usage: python3 .agents/skills/feature-workflow/scripts/test_git_hooks.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import constraints  # noqa: E402
import git_hooks  # noqa: E402
import resume_note  # noqa: E402

ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
       "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}


class Repo:
    def __init__(self, root):
        self.root = root
        self.git("init", "-q", "-b", "main")
        scripts = root / Path(git_hooks.SCRIPT).parent
        shutil.copytree(HERE, scripts, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: add workflow scripts")

    def git(self, *args, check=True):
        result = subprocess.run(["git", *args], cwd=self.root, env=ENV, capture_output=True, text=True)
        if check and result.returncode:
            raise AssertionError(f"git {' '.join(args)} failed:\n{result.stdout}{result.stderr}")
        return result

    def hooks(self, action):
        return subprocess.run([sys.executable, git_hooks.SCRIPT, action], cwd=self.root, env=ENV,
                              capture_output=True, text=True)

    def write(self, relative, text="x\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit(self, message, *paths, extra=()):
        if paths:
            self.git("add", "-f", *paths)
        return self.git("commit", "-q", *extra, "-m", message, check=False)


class GitHooksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def installed(self):
        result = self.repo.hooks("install")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.repo

    def test_install_status_uninstall(self):
        self.assertEqual(self.repo.hooks("status").stdout.strip(), "not installed")
        self.installed()
        self.assertEqual(self.repo.hooks("status").stdout.strip(), "installed")
        self.assertEqual(self.repo.hooks("install").returncode, 0)
        self.repo.hooks("uninstall")
        self.assertEqual(self.repo.hooks("status").stdout.strip(), "not installed")

    def test_foreign_hook_is_kept(self):
        foreign = self.repo.root / ".git/hooks/commit-msg"
        foreign.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        result = self.repo.hooks("install")
        self.assertEqual(result.returncode, 3)
        self.assertIn("git_hooks.py commit-msg", result.stdout)
        self.assertEqual(foreign.read_text(encoding="utf-8"), "#!/bin/sh\nexit 0\n")
        self.assertFalse((self.repo.root / ".git/hooks/pre-commit").exists())

    def test_hook_manager_is_respected(self):
        self.repo.git("config", "core.hooksPath", ".husky")
        self.assertEqual(self.repo.hooks("install").returncode, 3)
        self.assertTrue(self.repo.hooks("status").stdout.startswith("managed"))
        self.assertFalse((self.repo.root / ".husky").exists())

    def test_message_is_checked(self):
        repo = self.installed()
        repo.write("src/a.py")
        self.assertNotEqual(repo.commit("Add a thing.", "src/a.py").returncode, 0)
        self.assertEqual(repo.commit("feat(core): add a thing\n\nBody line.", "src/a.py").returncode, 0)

    def test_commit_all_is_checked(self):
        repo = self.installed()
        repo.write("src/a.py")
        repo.commit("feat: add a", "src/a.py")
        repo.write("src/a.py", "y\n")
        self.assertNotEqual(repo.commit("bad message", extra=("-a",)).returncode, 0)
        self.assertEqual(repo.commit("fix: change a", extra=("-a",)).returncode, 0)

    def test_feature_folder_is_blocked(self):
        repo = self.installed()
        repo.write(".specs/features/f1/plan.md")
        result = repo.commit("docs: add plan", ".specs/features/f1/plan.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("feature folders", result.stderr)

    def test_lessons_commit_alone_as_chore_specs(self):
        repo = self.installed()
        repo.write(".specs/lessons/abc.json", "{}\n")
        repo.write("src/a.py")
        self.assertNotEqual(repo.commit("chore(specs): record lesson", ".specs/lessons/abc.json",
                                        "src/a.py").returncode, 0)
        repo.git("reset", "-q")
        self.assertNotEqual(repo.commit("feat: record lesson", ".specs/lessons/abc.json").returncode, 0)
        self.assertEqual(repo.commit("chore(specs): record lesson", ".specs/lessons/abc.json").returncode, 0)

    def test_constraints_are_checked(self):
        repo = self.installed()
        repo.write(".specs/constraints/bad.md", "not a record\n")
        repo.write("src/a.py")
        result = repo.commit("feat: add a", "src/a.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("constraint", result.stderr)
        result = repo.commit("feat: add a", ".specs/constraints/bad.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("constraints.py check", result.stderr)

    def test_constraints_checked_as_staged(self):
        repo = self.installed()
        repo.write(".specs/constraints/bad.md", "not a record\n")
        repo.git("add", ".specs/constraints/bad.md")
        (repo.root / ".specs/constraints/bad.md").unlink()
        result = repo.commit("feat: add constraint")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stage or discard", result.stderr)

    def test_constraints_deleted_from_worktree(self):
        repo = self.installed()
        repo.write(".specs/constraints/bad.md", "not a record\n")
        repo.git("add", ".specs/constraints/bad.md")
        shutil.rmtree(repo.root / ".specs/constraints")
        result = repo.commit("feat: add constraint")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stage or discard", result.stderr)

    def test_amend_checks_the_whole_commit(self):
        repo = self.installed()
        repo.write("src/a.py")
        self.assertEqual(repo.commit("feat: add a", "src/a.py").returncode, 0)
        repo.write(".specs/lessons/abc.json", "{}\n")
        repo.git("add", ".specs/lessons/abc.json")
        result = repo.commit("chore(specs): record lesson", extra=("--amend",))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lesson", result.stderr)
        repo.git("reset", "-q", "HEAD", "--", ".specs/lessons/abc.json")
        repo.git("checkout", "-q", "-b", "lessons")
        self.assertEqual(repo.commit("chore(specs): record lesson", ".specs/lessons/abc.json").returncode, 0)
        result = repo.commit("feat: record lesson", extra=("--amend",))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("chore(specs)", result.stderr)
        self.assertEqual(repo.commit("chore(specs): record a lesson", extra=("--amend",)).returncode, 0)

    def test_first_commit_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, env=ENV, check=True)
            scripts = root / Path(git_hooks.SCRIPT).parent
            shutil.copytree(HERE, scripts, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            repo = Repo.__new__(Repo)
            repo.root = root
            self.assertEqual(repo.hooks("install").returncode, 0)
            self.assertNotEqual(repo.commit("bad message", ".").returncode, 0)
            result = repo.commit("chore: add workflow scripts", ".")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_symlinked_hook_is_foreign(self):
        link = self.repo.root / ".git/hooks/pre-commit"
        link.symlink_to(self.repo.root / "manager-hook")
        self.assertEqual(self.repo.hooks("install").returncode, 3)
        self.assertFalse((self.repo.root / "manager-hook").exists())

    def test_status_needs_executable_hooks(self):
        self.installed()
        (self.repo.root / ".git/hooks/commit-msg").chmod(0o644)
        self.assertIn("commit-msg not executable", self.repo.hooks("status").stdout)
        self.installed()
        self.assertEqual(self.repo.hooks("status").stdout.strip(), "installed")

    def test_merge_commit_is_skipped(self):
        repo = self.installed()
        repo.git("checkout", "-q", "-b", "side")
        repo.write("src/b.py")
        repo.commit("feat: add b", "src/b.py")
        repo.git("checkout", "-q", "main")
        repo.write("src/c.py")
        repo.commit("feat: add c", "src/c.py")
        self.assertEqual(repo.git("merge", "-q", "--no-edit", "side", check=False).returncode, 0)

    def test_missing_script_skips(self):
        repo = self.installed()
        shutil.rmtree(repo.root / Path(git_hooks.SCRIPT).parts[0])
        repo.write("src/a.py")
        result = repo.commit("not conventional", "src/a.py")
        self.assertEqual(result.returncode, 0)
        self.assertIn("missing in this checkout", result.stderr)


class ConstraintsIndexTest(unittest.TestCase):
    def test_index_names_no_harness_folder(self):
        # The commit hook runs one port's check; an index rendered by another port must still pass it.
        self.assertNotIn("/skills/", constraints.index_text([]))


class ResumeNoteTest(unittest.TestCase):
    def test_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(resume_note.note(root), "")
            repo = Repo(root)
            self.assertEqual(resume_note.note(root), "")
            repo.write(".specs/features/f1/execution/handoff.md")
            text = resume_note.note(root)
            self.assertIn(".specs/features/f1/execution/handoff.md", text)
            self.assertIn("on main", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
