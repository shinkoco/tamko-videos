import os, math, json
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
HX = 360  # header centre x (title, subtitle, header lines): true screen centre (26/11/2026)
_mini = Image.open(os.path.join(A, "tamko_mini_sticker.png")).convert("RGBA")
_full = Image.open(os.path.join(A, "tamko_B.png")).convert("RGBA")
_wm = None  # built after tamko_sprite is defined

def out(d, xy, t, f, fill, anc="mm", sw=7):
    d.text(xy, t, font=f, fill=fill, anchor=anc, stroke_width=sw, stroke_fill=INK)

def fit(t, maxw, size, fn=lilita):
    f = fn(size)
    while f.getlength(t) > maxw and size > 20: size -= 2; f = fn(size)
    return f

_gl = {}
def glossy_layer(text, size, maxw=600):
    key = (text, size, maxw)
    if key in _gl: return _gl[key]
    from PIL import ImageFilter
    while lilita(size).getlength(text) + size*.3 > maxw and size > 24: size -= 2
    f = lilita(size); w, h = int(maxw + size), int(size*2.2); x, y = w/2, h/2
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(L)
    gd.text((x, y), text, font=f, anchor="mm", fill=(80, 210, 255, 200), stroke_width=int(size*.2), stroke_fill=(80, 210, 255, 200))
    L = L.filter(ImageFilter.GaussianBlur(size*.22)); d = ImageDraw.Draw(L)
    d.text((x+size*.05, y+size*.09), text, font=f, anchor="mm", fill=(10, 20, 45), stroke_width=int(size*.14), stroke_fill=(255, 196, 40))
    d.text((x, y), text, font=f, anchor="mm", fill=(60, 200, 245), stroke_width=int(size*.09), stroke_fill=(10, 20, 45))
    hl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); hd = ImageDraw.Draw(hl); hd.text((x, y), text, font=f, anchor="mm", fill=(200, 243, 255))
    bb = hd.textbbox((x, y), text, font=f, anchor="mm"); m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rectangle([0, 0, w, (bb[1]+bb[3])/2], fill=255)
    hl.putalpha(Image.composite(hl.getchannel("A"), m, m)); L.alpha_composite(hl)
    _gl[key] = L; return L

def header(img, title, sub=None, y=250):
    L = glossy_layer(title, 72, 520)  # 520: stays inside TikTok's side crop on tall phones
    if img.mode == "RGBA": img.alpha_composite(L, (int(HX - L.width/2), int(y - L.height/2)))
    else: img.paste(L, (int(HX - L.width/2), int(y - L.height/2)), L)
    d = ImageDraw.Draw(img)
    if sub: out(d, (HX, y+70), sub, fit(sub, 480, 40, fredoka), "white", sw=5)

_tick = [0]
def tamko_sprite(img, cx, cy, s, phase=0.0):
    """Tamko mascot, 2026-11 charter: flat yellow ball, navy offset shadow, white headband with red dot, waving tails."""
    d = ImageDraw.Draw(img); r = s/2; DEEP = (10, 20, 45)
    d.ellipse([cx-r+r*.12, cy-r+r*.16, cx+r+r*.12, cy+r+r*.16], fill=DEEP, outline=(255, 196, 40), width=max(1, int(s/40)))
    hb = cy - r*.45
    for k in (0, 1):
        a = -.45 + .5*k + math.sin(phase*6 + k*1.3)*.3; L = r*.8; b0 = (cx + r*.85, hb)
        tip = (b0[0] + L*math.cos(a), b0[1] + L*math.sin(a)); m = (b0[0] + L*.5*math.cos(a-.4), b0[1] + L*.5*math.sin(a-.4))
        d.polygon([b0, m, tip, (b0[0], b0[1] + r*.2)], fill="white", outline=DEEP)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(250, 200, 50))
    d.ellipse([cx-r*.62, cy-r*.82, cx-r*.2, cy-r*.55], fill=(255, 235, 150))
    d.rectangle([cx-r*.99, hb-r*.15, cx+r*.99, hb+r*.15], fill="white", outline=DEEP, width=max(1, int(s/60)))
    d.ellipse([cx-r*.13, hb-r*.13, cx+r*.13, hb+r*.13], fill=(220, 30, 40))
    for ex in (-.33, .33):
        x, y = cx + ex*r, cy + r*.08; w, h = .14*r, .19*r
        d.ellipse([x-w, y-h, x+w, y+h], fill=(15, 12, 20)); d.ellipse([x-w*.55, y-h*.7, x+w*.05, y-h*.1], fill="white")
    for ex in (-.6, .6):
        d.ellipse([cx+ex*r-.16*r, cy+.33*r-.08*r, cx+ex*r+.16*r, cy+.33*r+.08*r], fill=(245, 120, 110))
    d.chord([cx-.2*r, cy+.22*r, cx+.2*r, cy+.55*r], 0, 180, fill=(150, 30, 35), outline=DEEP)

