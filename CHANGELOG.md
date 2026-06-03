# Changelog

All notable changes to SafeLicensing are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

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
