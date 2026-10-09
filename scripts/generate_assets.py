"""Generate deterministic PNG/ICO application icons from the brand geometry."""
from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def icon(size: int = 512) -> Image.Image:
    scale = size / 512
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    navy = "#091522"
    amber = "#f4b942"
    teal = "#45c4b0"
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=112 * scale, fill=navy)
    width = max(3, round(28 * scale))
    draw.line([(126*scale,206*scale),(160*scale,132*scale),(352*scale,132*scale),(386*scale,206*scale)], fill=amber, width=width, joint="curve")
    draw.line([(146*scale,216*scale),(146*scale,370*scale),(366*scale,370*scale),(366*scale,216*scale)], fill=amber, width=max(3,round(24*scale)), joint="curve")
    draw.polygon([(229*scale,244*scale),(320*scale,299*scale),(229*scale,354*scale)], fill=teal)
    for x in (174,256,338):
        r = 10*scale
        draw.ellipse((x*scale-r,178*scale-r,x*scale+r,178*scale+r), fill=amber)
    return image


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    source = icon()
    source.save(ASSETS / "app-icon.png", optimize=True)
    source.save(ASSETS / "app-icon.ico", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
    print(f"Generated {ASSETS / 'app-icon.png'} and app-icon.ico")


if __name__ == "__main__":
    main()

