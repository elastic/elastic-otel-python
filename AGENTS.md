# Release updates

- Set the package version in `src/elasticotel/distro/version.py`. `pyproject.toml` reads this value dynamically.
- Add matching release entries to `CHANGELOG.md` and `docs/release-notes/index.md`, following each file's existing format, including release-note anchors and linked PR references.
- When the user specifies commits to include, list only those changes in the new release entries. Preserve earlier release entries.
- For OpenTelemetry SDK bumps, include an `Upstream changes:` list linking to the release discussions in both `open-telemetry/opentelemetry-python` and `open-telemetry/opentelemetry-python-contrib`. Include intermediate releases covered by the bump, such as both 1.45.0 and 1.45.1 when upgrading from 1.44.0 to 1.45.1. Use the v1.13.0 and v1.18.0 entries as formatting examples.
- Verify discussion URLs and release titles through GitHub rather than guessing discussion numbers. The REST discussions endpoint defaults to oldest first; use pagination or GraphQL discussions ordered by `CREATED_AT` descending to find recent announcements.
- Run `git diff --check` and review the diff to confirm the version, release entries, and requested scope agree.
