# score_rust_policies
Centralized Rust linting and formatting policies for the Eclipse Safe Open Vehicle Core (S-CORE). This repository packages shared Rust lint/format defaults so every S-CORE crate can use the same safety-focused rules.

## Goals
- Provide one set of vetted Rust linting and formatting defaults for S-CORE projects.
- Distribute those policies as a Bazel module (`score_rust_policies`) so bzlmod users can depend on them directly.
- Keep tooling configurations (e.g., Clippy, rustfmt) versioned and auditable in one place.

## Rust lint policy levels
- `clippy/strict/clippy.toml`: ASIL-B–oriented settings for safety-critical code (enables `pedantic`/`nursery`, disallows `panic`/`unwrap`/`expect`, forbids debug/print macros, and enforces size/complexity thresholds).
- `clippy/relaxed/clippy.toml`: For tooling, generators, and tests where controlled panics/unwraps and debug printing are acceptable. Still forbids `todo` and `unimplemented`.
- `lint-profiles/strict/Cargo.toml` / `lint-profiles/relaxed/Cargo.toml`: Corresponding `[lints.rust]`, `[lints.clippy]`, and `[profile.release]` settings for use directly in a project's `Cargo.toml`. See the [SCORE Rust Coding Guidelines](https://eclipse-score.github.io/score/contribute/development/rust/coding_guidelines.html) for the full rationale and coverage matrix.

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

## Local validation
- From `tests/` (consumer workspace with a local_path_override) run:
  - `bazel build --config=strict //:sample_clippy`
  - `bazel build --config=relaxed //:sample_clippy`
- The `tests/.bazelrc` sets the strict/relaxed Clippy configs to `@score_rust_policies//clippy/{strict,relaxed}:clippy.toml` via `@rules_rust//rust/settings:clippy.toml`.

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
- `tests/`: consumer workspace that depends on this module via `local_path_override` and runs Clippy with strict/relaxed configs.
- `rustfmt/`: rustfmt defaults.

## Contributing
See `CONTRIBUTION.md` for how to propose and review policy changes. All contributions require ECA/DCO sign-off and follow the Eclipse Foundation project handbook.

## License
Apache License 2.0. See `LICENSE.md`.
