# Enhanced Theme Studio - A color palette generator
# Copyright (C) 2024 Soundchazer2k
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import json
import colorsys
import re
import math
import numpy as np
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSlot, QRegularExpression, QTimer
import random
from datetime import datetime
from PIL import Image


# Version information
__version__ = "1.1.0"
__version_info__ = (1, 1, 0)
__release_date__ = "2025-06-29"

# --- Utilities for color math & contrast ---
def hex_to_rgb(h):
    h_orig = h
    try:
        h = h.lstrip("#")
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return (0, 0, 0)  # Return black for invalid hex


def is_valid_hex(hex_color):
    pattern = r"^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    return bool(re.match(pattern, hex_color))


def rgb_to_hls(r, g, b):
    return colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)


def hls_to_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def relative_luminance(r, g, b):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    R, G, B = chan(r), chan(g), chan(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def contrast_ratio(hex1, hex2):
    L1 = relative_luminance(*hex_to_rgb(hex1))
    L2 = relative_luminance(*hex_to_rgb(hex2))
    lighter, darker = max(L1, L2), min(L1, L2)
    return (lighter + 0.05) / (darker + 0.05)


def pick_foreground(bg_hex):
    return "#000000" if contrast_ratio(bg_hex, "#000000") >= 4.5 else "#FFFFFF"


def get_wcag_level(ratio):
    if ratio >= 7:
        return "AAA"
    elif ratio >= 4.5:
        return "AA"
    elif ratio >= 3:
        return "AA Large"
    else:
        return "Fail"


# Function to darken or lighten a color while maintaining hue
def adjust_luminance(hex_color, factor):
    """Adjust luminance of a color (factor < 1 darkens, factor > 1 lightens)"""
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = rgb_to_hls(r, g, b)
    new_l = max(0.05, min(0.95, l * factor))  # Clamp to avoid pure black/white
    return hls_to_hex(h, new_l, s)


# Function to ensure WCAG compliance by adjusting colors
def ensure_wcag_compliant(fg_color, bg_color, min_ratio=4.5, preserve_character=True):
    """
    Adjust background color until it meets WCAG standards with foreground

    Parameters:
    - fg_color: Foreground color (text color)
    - bg_color: Background color to adjust
    - min_ratio: Minimum contrast ratio to achieve (4.5 for AA, 7 for AAA)
    - preserve_character: If True, attempt to preserve the color's character
    """
    # Check if the color is already compliant
    if contrast_ratio(fg_color, bg_color) >= min_ratio:
        return bg_color

    # Convert the background color to HSL
    r, g, b = hex_to_rgb(bg_color)
    h, l, s = rgb_to_hls(r, g, b)

    # Determine whether to lighten or darken the background color
    if contrast_ratio(fg_color, "#000000") > contrast_ratio(fg_color, "#FFFFFF"):
        # The foreground color is lighter, so we should darken the background
        direction = -1
    else:
        # The foreground color is darker, so we should lighten the background
        direction = 1

    # Iteratively adjust the lightness of the background color until the contrast ratio is met
    for _ in range(100):
        l += direction * 0.01
        l = max(0.0, min(1.0, l))

        if preserve_character:
            adjusted_bg = hls_to_hex(h, l, s)
        else:
            adjusted_bg = hls_to_hex(h, l, s)

        if contrast_ratio(fg_color, adjusted_bg) >= min_ratio:
            return adjusted_bg

    # If the contrast ratio cannot be met, return the original background color
    return bg_color


# --- Scheme generation ---
def generate_scheme(base_hex, scheme, n):
    if not is_valid_hex(base_hex):
        return ["#3498DB"] * n

    h, l, s = rgb_to_hls(*hex_to_rgb(base_hex))
    colors = []
    if scheme == "Monochromatic":
        span = 0.5
        for i in range(n):
            li = max(0.1, min(0.9, l - span / 2 + span * i / (n - 1)))
            colors.append(hls_to_hex(h, li, s))
    elif scheme == "Analogous":
        deg = 30 / 360
        for i in range(n):
            hi = (h - deg + 2 * deg * i / (n - 1)) % 1.0
            colors.append(hls_to_hex(hi, l, s))
    elif scheme == "Complementary":
        for i in range(n):
            hi = (h + 0.5 * i / (n - 1)) % 1.0
            colors.append(hls_to_hex(hi, l, s))
    elif scheme == "Split-Complementary":
        angles = [h, (h + 150 / 360) % 1.0, (h + 210 / 360) % 1.0]
        for ai in angles:
            colors.append(hls_to_hex(ai, l, s))
    elif scheme == "Triadic":
        for k in range(3):
            ai = (h + k / 3) % 1.0
            colors.append(hls_to_hex(ai, l, s))
    elif scheme == "Tetradic":
        for k in range(4):
            ai = (h + k / 4) % 1.0
            colors.append(hls_to_hex(ai, l, s))
    else:
        for i in range(n):
            hi = (h + i / n) % 1.0
            colors.append(hls_to_hex(hi, l, s))
    return colors


# --- Color Picker Widget ---
class ColorPickerWidget(QtWidgets.QWidget):
    colorChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.color_button = QtWidgets.QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.color_button.clicked.connect(self.open_color_dialog)

        self.hex_input = QtWidgets.QLineEdit("#3498DB")
        self.hex_input.setValidator(
            QtGui.QRegularExpressionValidator(QRegularExpression(r"#?[0-9A-Fa-f]{0,8}"))
        )
        self.hex_input.textChanged.connect(self.on_text_changed)

        layout.addWidget(self.color_button)
        layout.addWidget(self.hex_input)

        self.set_color("#3498DB")

    def set_color(self, hex_color):
        if not hex_color.startswith("#"):
            hex_color = f"#{hex_color}"

        if is_valid_hex(hex_color):
            self.color_button.setStyleSheet(f"background-color: {hex_color};")
            self.hex_input.setText(hex_color.upper())
            self.colorChanged.emit(hex_color.upper())

    def on_text_changed(self, text):
        if is_valid_hex(text):
            self.color_button.setStyleSheet(f"background-color: {text};")
            self.colorChanged.emit(text.upper())

    def open_color_dialog(self):
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(self.hex_input.text()), self
        )
        if color.isValid():
            self.set_color(color.name().upper())


