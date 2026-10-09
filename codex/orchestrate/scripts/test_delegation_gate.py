"""Exercise gate boundaries, task scope validation and explicit exceptions."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GATE = Path(__file__).with_name("delegation_gate.py")


class DelegationGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def file(self, size):
        path = self.root / "scope.txt"
        path.write_bytes(b"a" * size)
        return str(path)

    def run_gate(self, *args):
        return subprocess.run(
            [sys.executable, str(GATE), "--scope", "fixture", *args],
            capture_output=True, text=True,
        )

    def test_size_boundaries(self):
        for size, expected, code in [
            (99_996, "local", 0),
            (100_000, "delegate", 0),
            (600_000, "delegate", 0),
            (600_001, "split_required", 3),
        ]:
            with self.subTest(size=size):
                result = self.run_gate(self.file(size))
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)["decision"], expected)

    def test_aliases_count_once(self):
        source = self.file(99_996)
        alias = self.root / "alias.txt"
        alias.symlink_to(source)
        hardlink = self.root / "hardlink.txt"
        hardlink.hardlink_to(source)
        result = self.run_gate(source, source, str(alias), str(hardlink))
        record = json.loads(result.stdout)
        self.assertEqual(record["measured_bytes"], 99_996)
        self.assertEqual(record["decision"], "local")

    def test_explicit_exceptions_and_ceiling(self):
        for exception in ["user-request", "independent-verification"]:
            with self.subTest(exception=exception):
                result = self.run_gate(self.file(4), "--exception", exception,
                                       "--reason", "Explicit workflow requirement")
                self.assertEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout)["decision"], "delegate_exception")
                oversized = self.run_gate(self.file(600_001), "--exception", exception,
                                          "--reason", "Explicit workflow requirement")
                self.assertEqual(oversized.returncode, 3)
                self.assertEqual(json.loads(oversized.stdout)["decision"], "split_required")

    def test_planned_work_is_labelled_and_counted(self):
        result = self.run_gate("--planned-bytes", "100000", "--reason", "Declared new text bound")
        record = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(record["decision"], "delegate")
        self.assertEqual(record["measured_bytes"], 0)
        self.assertEqual(record["planned_bytes"], 100_000)

    def test_invalid_scope_fails_closed(self):
        for args in [
            [],
            [str(self.root / "missing.txt")],
            [str(self.root)],
            [self.file(4), "--exception", "user-request"],
            ["--planned-bytes", "80000"],
            ["--planned-bytes", "-1", "--reason", "Invalid"],
        ]:
            with self.subTest(args=args):
                result = self.run_gate(*args)
                self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
