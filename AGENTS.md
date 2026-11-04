# Documentation

- When changing documentation, run Vale over the affected documentation files.
- Fix every Vale error and warning. Investigate every suggestion and apply it when appropriate.

# OpenTelemetry dependency updates

- Take the target SDK version as input from the user. If it is missing, ask for it before changing dependencies; do not choose a version or default to the latest release.
- For an SDK bump, update all matching stable and beta OpenTelemetry pins together in `pyproject.toml` and `operator/requirements.txt`, then regenerate `dev-requirements.txt`. Commit `ed6c354` (SDK 1.45.1 to 1.45.2, beta 0.66b1 to 0.66b2) is an example of the expected scope.
- Verify the target stable/beta release pair using upstream release announcements or package metadata; do not infer the beta version from the SDK version. Packages with independent release cycles (such as AWS extensions, cloud resource detectors, OpAMP, and Elastic instrumentations) should retain their existing versions unless the bump requires a change.
- In `pyproject.toml`, update the API, SDK, OTLP exporter, instrumentation, system metrics instrumentation, container ID resource detector, and semantic conventions pins. Update also the configuration package in the optional dependencies config group. In `operator/requirements.txt`, update the matching exporter, propagator, and instrumentation pins while preserving the package list and file format.
- Generate `dev-requirements.txt` with the baseline Python version supported by the package and pip-tools using the command recorded in its header: `pip-compile --extra=dev --output-file=dev-requirements.txt --strip-extras pyproject.toml`. Use an isolated environment. Preserve the generated dependency annotations and review any transitive or development dependency changes; do not hand-edit the generated pins or broadly upgrade unrelated packages by default.
- Search tracked files for the previous stable and beta versions to catch missed dependency pins. Review matches individually so historical release notes and unrelated version strings remain intact.
- Validate the updated dependencies with the test suite (`nox -- --with-integration-tests`) and check that the distro and `operator/requirements.txt` resolve together in a clean environment. Run `git diff --check` and review the diff for consistent pins and unintended dependency changes. Report any checks that could not run.
- A dependency-only bump does not require a distro version change or new release entries.

# Release updates

- Set the package version in `src/elasticotel/distro/version.py`. `pyproject.toml` reads this value dynamically.
- Add matching release entries to `CHANGELOG.md` and `docs/release-notes/index.md`, following each file's existing format, including release-note anchors and linked PR references.
- Update the reference to the upstream version in `README.md`
- When the user specifies commits to include, list only those changes in the new release entries. Preserve earlier release entries.
- For OpenTelemetry SDK bumps, include an `Upstream changes:` list linking to the release discussions in both `open-telemetry/opentelemetry-python` and `open-telemetry/opentelemetry-python-contrib`. Include intermediate releases covered by the bump, such as both 1.45.0 and 1.45.1 when upgrading from 1.44.0 to 1.45.1. Use the v1.13.0 and v1.18.0 entries as formatting examples.
- Verify discussion URLs and release titles through GitHub rather than guessing discussion numbers. The REST discussions endpoint defaults to oldest first; use pagination or GraphQL discussions ordered by `CREATED_AT` descending to find recent announcements.
- Run `git diff --check` and review the diff to confirm the version, release entries, and requested scope agree.
