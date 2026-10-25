"""Estimate a dispatch's tokens from file bytes and print its route. Standard library only."""

import argparse
import sys
from pathlib import Path

# The only place the dispatch and review limits are set.
FLOOR = 20_000
CEILING = 150_000


def total_bytes(paths):
    total = 0
    for path in paths:
        if path.is_file():
            total += path.stat().st_size
        elif path.is_dir():
            total += sum(item.stat().st_size for item in path.rglob("*")
                         if item.is_file() and ".git" not in item.relative_to(path).parts)
        else:
            raise ValueError(f"Not found: {path}")
    return total


def route(tokens):
    if tokens < FLOOR:
        return "main session"
    if tokens <= CEILING:
        return "one subagent"
    return f"split into at least {-(-tokens // CEILING)} pieces of {CEILING:,} tokens or less"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sum file bytes, divide by four, and print the dispatch route.")
    parser.add_argument("paths", nargs="+", type=Path, help="Files and folders the work reads or touches")
    args = parser.parse_args(argv)
    try:
        size = total_bytes(args.paths)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    tokens = size // 4
    print(f"Bytes: {size:,}; tokens: {tokens:,}; route: {route(tokens)} (floor {FLOOR:,}; ceiling {CEILING:,})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
