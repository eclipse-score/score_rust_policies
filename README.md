# score_rust_policies
Centralized Rust linting and formatting policies for the Eclipse Safe Open Vehicle Core (S-CORE). This repository packages shared Rust lint/format defaults so every S-CORE crate can use the same safety-focused rules.

## Goals
- Provide one set of vetted Rust linting and formatting defaults for S-CORE projects.
- Distribute those policies as a Bazel module (`score_rust_policies`) so bzlmod users can depend on them directly.
- Keep tooling configurations (e.g., Clippy, rustfmt) versioned and auditable in one place.

## Rust lint policy levels
Lint *levels* (which lints warn or are hard errors) come from the Cargo
`[lints.rust]` / `[lints.clippy]` tables in `lint-profiles/` (or, for Bazel-first
repos, from `rustc-lints/flags.bzl` and `rules_rust` lint config). The
`clippy.toml` files only configure Clippy *options* (e.g. `msrv`,
`check-private-items`, thresholds, allowed/disallowed names); they do not by
themselves set the `unwrap_used`/`panic`/`print_stdout` levels.

- `clippy/strict/clippy.toml`: ASIL-B–oriented Clippy *options* for safety-critical code (sets `msrv`, checks private items, and tunes size/complexity thresholds). Pair it with `lint-profiles/strict/Cargo.toml` (or `STRICT_RUSTC_FLAGS`) to actually enforce the `pedantic`/`nursery` and `panic`/`unwrap`/`expect`/debug-macro levels.
- `clippy/relaxed/clippy.toml`: Clippy *options* for tooling, generators, and tests. Pair it with `lint-profiles/relaxed/Cargo.toml` for the relaxed lint levels.
- `lint-profiles/strict/Cargo.toml` / `lint-profiles/relaxed/Cargo.toml`: Corresponding `[lints.rust]`, `[lints.clippy]`, and `[profile.release]` settings for use directly in a project's `Cargo.toml`. The main behavioral split today is that `strict` keeps `unsafe_op_in_unsafe_fn = "deny"`, while `relaxed` downgrades it to `warn`; the rest is currently aligned. See the [SCORE Rust Coding Guidelines](https://eclipse-score.github.io/score/contribute/development/rust/coding_guidelines.html) for the full rationale and coverage matrix.

### Relaxed profile boundary
The relaxed profile is meant for tooling, generators, and tests where controlled
panics/unwraps and debug printing are acceptable, so lints like `unwrap_used` and
debug-macro checks are downgraded to `warn`. It intentionally keeps several
safety/documentation lints as hard errors (`deny`), including
`missing_panics_doc`, `undocumented_unsafe_blocks`, `wildcard_imports`, and
`declare_interior_mutable_const`. The only rustc level that currently differs
between strict and relaxed is `unsafe_op_in_unsafe_fn` (`deny` in strict, `warn`
in relaxed).


## How to use lint policies in consumers
- Wire configs in your repo’s `.bazelrc` (mirrors `tests/.bazelrc`):
  ```
  build:clippy-strict  --@rules_rust//rust/settings:clippy.toml=@score_rust_policies//clippy/strict:clippy.toml
  build:clippy-relaxed --@rules_rust//rust/settings:clippy.toml=@score_rust_policies//clippy/relaxed:clippy.toml
  ```
- Exclude targets that shouldn’t be linted (e.g., generated code, some tests) by tagging them `no-clippy`:
  ```
  rust_test(
      name = "my_test",
      srcs = [...],
      tags = ["no-clippy"],
  )
  ```
- Add a dedicated lint target (pattern from `rules_rust`):
  ```
  load("@rules_rust//rust:defs.bzl", "rust_clippy")

  rust_clippy(
      name = "clippy",
      deps = ["//src/rust/..."],
      tags = ["manual"],
      testonly = True,
      visibility = ["//visibility:public"],
  )
  ```
  Then run `bazel build --config=clippy-strict //:clippy` (or `--config=clippy-relaxed`).

## Applying rustc lints in a Bazel-first repo
The `[lints.rust]` table in `lint-profiles/{strict,relaxed}/Cargo.toml` is a Cargo
feature and is **not** read by `rules_rust`. For Bazel-only consumers (e.g.
`baselibs_rust`), the same rustc lints are exported as ready-to-use flag lists in
[rustc-lints/flags.bzl](rustc-lints/flags.bzl), so they don't have to be redefined.

