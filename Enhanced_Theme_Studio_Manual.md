# Enhanced Theme Studio User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Interface Overview](#interface-overview)
4. [Creating Color Palettes](#creating-color-palettes)
5. [Image-Based Palettes](#image-based-palettes)
6. [Trending Palettes](#trending-palettes)
7. [Accessibility Features](#accessibility-features)
8. [Light/Dark Mode](#lightdark-mode)
9. [Preview and Testing](#preview-and-testing)
10. [Exporting Themes](#exporting-themes)
11. [Saving and Loading Palettes](#saving-and-loading-palettes)
12. [Keyboard Shortcuts](#keyboard-shortcuts)
13. [Troubleshooting](#troubleshooting)

## Introduction

Enhanced Theme Studio is a powerful color palette and theme generation tool built with PyQt6. It helps designers, developers, and artists create harmonious color schemes that can be exported to various formats for use in applications, websites, and design projects.

Key features include:
- Color scheme generation based on color theory principles
- Accessibility testing and automatic WCAG compliance adjustments
- Colorblindness simulation
- Light and dark mode theme generation
- Multiple export formats (CSS, QSS, Tailwind, JSON, SVG)
- Interactive preview of UI components with your palette
- Visual color relationship mapping

## Getting Started

### System Requirements
- Python 3.8 or higher
- PyQt6
- NumPy

### Installation

1. Ensure Python is installed on your system
2. Install required dependencies:
   ```
   pip install PyQt6 numpy
   ```
3. Run the application:
   ```
   python enhanced_theme_generator.py
   ```

## Interface Overview

The Enhanced Theme Studio interface is divided into several sections:

![Interface Overview](interface_overview.png)

1. **Theme Settings** (Left Panel)
   - Base color selection
   - Color scheme type
   - Number of colors
   - Accessibility options
   - Theme mode toggle

2. **Color Palette** (Right Panel)
   - Generated color swatches
   - Contrast ratios
   - WCAG compliance indicators
   - Adjusted colors

3. **Preview Tabs** (Bottom Section)
   - Basic UI components preview
   - Advanced UI patterns preview
   - Color relationships visualization

4. **Action Buttons**
   - Generate New Palette
   - Save Palette
   - Load Palette
   - Export

## Creating Color Palettes

### Selecting a Base Color

The base color is the foundation of your color scheme. To set a base color:

1. Click on the color swatch next to "Base Color"
2. Use the color picker to select a color, or
3. Enter a hex color code in the input field (e.g., #3498DB)
4. For a random color, click the refresh icon button

### Choosing a Color Scheme

Enhanced Theme Studio offers several color scheme types based on color theory:

- **Monochromatic**: Different shades and tints of a single color
- **Analogous**: Colors adjacent to each other on the color wheel
- **Complementary**: Colors opposite each other on the color wheel
- **Split-Complementary**: A color and two colors adjacent to its complement
- **Triadic**: Three colors evenly spaced around the color wheel
- **Tetradic**: Four colors arranged as two complementary pairs

Select your desired scheme from the dropdown menu.

### Setting Number of Colors

Choose how many colors should be in your palette (2-12) using the dropdown. 

**Note**: Some schemes (Split-Complementary, Triadic, Tetradic) use a fixed number of colors.

### Generating a New Palette

To generate a fresh palette:
1. Click the "Generate New Palette" button
2. This will create a slight variation on your current base color for visual distinction

## Image-Based Palettes

Enhanced Theme Studio allows you to extract color palettes directly from images, providing a unique way to derive inspiration from existing visuals.

### Creating a Palette from an Image

1.  **Click the "Create Palette from Image" button** located in the "Image-Based Palette" section of the "Theme Settings" panel.
2.  A file dialog will appear. **Select an image file** (e.g., PNG, JPG, JPEG, BMP) from your computer.
3.  The application will analyze the image and extract a set of dominant colors.
4.  A new dialog titled "Extracted Colors" will open, displaying the extracted colors as large swatches.
5.  **Click on any of the color swatches** in this dialog to set that color as the new "Base Color" in the main application. The dialog will then close, and the main palette will update based on this new base color.

## Trending Palettes

Explore a curated collection of popular and pre-defined color palettes to kickstart your design process.

### Loading a Trending Palette

1.  **Click the "Trending Palettes" button** in the main action button area.
2.  A new dialog titled "Trending Palettes" will appear, listing various palettes by name and showing a small preview of their colors.
3.  **Click the "Load" button** next to the palette you wish to use.
4.  The selected trending palette will be loaded directly into the main application's color table. The "Color Scheme" will automatically be set to "Custom" to reflect that these colors are not generated by a specific color theory scheme.

## Accessibility Features

### WCAG Compliance

The Web Content Accessibility Guidelines (WCAG) ensure text is readable against its background. Enhanced Theme Studio provides:

1. **Auto-adjust for accessibility**: When checked, colors are automatically adjusted to meet the selected WCAG level
2. **WCAG Level selection**: Choose between AA (4.5:1 contrast ratio) and AAA (7:1 contrast ratio)
3. **Color character preservation**: When checked, attempts to maintain the hue and saturation while adjusting luminance

The palette table shows:
- Original colors
- Contrast ratios with optimal text color
- WCAG compliance level (color-coded)
- Adjusted colors that meet the WCAG requirements (marked with ✓)

### Colorblindness Simulation

To test how your palette appears to users with color vision deficiencies:

1. Select a simulation type from the "Preview for" dropdown:
   - Normal Vision
   - Protanopia (red-blind)
   - Deuteranopia (green-blind)
   - Tritanopia (blue-blind)
   - Grayscale

The entire UI preview will update to show how your palette would appear to someone with the selected vision type.

## Light/Dark Mode

Enhanced Theme Studio allows you to create and test both light and dark theme variants:

1. **Theme Mode**: Toggle between Light Mode and Dark Mode
2. **Auto-create matching variant**: When checked, automatically generates a matching dark/light variant when switching modes

The dark mode generator:
- Inverts the lightness of colors where appropriate
- Creates a dark background (typically the 4th color)
- Maintains color relationships while adapting to dark contexts
- Can be manually adjusted if needed

When this feature is enabled, both light and dark variants can be included in exports.

## Preview and Testing

### Basic Components Tab

Test your palette on common UI elements:
- Buttons (primary and secondary)
- Text labels
- Form elements (checkboxes, radio buttons, inputs)
- Sliders and progress bars

### UI Patterns Tab

See how your palette works in more complex UI scenarios:
- Card components
- Navigation elements
- Tabs and toolbars

### Color Relationships Tab

Visualize your color scheme on a color wheel showing:
- Base color (center)
- Relationships between colors based on your chosen scheme
- Relative positions on the color wheel

## Exporting Themes

To export your theme:

1. Click the "Export" button
2. In the export dialog:
   - Enter a theme name (defaults to scheme name + base color)
   - Select an export format
   - Choose export options
3. Click "Export" and select a save location

### Export Formats

- **QSS (Qt Style Sheet)**: For Qt applications
- **CSS Variables**: For web projects using CSS custom properties
- **Tailwind Config**: For Tailwind CSS projects
- **JSON**: Universal format for applications
- **Color Palette (SVG)**: Visual representation of your palette

### Export Options

- **Include comments/documentation**: Adds metadata about your palette
- **Include semantic naming**: Adds semantic color variables (primary, secondary, accent, etc.)
- **Include both light and dark variants**: Includes both theme modes in formats that support it

## Saving and Loading Palettes

### Saving a Palette

To save a palette for later use:

1. Click "Save Palette"
2. Enter a name for your palette
3. The palette will be stored in memory during your session

### Loading a Palette

To load a previously saved palette:

1. Click "Load Palette"
2. Select a palette from the visual list
3. Click "Load"

The palette list shows:
- Palette name
- Scheme type
- Color preview

### Deleting a Palette

To delete a saved palette:

1. Click "Load Palette"
2. Select the palette to delete
3. Click "Delete"
4. Confirm deletion

## Keyboard Shortcuts

- **Ctrl+G**: Generate new palette
- **Ctrl+S**: Save palette
- **Ctrl+O**: Load palette
- **Ctrl+E**: Export theme
- **Ctrl+D**: Toggle dark/light mode

## Troubleshooting

### Common Issues

**Issue**: UI preview doesn't update after changing colors
**Solution**: Click "Generate New Palette" to refresh the preview

**Issue**: Theme mode reverts when changing number of colors
**Solution**: Ensure "Auto-create matching dark/light variant" is checked

**Issue**: WCAG adjustments make colors look too similar
**Solution**: Try unchecking "Preserve color character" for more aggressive adjustments

### Support

For support, bug reports, or feature requests, please contact me at soundchazer@gmail.com.

## Acknowledgements

### Core Technologies
- **Python** – The fundamental programming language (Python Software Foundation License)
- **PyQt6** – Python bindings for the Qt6 application framework (GPL v3 / commercial license)
- **NumPy** - Scientific computing package used for color transformations
- **colorsys and json** – Standard Python libraries for HLS conversion and JSON handling

### Design Resources
- **WCAG Contrast Ratio** formulas from WebAIM Contrast Checker for ensuring accessibility
- **Light vs. Dark mode** guidance from the Design Bootcamp article on Medium
- **Color theory taxonomy** (Monochromatic, Analogous, etc.) from Sankarraj's "Color Theory in UX/UI Design" on Medium

### Inspiration
- User-provided aquamarine.json and cottoncandy.json themes
- Coolors.co for popular palette ideas (no API used; inspiration only)

## Disclaimer

Enhanced Theme Studio was created by a solo developer with limited Python experience. The development utilized AI-assisted "vibe coding" - a collaborative approach where AI large language models help guide the coding process.

There may be areas where the code could be improved or optimized. Any issues or inefficiencies in the application are due to my ongoing learning journey. I'm continually working to enhance the application and improve my coding skills.

Development progresses at a measured pace as I balance this project with my full-time job. Your patience and understanding are appreciated.

---

© 2025 Soundchazer2k. All rights reserved. 