"""Hydraulic press: every slam splits every ball in two."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
X0, X1, FLOOR, TOP = 60, 620, 975, 480
SLAMS = P.get("slams", 10); PERIOD = 50/SLAMS; HUE0 = P.get("hue", rng.random())
x = np.array([float(AX)]); y = np.array([FLOOR-110.0]); vx = np.array([0.0]); vy = np.array([0.0]); r = np.array([110.0]); hue = np.array([HUE0])
slam = 0; plate = TOP; done_t = None; flash = 0
while True:
    t = o.t
    if done_t and t > max(done_t+4, 61): break
    phase = (t-3) % PERIOD if t > 3 else -1
    if slam < SLAMS and phase >= 0:
        k = phase/PERIOD
        plate = TOP + (FLOOR-TOP-30)*(k/0.12)**2 if k < 0.12 else (FLOOR-30 if k < 0.2 else FLOOR-30 - (FLOOR-30-TOP)*min(1, (k-.2)/.3))
        if k >= 0.12 and slam < int((t-3)/PERIOD) + 1:  # impact (once per period)
            slam += 1; flash = 1.0; o.sound(60, .6, .7, 5, "square"); o.sound(0, .3, .5, 10, "noise")
            n = len(x); f = 0.8
            x = np.r_[x-r*.3, x+r*.3]; y = np.r_[y, y]; r = np.r_[r*f, r*f]
            vx = np.r_[-np.abs(rng.normal(3, 1.5, n)), np.abs(rng.normal(3, 1.5, n))]; vy = np.r_[rng.uniform(-14, -6, n), rng.uniform(-14, -6, n)]
            hue = np.r_[hue, hue+0.04]
            if slam == SLAMS: done_t = t + 1.5; fanfare(o, t+1.5)
    else:
        plate = max(TOP, plate - 6)
    vy += .6; x += vx; y += vy; vx *= .99
    m = y + r > FLOOR; y[m] = FLOOR - r[m]; vy[m] *= -.35; vx[m] *= .9
    m = x - r < X0; x[m] = X0 + r[m]; vx[m] = np.abs(vx[m])*.6
    m = x + r > X1; x[m] = X1 - r[m]; vx[m] = -np.abs(vx[m])*.6
    m = y - r < plate; y[m] = plate + r[m]; vy[m] = np.maximum(vy[m], 0)
    y += rng.normal(0, .4, len(y))
    for _ in range(4 if len(x) <= 300 else 2):  # ball-ball separation so they pile up
        dx = x[:, None]-x[None, :]; dy = y[:, None]-y[None, :]; d = np.hypot(dx, dy)+1e-6; ov = (r[:, None]+r[None, :]) - d
        np.fill_diagonal(ov, 0); ov = np.clip(ov, 0, None)
        cnt = (ov > 0).sum(1) + 1
        x += (dx/d*ov).sum(1)/cnt*.9; y += (dy/d*ov).sum(1)/cnt*.9 - (ov.sum(1) > 0)*0.0
        m = y + r > FLOOR; y[m] = FLOOR - r[m]; m = x - r < X0; x[m] = X0 + r[m]; m = x + r > X1; x[m] = X1 - r[m]
        m = y - r < plate; y[m] = plate + r[m]
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    dr.rectangle([X0-10, TOP-20, X0, FLOOR+12], fill=(90, 95, 110)); dr.rectangle([X1, TOP-20, X1+10, FLOOR+12], fill=(90, 95, 110))
    dr.rectangle([X0-10, FLOOR, X1+10, FLOOR+12], fill=(90, 95, 110))
    for i in range(len(x)):
        dr.ellipse([x[i]-r[i], y[i]-r[i], x[i]+r[i], y[i]+r[i]], fill=hsv(hue[i], .7, 1), outline=INK if r[i] > 6 else None)
    dr.rectangle([X0+4, plate-26, X1-4, plate], fill=(200, 205, 215), outline=INK, width=3)
    dr.rectangle([AX-30, TOP-120, AX+30, plate-26], fill=(150, 155, 170), outline=INK, width=3)
    if flash > 0: dr.rectangle([X0, plate, X1, plate+8], fill=YEL); flash -= .1
    header(img, P.get("title", f"1 BALL VS {SLAMS} SLAMS"), f"Slams: {slam}/{SLAMS}  •  Balls: {len(x)}")
    cta(img, f"{len(x)} BALLS!" if done_t and t >= done_t else "How many balls at the end?", col=YEL if done_t and t >= done_t else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("press", len(x), o.t)
o.close()
