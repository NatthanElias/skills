#!/usr/bin/env python3
"""Decide task placement from scoped file bytes / 4, not actual model usage."""

import argparse
import json
import sys
from pathlib import Path

FLOOR_TOKENS = 25_000
CEILING_TOKENS = 150_000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Relevant task inputs; files only")
    parser.add_argument("--scope", required=True, help="The bounded task being placed")
    parser.add_argument("--planned-bytes", type=int, default=0,
                        help="Additional, unmeasured text expected for this task")
    parser.add_argument("--exception", choices=("user-request", "independent-verification"))
    parser.add_argument("--reason", help="Source of the exception or planned-size estimate")
    parser.add_argument("--floor-tokens", type=int, default=FLOOR_TOKENS,
                        help="Explicit project/user policy override for delegation floor")
    parser.add_argument("--ceiling-tokens", type=int, default=CEILING_TOKENS,
                        help="Explicit project/user policy override for task ceiling")
    args = parser.parse_args()
    if not args.scope.strip():
        parser.error("--scope must name the task")
    if args.planned_bytes < 0:
        parser.error("--planned-bytes must be nonnegative")
    if not 0 < args.floor_tokens <= args.ceiling_tokens:
        parser.error("thresholds must satisfy 0 < floor <= ceiling")
    if (args.exception or args.planned_bytes) and not (args.reason or "").strip():
        parser.error("an exception or planned estimate requires --reason")
    if not args.files and not args.planned_bytes:
        parser.error("provide scoped files or a justified planned-size estimate")

    files = {}
    try:
        for name in args.files:
            path = Path(name).resolve(strict=True)
            if not path.is_file():
                raise ValueError(f"not a regular file: {name}")
            stat = path.stat()
            # Count aliases and hard links to the same file only once.
            key = (stat.st_dev, stat.st_ino)
            if key not in files:
                files[key] = {"path": str(path), "bytes": stat.st_size}
    except (OSError, ValueError) as error:
        print(json.dumps({"decision": "invalid_scope", "error": str(error)}))
        return 2

    measured = sum(item["bytes"] for item in files.values())
    total = measured + args.planned_bytes
    estimate = (total + 3) // 4
    if estimate > args.ceiling_tokens:
        decision = "split_required"
    elif estimate >= args.floor_tokens:
        decision = "delegate"
    elif args.exception:
        decision = "delegate_exception"
    else:
        decision = "local"
    result = {
        "scope": args.scope,
        "decision": decision,
        "estimated_tokens": estimate,
        "measured_bytes": measured,
        "planned_bytes": args.planned_bytes,
        "estimator": "ceil((measured_bytes + planned_bytes) / 4)",
        "floor_tokens": args.floor_tokens,
        "ceiling_tokens": args.ceiling_tokens,
        "exception": args.exception,
        "reason": args.reason,
        "files": sorted(files.values(), key=lambda item: item["path"]),
    }
    print(json.dumps(result, sort_keys=True))
    return 3 if decision == "split_required" else 0


if __name__ == "__main__":
    sys.exit(main())
