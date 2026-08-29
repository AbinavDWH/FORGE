"""Generate demo media: one camera-like photo with EXIF, one synthetic-looking sample."""
import os

from PIL import Image, ImageDraw, ImageFont

os.makedirs("data/sample_media/images", exist_ok=True)
os.makedirs("data/sample_media/synthetic", exist_ok=True)


def load_font(size=32):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render(lines, size):
    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    font = load_font()
    y = 60
    for line in lines:
        draw.text((60, y), line, fill="black", font=font)
        y += 60
    return img


DIARY_LINES = [
    "SITE DIARY - NRL GOLAGHAT",
    "Zone B / Pier 14",
    "Concrete pouring completed",
    "Progress: 100%",
    "Supervisor: Rahul",
]

# Camera-like photo: EXIF make/model present, non-generator dimensions -> low risk
real = render(DIARY_LINES, (1200, 900))
exif = Image.Exif()
exif[0x010F] = "Apple"
exif[0x0110] = "iPhone 13"
exif[0x0132] = "2026:08:28 10:30:00"
real.save("data/sample_media/images/pier14_site_photo.jpg", exif=exif)

# Synthetic-looking: no EXIF, generator-typical 1024x1024 -> high risk
synth = render(["Generated site render", "diffusion sample"], (1024, 1024))
synth.save("data/sample_media/synthetic/ai_generated_sample.jpg")

print("Sample media written to data/sample_media/")