# --- Main PyQt6 App ---
class EnhancedThemeGenerator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Enhanced Theme Studio v{__version__} (PyQt6)")
        self.setMinimumSize(900, 650)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)

        # Create menu bar
        self.setup_menu_bar()

        # Saved palettes
        self.saved_palettes = []

        # Status message timer
        self.status_timer = QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_status)

        # Main splitter for resizable sections
        main_splitter = QtWidgets.QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(main_splitter)

        # Top container for controls and palette
        top_widget = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout(top_widget)

        # Controls section - left side
        ctrl_group = QtWidgets.QGroupBox("Theme Settings")
        ctrl_layout = QtWidgets.QVBoxLayout(ctrl_group)

        # Color and scheme controls
        color_layout = QtWidgets.QFormLayout()

        # Base color selector
        base_color_widget = QtWidgets.QWidget()
        base_color_layout = QtWidgets.QHBoxLayout(base_color_widget)
        base_color_layout.setContentsMargins(0, 0, 0, 0)

        self.color_picker = ColorPickerWidget()
        self.color_picker.colorChanged.connect(self.on_color_changed)

        self.random_color_btn = QtWidgets.QPushButton()
        self.random_color_btn.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload)
        )
        self.random_color_btn.setToolTip("Generate Random Color")
        self.random_color_btn.setFixedSize(30, 30)
        self.random_color_btn.clicked.connect(self.generate_random_color)

        base_color_layout.addWidget(self.color_picker)
        base_color_layout.addWidget(self.random_color_btn)

        # Image-based palette generation
        image_group = QtWidgets.QGroupBox("Image-Based Palette")
        image_layout = QtWidgets.QVBoxLayout(image_group)

        self.pick_from_image_btn = QtWidgets.QPushButton("Create Palette from Image")
        self.pick_from_image_btn.setToolTip("Extract a color palette from an image.")
        self.pick_from_image_btn.clicked.connect(self.pick_from_image)

        image_layout.addWidget(self.pick_from_image_btn)

        # Scheme selection with icon indicators
        self.scheme_combo = QtWidgets.QComboBox()
        scheme_items = [
            "Monochromatic",
            "Analogous",
            "Complementary",
            "Split-Complementary",
            "Triadic",
            "Tetradic",
            "Custom",
        ]
        self.scheme_combo.addItems(scheme_items)
        self.scheme_combo.currentTextChanged.connect(self.on_scheme_changed)

        # Count selection
        self.num_combo = QtWidgets.QComboBox()
        self.num_combo.addItems([str(i) for i in range(2, 13)])
        self.num_combo.setCurrentText("5")
        self.num_combo.currentTextChanged.connect(self.on_count_changed)

        # Add to form layout
        color_layout.addRow("Base Color:", base_color_widget)
        color_layout.addRow("Color Scheme:", self.scheme_combo)
        color_layout.addRow("Number of Colors:", self.num_combo)

        # Add to control layout
        ctrl_layout.addLayout(color_layout)
        ctrl_layout.addWidget(image_group)

        # Add separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        ctrl_layout.addWidget(separator)

        # Accessibility section with toggle switch
        access_group = QtWidgets.QGroupBox("Accessibility")
        access_layout = QtWidgets.QVBoxLayout(access_group)

        # WCAG toggle with custom styling
        wcag_widget = QtWidgets.QWidget()
        wcag_layout = QtWidgets.QHBoxLayout(wcag_widget)
        wcag_layout.setContentsMargins(0, 0, 0, 0)

        self.wcag_check = QtWidgets.QCheckBox("Auto-adjust for accessibility")
        self.wcag_check.setChecked(True)
        self.wcag_check.stateChanged.connect(self.update_palette)

        self.wcag_level = QtWidgets.QComboBox()
        self.wcag_level.addItems(["AA (4.5:1)", "AAA (7:1)"])
        self.wcag_level.currentTextChanged.connect(self.update_palette)

        wcag_layout.addWidget(self.wcag_check)
        wcag_layout.addWidget(self.wcag_level)

        # Character preservation checkbox
        self.preserve_character_check = QtWidgets.QCheckBox(
            "Preserve color character when adjusting"
        )
        self.preserve_character_check.setChecked(True)
        self.preserve_character_check.setToolTip(
            "When checked, tries to maintain the color's hue and saturation while adjusting luminance"
        )
        self.preserve_character_check.stateChanged.connect(self.update_palette)

        # Color blindness simulation
        colorblind_layout = QtWidgets.QHBoxLayout()
        colorblind_label = QtWidgets.QLabel("Preview for:")
        self.colorblind_combo = QtWidgets.QComboBox()
        self.colorblind_combo.addItems(
            ["Normal Vision", "Protanopia", "Deuteranopia", "Tritanopia", "Grayscale"]
        )
        self.colorblind_combo.currentTextChanged.connect(self.update_palette)

        colorblind_layout.addWidget(colorblind_label)
        colorblind_layout.addWidget(self.colorblind_combo)

        # Theme mode toggle
        theme_layout = QtWidgets.QHBoxLayout()
        theme_label = QtWidgets.QLabel("Theme Mode:")

        self.theme_toggle = QtWidgets.QComboBox()
        self.theme_toggle.addItems(["Light Mode", "Dark Mode"])
        self.theme_toggle.currentTextChanged.connect(self.on_theme_mode_changed)

        self.auto_adjust_dark = QtWidgets.QCheckBox(
            "Auto-create matching dark/light variant"
        )
        self.auto_adjust_dark.setChecked(True)
        self.auto_adjust_dark.setToolTip(
            "Automatically generates a matching variant when switching modes"
        )

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_toggle)
        theme_layout.addWidget(self.auto_adjust_dark)
        theme_layout.addStretch()

        # Add to accessibility layout
        access_layout.addWidget(wcag_widget)
        access_layout.addWidget(self.preserve_character_check)
        access_layout.addLayout(colorblind_layout)
        access_layout.addLayout(theme_layout)

        # Add to control layout
        ctrl_layout.addWidget(access_group)

        # Buttons for actions
        btn_layout = QtWidgets.QHBoxLayout()

        generate_btn = QtWidgets.QPushButton("Generate New Palette")
        generate_btn.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload)
        )
        generate_btn.setToolTip(
            "Generate a new color palette based on current settings"
        )
        generate_btn.clicked.connect(self.generate_new_palette)

        self.save_btn = QtWidgets.QPushButton("Save Palette")
        self.save_btn.clicked.connect(self.save_palette)

        self.load_btn = QtWidgets.QPushButton("Load Palette")
        self.load_btn.clicked.connect(self.load_palette)

        self.export_btn = QtWidgets.QPushButton("Export")
        self.export_btn.clicked.connect(self.export_theme)

        self.trending_btn = QtWidgets.QPushButton("Trending Palettes")
        self.trending_btn.clicked.connect(self.show_trending_palettes)

        btn_layout.addWidget(generate_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.trending_btn)
        btn_layout.addWidget(self.export_btn)

        ctrl_layout.addLayout(btn_layout)
        ctrl_layout.addStretch()

        # Palette table - right side
        palette_group = QtWidgets.QGroupBox("Color Palette")
        palette_layout = QtWidgets.QVBoxLayout(palette_group)

        self.table = QtWidgets.QTableWidget(4, 5)
        self.table.setVerticalHeaderLabels(["Color", "Contrast", "WCAG", "Adjusted"])
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.horizontalHeader().setDefaultSectionSize(80)
        self.table.setMinimumHeight(160)
        palette_layout.addWidget(self.table)

        # Add controls and palette to top layout
        top_layout.addWidget(ctrl_group, 1)
        top_layout.addWidget(palette_group, 2)

        # Preview section for UI components
        preview_container = QtWidgets.QWidget()
        preview_layout = QtWidgets.QVBoxLayout(preview_container)

        preview_tabs = QtWidgets.QTabWidget()

        # Basic widgets tab
        basic_widget = QtWidgets.QWidget()
        self.create_basic_widgets_preview(basic_widget)
        preview_tabs.addTab(basic_widget, "Basic Components")

        # Advanced UI patterns tab
        advanced_widget = QtWidgets.QWidget()
        self.create_advanced_widgets_preview(advanced_widget)
        preview_tabs.addTab(advanced_widget, "UI Patterns")

        # Color relationships tab
        relationships_widget = QtWidgets.QWidget()
        self.create_relationships_preview(relationships_widget)
        preview_tabs.addTab(relationships_widget, "Color Relationships")

        preview_layout.addWidget(preview_tabs)

        # Add widgets to main splitter
        main_splitter.addWidget(top_widget)
        main_splitter.addWidget(preview_container)
        main_splitter.setSizes([300, 300])

        # Status bar for messages
        self.statusBar().showMessage("Ready")

        # Init with default palette
        self.update_palette()

    def setup_menu_bar(self):
        """Set up the application menu bar"""
        menu_bar = self.menuBar()

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        about_action = QtGui.QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_basic_widgets_preview(self, container):
        """Create preview of basic UI widgets"""
        layout = QtWidgets.QVBoxLayout(container)

        # Row 1 - buttons and labels
        row1 = QtWidgets.QHBoxLayout()

        self.sample_btn = QtWidgets.QPushButton("Primary Button")
        self.sample_btn.setMinimumWidth(150)

        self.sample_btn_secondary = QtWidgets.QPushButton("Secondary Button")
        self.sample_btn_secondary.setMinimumWidth(150)

        self.sample_lbl = QtWidgets.QLabel("Sample Label")
        self.sample_lbl.setMinimumWidth(150)

        row1.addWidget(self.sample_btn)
        row1.addWidget(self.sample_btn_secondary)
        row1.addWidget(self.sample_lbl)
        row1.addStretch()

        # Row 2 - form elements
        row2 = QtWidgets.QHBoxLayout()

        self.sample_check = QtWidgets.QCheckBox("Sample Checkbox")
        self.sample_radio = QtWidgets.QRadioButton("Sample Radio")
        self.sample_line = QtWidgets.QLineEdit("Sample Input")
        self.sample_combo = QtWidgets.QComboBox()
        self.sample_combo.addItems(["Option 1", "Option 2", "Option 3"])

        row2.addWidget(self.sample_check)
        row2.addWidget(self.sample_radio)
        row2.addWidget(self.sample_line)
        row2.addWidget(self.sample_combo)

        # Row 3 - sliders and progress
        row3 = QtWidgets.QHBoxLayout()

        self.sample_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.sample_slider.setMinimumWidth(150)

        self.sample_progress = QtWidgets.QProgressBar()
        self.sample_progress.setValue(70)
        self.sample_progress.setMinimumWidth(150)

        self.sample_spin = QtWidgets.QSpinBox()

        row3.addWidget(self.sample_slider)
        row3.addWidget(self.sample_progress)
        row3.addWidget(self.sample_spin)
        row3.addStretch()

        # Add all rows to main layout
        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(row3)
        layout.addStretch()

    def create_advanced_widgets_preview(self, container):
        """Create preview of advanced UI patterns"""
        layout = QtWidgets.QHBoxLayout(container)

        # Card pattern
        card_group = QtWidgets.QGroupBox("Card Component")
        card_layout = QtWidgets.QVBoxLayout(card_group)

        self.card_title = QtWidgets.QLabel("Card Title")
        self.card_title.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.card_content = QtWidgets.QLabel(
            "This is sample content for a card component that demonstrates how colors work in a common UI pattern."
        )
        self.card_content.setWordWrap(True)

        self.card_button = QtWidgets.QPushButton("Card Action")

        card_layout.addWidget(self.card_title)
        card_layout.addWidget(self.card_content)
        card_layout.addWidget(self.card_button)
        card_layout.addStretch()

        # Navigation pattern
        nav_group = QtWidgets.QGroupBox("Navigation")
        nav_layout = QtWidgets.QVBoxLayout(nav_group)

        toolbar = QtWidgets.QToolBar()
        toolbar.addAction("Home")
        toolbar.addAction("Products")
        toolbar.addAction("About")
        toolbar.addAction("Contact")

        self.nav_tabs = QtWidgets.QTabWidget()
        self.nav_tabs.addTab(QtWidgets.QWidget(), "Tab 1")
        self.nav_tabs.addTab(QtWidgets.QWidget(), "Tab 2")
        self.nav_tabs.addTab(QtWidgets.QWidget(), "Tab 3")

        nav_layout.addWidget(toolbar)
        nav_layout.addWidget(self.nav_tabs)
        nav_layout.addStretch()

        # Add components to layout
        layout.addWidget(card_group)
        layout.addWidget(nav_group)

    def create_relationships_preview(self, container):
        """Create preview showing color relationships"""
        layout = QtWidgets.QVBoxLayout(container)

        # Create a custom color wheel widget
        self.color_wheel = ColorWheelWidget()
        layout.addWidget(self.color_wheel)

        # Add some explanation
        explanation = QtWidgets.QLabel(
            "This wheel shows the relationships between colors in your palette. "
            "The base color is highlighted, and the color scheme type determines "
            "the pattern of the other colors."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

    def pick_from_image(self):
        """Open an image and extract a color palette."""
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            try:
                with Image.open(file_name) as img:
                    # Resize for faster processing
                    img.thumbnail((100, 100))
                    # Get colors
                    result = img.convert("P", palette=Image.ADAPTIVE, colors=8).convert("RGB")
                    colors = result.getcolors()
                    if colors:
                        # Sort by frequency
                        colors.sort(key=lambda x: x[0], reverse=True)
                        # Create a dialog to show the extracted colors
                        self.show_extracted_colors_dialog([c[1] for c in colors])
                    else:
                        self.statusBar().showMessage("Could not extract colors from image.")
            except Exception as e:
                self.statusBar().showMessage(f"Error opening image: {e}")

    def show_extracted_colors_dialog(self, colors):
        """Show a dialog with the extracted colors."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Extracted Colors")
        layout = QtWidgets.QVBoxLayout(dialog)

        label = QtWidgets.QLabel("Click a color to set it as the base color:")
        layout.addWidget(label)

        color_layout = QtWidgets.QHBoxLayout()
        for r, g, b in colors:
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"background-color: {hex_color};")
            btn.clicked.connect(lambda _, c=hex_color: self.set_base_color_from_dialog(c, dialog))
            color_layout.addWidget(btn)
        
        layout.addLayout(color_layout)
        dialog.exec()

    def set_base_color_from_dialog(self, color, dialog):
        """Set the base color from the extracted color dialog."""
        self.color_picker.set_color(color)
        self.update_palette()
        dialog.accept()

    def generate_random_color(self):
        """Generate a random color and update the picker"""
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        self.color_picker.set_color(hex_color)
        self.update_palette()

    @pyqtSlot(str)
    def on_color_changed(self, color):
        self.update_palette()

    @pyqtSlot(str)
    def on_scheme_changed(self, scheme):
        if scheme in ("Split-Complementary", "Triadic", "Tetradic"):
            # Update note for fixed-count schemes
            count = 3 if scheme in ("Split-Complementary", "Triadic") else 4
            self.statusBar().showMessage(
                f"Note: {scheme} scheme uses fixed count of {count} colors"
            )
        else:
            self.statusBar().showMessage("Ready")
        self.update_palette()

    @pyqtSlot(str)
    def on_count_changed(self, count):
        self.update_palette()

    def update_palette(self, custom_colors=None):
        cols = []  # Initialize cols to an empty list

        if custom_colors is not None:
            # Scenario 1: A specific palette is provided (e.g., from trending)
            cols = custom_colors
            # Update UI controls to reflect this custom palette
            self.num_combo.blockSignals(True)
            self.num_combo.setCurrentText(str(len(cols)))
            self.num_combo.blockSignals(False)
            self.scheme_combo.blockSignals(True)
            self.scheme_combo.setCurrentText("Custom")
            self.scheme_combo.blockSignals(False)
        else:
            # Scenario 2: Generate palette based on current UI settings
            base = self.color_picker.hex_input.text().strip()
            if not is_valid_hex(base):
                self.statusBar().showMessage("Invalid hex color! Using default color.")
                base = "#3498DB"
                self.color_picker.set_color(base)

            scheme = self.scheme_combo.currentText()
            n = int(self.num_combo.currentText())

            if scheme == "Custom":
                # If 'Custom' is selected manually, try to read from the table.
                # If table is empty (e.g., at startup), provide a default.
                current_table_colors = []
                if self.table.columnCount() > 0 and self.table.item(0, 0) is not None:
                    for i in range(self.table.columnCount()):
                        item = self.table.item(0, i)
                        if item:
                            current_table_colors.append(item.text())
                
                if current_table_colors:
                    cols = current_table_colors
                else:
                    # Default custom palette if no colors are in the table or table is empty
                    cols = ["#3498DB", "#DB9834", "#808080", "#555555", "#AAAAAA"] # More colors for a default
            else:
                # Generate scheme based on selected type
                cols = generate_scheme(base, scheme, n)
                # Handle fixed-count schemes (already present)
                if scheme in ("Split-Complementary", "Triadic", "Tetradic"):
                    n = len(cols)
                    self.num_combo.blockSignals(True)
                    self.num_combo.setCurrentText(str(n))
                    self.num_combo.blockSignals(False)

        # Now, 'cols' contains the definitive palette to be displayed and processed.
        # The rest of the update_palette function can proceed with 'cols'.

        # Update palette table (common logic)
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels([f"Color {i + 1}" for i in range(len(cols))])
        self.table.setVerticalHeaderLabels(
            ["Original", "Contrast", "WCAG Level", "Adjusted for Accessibility"]
        )

        self.table.hide() # Flicker effect

        min_ratio = 7.0 if "AAA" in self.wcag_level.currentText() else 4.5
        preserve_character = self.preserve_character_check.isChecked()
        adjusted_cols = []

        for i, hexcol in enumerate(cols):
            # ... (existing logic for populating table rows) ...
            swatch = QtWidgets.QTableWidgetItem(hexcol)
            swatch.setBackground(QtGui.QColor(hexcol))
            fg = pick_foreground(hexcol)
            swatch.setForeground(QtGui.QColor(fg))
            swatch.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            ratio = contrast_ratio(hexcol, fg)
            ratio_item = QtWidgets.QTableWidgetItem(f"{ratio:.1f}:1")
            ratio_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            wcag = get_wcag_level(ratio)
            wcag_item = QtWidgets.QTableWidgetItem(wcag)
            wcag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if wcag == "AAA":
                wcag_bg = QtGui.QColor(50, 150, 50)
                wcag_fg = QtGui.QColor(255, 255, 255)
            elif wcag == "AA":
                wcag_bg = QtGui.QColor(100, 150, 50)
                wcag_fg = QtGui.QColor(0, 0, 0)
            elif wcag == "AA Large":
                wcag_bg = QtGui.QColor(180, 150, 10)
                wcag_fg = QtGui.QColor(0, 0, 0)
            else:
                wcag_bg = QtGui.QColor(180, 50, 50)
                wcag_fg = QtGui.QColor(255, 255, 255)

            wcag_item.setBackground(wcag_bg)
            wcag_item.setForeground(wcag_fg)

            font = wcag_item.font()
            font.setBold(True)
            wcag_item.setFont(font)

            if (
                self.wcag_check.isChecked()
                and wcag not in ["AAA"]
                and ratio < min_ratio
            ):
                adjusted_col = ensure_wcag_compliant(
                    fg, hexcol, min_ratio, preserve_character
                )
                adjusted_ratio = contrast_ratio(adjusted_col, fg)
                adjusted_wcag = get_wcag_level(adjusted_ratio)
            else:
                adjusted_col = hexcol
                adjusted_wcag = wcag
                adjusted_ratio = ratio

            adjusted_cols.append(adjusted_col)

            adjusted_swatch = QtWidgets.QTableWidgetItem(adjusted_col)
            adjusted_swatch.setBackground(QtGui.QColor(adjusted_col))
            adjusted_swatch.setForeground(QtGui.QColor(fg))
            adjusted_swatch.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if adjusted_col != hexcol:
                adjusted_swatch.setToolTip(
                    f"Adjusted from {hexcol} for {adjusted_wcag} compliance"
                )
                adjusted_swatch.setText("✓")
                font = adjusted_swatch.font()
                font.setBold(True)
                adjusted_swatch.setFont(font)

            self.table.setItem(0, i, swatch)
            self.table.setItem(1, i, ratio_item)
            self.table.setItem(2, i, wcag_item)
            self.table.setItem(3, i, adjusted_swatch)

        self.light_palette = cols # Store the original light theme palette

        self.table.show()
        self.table.resizeColumnsToContents()

        current_mode = self.theme_toggle.currentText()

        if current_mode == "Dark Mode" and self.auto_adjust_dark.isChecked():
            self.create_dark_variant()
            palette_for_preview = self.dark_palette
        else:
            self.current_palette = cols
            if self.wcag_check.isChecked():
                palette_for_preview = adjusted_cols
            else:
                palette_for_preview = cols

        if palette_for_preview:
            self.update_preview_components(palette_for_preview)

    def update_preview_components(self, palette):
        """Update all preview components with the given palette"""
        if not palette:
            return

        # Apply colorblindness simulation if selected
        simulation_type = self.colorblind_combo.currentText()
        if simulation_type != "Normal Vision":
            simulated_palette = simulate_palette(palette, simulation_type)
            self.set_status(
                f"Simulating {simulation_type} vision", 0
            )  # Don't auto-clear this message
        else:
            simulated_palette = palette

        # Extract semantic colors from palette
        primary = simulated_palette[0]
        secondary = simulated_palette[1] if len(simulated_palette) > 1 else primary
        accent = simulated_palette[2] if len(simulated_palette) > 2 else secondary
        bg = simulated_palette[3] if len(simulated_palette) > 3 else "#FFFFFF"

        # Foreground colors with good contrast
        fg_primary = pick_foreground(primary)
        fg_secondary = pick_foreground(secondary)
        fg_accent = pick_foreground(accent)
        fg_bg = pick_foreground(bg)

        # Generate theme style sheet
        qss = self.generate_theme_qss(simulated_palette)

        # Apply the stylesheet to the central widget
        self.centralWidget().setStyleSheet(qss)

        # Update color wheel
        if hasattr(self, "color_wheel"):
            self.color_wheel.set_colors(
                simulated_palette,
                self.scheme_combo.currentText(),
                simulate_colorblindness(
                    self.color_picker.hex_input.text(), simulation_type
                ),
            )

    def generate_theme_qss(self, palette):
        """Generate a complete QSS theme from the palette"""
        if not palette:
            return ""

        # Extract semantic colors
        primary = palette[0]
        secondary = palette[1] if len(palette) > 1 else primary
        accent = palette[2] if len(palette) > 2 else secondary
        bg = palette[3] if len(palette) > 3 else "#FFFFFF"

        # Get contrasting text colors
        fg_primary = pick_foreground(primary)
        fg_secondary = pick_foreground(secondary)
        fg_accent = pick_foreground(accent)
        fg_bg = pick_foreground(bg)

        # Create a more sophisticated theme
        qss = f"""
        /* Main theme */
        QWidget {{ background-color: {bg}; color: {fg_bg}; }}
        
        /* Button styling */
        QPushButton {{ 
            background-color: {primary}; 
            color: {fg_primary}; 
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
            font-weight: bold;
        }}
        
        QPushButton:hover {{ 
            background-color: {accent}; 
            color: {fg_accent}; 
        }}
        
        QPushButton:pressed {{ 
            background-color: {secondary}; 
            color: {fg_secondary}; 
        }}
        
        /* Secondary button */
        #sample_btn_secondary {{
            background-color: {secondary};
            color: {fg_secondary};
        }}
        
        /* Label styling */
        QLabel {{ color: {fg_bg}; }}
        
        /* Card title */
        #card_title {{ 
            color: {fg_bg}; 
            font-weight: bold; 
            font-size: 14px;
        }}
        
        /* Input elements */
        QLineEdit, QComboBox, QSpinBox {{ 
            background-color: {bg}; 
            color: {fg_bg}; 
            border: 1px solid {secondary};
            border-radius: 3px;
            padding: 4px 8px;
        }}
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ 
            border: 2px solid {accent};
        }}
        
        /* Checkbox and Radio */
        QCheckBox, QRadioButton {{ color: {fg_bg}; }}
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{ 
            background-color: {accent}; 
            border: 2px solid {fg_accent};
        }}
        
        /* Slider */
        QSlider::groove:horizontal {{
            background: {secondary};
            height: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {primary};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        /* Progress Bar */
        QProgressBar {{
            background-color: {bg};
            border: 1px solid {secondary};
            border-radius: 5px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {primary};
            width: 10px;
        }}
        
        /* Group Box */
        QGroupBox {{
            border: 1px solid {secondary};
            border-radius: 5px;
            margin-top: 1ex;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            background-color: {bg};
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {secondary};
            border-radius: 3px;
        }}
        
        QTabBar::tab {{
            background-color: {bg};
            border: 1px solid {secondary};
            border-bottom-color: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {primary};
            color: {fg_primary};
        }}
        
        /* Toolbar */
        QToolBar {{
            background-color: {secondary};
            spacing: 3px;
            border: 1px solid {secondary};
        }}
        
        QToolBar::handle {{
            background-color: {accent};
        }}
        
        QToolButton {{
            background-color: transparent;
            color: {fg_secondary};
            border-radius: 3px;
            padding: 5px;
        }}
        
        QToolButton:hover {{
            background-color: {accent};
            color: {fg_accent};
        }}
        """

        return qss

    def export_theme(self):
        """Export the current theme in various formats"""
        n = self.table.columnCount()
        if n == 0:
            return

        # Determine if we should use adjusted colors
        if self.wcag_check.isChecked():
            palette = [self.table.item(3, i).text() for i in range(n)]
        else:
            palette = [self.table.item(0, i).text() for i in range(n)]

        foregrounds = [pick_foreground(c) for c in palette]

        # Create a dialog to select export format
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Export Theme")
        dialog.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Theme name field
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Theme Name:")
        theme_name = QtWidgets.QLineEdit()

        # Generate a default name based on base color and scheme
        default_name = f"{self.scheme_combo.currentText()}-{self.color_picker.hex_input.text().replace('#', '')}"
        theme_name.setText(default_name)

        name_layout.addWidget(name_label)
        name_layout.addWidget(theme_name)

        # Format selection
        format_group = QtWidgets.QGroupBox("Export Format")
        format_layout = QtWidgets.QVBoxLayout(format_group)

        format_combo = QtWidgets.QComboBox()
        format_combo.addItems(
            [
                "QSS (Qt Style Sheet)",
                "CSS Variables",
                "Tailwind Config",
                "JSON",
                "Color Palette (SVG)",
            ]
        )

        format_layout.addWidget(format_combo)

        # Options
        options_group = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout(options_group)

        include_comments = QtWidgets.QCheckBox("Include comments/documentation")
        include_comments.setChecked(True)

        include_semantic = QtWidgets.QCheckBox(
            "Include semantic naming (primary, secondary, etc.)"
        )
        include_semantic.setChecked(True)

        include_both_modes = QtWidgets.QCheckBox("Include both light and dark variants")
        include_both_modes.setChecked(True)
        include_both_modes.setEnabled(self.auto_adjust_dark.isChecked())

        options_layout.addWidget(include_comments)
        options_layout.addWidget(include_semantic)
        options_layout.addWidget(include_both_modes)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        export_btn = QtWidgets.QPushButton("Export")
        export_btn.clicked.connect(dialog.accept)
        export_btn.setDefault(True)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(export_btn)

        # Add all to dialog
        layout.addLayout(name_layout)
        layout.addWidget(format_group)
        layout.addWidget(options_group)
        layout.addLayout(btn_layout)

        # Show dialog
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        # Get export format and options
        format_type = format_combo.currentText()
        with_comments = include_comments.isChecked()
        with_semantic = include_semantic.isChecked()
        include_both_modes = include_both_modes.isChecked()
        theme_name_value = theme_name.text().strip()

        if not theme_name_value:
            theme_name_value = default_name

        # Prepare export content based on format
        content = ""
        file_filter = ""

        # Extract semantic colors
        primary = palette[0]
        secondary = palette[1] if len(palette) > 1 else primary
        accent = palette[2] if len(palette) > 2 else secondary
        bg = palette[3] if len(palette) > 3 else "#FFFFFF"

        if format_type == "QSS (Qt Style Sheet)":
            content = self.export_as_qss(
                palette, foregrounds, with_comments, with_semantic, theme_name_value
            )
            file_filter = "QSS files (*.qss)"
        elif format_type == "CSS Variables":
            content = self.export_as_css(
                palette, foregrounds, with_comments, with_semantic, theme_name_value
            )
            file_filter = "CSS files (*.css)"
        elif format_type == "Tailwind Config":
            content = self.export_as_tailwind(
                palette, with_comments, with_semantic, theme_name_value
            )
            file_filter = "JavaScript files (*.js)"
        elif format_type == "JSON":
            content = self.export_as_json(
                palette,
                foregrounds,
                with_comments,
                with_semantic,
                include_both_modes,
                theme_name_value,
            )
            file_filter = "JSON files (*.json)"
        elif format_type == "Color Palette (SVG)":
            content = self.export_as_svg(palette, theme_name_value)
            file_filter = "SVG files (*.svg)"

        # Get save path with suggested filename based on theme name
        filename_suggestion = f"{theme_name_value.replace(' ', '_')}"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Theme", filename_suggestion, filter=file_filter
        )

        if path:
            with open(path, "w") as f:
                f.write(content)
            QtWidgets.QMessageBox.information(
                self, "Export", f"Theme '{theme_name_value}' saved to {path}"
            )

    def export_as_qss(
        self,
        palette,
        foregrounds,
        with_comments=True,
        with_semantic=True,
        theme_name="Theme",
    ):
        """Export theme as QSS (Qt Style Sheet)"""
        # Extract semantic colors
        primary = palette[0]
        secondary = palette[1] if len(palette) > 1 else primary
        accent = palette[2] if len(palette) > 2 else secondary
        bg = palette[3] if len(palette) > 3 else "#FFFFFF"

        fg_primary = foregrounds[0]
        fg_secondary = foregrounds[1] if len(foregrounds) > 1 else foregrounds[0]
        fg_accent = foregrounds[2] if len(foregrounds) > 2 else fg_secondary
        fg_bg = foregrounds[3] if len(foregrounds) > 3 else "#000000"

        # Create header
        header = f"/* {theme_name} - Generated Theme QSS */\n\n"

        if with_comments:
            header += "/*\n"
            header += f" * Theme: {theme_name}\n"
            header += " * Generated with Enhanced Theme Studio\n"
            header += f" * Base color: {self.color_picker.hex_input.text()}\n"
            header += f" * Scheme: {self.scheme_combo.currentText()}\n"
            header += f" * WCAG compliance: {self.wcag_level.currentText() if self.wcag_check.isChecked() else 'Off'}\n"
            header += f" * Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            header += " */\n\n"

        content = header

        # Color variables section
        content += "/* Color variables */\n"

        if with_semantic and len(palette) >= 3:
            content += "* {\n"
            content += f'    --theme-name: "{theme_name}";\n'
            content += f"    --color-primary: {primary};\n"
            content += f"    --color-secondary: {secondary};\n"
            content += f"    --color-accent: {accent};\n"
            content += f"    --color-background: {bg};\n"
            content += f"    --color-fg-primary: {fg_primary};\n"
            content += f"    --color-fg-secondary: {fg_secondary};\n"
            content += f"    --color-fg-accent: {fg_accent};\n"
            content += f"    --color-fg-background: {fg_bg};\n"
            content += "}\n\n"

        # Add all palette colors as variables
        content += "/* All palette colors */\n"
        content += "* {\n"
        for i, c in enumerate(palette):
            content += f"    --color{i}: {c};\n"
            content += f"    --fg-color{i}: {foregrounds[i]};\n"
        content += "}\n\n"

        # Add comprehensive widget styling
        content += "/* Main application styling */\n"
        content += self.generate_theme_qss(palette)

        return content

    def export_as_css(
        self,
        palette,
        foregrounds,
        with_comments=True,
        with_semantic=True,
        theme_name="Theme",
    ):
        """Export theme as CSS variables"""
        # Extract semantic colors
        primary = palette[0]
        secondary = palette[1] if len(palette) > 1 else primary
        accent = palette[2] if len(palette) > 2 else secondary
        bg = palette[3] if len(palette) > 3 else "#FFFFFF"

        fg_primary = foregrounds[0]
        fg_secondary = foregrounds[1] if len(foregrounds) > 1 else foregrounds[0]
        fg_accent = foregrounds[2] if len(foregrounds) > 2 else fg_secondary
        fg_bg = foregrounds[3] if len(foregrounds) > 3 else "#000000"

        # Create header
        header = f"/* {theme_name} - Generated CSS Theme Variables */\n\n"

        if with_comments:
            header += "/*\n"
            header += f" * Theme: {theme_name}\n"
            header += " * Generated with Enhanced Theme Studio\n"
            header += f" * Base color: {self.color_picker.hex_input.text()}\n"
            header += f" * Scheme: {self.scheme_combo.currentText()}\n"
            header += f" * WCAG compliance: {self.wcag_level.currentText() if self.wcag_check.isChecked() else 'Off'}\n"
            header += f" * Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            header += " */\n\n"

        content = header

        # Root variables
        content += ":root {\n"
        content += f'    --theme-name: "{theme_name}";\n'

        if with_semantic and len(palette) >= 3:
            content += f"    --color-primary: {primary};\n"
            content += f"    --color-secondary: {secondary};\n"
            content += f"    --color-accent: {accent};\n"
            content += f"    --color-background: {bg};\n"
            content += f"    --color-text-primary: {fg_primary};\n"
            content += f"    --color-text-secondary: {fg_secondary};\n"
            content += f"    --color-text-accent: {fg_accent};\n"
            content += f"    --color-text-background: {fg_bg};\n\n"

        # Add all palette colors as variables
        for i, c in enumerate(palette):
            content += f"    --color-{i}: {c};\n"
            content += f"    --text-color-{i}: {foregrounds[i]};\n"

        content += "}\n\n"

        # Add basic component styles
        if with_comments:
            content += "/* Basic component styling examples */\n"

        content += "body {\n"
        content += "    background-color: var(--color-background);\n"
        content += "    color: var(--color-text-background);\n"
        content += "    font-family: Arial, sans-serif;\n"
        content += "}\n\n"

        content += "button, .button {\n"
        content += "    background-color: var(--color-primary);\n"
        content += "    color: var(--color-text-primary);\n"
        content += "    padding: 8px 16px;\n"
        content += "    border-radius: 4px;\n"
        content += "    border: none;\n"
        content += "    font-weight: bold;\n"
        content += "}\n\n"

        content += "button:hover, .button:hover {\n"
        content += "    background-color: var(--color-accent);\n"
        content += "    color: var(--color-text-accent);\n"
        content += "}\n\n"

        content += "input, select {\n"
        content += "    background-color: var(--color-background);\n"
        content += "    color: var(--color-text-background);\n"
        content += "    border: 1px solid var(--color-secondary);\n"
        content += "    border-radius: 3px;\n"
        content += "    padding: 8px;\n"
        content += "}\n\n"

        return content

    def export_as_tailwind(
        self, palette, with_comments=True, with_semantic=True, theme_name="Theme"
    ):
        """Export theme as Tailwind config"""
        # Create header
        header = f"// {theme_name} - Tailwind Config\n\n"

        if with_comments:
            header += "/**\n"
            header += f" * Theme: {theme_name}\n"
            header += " * Generated with Enhanced Theme Studio\n"
            header += f" * Base color: {self.color_picker.hex_input.text()}\n"
            header += f" * Scheme: {self.scheme_combo.currentText()}\n"
            header += f" * WCAG compliance: {self.wcag_level.currentText() if self.wcag_check.isChecked() else 'Off'}\n"
            header += f" * Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            header += " */\n\n"

        content = header

        # Tailwind config
        content += "module.exports = {\n"
        content += "  theme: {\n"
        content += "    extend: {\n"
        content += "      colors: {\n"

        # Add semantic colors if requested
        if with_semantic and len(palette) >= 3:
            content += f"        primary: '{palette[0]}',\n"
            content += f"        secondary: '{palette[1]}',\n"
            content += f"        accent: '{palette[2]}',\n"
            content += (
                f"        background: '{palette[3 if len(palette) > 3 else 0]}',\n"
            )

        # Add all palette colors
        content += f"        {theme_name.lower().replace(' ', '_')}: {{\n"
        for i, c in enumerate(palette):
            content += f"          {i}: '{c}',\n"
        content += "        },\n"
        content += "      },\n"
        content += "    },\n"
        content += "  },\n"
        content += "  plugins: [],\n"
        content += "};\n"

        return content

    def export_as_json(
        self,
        palette,
        foregrounds,
        with_comments=True,
        with_semantic=True,
        include_both_modes=True,
        theme_name="Theme",
    ):
        """Export theme as JSON"""
        theme = {
            "name": theme_name,
            "metadata": {
                "generator": "Enhanced Theme Studio",
                "base_color": self.color_picker.hex_input.text(),
                "scheme": self.scheme_combo.currentText(),
                "wcag_compliance": self.wcag_level.currentText()
                if self.wcag_check.isChecked()
                else "Off",
                "date_created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            },
            "palette": palette,
            "foregrounds": foregrounds,
        }

        # Add semantic colors if requested
        if with_semantic and len(palette) >= 3:
            theme["semantic"] = {
                "primary": palette[0],
                "secondary": palette[1],
                "accent": palette[2],
                "background": palette[3] if len(palette) > 3 else "#FFFFFF",
                "text_primary": foregrounds[0],
                "text_secondary": foregrounds[1]
                if len(foregrounds) > 1
                else foregrounds[0],
                "text_accent": foregrounds[2]
                if len(foregrounds) > 2
                else foregrounds[0],
                "text_background": foregrounds[3]
                if len(foregrounds) > 3
                else "#000000",
            }

        # Add theme mode variants if requested
        if (
            include_both_modes
            and hasattr(self, "light_palette")
            and hasattr(self, "dark_palette")
        ):
            theme["light_mode"] = {
                "palette": self.light_palette,
                "foregrounds": [pick_foreground(c) for c in self.light_palette],
            }

            theme["dark_mode"] = {
                "palette": self.dark_palette,
                "foregrounds": [pick_foreground(c) for c in self.dark_palette],
            }

        # Convert to JSON string
        return json.dumps(theme, indent=2)

    def export_as_svg(self, palette, theme_name="Theme"):
        """Export palette as SVG color chart"""
        svg_width = 800
        svg_height = 200
        rect_width = svg_width / len(palette)

        svg = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <title>{theme_name}</title>
  <desc>Generated with Enhanced Theme Studio</desc>
"""

        for i, color in enumerate(palette):
            x = i * rect_width
            svg += f'  <rect x="{x}" y="0" width="{rect_width}" height="{svg_height - 40}" fill="{color}" />\n'
            svg += f'  <text x="{x + rect_width / 2}" y="{svg_height - 20}" text-anchor="middle" font-family="Arial" font-size="14">{color}</text>\n'

        svg += "</svg>"
        return svg

    def show_about_dialog(self):
        """Display information about the application"""
        about_text = f"""
        <h2>Enhanced Theme Studio v{__version__}</h2>
        <p>Released: {__release_date__}</p>
        <p>A powerful color palette and theme generator built with PyQt6.</p>
        <p>Features:</p>
        <ul>
            <li>Color scheme generation based on color theory</li>
            <li>WCAG accessibility testing</li>
            <li>Colorblindness simulation</li>
            <li>Light/dark mode theme generation</li>
            <li>Multiple export formats</li>
        </ul>
        <p>Built with: Python, PyQt6, NumPy</p>
        <p>WCAG formulas from WebAIM, Color theory principles from UI/UX design resources</p>
        <p>Documentation: <a href="Enhanced_Theme_Studio_Manual.md">User Manual</a></p>
        <p><b>Disclaimer:</b> I developed this as a solo project using AI-assisted "vibe coding". 
        Any issues in the code are part of my learning journey.</p>
        <p>Contact: soundchazer@gmail.com</p>
        <p>© 2025 Soundchazer2k. All rights reserved.</p>
        """

        QtWidgets.QMessageBox.about(self, "About Enhanced Theme Studio", about_text)

    def show_trending_palettes(self):
        """Show a dialog with trending palettes from a JSON file."""
        try:
            with open("trending_palettes.json", "r") as f:
                trending_palettes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.statusBar().showMessage("Could not load trending palettes.")
            return

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Trending Palettes")
        layout = QtWidgets.QVBoxLayout(dialog)

        label = QtWidgets.QLabel("Click a palette to load it:")
        layout.addWidget(label)

        for palette in trending_palettes:
            palette_widget = QtWidgets.QWidget()
            palette_layout = QtWidgets.QHBoxLayout(palette_widget)

            name_label = QtWidgets.QLabel(palette["name"])
            palette_layout.addWidget(name_label)

            for color in palette["colors"]:
                swatch = QtWidgets.QLabel()
                swatch.setFixedSize(20, 20)
                swatch.setStyleSheet(f"background-color: {color};")
                palette_layout.addWidget(swatch)
            
            btn = QtWidgets.QPushButton("Load")
            btn.clicked.connect(lambda _, p=palette: self.load_trending_palette(p, dialog))
            palette_layout.addWidget(btn)

            layout.addWidget(palette_widget)

        dialog.exec()

    def load_trending_palette(self, palette, dialog):
        """Load a trending palette."""
        self.color_picker.set_color(palette["colors"][0])
        self.num_combo.blockSignals(True)
        self.num_combo.setCurrentText(str(len(palette["colors"])))
        self.num_combo.blockSignals(False)
        self.scheme_combo.blockSignals(True)
        self.scheme_combo.setCurrentText("Custom")
        self.scheme_combo.blockSignals(False)
        self.update_palette(custom_colors=palette["colors"])
        dialog.accept()

    def save_palette(self):
        """Save the current palette to the favorites"""
        n = self.table.columnCount()
        if n == 0:
            return

        # Get the original (unadjusted) colors
        colors = [self.table.item(0, i).text() for i in range(n)]

        # Prompt for palette name
        palette_name, ok = QtWidgets.QInputDialog.getText(
            self, "Save Palette", "Enter a name for this palette:"
        )

        if ok and palette_name:
            palette_data = {
                "name": palette_name,
                "colors": colors,
                "scheme": self.scheme_combo.currentText(),
                "base_color": self.color_picker.hex_input.text(),
            }

            # Check if name already exists
            for i, p in enumerate(self.saved_palettes):
                if p["name"] == palette_name:
                    reply = QtWidgets.QMessageBox.question(
                        self,
                        "Overwrite Palette",
                        f"A palette named '{palette_name}' already exists. Overwrite it?",
                        QtWidgets.QMessageBox.StandardButton.Yes
                        | QtWidgets.QMessageBox.StandardButton.No,
                    )

                    if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                        self.saved_palettes[i] = palette_data
                        self.statusBar().showMessage(
                            f"Palette '{palette_name}' updated"
                        )
                        return
                    else:
                        return

            # Add new palette
            self.saved_palettes.append(palette_data)
            self.statusBar().showMessage(f"Palette '{palette_name}' saved")

    def load_palette(self):
        """Load a saved palette"""
        if not self.saved_palettes:
            QtWidgets.QMessageBox.information(
                self,
                "No Saved Palettes",
                "You don't have any saved palettes yet. Create a palette first.",
            )
            return

        # Create a more visual palette selector dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Load Palette")
        dialog.setMinimumWidth(500)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Palette list with preview
        list_widget = QtWidgets.QListWidget()
        for palette in self.saved_palettes:
            item = QtWidgets.QListWidgetItem(palette["name"])

            # Create a color preview widget
            preview = QtWidgets.QWidget()
            preview_layout = QtWidgets.QHBoxLayout(preview)
            preview_layout.setContentsMargins(0, 0, 0, 0)
            preview_layout.setSpacing(1)

            # Add small color swatches
            for color in palette["colors"]:
                swatch = QtWidgets.QLabel()
                swatch.setFixedSize(15, 15)
                swatch.setStyleSheet(
                    f"background-color: {color}; border: 1px solid #CCCCCC;"
                )
                preview_layout.addWidget(swatch)

            preview_layout.addStretch()

            # Custom item widget with preview
            item_widget = QtWidgets.QWidget()
            item_layout = QtWidgets.QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 5, 5, 5)

            name_label = QtWidgets.QLabel(palette["name"])
            name_label.setStyleSheet("font-weight: bold;")

            scheme_label = QtWidgets.QLabel(f"({palette['scheme']})")
            scheme_label.setStyleSheet("color: #666666;")

            item_layout.addWidget(name_label)
            item_layout.addWidget(scheme_label)
            item_layout.addStretch()
            item_layout.addWidget(preview)

            # Set the custom widget for this item
            list_widget.addItem(item)
            list_widget.setItemWidget(item, item_widget)

            # Make the item height appropriate for the widget
            item.setSizeHint(item_widget.sizeHint())

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        load_btn = QtWidgets.QPushButton("Load")
        load_btn.clicked.connect(dialog.accept)
        load_btn.setDefault(True)

        delete_btn = QtWidgets.QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_palette(list_widget, dialog))

        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(load_btn)

        # Add widgets to dialog
        layout.addWidget(QtWidgets.QLabel("Select a palette to load:"))
        layout.addWidget(list_widget)
        layout.addLayout(btn_layout)

        # Show dialog
        if (
            dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted
            and list_widget.currentItem()
        ):
            name = list_widget.currentItem().text()
            for palette in self.saved_palettes:
                if palette["name"] == name:
                    self.color_picker.set_color(palette["base_color"])
                    self.scheme_combo.setCurrentText(palette["scheme"])
                    self.num_combo.setCurrentText(str(len(palette["colors"])))
                    self.update_palette()
                    self.statusBar().showMessage(f"Palette '{name}' loaded")
                    break

    def delete_palette(self, list_widget, dialog):
        """Delete the selected palette"""
        if not list_widget.currentItem():
            return

        name = list_widget.currentItem().text()

        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Palette",
            f"Are you sure you want to delete the palette '{name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Remove from saved palettes
            self.saved_palettes = [p for p in self.saved_palettes if p["name"] != name]

            # Update list widget
            item = list_widget.currentItem()
            list_widget.takeItem(list_widget.row(item))

            # Close dialog if no palettes left
            if not self.saved_palettes:
                dialog.reject()
                QtWidgets.QMessageBox.information(
                    self, "No Saved Palettes", "You don't have any saved palettes left."
                )

    def statusBar(self):
        """Override to add timer-based status clearing"""
        status_bar = super().statusBar()
        return status_bar

    def set_status(self, message, timeout=5000):
        """Set status message with auto-clear after timeout"""
        self.statusBar().showMessage(message)
        self.status_timer.start(timeout)

    def clear_status(self):
        """Clear the status bar message"""
        self.statusBar().clearMessage()

    def generate_new_palette(self):
        """Generate a new color palette with visual feedback"""
        # Apply a slight animation effect to show something is happening
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)

        # Save current settings
        old_base = self.color_picker.hex_input.text()

        # Apply a slight variation to base color to make the change visible
        # even if all settings are the same
        # Save current settings
        old_base = self.color_picker.hex_input.text()

        try:
            r, g, b = hex_to_rgb(old_base)
        except ValueError:
            # If old_base somehow became invalid, default to black or another failsafe
            r, g, b = (0,0,0)
            self.set_status(f"Warning: Could not parse previous base color {old_base}. Varied from black.")
        
        # Add small random variation (±5%)
        r = max(0, min(255, r + random.randint(-13, 13)))
        g = max(0, min(255, g + random.randint(-13, 13)))
        b = max(0, min(255, b + random.randint(-13, 13)))

        # Create new base color
        new_base = f"#{r:02X}{g:02X}{b:02X}"

        # Temporarily update base color without triggering update
        self.color_picker.blockSignals(True)
        self.color_picker.set_color(new_base)
        self.color_picker.blockSignals(False)

        # Generate palette
        self.update_palette()

        # Show message
        self.set_status(
            f"New palette generated! Base color slightly varied from {old_base} to {new_base}"
        )

        # Restore cursor
        QtWidgets.QApplication.restoreOverrideCursor()

    def on_theme_mode_changed(self, mode):
        """Handle theme mode changes between light and dark"""
        if not hasattr(self, "current_palette") or not self.current_palette:
            self.update_palette()
            return

        # Check if we should auto-adjust
        if self.auto_adjust_dark.isChecked():
            # Switch between light and dark variants
            if mode == "Dark Mode":
                # Convert light palette to dark
                self.create_dark_variant()
            else:
                # Convert dark palette to light
                self.create_light_variant()

        # Update preview with current palette
        self.update_preview_components(self.current_palette)

        # Update status
        self.set_status(f"Switched to {mode}")

    def _update_theme_variant(self, palette):
        """Helper to update UI with a new theme variant."""
        self.current_palette = palette
        self.update_table_with_palette(self.current_palette)

        if self.wcag_check.isChecked():
            adjusted_palette = []
            min_ratio = 7.0 if "AAA" in self.wcag_level.currentText() else 4.5
            preserve_character = self.preserve_character_check.isChecked()

            for color in palette:
                fg = pick_foreground(color)
                ratio = contrast_ratio(color, fg)
                wcag = get_wcag_level(ratio)

                if wcag not in ["AAA"] and ratio < min_ratio:
                    adjusted_color = ensure_wcag_compliant(
                        fg, color, min_ratio, preserve_character
                    )
                else:
                    adjusted_color = color
                adjusted_palette.append(adjusted_color)
            self.update_preview_components(adjusted_palette)
        else:
            self.update_preview_components(palette)

    def create_dark_variant(self):
        """Create a dark mode variant of the current palette"""
        if not hasattr(self, "light_palette") or not self.light_palette:
            return

        self.dark_palette = self._create_variant(self.light_palette, "dark")
        self._update_theme_variant(self.dark_palette)

    def create_light_variant(self):
        """Create a light mode variant of the current palette"""
        if not hasattr(self, "light_palette"):
            self.update_palette()
            return

        self._update_theme_variant(self.light_palette)

    def _create_variant(self, palette, mode):
        """Helper to create a light or dark variant of a palette."""
        variant_palette = []
        for i, color in enumerate(palette):
            r, g, b = hex_to_rgb(color)
            h, l, s = rgb_to_hls(r, g, b)

            if mode == "dark":
                if i == 0:
                    new_l = 0.7 if l < 0.5 else 0.3
                elif i == 1:
                    new_l = 0.6 if l < 0.5 else 0.4
                elif i == 2:
                    new_l = 0.8 if l < 0.5 else 0.75
                elif i == 3:
                    new_l = 0.1
                    s = min(s, 0.3)
                else:
                    new_l = 1.0 - l
            else: # mode == "light"
                new_l = l

            variant_color = hls_to_hex(h, new_l, s)
            variant_palette.append(variant_color)
        return variant_palette

    def update_table_with_palette(self, palette):
        """Update the palette table with the given colors"""
        n = len(palette)
        if n == 0:
            return

        for i, hexcol in enumerate(palette):
            if i >= self.table.columnCount():
                break

            # Update the color swatch
            swatch = self.table.item(0, i)
            if swatch:
                swatch.setText(hexcol)
                swatch.setBackground(QtGui.QColor(hexcol))

                # Update foreground
                fg = pick_foreground(hexcol)
                swatch.setForeground(QtGui.QColor(fg))

                # Update contrast cell
                ratio = contrast_ratio(hexcol, fg)
                ratio_item = self.table.item(1, i)
                if ratio_item:
                    ratio_item.setText(f"{ratio:.1f}:1")

                # Update WCAG cell
                wcag = get_wcag_level(ratio)
                wcag_item = self.table.item(2, i)
                if wcag_item:
                    wcag_item.setText(wcag)

                    # Set WCAG level colors
                    if wcag == "AAA":
                        wcag_bg = QtGui.QColor(50, 150, 50)
                        wcag_fg = QtGui.QColor(255, 255, 255)
                    elif wcag == "AA":
                        wcag_bg = QtGui.QColor(100, 150, 50)
                        wcag_fg = QtGui.QColor(0, 0, 0)
                    elif wcag == "AA Large":
                        wcag_bg = QtGui.QColor(180, 150, 10)
                        wcag_fg = QtGui.QColor(0, 0, 0)
                    else:
                        wcag_bg = QtGui.QColor(180, 50, 50)
                        wcag_fg = QtGui.QColor(255, 255, 255)

                    wcag_item.setBackground(wcag_bg)
                    wcag_item.setForeground(wcag_fg)


