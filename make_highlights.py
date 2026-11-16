# Makes 1080x1920 IG story images from messages.json. Run: python3 site/make_highlights.py
import json, pathlib, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "highlight"
W, H = 1080, 1920
PAPER, INK, CLAY, BLUSH, CARD = "#f3ebe1", "#1b1410", "#c2643a", "#f2c9b4", "#fffaf4"
F = "/System/Library/Fonts/Supplemental/"
impact = lambda s: ImageFont.truetype(F + "Impact.ttf", s)
serif = lambda s: ImageFont.truetype(F + "Georgia Bold Italic.ttf", s)
quote = lambda s: ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", s, index=2)
sans = lambda s: ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", s, index=2)  # demi bold

data = json.loads((ROOT / "messages.json").read_text())

def base():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    # header (kept below IG's top bar)
    d.text((W // 2, 250), "Is He Good?", font=serif(96), fill=INK, anchor="mm")
    d.line([(W // 2 - 60, 318), (W // 2 + 60, 318)], fill=CLAY, width=6)
    return im, d

def footer(d):
    # pill button, kept above IG's reply bar
    bw, bh, y = 760, 120, 1600
    d.rounded_rectangle([(W - bw) // 2, y + 10, (W + bw) // 2, y + bh + 10], 60, fill=CLAY)
    d.rounded_rectangle([(W - bw) // 2, y, (W + bw) // 2, y + bh], 60, fill=INK)
    d.text((W // 2, y + bh // 2), "BOOK A CALL  ·  LINK IN BIO", font=sans(40), fill=PAPER, anchor="mm")

def stamp(im, text, cy, size=120, rot=-3):
    f = impact(size)
    tw = int(f.getlength(text)); pad = 34
    s = Image.new("RGBA", (tw + pad * 2 + 16, size + 60 + 16), (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    sd.rounded_rectangle([12, 12, tw + pad * 2 + 12, size + 56 + 12], 22, fill=INK)
    sd.rounded_rectangle([0, 0, tw + pad * 2, size + 56], 22, fill=CLAY, outline=INK, width=5)
    sd.text((pad + tw // 2, (size + 56) // 2), text, font=f, fill="white", anchor="mm")
    s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
    im.paste(s, ((W - s.width) // 2, cy - s.height // 2), s)

def fit(img, maxw, maxh):
    r = min(maxw / img.width, maxh / img.height)
    return img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)

def card(im, shot, top, bottom, maxw=920):
    shot = fit(shot, maxw, bottom - top - 60)
    pad = 26
    cw, ch = shot.width + pad * 2, shot.height + pad * 2
    x = (W - cw) // 2; y = top + (bottom - top - ch) // 2
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x, y + 10, x + cw, y + ch + 10], 34, fill=INK)
    d.rounded_rectangle([x, y, x + cw, y + ch], 34, fill=CARD, outline=INK, width=4)
    m = Image.new("L", shot.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, *shot.size], 18, fill=255)
    im.paste(shot, (x + pad, y + pad), m)

def label(t): return t.replace("→", "TO").upper()

n = 0
def save(im):
    global n; n += 1
    im.save(OUT / f"{n:02d}.png", optimize=True)

# 1) photo stories
for p in data["photos"]:
    im, d = base()
    card(im, Image.open(ROOT / p["img"]).convert("RGB"), 420, 1340, maxw=960)
    stamp(im, label(p["tag"]), 450, size=110)
    # quote, wrapped
    f = quote(52); words = p["quote"].split(); lines = [""]
    for w in words:
        t = (lines[-1] + " " + w).strip()
        if f.getlength("“" + t + "”") > 900: lines.append(w)
        else: lines[-1] = t
    lines[0] = "“" + lines[0]; lines[-1] += "”"
    y = 1330 + (260 - len(lines) * 64) // 2 + 32
    for ln in lines:
        d.text((W // 2, y), ln, font=f, fill=INK, anchor="mm"); y += 64
    footer(d); save(im)

# 2) every message: big readable words on top, the real screenshot below as proof
EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+")
def wrap(text, f, maxw):
    lines = [""]
    for w in text.split():
        t = (lines[-1] + " " + w).strip()
        if f.getlength(t) > maxw and lines[-1]: lines.append(w)
        else: lines[-1] = t
    return lines
for m in data["messages"]:
    im, d = base()
    stamp(im, label(m["tag"]), 450)
    text = EMOJI.sub("", m["text"]).strip()
    for size in (64, 58, 52, 46, 42, 38):
        f = quote(size); lines = wrap("\u201c" + text + "\u201d", f, 930)
        if len(lines) * size * 1.3 <= 560: break
    lh = int(size * 1.3); y = 590
    for ln in lines:
        d.text((W // 2, y), ln, font=f, fill=INK, anchor="ma"); y += lh
    who = ("— " + m["name"]) if m["name"] else ""
    if who: d.text((W // 2, y + 18), who, font=sans(34), fill=CLAY, anchor="ma"); y += 70
    card(im, Image.open(ROOT / "img/msg" / (m["img"] + ".jpg")).convert("RGB"), max(y + 20, 1000), 1560, maxw=860)
    footer(d); save(im)

# 3) last slide: the ask
im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im)
d.text((W // 2, 620), "Want to be", font=serif(110), fill=PAPER, anchor="mm")
d.text((W // 2, 750), "the next one?", font=serif(110), fill=BLUSH, anchor="mm")
d.text((W // 2, 930), "15 min strategy call.", font=sans(52), fill=PAPER, anchor="mm")
bw, bh, y = 760, 130, 1080
d.rounded_rectangle([(W - bw) // 2, y + 10, (W + bw) // 2, y + bh + 10], 65, fill=PAPER)
d.rounded_rectangle([(W - bw) // 2, y, (W + bw) // 2, y + bh], 65, fill=CLAY)
d.text((W // 2, y + bh // 2), "TAP THE LINK IN MY BIO", font=sans(44), fill="white", anchor="mm")
save(im)

# 4) highlight cover (IG shows the middle circle)
im = Image.new("RGB", (W, H), CLAY); d = ImageDraw.Draw(im)
d.ellipse([W // 2 - 330, H // 2 - 330, W // 2 + 330, H // 2 + 330], fill=PAPER)
d.text((W // 2, H // 2 - 40), "IS HE", font=impact(150), fill=INK, anchor="mm")
d.text((W // 2, H // 2 + 110), "GOOD?", font=impact(150), fill=CLAY, anchor="mm")
im.save(OUT / "00-cover.png", optimize=True)
print("made", n, "slides + cover in", OUT)
