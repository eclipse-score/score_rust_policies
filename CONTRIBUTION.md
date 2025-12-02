# score_rust_policies Contribution Guide
The [Eclipse Safe Open Vehicle Core (S-CORE)](https://projects.eclipse.org/projects/automotive.score) project develops an open-source core stack for Software Defined Vehicles (SDVs). This repository centralizes the shared Rust linting and formatting policies that S-CORE crates reuse to maintain consistent, safety-focused defaults.

Project communication happens via the [`score-dev` mailing list](https://accounts.eclipse.org/mailing-list/score-dev), GitHub issues and pull requests, and the [Eclipse SCORE chatroom](https://chat.eclipse.org/#/room/#automotive.score:matrix.eclipse.org).

Please note that the [Eclipse Foundation’s Terms of Use](https://www.eclipse.org/legal/terms-of-use/) apply. Contributors must sign both the [ECA](https://www.eclipse.org/legal/ECA.php) and the [DCO](https://www.eclipse.org/legal/dco/).

## Contributing changes
1. Open an issue describing the policy change you propose (e.g., enabling/disabling a lint) and the rationale, including links to any affected projects.
2. Submit a PR referencing the issue. Keep changes minimal and well-documented, and include examples that justify the chosen defaults when possible.
3. Request reviews from the S-CORE committers. Follow the commit message rules in the [Eclipse Foundation Project Handbook](https://www.eclipse.org/projects/handbook/#resources-commit).

If you are new to the project, see the S-CORE process descriptions and templates at https://eclipse-score.github.io/score/process_description/.
