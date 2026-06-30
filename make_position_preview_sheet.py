from pathlib import Path

from PIL import Image, ImageDraw


root = Path(r"C:\Users\emine\OneDrive\Desktop\Website_Clone")
frame_dir = root / "caption_position_preview_frames"
files = sorted(frame_dir.glob("pos_*.jpg"))
imgs = [Image.open(path).convert("RGB") for path in files]

w, h = imgs[0].size
cols = 2
rows = (len(imgs) + cols - 1) // cols
label_h = 28
sheet = Image.new("RGB", (cols * w, rows * (h + label_h)), (245, 245, 245))
draw = ImageDraw.Draw(sheet)

labels = ["Cue 6", "Cue 7", "Cue 9", "Cue 10", "Cue 12", "Cue 13", "Cue 14", "Cue 15"]
for idx, img in enumerate(imgs):
    x = (idx % cols) * w
    y = (idx // cols) * (h + label_h)
    draw.rectangle([x, y, x + w, y + label_h], fill=(30, 30, 30))
    draw.text((x + 8, y + 6), labels[idx], fill=(255, 255, 255))
    sheet.paste(img, (x, y + label_h))

sheet.save(root / "caption_position_preview_sheet.jpg", quality=90)
