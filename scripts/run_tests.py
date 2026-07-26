#!/usr/bin/env python3
"""
Test Runner - Run all tests with coverage report

Usage:
    python scripts/run_tests.py           # Run all tests
    python scripts/run_tests.py --unit    # Run unit tests only
    python scripts/run_tests.py --integration  # Run integration tests
    python scripts/run_tests.py --coverage     # Run with coverage report
    python scripts/run_tests.py --watch        # Watch mode
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Run tests based on command-line arguments."""
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"

    args = sys.argv[1:]
    if not args:
        args = ["--all"]

    cmd = [sys.executable, "-m", "pytest"]

    if "--coverage" in args:
        cmd.extend(["--cov=backend/app", "--cov-report=term-missing", "--cov-report=html"])
        args.remove("--coverage")

    if "--unit" in args:
        cmd.append(str(tests_dir / "test_unit"))
    elif "--integration" in args:
        cmd.append(str(tests_dir / "test_integration"))
    elif "--all" in args or not args:
        cmd.append(str(tests_dir))

    if "-v" not in args:
        cmd.append("-v")

    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=str(project_root))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
