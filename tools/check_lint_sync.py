#!/usr/bin/env python3
# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
"""Verify that the rustc flag lists mirror the Cargo `[lints.rust]` tables.

Cargo reads `[lints.rust]` in `lint-profiles/{strict,relaxed}/Cargo.toml`, while
Bazel-first consumers use the flag lists in `rustc-lints/flags.bzl`. There is no
automatic translation between the two formats, so this check guards against
drift (for example, a lint set to `warn` in Cargo but `-D...` in the flag list).

Run from the repository root:

    python3 tools/check_lint_sync.py
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLAGS_BZL = REPO_ROOT / "rustc-lints" / "flags.bzl"

# Cargo lint level -> rustc flag prefix.
LEVEL_TO_PREFIX = {
    "allow": "-A",
    "warn": "-W",
    "deny": "-D",
    "forbid": "-F",
}

# Profile name -> (Cargo.toml path, flags.bzl variable name).
PROFILES = {
    "strict": (
        REPO_ROOT / "lint-profiles" / "strict" / "Cargo.toml",
        "STRICT_RUSTC_FLAGS",
    ),
    "relaxed": (
        REPO_ROOT / "lint-profiles" / "relaxed" / "Cargo.toml",
        "RELAXED_RUSTC_FLAGS",
    ),
}


def load_bzl_flag_lists() -> dict[str, list[str]]:
    """Execute flags.bzl (valid Python) and return its flag-list globals."""
    namespace: dict[str, object] = {}
    exec(compile(FLAGS_BZL.read_text(), str(FLAGS_BZL), "exec"), namespace)
    return {
        name: value
        for name, value in namespace.items()
        if name.endswith("_RUSTC_FLAGS") and isinstance(value, list)
    }


def cargo_lints_to_flags(cargo_path: Path) -> set[str]:
    """Translate a Cargo `[lints.rust]` table into the expected rustc flags."""
    data = tomllib.loads(cargo_path.read_text())
    rust_lints = data.get("lints", {}).get("rust", {})
    flags: set[str] = set()
    for lint, spec in rust_lints.items():
        level = spec["level"] if isinstance(spec, dict) else spec
        if level not in LEVEL_TO_PREFIX:
            raise SystemExit(
                f"{cargo_path}: unknown lint level {level!r} for {lint!r}"
            )
        flags.add(f"{LEVEL_TO_PREFIX[level]}{lint}")
    return flags


def main() -> int:
    bzl_flag_lists = load_bzl_flag_lists()
    ok = True

    for profile, (cargo_path, var_name) in PROFILES.items():
        expected = cargo_lints_to_flags(cargo_path)
        actual = set(bzl_flag_lists.get(var_name, []))

        if expected == actual:
            print(f"[ok] {profile}: {var_name} matches {cargo_path.name} [lints.rust]")
            continue

        ok = False
        print(f"[FAIL] {profile}: {var_name} is out of sync with {cargo_path}")
        for flag in sorted(expected - actual):
            print(f"    missing from {var_name}: {flag}")
        for flag in sorted(actual - expected):
            print(f"    extra in {var_name}:    {flag}")

    if not ok:
        print(
            "\nUpdate rustc-lints/flags.bzl and the Cargo [lints.rust] tables so "
            "they stay in sync."
        )
        return 1

    print("\nAll rustc lint profiles are in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
