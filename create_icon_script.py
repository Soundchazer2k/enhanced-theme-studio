"""
Script to create a simple application icon for Enhanced Theme Studio
Requires Pillow: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create a 256x256 icon with a color wheel design
icon_size = 256
img = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a color circle
center = icon_size // 2
radius = icon_size // 2 - 10

# Draw a color wheel with segments
segments = 12
for i in range(segments):
    start_angle = i * 360 / segments
    end_angle = (i + 1) * 360 / segments
    # HSL-like colors around the wheel
    hue = i / segments
    r = int(255 * (1 - abs((hue * 6) % 2 - 1)))
    g = int(255 * (1 - abs(((hue * 6 + 2) % 6) - 1)))
    b = int(255 * (1 - abs(((hue * 6 + 4) % 6) - 1)))
    draw.pieslice(
        [10, 10, icon_size - 10, icon_size - 10],
        start_angle,
        end_angle,
        fill=(r, g, b, 255)
    )

# Draw a white circle in the middle
inner_radius = radius // 2
draw.ellipse(
    [center - inner_radius, center - inner_radius,
     center + inner_radius, center + inner_radius],
    fill=(255, 255, 255, 255)
)

# Draw inner circle with "ETS" text
try:
    # Try to use a font if available
    font = ImageFont.truetype("arial.ttf", inner_radius)
except IOError:
    # Fall back to default font
    font = ImageFont.load_default()
    
# Draw "ETS" centered in the circle
text = "ETS"
text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else font.getsize(text)
text_position = (center - text_width // 2, center - text_height // 2)
draw.text(text_position, text, fill=(50, 50, 50, 255), font=font)

# Save as PNG
png_path = "app_icon.png"
img.save(png_path)
print(f"Created {png_path}")

# If we're on Windows, try to create an .ico file
try:
    if os.name == 'nt':  # Windows
        ico_path = "app_icon.ico"
        # Convert to different sizes for .ico
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ico_path, sizes=sizes)
        print(f"Created {ico_path}")
    else:
        # On macOS, create .icns using iconutil (requires external tools)
        print("On macOS, use 'iconutil' to create .icns file from PNG")
except Exception as e:
    print(f"Could not create icon file: {e}")
    print("You may need to convert app_icon.png to .ico format manually using an online converter.")

print("Icon creation complete!") 