_cta = [None, -1]  # comment prompt text, frame it was set
def cta(img, text, y=388, col=None, mascot=True):
    col = col or BLUE; _tick[0] += 1
    # 2026-11-24: the opening prompt (first CTA of the video) becomes a TikTok-style comment pop-up (option A);
    # later CTAs (results such as "#3 WINS!") are still drawn in the header.
    if "  •  " in text:  # "8 CARS LEFT  •  Pick your car!": live info stays, the prompt pops up
        info, text = text.split("  •  ", 1); out(ImageDraw.Draw(img), (HX, y), info, fit(info, 540, 42), col, sw=6)
        if _cta[0] is None: _cta[0] = text
        if text == _cta[0]: _cta[1] = _wf[0]
        return
    if _cta[0] is None: _cta[0] = text
    if text == _cta[0]: _cta[1] = _wf[0]; return
    f = fit(text, 480 if mascot else 540, 42); d = ImageDraw.Draw(img)
    if not mascot:
        out(d, (HX, y), text, f, col, sw=6); return
    tw = f.getlength(text); s = 52; gap = 10; x0 = HX - (tw + gap + s)/2
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

_HOOKS = ["WAIT FOR THE END!", "ONLY 1% GUESS RIGHT", "PICK ONE NOW!", "DON'T SCROLL!", "THE ENDING IS CRAZY", "GUESS BEFORE IT ENDS!"]
try:
    _seed = json.loads(os.environ.get("TP", "{}")).get("seed", 0)
except Exception:
    _seed = 0
