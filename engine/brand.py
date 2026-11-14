import os, math
from PIL import Image, ImageDraw, ImageFont
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
FD = A + "/"
def lilita(s): return ImageFont.truetype(FD+"LilitaOne-Regular.ttf", s)
def fredoka(s):
    f = ImageFont.truetype(FD+"Fredoka.ttf", s); f.set_variation_by_axes([600, 100]); return f
YEL, BLUE, INK = (255, 205, 60), (60, 170, 255), (20, 15, 35)

W, H = 720, 1280
FPS_GUESS = 30
BG, RED = (14, 16, 30), (255, 90, 110)
import datetime, random as _r
def _auto_theme():
    d = datetime.date.today()
    if d.month == 12 and d.day <= 26: return "christmas"
    return "default"
THEME = os.environ.get("TAMKO_THEME") or _auto_theme()
if THEME == "christmas":
    BG = (14, 24, 52)
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

_tick = [0]
def tamko_sprite(img, cx, cy, s, phase=0.0):
    """Draw the Tamko mascot (champion headband with tails waving in the wind)."""
    d = ImageDraw.Draw(img); r = s/2
    w1 = math.sin(phase*6.0)*0.25; w2 = math.sin(phase*6.0 + 1.3)*0.25
    hb_y = cy - r*0.42
    for k, w in ((0, w1), (1, w2)):  # headband tails, flapping
        base = (cx + r*0.88, hb_y + (k*0.12 - 0.04)*r)
        ang = (-0.35 + 0.55*k) + w*1.4; L = r*0.95
        tip = (base[0] + L*math.cos(ang), base[1] + L*math.sin(ang))
        mid = (base[0] + L*0.55*math.cos(ang-0.35), base[1] + L*0.55*math.sin(ang-0.35))
        d.polygon([base, mid, tip, (base[0], base[1] + r*0.16)], fill="white", outline=INK)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 205, 60), outline=INK, width=max(2, int(s/22)))
    d.ellipse([cx-r*.6, cy-r*.75, cx-r*.25, cy-r*.45], fill=(255, 240, 170))
    d.polygon([(cx-r*.93, cy-r*.55), (cx+r*.93, cy-r*.55), (cx+r*.97, cy-r*.3), (cx-r*.97, cy-r*.3)], fill="white", outline=INK)
    d.ellipse([cx-r*.13, hb_y-r*.13, cx+r*.13, hb_y+r*.13], fill=(230, 40, 60))
    for ex in (-.32, .32):
        x, y = cx+ex*r, cy+r*.05; w, h = .15*r, .2*r
        d.ellipse([x-w, y-h, x+w, y+h], fill=(30, 25, 40)); d.ellipse([x-w*.5, y-h*.6, x, y-h*.1], fill="white")
    for ex in (-.55, .55):
        d.ellipse([cx+ex*r-.13*r, cy+.3*r-.07*r, cx+ex*r+.13*r, cy+.3*r+.07*r], fill=(255, 140, 90))
    d.chord([cx-.2*r, cy+.15*r, cx+.2*r, cy+.48*r], 0, 180, fill=(120, 30, 40), outline=INK)

def cta(img, text, y=388, col=None, mascot=True):
    col = col or BLUE; _tick[0] += 1
    f = fit(text, 480 if mascot else 540, 42); d = ImageDraw.Draw(img)
    if not mascot:
        out(d, (AX, y), text, f, col, sw=6); return
    tw = f.getlength(text); s = 52; gap = 10; x0 = AX - (tw + gap + s)/2
    out(d, (x0 + tw/2, y), text, f, col, sw=6)
    bob = math.sin(_tick[0]/5)*3
    tamko_sprite(img, x0 + tw + gap + s/2, y + bob, s, _tick[0]/FPS_GUESS)

if THEME == "christmas":
    YEL, BLUE = (255, 215, 90), (140, 210, 255)
_snow = [[_r.uniform(0, 720), _r.uniform(0, 1280), _r.uniform(1.5, 4.5), _r.uniform(0, 6.28)] for _ in range(110)]
_frame = [0]
def season(img):
    if THEME != "christmas": return img
    _frame[0] += 1; f = _frame[0]
    d = ImageDraw.Draw(img)
    for fl in _snow:
        fl[1] += fl[2]*0.7; fl[0] += math.sin(f/30 + fl[3])*0.6
        if fl[1] > 1290: fl[1] = -10; fl[0] = _r.uniform(0, 720)
        d.ellipse([fl[0]-fl[2], fl[1]-fl[2], fl[0]+fl[2], fl[1]+fl[2]], fill=(255, 255, 255))
    cols = [(255, 60, 60), (255, 210, 60), (80, 200, 255), (80, 230, 120)]
    pts = [(x, 150 + 14*math.sin(x/55)) for x in range(-20, 760, 10)]
    d.line(pts, fill=(30, 70, 40), width=4)
    for i, x in enumerate(range(0, 720, 45)):
        y = 150 + 14*math.sin(x/55) + 8; on = (i + f//8) % 2 == 0
        c = cols[i % 4] if on else tuple(v//3 for v in cols[i % 4])
        d.ellipse([x-8, y-6, x+8, y+12], fill=c)
    return img

def watermark(img):
    season(img)
    if img.mode != "RGBA":
        base = img.convert("RGBA"); base.alpha_composite(_wm, (64, 560))
        d = ImageDraw.Draw(base); d.text((91, 624), "@tamkoplay", font=fredoka(16), fill=(255, 255, 255, 140), anchor="mm")
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
