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
"""Rust compiler (rustc) lint flags for Bazel consumers.

These lists mirror the `[lints.rust]` tables in
`lint-profiles/{strict,relaxed}/Cargo.toml`. Cargo reads `[lints.rust]`;
`rules_rust` does not, so Bazel-first repositories use the flag lists below.

Keep these lists in sync with the corresponding Cargo.toml `[lints.rust]`
tables. There is no automatic translation between the two formats.

Usage (per target):

    load("@score_rust_policies//rustc-lints:flags.bzl", "STRICT_RUSTC_FLAGS")

    rust_library(
        name = "my_lib",
        srcs = [...],
        rustc_flags = STRICT_RUSTC_FLAGS,
    )

Lint group flags (e.g. `-Wunused`) are listed first so that specific lints
can override the group, matching the Cargo `priority = -1` semantics.
"""

# Mirrors lint-profiles/strict/Cargo.toml [lints.rust].
STRICT_RUSTC_FLAGS = [
    # Lint groups first (lower priority).
    "-Wunused",
    # Specific lints.
    "-Dunsafe_op_in_unsafe_fn",
    "-Wmissing_abi",
    "-Wunreachable_pub",
    "-Wmissing_docs",
    "-Wunused_results",
    "-Wlet_underscore_drop",
    "-Wnon_exhaustive_omitted_patterns",
    "-Welided_lifetimes_in_paths",
    "-Wexplicit_outlives_requirements",
    "-Wmacro_use_extern_crate",
    "-Wmeta_variable_misuse",
    "-Wnon_local_definitions",
    "-Wredundant_lifetimes",
    "-Wsingle_use_lifetimes",
    "-Wtrivial_numeric_casts",
    "-Wunit_bindings",
    "-Wunnameable_types",
    "-Wvariant_size_differences",
]

# Mirrors lint-profiles/relaxed/Cargo.toml [lints.rust].
RELAXED_RUSTC_FLAGS = [
    # Lint groups first (lower priority).
    "-Wunused",
    # Specific lints.
    "-Dunsafe_op_in_unsafe_fn",
    "-Wmissing_abi",
    "-Wunreachable_pub",
    "-Wmissing_docs",
    "-Wunused_results",
    "-Wlet_underscore_drop",
    "-Wnon_exhaustive_omitted_patterns",
    "-Welided_lifetimes_in_paths",
    "-Wexplicit_outlives_requirements",
    "-Wmacro_use_extern_crate",
    "-Wmeta_variable_misuse",
    "-Wnon_local_definitions",
    "-Wredundant_lifetimes",
    "-Wsingle_use_lifetimes",
    "-Wtrivial_numeric_casts",
    "-Wunit_bindings",
    "-Wunnameable_types",
    "-Wvariant_size_differences",
]
