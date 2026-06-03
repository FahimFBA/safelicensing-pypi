# Changelog

All notable changes to SafeLicensing are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## [1.0.2] - 2026-06-04

### Added
- Docusaurus documentation site with full API reference, quick start, encryption details, and citation page
- Custom license-plate-and-lock SVG logo and favicon for the docs site
- `.whl` and `.tar.gz` artifacts automatically attached to every GitHub Release
- Changelog-driven release workflow: updating `CHANGELOG.md` and pushing to `main` now triggers the full release pipeline automatically
- Shields.io badges in README (PyPI version, Python, license, CI status, docs)
- Non-fast-forward push fix in release workflow using `git pull --rebase` before push

### Changed
- Release workflow consolidated from `publish.yml` into single `release.yml` triggered on `CHANGELOG.md` push
- `pyproject.toml` and `__init__.py` version now auto-synced by CI from `CHANGELOG.md`
- README updated with docs site link, GitHub Packages install instructions, and release guide

### Fixed
- Navbar hide-on-scroll removed (was hiding navbar on mobile screen resize)
- Duplicate PyPI upload gracefully skipped with `skip-existing: true`

---

## [1.0.1] - 2026-05-15

### Added
- Initial public PyPI release
- `protect_image()` and `protect_video()` high-level API with `ProtectImageResult` and `ProtectVideoResult` dataclasses
- Bundled YOLOv8 model (`best.pt`, 6 MB) - no separate download required
- Streamlit browser UI launched via `safelicensing` CLI command
- Dual-pass chaotic XOR encryption using the logistic map at `r = 3.9`
- Low-level research API: `logistic_map`, `generate_key`, `shuffle_pixels`, `encrypt_image`
- Video support with original audio preservation via MoviePy
- Full Docusaurus documentation site with API reference
- GitHub Actions workflow for automated PyPI and GitHub Packages publishing
- GitHub Actions workflow for automated docs deployment to GitHub Pages

### Fixed
- Seed overflow bug: `second_seed = min(seed * 1.1, 0.9999)` prevents seed reaching 1.0

---

## [1.0.0] - 2026-05-01

### Added
- Initial internal release
- YOLOv8-based license plate detection
- Chaotic-map encryption scheme
- Streamlit UI prototype