# Add after color utility functions
def simulate_colorblindness(hex_color, simulation_type):
    """
    Simulate how a color would appear to someone with color vision deficiency

    Parameters:
    - hex_color: Hex color to transform
    - simulation_type: One of "Protanopia", "Deuteranopia", "Tritanopia", "Grayscale"

    Returns:
    - Transformed hex color
    """
    if simulation_type == "Normal Vision":
        return hex_color

    # Convert hex to RGB
    r, g, b = hex_to_rgb(hex_color)
    rgb = np.array([r, g, b], dtype=float) / 255.0

    # Transformation matrices for different types of color blindness
    if simulation_type == "Protanopia":  # Red-blind
        matrix = np.array(
            [[0.567, 0.433, 0.000], [0.558, 0.442, 0.000], [0.000, 0.242, 0.758]]
        )
    elif simulation_type == "Deuteranopia":  # Green-blind
        matrix = np.array(
            [[0.625, 0.375, 0.000], [0.700, 0.300, 0.000], [0.000, 0.300, 0.700]]
        )
    elif simulation_type == "Tritanopia":  # Blue-blind
        matrix = np.array(
            [[0.950, 0.050, 0.000], [0.000, 0.433, 0.567], [0.000, 0.475, 0.525]]
        )
    elif simulation_type == "Grayscale":
        # Use luminance formula
        gray = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        transformed = np.array([gray, gray, gray])
    else:
        return hex_color

    # Apply transformation
    if simulation_type != "Grayscale":
        transformed = np.dot(matrix, rgb)

    # Ensure values are within range [0, 1]
    transformed = np.clip(transformed, 0, 1)

    # Convert back to hex
    r_new, g_new, b_new = [int(c * 255) for c in transformed]
    return f"#{r_new:02X}{g_new:02X}{b_new:02X}"

