import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
MAX = P.get('max', 2000); GR = 54/math.log2(MAX); GV = P.get('g', 0.45); HUE0 = P.get('hue', 0.0)
from PIL import Image, ImageDraw
CX, CY, R = AX, 740, 265
x = np.array([CX]); y = np.array([CY-150]); vx = np.array([5.0]); vy = np.array([0.0])
hue = np.array([HUE0]); F1, F2 = font(54), font(40)
pent = [261.6, 293.7, 329.6, 392, 440]
while o.t < 62:
    t = o.t; n = len(x)
    vy = vy + GV; x = x + vx; y = y + vy
    dx, dy = x-CX, y-CY; d = np.hypot(dx, dy); r = 9 if n < 200 else (6 if n < 800 else 4)
    hit = d > R - r
    if hit.any():
        nx, ny = dx[hit]/d[hit], dy[hit]/d[hit]; vn = vx[hit]*nx + vy[hit]*ny
        vx[hit] -= 2*vn*nx; vy[hit] -= 2*vn*ny
        x[hit] = CX + nx*(R-r-1); y[hit] = CY + ny*(R-r-1)
        target = min(MAX, 2**(t/GR))
        k = int(min(hit.sum(), max(0, target - n)))
        if k:
            idx = np.where(hit)[0][:k]
            x = np.r_[x, x[idx]]; y = np.r_[y, y[idx]]
            vx = np.r_[vx, vx[idx]*rng.uniform(.8, 1.2, k) + rng.uniform(-2, 2, k)]
            vy = np.r_[vy, vy[idx]*rng.uniform(.8, 1.2, k)]; hue = np.r_[hue, rng.uniform(0, 1, k)]
        if n < 300 or o.n % 2 == 0:
            o.sound(pent[o.n % 5]*(2 if n > 100 else 1), vol=0.25 if n < 100 else 0.12)
    sp = np.hypot(vx, vy); m = sp > 16; vx[m] *= 16/sp[m]; vy[m] *= 16/sp[m]
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    dr.ellipse([CX-R-6, CY-R-6, CX+R+6, CY+R+6], outline=hsv(HUE0+t*0.05, .7), width=6)
    for i in range(len(x)):
        dr.ellipse([x[i]-r, y[i]-r, x[i]+r, y[i]+r], fill=hsv(hue[i]))
    nb = len(x)
    header(img, P.get("title", "EVERY BOUNCE = +1 BALL"), f"{nb} ball" + ("s" if nb > 1 else ""))
    if nb >= MAX: cta(img, "MAXIMUM CHAOS!", col=RED)
    else: cta(img, "How many at the end? 👇"[:-2])
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
o.close()
