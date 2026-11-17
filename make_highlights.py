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

HEADLINE = "I help women business owners lose their first 20lbs in 6 weeks"
def header(d, color):
    # top line on every slide; starts below IG's progress bar + profile row
    f = heavy(62); y = 190
    for ln in wrap(HEADLINE.upper(), f, 940):
        d.text((W // 2, y), ln, font=f, fill=color, anchor="ma"); y += 74

def button(d, bg, fg, text="SEE IF YOU'RE A FIT · LINK IN BIO"):
    bw, bh, y = 900, 124, 1600
    d.rounded_rectangle([(W - bw) // 2, y, (W + bw) // 2, y + bh], 16, fill=bg)
    d.text((W // 2, y + bh // 2), text, font=heavy(40), fill=fg, anchor="mm")

def label(t): return t.replace("→", "TO").upper()

n = 0
def save(im):
    global n; n += 1
    im.save(OUT / f"{n:02d}.png", optimize=True)

# 1) before & after photos (black slides, like the top of the website)
for p in data["photos"]:
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
    header(d, WHITE)
    photo = fit(Image.open(ROOT / p["img"]).convert("RGB"), 940, 820)
    x, y = (W - photo.width) // 2, 440
    rounded_paste(im, photo, x, y, 20)
    pill(d, W // 2, y + photo.height, label(p["tag"]), heavy(64), WHITE, BLACK)
    f = demi(50); lines = wrap("“" + p["quote"] + "”", f, 920)
    ty = y + photo.height + 90
    for ln in lines:
        d.text((W // 2, ty), ln, font=f, fill=WHITE, anchor="ma"); ty += 66
    button(d, WHITE, BLACK); save(im)

# 2) every message (white slides, like the review cards)
for m in data["messages"]:
    im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)
    header(d, BLACK)
    pill(d, W // 2, 520, label(m["tag"]), heavy(80), BLACK, WHITE, h=132)
    text = EMOJI.sub("", m["text"]).strip()
    for size in (64, 58, 52, 46, 42, 38):
        f = demi(size); lines = wrap("“" + text + "”", f, 930)
        if len(lines) * size * 1.3 <= 500: break
    lh = int(size * 1.3); y = 650
    for ln in lines:
        d.text((W // 2, y), ln, font=f, fill=BLACK, anchor="ma"); y += lh
    d.text((W // 2, y + 18), m["name"] or "Direct message", font=medium(36), fill=GREY, anchor="ma"); y += 80
    # the real screenshot, as proof
    top, bottom = max(y + 20, 1050), 1560
    shot = fit(Image.open(ROOT / "img/msg" / (m["img"] + ".jpg")).convert("RGB"), 860, bottom - top - 60)
    pad = 22; cw, ch = shot.width + pad * 2, shot.height + pad * 2
    cx, cy = (W - cw) // 2, top + (bottom - top - ch) // 2
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], 24, fill=WHITE, outline=LINE, width=3)
    rounded_paste(im, shot, cx + pad, cy + pad, 12)
    button(d, BLACK, WHITE); save(im)

# 3) last slide: the ask
im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
for i, ln in enumerate(["WANT TO BE", "THE NEXT ONE?"]):
    d.text((W // 2, 680 + i * 130), ln, font=heavy(116), fill=WHITE, anchor="mm")
d.text((W // 2, 930), "15 minute call. By phone.", font=demi(48), fill="#bdbdbd", anchor="mm")
bw, bh, y = 900, 130, 1060
d.rounded_rectangle([(W - bw) // 2, y, (W + bw) // 2, y + bh], 16, fill=WHITE)
d.text((W // 2, y + bh // 2), "TAP THE LINK IN MY BIO", font=heavy(46), fill=BLACK, anchor="mm")
save(im)

# 4) highlight cover (IG shows only the middle circle)
im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
d.ellipse([W // 2 - 330, H // 2 - 330, W // 2 + 330, H // 2 + 330], fill=WHITE)
d.text((W // 2, H // 2 - 70), "IS HE", font=heavy(150), fill=BLACK, anchor="mm")
d.text((W // 2, H // 2 + 85), "GOOD?", font=heavy(150), fill=BLACK, anchor="mm")
im.save(OUT / "00-cover.png", optimize=True)
print("made", n, "slides + cover in", OUT)
