import os, math
from PIL import Image, ImageDraw, ImageFont
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
FD = A + "/"
def lilita(s): return ImageFont.truetype(FD+"LilitaOne-Regular.ttf", s)
def fredoka(s):
    f = ImageFont.truetype(FD+"Fredoka.ttf", s); f.set_variation_by_axes([600, 100]); return f
YEL, BLUE, INK = (255, 205, 60), (60, 170, 255), (20, 15, 35)
W, H = 720, 1280
BG, RED = (14, 16, 30), (255, 90, 110)
AX = 340  # action centre x (shifted left of TikTok right rail)
_mini = Image.open(os.path.join(A, "tamko_mini_sticker.png")).convert("RGBA")
_full = Image.open(os.path.join(A, "tamko_B.png")).convert("RGBA")
_wm = _mini.resize((54, 54)); _wm.putalpha(_wm.getchannel("A").point(lambda a: a*0.55))

def out(d, xy, t, f, fill, anc="mm", sw=7):
    d.text(xy, t, font=f, fill=fill, anchor=anc, stroke_width=sw, stroke_fill=INK)

def fit(t, maxw, size, fn=lilita):
    f = fn(size)
    while f.getlength(t) > maxw and size > 20: size -= 2; f = fn(size)
    return f

def header(img, title, sub=None, y=250):
    d = ImageDraw.Draw(img)
    out(d, (AX, y), title, fit(title, 560, 76), YEL)
    if sub: out(d, (AX, y+70), sub, fit(sub, 540, 40, fredoka), "white", sw=5)

def cta(img, text, y=1075, col=BLUE):
    d = ImageDraw.Draw(img); out(d, (AX, y), text, fit(text, 540, 42), col, sw=6)

def watermark(img):
    if img.mode != "RGBA":
        base = img.convert("RGBA"); base.alpha_composite(_wm, (34, 560))
        d = ImageDraw.Draw(base); d.text((61, 624), "@tamkoplay", font=fredoka(16), fill=(255, 255, 255, 140), anchor="mm")
        img.paste(base.convert(img.mode))
    return img

def outro_frames(fps=30, secs=2.5, bg=(14, 16, 30)):
    fr = []
    for i in range(int(fps*secs)):
        t = i/fps; im = Image.new("RGB", (W, H), bg).convert("RGBA")
        s = int(360 * min(1, t*3)**0.5) or 1; bounce = abs(math.sin(t*5))*30*max(0, 1-t/1.5)
        m = _full.resize((s, s)); mask = Image.new("L", (s, s), 0); ImageDraw.Draw(mask).ellipse([0, 0, s, s], fill=255)
        im.paste(m, (AX-s//2, int(560-s//2-bounce)), mask)
        d = ImageDraw.Draw(im)
        if t > 0.4:
            out(d, (AX, 820), "Follow for more!", lilita(64), YEL)
            out(d, (AX, 900), "@tamkoplay", fredoka(44), "white", sw=5)
        fr.append(im.convert("RGB"))
    return fr