HOOK = _HOOKS[_seed % len(_HOOKS)]
_wf = [0]
def hook(img):
    """Big pulsing hook text during the first 3 seconds (retention)."""
    f = _wf[0]
    if f >= 90: return
    k = f/90; pop = 1 + 0.12*math.sin(f/3) if f > 6 else 0.4 + 0.6*f/6
    fnt = fit(HOOK, 600, int(64*pop)); d = ImageDraw.Draw(img)
    pad = 18; tw = fnt.getlength(HOOK); y = 560
    alpha_ok = f < 80 or (f//3) % 2 == 0  # quick blink before vanishing
    if alpha_ok:
        d.rounded_rectangle([AX-tw/2-pad, y-46, AX+tw/2+pad, y+46], 22, fill=RED, outline="white", width=4)
        out(d, (AX, y), HOOK, fnt, "white", sw=4)

def _night():
    import random as R
    rr = R.Random(7); im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    c0, c1 = (6, 10, 26), (16, 34, 70)
    for y in range(H):
        k = y/H; d.line([(0, y), (W, y)], fill=tuple(int(c0[i]+(c1[i]-c0[i])*k) for i in range(3)))
    for _ in range(170):
        x, y, z = rr.uniform(0, W), rr.uniform(0, H), rr.choice([1, 1, 1.5, 2])
        d.ellipse([x-z, y-z, x+z, y+z], fill=(255, 196, 40) if rr.random() < .5 else (210, 225, 255))
    def cloud(cx, cy, sz, col, dk):
        for dx, dy, q in [(-.5, .1, .38), (0, -.15, .5), (.5, .1, .38), (0, .2, .4)]:
            X, Y, Q = cx+dx*sz, cy+dy*sz, q*sz; d.ellipse([X-Q, Y-Q, X+Q, Y+Q], fill=col, outline=dk, width=2)
        for dx in (-.25, .25):
            X, Y, Q = cx+dx*sz, cy-.05*sz, .17*sz; d.arc([X-Q, Y-Q, X+Q, Y+Q], 180, 470, fill=dk, width=3)
    cloud(-5, 30, 70, (230, 175, 40), (170, 120, 20)); cloud(735, 470, 60, (230, 175, 40), (170, 120, 20))
    cloud(700, 25, 55, (50, 170, 220), (20, 100, 150))
    import numpy as _np
    return _np.asarray(im)
_NIGHT = [None]
def brand_bg(img):
    """Swap the flat BG colour for the starry night backdrop (charter 2026-11)."""
    import numpy as _np
    if _NIGHT[0] is None: _NIGHT[0] = _night()
    if img.mode != "RGB": return img
    a = _np.array(img); m = (a[:, :, 0] == BG[0]) & (a[:, :, 1] == BG[1]) & (a[:, :, 2] == BG[2])
    _np.copyto(a, _NIGHT[0], where=m[:, :, None]); img.paste(Image.frombuffer("RGB", (W, H), a.tobytes())); return img

SHIFT = 55  # charter v2: header block moved up under the TikTok top bar (option 1, 2026-11-19)
def lift_header(img):
    # Only lift when the gameplay does not reach into the header band (otherwise we would cut a shape in two)
    import numpy as _np
    band = _np.asarray(img.convert("RGB"))[440:470]
    if not _np.all(band == _np.array(BG, _np.uint8)): return img
    blk = img.crop((0, 190, W, 466)); img.paste(blk, (0, 190 - SHIFT))
    ImageDraw.Draw(img).rectangle([0, 466 - SHIFT, W, 465], fill=BG)
    return img

def close_gap(img):
    # the old CTA line (y~388) is gone: pull the format's extra line (y~440) up under the subtitle
    import numpy as _np
    a = _np.asarray(img.convert("RGB")); bg = _np.array(BG, _np.uint8)
    if not _np.all(a[360:412] == bg): return img
    rowbg = _np.all(a == bg, axis=(1, 2))
    end = next((y for y in range(420, 476) if rowbg[y]), None)
    if end is None: return img
    blk = img.crop((0, 412, W, end)); img.paste(blk, (0, 367))
    ImageDraw.Draw(img).rectangle([0, 367 + end - 412, W, end - 1], fill=BG); return img

POP_WIN = ((3.0, 8.0), (30.0, 35.0))  # seconds in the 60 s version (= 1.5-4 s and 15-17.5 s in the 2x short)
def comment_pop(img):
    if not _cta[0] or _wf[0] - _cta[1] > 2: return img
    t = _wf[0]/FPS_GUESS; w = [a for a in POP_WIN if a[0] <= t <= a[1]]
    if not w: return img
    k = min(1, (t - w[0][0])/.18, (w[0][1] - t)/.18); k = k*(1.15 - .15*k)  # pop in / out
    card = Image.new("RGBA", (620, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((2, 2, 617, 147), 28, fill=(255, 255, 255), outline=(20, 20, 30), width=4)
    tamko_sprite(card, 62, 75, 68, t)
    d.text((120, 22), "@tamkoplay  asks:", font=fredoka(26), fill=(120, 120, 130))
    f = fit(_cta[0], 470, 40); d.text((120, 62), _cta[0], font=f, fill=(20, 20, 30))
    d.text((120, 108), "Reply below", font=fredoka(22), fill=(150, 150, 160))
    PS, PY = .78, 830  # 26/11/2026 option C: smaller, just above TikTok's caption zone
    sw, sh = max(1, int(620*k*PS)), max(1, int(150*k*PS)); card = card.resize((sw, sh))
    base = img.convert("RGBA"); base.alpha_composite(card, (int(HX - sw/2), int(PY - sh/2)))
    ay = PY + sh/2 + 8; dr = ImageDraw.Draw(base); dr.polygon([(HX-14, ay), (HX+14, ay), (HX, ay+18)], fill="white") if k > .9 else None
    img.paste(base.convert(img.mode)); return img

def watermark(img):
    _wf[0] += 1
    close_gap(img)
    lift_header(img)
    brand_bg(img)
    hook(img)
    season(img)
    comment_pop(img)
    if img.mode != "RGBA":
        global _wm
        if _wm is None:
            _wm = Image.new("RGBA", (60, 60), (0, 0, 0, 0)); tamko_sprite(_wm, 27, 28, 46)
            _wm.putalpha(_wm.getchannel("A").point(lambda a: a*0.6))
        base = img.convert("RGBA"); base.alpha_composite(_wm, (64, 560))
        d = ImageDraw.Draw(base); d.text((91, 624), "@tamkoplay", font=fredoka(16), fill=(255, 255, 255, 140), anchor="mm")
        img.paste(base.convert(img.mode))
    return img

def outro_frames(fps=30, secs=2.5, bg=None):
    if _NIGHT[0] is None: _NIGHT[0] = _night()
    base = Image.fromarray(_NIGHT[0]).convert("RGBA"); fr = []
    logo = glossy_layer("TAMKO", 140, 560)
    for i in range(int(fps*secs)):
        t = i/fps; im = base.copy()
        s = int(300 * min(1, t*3)**0.5) or 1; bounce = abs(math.sin(t*5))*30*max(0, 1-t/1.5)
        tamko_sprite(im, AX, 470 - bounce, s, t)
        if t > 0.25: im.alpha_composite(logo, (int(AX - logo.width/2), int(760 - logo.height/2)))
        d = ImageDraw.Draw(im)
        if t > 0.5:
            out(d, (AX, 900), "Follow for a new game every day!", fit("Follow for a new game every day!", 620, 50), YEL, sw=6)
            out(d, (AX, 970), "@tamkoplay", fredoka(40), "white", sw=5)
        fr.append(im.convert("RGB"))
    return fr