- Load the shared flag list and apply it per target:
  ```starlark
  load("@score_rust_policies//rustc-lints:flags.bzl", "STRICT_RUSTC_FLAGS")

  rust_library(
      name = "my_lib",
      srcs = [...],
      rustc_flags = STRICT_RUSTC_FLAGS,  # or RELAXED_RUSTC_FLAGS
  )
  ```
- To apply the same lints to every target via a `.bazelrc` config instead, use
  `@rules_rust//rust/settings:extra_rustc_flags`. Note: a `.bazelrc` cannot `load`
  a `.bzl`, so the flags must be repeated literally there:
  ```
  build:rustc-strict --@rules_rust//rust/settings:extra_rustc_flags=-Wunused,-Dunsafe_op_in_unsafe_fn,-Wmissing_abi,-Wunreachable_pub,-Wmissing_docs,-Wunused_results,-Wlet_underscore_drop,-Welided_lifetimes_in_paths,-Wexplicit_outlives_requirements,-Wmacro_use_extern_crate,-Wmeta_variable_misuse,-Wnon_local_definitions,-Wredundant_lifetimes,-Wsingle_use_lifetimes,-Wtrivial_numeric_casts,-Wunit_bindings,-Wunnameable_types,-Wvariant_size_differences
  ```
- Combine with the matching Clippy profile when building:
  ```
  bazel build --config=clippy-strict --config=rustc-strict //src/...
  ```

Notes:
- The flag lists in [rustc-lints/flags.bzl](rustc-lints/flags.bzl) mirror the
  `[lints.rust]` tables in lint-profiles; keep both in sync (there is no automatic
  translation from `[lints.rust]` to rustc flags). `tools/check_lint_sync.py`
  (run in CI) fails if they drift apart.
- Loading the constant (per target) avoids duplicating the flags; the global
  `.bazelrc` path cannot read the `.bzl` and therefore repeats them.

## Local validation
- From `tests/` (consumer workspace with a local_path_override) run:
  - `bazel build --config=clippy-strict //:sample_clippy`
  - `bazel build --config=clippy-relaxed //:sample_clippy`
- The `tests/.bazelrc` sets the `clippy-strict`/`clippy-relaxed` Clippy configs to `@score_rust_policies//clippy/{strict,relaxed}:clippy.toml` via `@rules_rust//rust/settings:clippy.toml`.

## Using with Bazel (bzlmod)
- Add to your `MODULE.bazel`:
  ```
  bazel_dep(name = "score_rust_policies", version = "<latest-version>")
  ```
- During local development you can pin a checkout with:
  ```
  local_path_override(
      module_name = "score_rust_policies",
      path = "<path-to-this-repo>",
  )
  ```
- Reference policy files in Bazel targets with:
  - `@score_rust_policies//clippy/strict:clippy.toml` for safety components.
  - `@score_rust_policies//clippy/relaxed:clippy.toml` for tooling/tests.
- When running Clippy directly, pass the config you need: `cargo clippy --config-path path/to/clippy/clippy.toml`.

## Repository layout
- `MODULE.bazel`: Bazel module metadata for `score_rust_policies`.
- `BUILD.bazel`: repo root package (tooling configs live in subpackages).
- `LICENSE.md`: Apache License 2.0.
- `CONTRIBUTION.md`: contribution process and links to S-CORE guidelines.
- `.gitignore`: common ignores for Bazel and development tooling.
- `clippy/`: Clippy-only configs exported as `@score_rust_policies//clippy/{strict,relaxed}:clippy.toml`.
- `lint-profiles/`: Cargo lint profiles exported as `@score_rust_policies//lint-profiles/{strict,relaxed}:Cargo.toml`.
- `rustc-lints/`: rustc lint flag lists for Bazel consumers, exported as `@score_rust_policies//rustc-lints:flags.bzl` (`STRICT_RUSTC_FLAGS` / `RELAXED_RUSTC_FLAGS`).
- `tools/`: maintenance scripts, including `check_lint_sync.py`, which verifies the `flags.bzl` lists stay in sync with the Cargo `[lints.rust]` tables.
- `tests/`: consumer workspace that depends on this module via `local_path_override` and runs Clippy with strict/relaxed configs.
- `rustfmt/`: rustfmt defaults.

## Contributing
See `CONTRIBUTION.md` for how to propose and review policy changes. All contributions require ECA/DCO sign-off and follow the Eclipse Foundation project handbook.

## License
Apache License 2.0. See `LICENSE.md`.
