from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "audit" / "eminent_source_photos"
OUT = ROOT / "public" / "images" / "photos"

sources = {
    "doctor_patient": SRC / "source_home_NB7Pde7.jpg",
    "care_team": SRC / "source_about_g00woqn.jpg",
    "hands_cane": SRC / "source_about_4073.jpg",
    "elder_hands": SRC / "source_services_10487.jpg",
    "seniors_swings": SRC / "source_services_jazA02z.jpg",
    "stock_hands": SRC / "repo_stock" / "homeHero.webp",
    "stock_beds": SRC / "repo_stock" / "homeLevelInpatient.webp",
    "stock_lab": SRC / "repo_stock" / "servicesHero.webp",
    "stock_books": SRC / "repo_stock" / "contactHero.webp",
    "stock_flowers": SRC / "repo_stock" / "griefHero.webp",
}

slots = {
    "homeHero.webp": ("doctor_patient", 1600, 1000),
    "homePhilosophyPortrait.webp": ("hands_cane", 1200, 1500),
    "homeLevelRoutine.webp": ("elder_hands", 1000, 750),
    "homeLevelContinuous.webp": ("care_team", 1000, 750),
    "homeLevelInpatient.webp": ("stock_beds", 1000, 750),
    "aboutHero.webp": ("seniors_swings", 1600, 1000),
    "servicesHero.webp": ("stock_lab", 1600, 1000),
    "familiesHero.webp": ("stock_hands", 1600, 1000),
    "contactHero.webp": ("stock_books", 1600, 1000),
    "griefHero.webp": ("stock_flowers", 1600, 1000),
}


def cover_crop(image: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = image.size
    target_ratio = width / height
    source_ratio = src_w / src_h

    if source_ratio > target_ratio:
        crop_w = int(src_h * target_ratio)
        left = (src_w - crop_w) // 2
        box = (left, 0, left + crop_w, src_h)
    else:
        crop_h = int(src_w / target_ratio)
        top = (src_h - crop_h) // 2
        box = (0, top, src_w, top + crop_h)

    return image.crop(box).resize((width, height), Image.Resampling.LANCZOS)


OUT.mkdir(parents=True, exist_ok=True)

for filename, (source_key, width, height) in slots.items():
    source = Image.open(sources[source_key]).convert("RGB")
    output = cover_crop(source, width, height)
    output.save(OUT / filename, "WEBP", quality=84, method=6)
    print(f"{filename}: {source_key} -> {width}x{height}")
