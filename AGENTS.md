# AGENTS.md

Guidance for AI coding agents working in the **wdgrid** repository
(NiceGUI-based Wikidata grid display and sync).

## Project layout

| Path | Purpose |
| :--- | :--- |
| `wd/` | Python package (source). Entry point: `wd.wdgrid_cmd:main` |
| `tests/` | Unit tests (`test_*.py`, run with `unittest`/`green`) |
| `scripts/` | Dev/build/release shell scripts |
| `docs/` | Documentation sources (mkdocs / sphinx) |
| `site/` | Generated site output |
| `pyproject.toml` | Build (hatchling) + project metadata; version from `wd/__init__.py` |
| `.github/workflows/` | CI: `build.yml` (test matrix), `upload-to-pypi.yml` (release) |

## Setup, build & test

```bash
scripts/install          # pip install . -U
scripts/test             # python -m unittest discover (default)
scripts/test --green     # run with green
scripts/test --module    # run module-by-module
scripts/blackisort       # isort + black on wd/ and tests/
scripts/doc              # build docs
scripts/release          # release pipeline
```

- Python `>=3.10`; supported: 3.10, 3.11, 3.12, 3.13.
- Always run `scripts/test` before committing.

## Code style

- **black** for formatting and **isort** for imports (run `scripts/blackisort`).
- Google-style docstrings (`docformatter`).
- Keep changes minimal and consistent with the existing code.

## Open-source conformance: `checkos`

This project follows the WolfgangFahl open-source project conventions, which are
verified by the `checkos` tool. Run it to check that workflows, README badges,
`pyproject.toml`, and scripts conform:

```bash
checkos -p wdgrid -o WolfgangFahl --local -v       # verbose check
checkos -p wdgrid -o WolfgangFahl --local -v -d    # with per-rule debug detail
checkos -p wdgrid -o WolfgangFahl -b               # emit standard README badge markup
```

A `❌` line indicates a non-conforming file with a count of failing rules; `✅`
lines are passing rules. After making changes that affect CI workflows, README
badges, or packaging, **re-run `checkos` and resolve every `❌`** before finishing.

Common conformance requirements:
- CI uses `actions/checkout@v6` and `actions/setup-python@v6`.
- `build.yml` test matrix: `python-version: [ '3.10', '3.11', '3.12', '3.13' ]`.
- README contains the standard badge set (PyPI, build, issues, API docs, license).

## Commit / PR conventions

- Do not commit, push, or open PRs unless explicitly requested.
- Stage only intended files; never commit secrets.
- Match the existing commit message style.
