import unittest
from enhanced_theme_generator import (
    hex_to_rgb,
    rgb_to_hls,
    hls_to_hex,
    relative_luminance,
    contrast_ratio,
    get_wcag_level,
    generate_scheme,
    ensure_wcag_compliant,
)

class TestColorUtils(unittest.TestCase):
    def test_hex_to_rgb(self):
        self.assertEqual(hex_to_rgb("#FFFFFF"), (255, 255, 255))
        self.assertEqual(hex_to_rgb("#000000"), (0, 0, 0))
        self.assertEqual(hex_to_rgb("3498DB"), (52, 152, 219))

    def test_rgb_to_hls(self):
        # Test with a known color
        r, g, b = 52, 152, 219
        h, l, s = rgb_to_hls(r, g, b)
        self.assertAlmostEqual(h, 0.57, places=2)
        self.assertAlmostEqual(l, 0.53, places=2)
        self.assertAlmostEqual(s, 0.7, places=2)

    def test_hls_to_hex(self):
        self.assertEqual(hls_to_hex(0.57, 0.53, 0.7), "#3394DB")

    def test_contrast_ratio(self):
        # High contrast
        self.assertGreater(contrast_ratio("#FFFFFF", "#000000"), 20)
        # Low contrast
        self.assertLess(contrast_ratio("#808080", "#707070"), 1.3)

    def test_get_wcag_level(self):
        self.assertEqual(get_wcag_level(8), "AAA")
        self.assertEqual(get_wcag_level(5), "AA")
        self.assertEqual(get_wcag_level(3.5), "AA Large")
        self.assertEqual(get_wcag_level(2), "Fail")

    def test_generate_scheme(self):
        # Monochromatic
        colors = generate_scheme("#3498DB", "Monochromatic", 5)
        self.assertEqual(len(colors), 5)
        # All colors should have the same hue
        base_h, _, _ = rgb_to_hls(*hex_to_rgb("#3498DB"))
        for color in colors:
            h, _, _ = rgb_to_hls(*hex_to_rgb(color))
            self.assertAlmostEqual(h, base_h, places=1)

    def test_ensure_wcag_compliant(self):
        fg = "#000000"
        bg = "#808080"  # Low contrast
        compliant_bg = ensure_wcag_compliant(fg, bg, min_ratio=4.5)
        self.assertGreaterEqual(contrast_ratio(fg, compliant_bg), 4.5)

if __name__ == "__main__":
    unittest.main()
