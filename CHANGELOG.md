# Changelog
All notable changes to Enhanced Theme Studio will be documented in this file.

## [1.1.0] - 2025-06-29
### Added
- **Image-Based Palette Extraction**: Added ability to extract color palettes directly from uploaded images.
- **Trending Palettes**: Introduced a curated list of trending color palettes for quick loading and inspiration.
- **Custom Color Scheme**: Added a "Custom" scheme option to allow direct loading of palettes without applying color theory rules.

### Changed
- Improved UI for "Pick from Image" feature for better discoverability.
- Refactored `create_dark_variant` and `create_light_variant` methods to reduce code duplication.
- Updated minimum Python version requirement from 3.6 to 3.8 across all documentation and configuration files (`README.md`, `Enhanced_Theme_Studio_Manual.md`, `Enhanced_Theme_Studio_Quick_Start.md`, `pyproject.toml`, `setup.py`).
- Updated version number to 1.1.0.

### Fixed
- Resolved `RecursionError` caused by signal loops in `update_palette`.
- Fixed `AttributeError` when loading custom palettes into an unpopulated table.

## [1.0.0] - 2025-04-28
### Added
- Initial application release as a solo developer project
- Color scheme generation (Monochromatic, Analogous, Complementary, Split-Complementary, Triadic, Tetradic)
- Base color selection with visual picker
- WCAG accessibility testing and automatic adjustments
- Colorblindness simulation (Protanopia, Deuteranopia, Tritanopia, Grayscale)
- Light and dark mode toggle with automatic variant generation
- Multiple export formats (QSS, CSS, Tailwind, JSON, SVG)
- Theme naming in exports
- Interactive UI component preview
- Color relationship visualization
- Palette saving and loading
- Comprehensive documentation
- Project licensed under GPL v3 to ensure compatibility with PyQt6
- AI-assisted "vibe coding" approach throughout development 