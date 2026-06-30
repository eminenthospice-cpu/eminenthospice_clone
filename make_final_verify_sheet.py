from pathlib import Path

from PIL import Image, ImageDraw


root = Path(r"C:\Users\emine\OneDrive\Desktop\Website_Clone")
frame_dir = root / "caption_final_verify_frames"
files = sorted(frame_dir.glob("verify_*.jpg"))
imgs = [Image.open(path).convert("RGB") for path in files]

w, h = imgs[0].size
label_h = 28
sheet = Image.new("RGB", (w, len(imgs) * (h + label_h)), (245, 245, 245))
draw = ImageDraw.Draw(sheet)

labels = ["Cue 1 low", "Cue 6 raised", "Cue 9 raised", "Cue 12 raised", "Cue 14 raised"]
for idx, img in enumerate(imgs):
    y = idx * (h + label_h)
    draw.rectangle([0, y, w, y + label_h], fill=(30, 30, 30))
    draw.text((8, y + 6), labels[idx], fill=(255, 255, 255))
    sheet.paste(img, (0, y + label_h))

sheet.save(root / "caption_final_verify_sheet.jpg", quality=90)
