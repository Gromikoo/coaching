# Makes 1080x1920 IG story images (black & white, matches the website) from messages.json.
# Run: python3 site/make_highlights.py   -> writes to highlight/
import json, pathlib, re
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "highlight"
OUT.mkdir(exist_ok=True)
W, H = 1080, 1920
BLACK, WHITE, GREY, LINE = "#0b0b0b", "#ffffff", "#6b6b6b", "#dcdcdc"
AV = "/System/Library/Fonts/Avenir Next.ttc"
heavy = lambda s: ImageFont.truetype(AV, s, index=8)
demi = lambda s: ImageFont.truetype(AV, s, index=2)
medium = lambda s: ImageFont.truetype(AV, s, index=5)

data = json.loads((ROOT / "messages.json").read_text())
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]+")

def wrap(text, f, maxw):
    lines = [""]
    for w in text.split():
        t = (lines[-1] + " " + w).strip()
        if f.getlength(t) > maxw and lines[-1]: lines.append(w)
        else: lines[-1] = t
    return lines

def fit(img, maxw, maxh):
    r = min(maxw / img.width, maxh / img.height)
    return img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)

def rounded_paste(im, img, x, y, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], r, fill=255)
    im.paste(img, (x, y), m)

def pill(d, cx, cy, text, f, bg, fg, padx=34, h=None):
    tw = f.getlength(text); h = h or int(f.size * 1.5)
    d.rounded_rectangle([cx - tw / 2 - padx, cy - h / 2, cx + tw / 2 + padx, cy + h / 2], 14, fill=bg)
    d.text((cx, cy), text, font=f, fill=fg, anchor="mm")

def header(d, color):
    d.text((W // 2, 250), "RESULTS", font=heavy(110), fill=color, anchor="mm")

def button(d, bg, fg, text="SEE IF YOU'RE A FIT · LINK IN BIO"):
    bw, bh, y = 900, 124, 1600
    d.rounded_rectangle([(W - bw) // 2, y, (W + bw) // 2, y + bh], 16, fill=bg)
    d.text((W // 2, y + bh // 2), text, font=heavy(40), fill=fg, anchor="mm")

def label(t): return t.replace("→", "TO").upper()

n = 0
def save(im):
    global n; n += 1
    im.save(OUT / f"{n:02d}.png", optimize=True)

# 1) before & after photos -- no title (the highlight cover says TESTIMONIALS), centered top to bottom
for p in data["photos"]:
    im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)
    photo = fit(Image.open(ROOT / p["img"]).convert("RGB"), 960, 1000)
    f = demi(50); lines = wrap("\u201c" + p["quote"] + "\u201d", f, 920)
    total = photo.height + 90 + len(lines) * 66
    x, y = (W - photo.width) // 2, (H - total) // 2
    rounded_paste(im, photo, x, y, 20)
    pill(d, W // 2, y + photo.height, label(p["tag"]), heavy(64), BLACK, WHITE)
    ty = y + photo.height + 90
    for ln in lines:
        d.text((W // 2, ty), ln, font=f, fill=BLACK, anchor="ma"); ty += 66
    save(im)

# 2) every message: result label, their words, name, real screenshot -- centered top to bottom
for m in data["messages"]:
    im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)
    text = EMOJI.sub("", m["text"]).strip()
    for size in (64, 58, 52, 46, 42, 38):
        f = demi(size); lines = wrap("\u201c" + text + "\u201d", f, 930)
        if len(lines) * size * 1.3 <= 600: break
    lh = int(size * 1.3)
    shot = Image.open(ROOT / "img/msg" / (m["img"] + ".jpg")).convert("RGB")
    shot = fit(shot, 860, 1600 - len(lines) * lh - 360)   # keep the whole block inside the safe zone
    pad = 22; cw, ch = shot.width + pad * 2, shot.height + pad * 2
    PILL, GAP1, NAME, GAP2 = 140, 60, 56, 50
    total = PILL + GAP1 + len(lines) * lh + NAME + GAP2 + ch
    y = (H - total) // 2
    pill(d, W // 2, y + PILL // 2, label(m["tag"]), heavy(84), BLACK, WHITE, h=PILL)
    y += PILL + GAP1
    for ln in lines:
        d.text((W // 2, y), ln, font=f, fill=BLACK, anchor="ma"); y += lh
    d.text((W // 2, y + 12), m["name"] or "Direct message", font=medium(36), fill=GREY, anchor="ma")
    y += NAME + GAP2
    cx = (W - cw) // 2
    d.rounded_rectangle([cx, y, cx + cw, y + ch], 24, fill=WHITE, outline=LINE, width=3)
    rounded_paste(im, shot, cx + pad, y + pad, 12)
    save(im)

# 3) no call-to-action slide: these are results only (Miko, 2026-11-16)

# 4) highlight cover (IG shows only the middle circle)
im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)
d.ellipse([W // 2 - 330, H // 2 - 330, W // 2 + 330, H // 2 + 330], fill=WHITE, outline=BLACK, width=10)
size = 120
while heavy(size).getlength("TESTIMONIALS") > 560: size -= 2   # fit inside the circle
d.text((W // 2, H // 2), "TESTIMONIALS", font=heavy(size), fill=BLACK, anchor="mm")
im.save(OUT / "00-cover.png", optimize=True)
print("made", n, "slides + cover in", OUT)