def simulate_palette(palette, simulation_type):
    """Apply colorblindness simulation to entire palette"""
    if simulation_type == "Normal Vision":
        return palette
    return [simulate_colorblindness(color, simulation_type) for color in palette]


# Add back the ColorWheelWidget class
class ColorWheelWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.colors = []
        self.scheme = "Monochromatic"
        self.base_color = "#3498DB"

    def set_colors(self, colors, scheme, base_color):
        """Set the colors to display on the wheel"""
        self.colors = colors
        self.scheme = scheme
        self.base_color = base_color
        self.update()

    def paintEvent(self, event):
        """Draw the color wheel and palette relationships"""
        if not self.colors:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Calculate center and radius
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 30

        # Draw outer wheel with hue spectrum
        self.draw_color_wheel(painter, center_x, center_y, radius)

        # Draw palette colors on the wheel
        self.draw_palette_markers(painter, center_x, center_y, radius - 30)

        # Draw color scheme type
        painter.setPen(QtGui.QPen(QtGui.QColor("#000000")))
        painter.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Weight.Bold))
        painter.drawText(
            QtCore.QRect(0, height - 30, width, 30),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.scheme} Scheme",
        )

    def draw_color_wheel(self, painter, center_x, center_y, radius):
        """Draw the HSL color wheel"""
        # Draw hue wheel
        for angle in range(0, 360, 2):
            # Convert angle to radians
            rad = math.radians(angle)

            # Calculate color based on hue angle
            hue = angle / 360.0
            r, g, b = colorsys.hls_to_rgb(hue, 0.5, 1.0)

            # Create pen with color
            pen = QtGui.QPen(QtGui.QColor(int(r * 255), int(g * 255), int(b * 255)))
            pen.setWidth(3)
            painter.setPen(pen)

            # Draw line from inner to outer radius
            inner_x = center_x + (radius - 20) * math.cos(rad)
            inner_y = center_y + (radius - 20) * math.sin(rad)
            outer_x = center_x + radius * math.cos(rad)
            outer_y = center_y + radius * math.sin(rad)

            painter.drawLine(int(inner_x), int(inner_y), int(outer_x), int(outer_y))

    def draw_palette_markers(self, painter, center_x, center_y, radius):
        """Draw markers for the palette colors on the wheel"""
        if not self.colors:
            return

        # Draw base color at center
        try:
            base_r, base_g, base_b = hex_to_rgb(self.base_color)
        except ValueError:
            # Fallback to a default color for the wheel if base_color is invalid
            base_r, base_g, base_b = (52, 152, 219) # Default blue
        base_h, base_l, base_s = rgb_to_hls(base_r, base_g, base_b)

        # Draw center circle
        painter.setBrush(QtGui.QBrush(QtGui.QColor(base_r, base_g, base_b)))
        painter.setPen(QtGui.QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(QtCore.QPoint(int(center_x), int(center_y)), 20, 20)

        # Draw lines connecting colors
        painter.setPen(
            QtGui.QPen(QtGui.QColor(100, 100, 100, 150), 2, Qt.PenStyle.DashLine)
        )

        # Draw each color in the palette
        for i, color in enumerate(self.colors):
            r, g, b = hex_to_rgb(color)
            h, l, s = rgb_to_hls(r, g, b)

            # Convert hue to angle in radians
            angle = h * 2 * math.pi

            # Calculate position based on hue
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Draw line from center
            painter.drawLine(int(center_x), int(center_y), int(x), int(y))

            # Draw color marker
            painter.setBrush(QtGui.QBrush(QtGui.QColor(r, g, b)))
            painter.setPen(QtGui.QPen(QtGui.QColor("#000000")))
            painter.drawEllipse(QtCore.QPoint(int(x), int(y)), 10, 10)

            # Draw color number
            painter.setPen(
                QtGui.QPen(QtGui.QColor("#FFFFFF" if l < 0.5 else "#000000"))
            )
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(
                QtCore.QRect(int(x - 5), int(y - 5), 10, 10),
                Qt.AlignmentFlag.AlignCenter,
                str(i + 1),
            )

def run_studio():
    """Entry point for the application."""
    app = QtWidgets.QApplication(sys.argv)
    win = EnhancedThemeGenerator()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_studio()