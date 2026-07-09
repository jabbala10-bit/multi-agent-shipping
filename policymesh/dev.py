from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Sequence


def run(command: Sequence[str], env: dict[str, str] | None = None) -> int:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.call(command, env=merged_env)


def test() -> int:
    return run([sys.executable, "-m", "pytest"], {"POLICYMESH_OFFLINE_TOOLS": "1"})


def lint() -> int:
    return run([sys.executable, "-m", "ruff", "check", "."])


def smoke() -> int:
    return run([sys.executable, "-m", "pytest", "tests/test_smoke.py"], {"POLICYMESH_OFFLINE_TOOLS": "1"})


def adk(service: str) -> int:
    return run([sys.executable, "-m", "google.adk.cli", "web", service])


def doctor() -> int:
    checks = [
        ("python", [sys.executable, "--version"]),
        ("pytest", [sys.executable, "-m", "pytest", "--version"]),
        ("ruff", [sys.executable, "-m", "ruff", "--version"]),
    ]
    status = 0
    for name, command in checks:
        print(f"== {name} ==")
        status = max(status, run(command))
    return status


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="policymesh", description="PolicyMesh monorepo dev helper.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("test", help="Run the test suite in offline tool mode.")
    subcommands.add_parser("lint", help="Run Ruff lint checks.")
    subcommands.add_parser("smoke", help="Run smoke tests only.")
    subcommands.add_parser("doctor", help="Check local development tooling.")
    adk_parser = subcommands.add_parser("adk", help="Launch an ADK web server for a service package.")
    adk_parser.add_argument("service", choices=["shopping", "shipping", "storefront"])

    args = parser.parse_args(argv)
    if args.command == "test":
        return test()
    if args.command == "lint":
        return lint()
    if args.command == "smoke":
        return smoke()
    if args.command == "doctor":
        return doctor()
    if args.command == "adk":
        return adk(args.service)
    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
