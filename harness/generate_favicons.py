#!/usr/bin/env python3
"""Generate favicon assets from the canonical PRINCEPS glyph."""

from __future__ import annotations

import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLYPH = os.path.join(ROOT, "assets", "brand", "princeps-glyph.png")
OUT_DIRS = (
    os.path.join(ROOT, "assets"),
    os.path.join(ROOT, "site"),
)


def generate_favicons(*, glyph_path: str = GLYPH) -> None:
    img = Image.open(glyph_path).convert("RGBA")
    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "apple-touch-icon.png": 180,
    }
    ico_sizes = [16, 32, 48]

    for out_dir in OUT_DIRS:
        os.makedirs(out_dir, exist_ok=True)
        for name, size in sizes.items():
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(os.path.join(out_dir, name), optimize=True)

        ico_images = [
            img.resize((size, size), Image.Resampling.LANCZOS) for size in ico_sizes
        ]
        ico_images[0].save(
            os.path.join(out_dir, "favicon.ico"),
            format="ICO",
            sizes=[(s, s) for s in ico_sizes],
            append_images=ico_images[1:],
        )


if __name__ == "__main__":
    generate_favicons()
