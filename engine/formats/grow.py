import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
CX, CY, R = AX, 720, 255; r = 8.0; T_FILL = P.get("tfill", 54)
x, y, vx, vy = CX + rng.uniform(-40, 40), CY - 120, rng.uniform(3, 5)*rng.choice([-1, 1]), 0.0
G = P.get("g", 0.5); hue = P.get("hue", rng.random()); bounces = 0; done_t = None; ring = []; trail = []
while True:
    t = o.t
    if done_t and t > max(done_t+4, 61): break
    if t > 80: break
    if not done_t:
        for _ in range(3):
            vy += G/3; x += vx/3; y += vy/3
            dx, dy = x-CX, y-CY; d = math.hypot(dx, dy)
            if d + r > R:
                nx, ny = dx/d, dy/d; vn = vx*nx + vy*ny
                if vn > 0:
                    vx -= 2*vn*nx; vy -= 2*vn*ny; bounces += 1
                    sp = math.hypot(vx, vy); m = max(7, sp)
                    vx *= m/sp; vy *= m/sp
                    target = 8 + (R-8)*min(1, (t/T_FILL))**1.6
                    r = min(R, max(r + 0.6, target)); hue += 0.03
                    ring.append([x+nx*r, y+ny*r, 1.0])
                    o.sound(880*(8/r)**0.35, .15, .3)
                x, y = CX + nx*(R-r-0.5), CY + ny*(R-r-0.5)
        if r >= R - 3:
            done_t = t; r = R; x, y = CX, CY; fanfare(o, t); o.sound(60, 1.2, .5, 2, "square")
    trail.append((x, y, r)); trail = trail[-8:]
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    dr.ellipse([CX-R-8, CY-R-8, CX+R+8, CY+R+8], fill=(22, 26, 46), outline=(255, 255, 255), width=6)
    for i, (tx, ty, tr) in enumerate(trail[:-1]):
        k = (i+1)/len(trail)*.4
        dr.ellipse([tx-tr, ty-tr, tx+tr, ty+tr], fill=tuple(int(v*k) for v in hsv(hue, .7, 1)))
    dr.ellipse([x-r, y-r, x+r, y+r], fill=hsv(hue, .7, 1), outline="white", width=3)
    if r > 30:
        e = r/6; dr.ellipse([x-2.2*e, y-1.5*e, x-.8*e, y+.3*e], fill="white"); dr.ellipse([x+.8*e, y-1.5*e, x+2.2*e, y+.3*e], fill="white")
        dr.ellipse([x-1.8*e, y-1*e, x-1.1*e, y-.1*e], fill="black"); dr.ellipse([x+1.1*e, y-1*e, x+1.8*e, y-.1*e], fill="black")
    for rg in ring:
        rg[2] -= .06
        if rg[2] > 0: rr = 30*(1-rg[2]); dr.ellipse([rg[0]-rr, rg[1]-rr, rg[0]+rr, rg[1]+rr], outline=YEL, width=3)
    ring = [g for g in ring if g[2] > 0]
    pct = int(100*(r*r)/(R*R))
    header(img, P.get("title", "IT GROWS EVERY BOUNCE"), f"Size: {pct}%   •   Bounces: {bounces}")
    cta(img, "IT FILLED THE CIRCLE!" if done_t else "How many bounces to fill it?", col=YEL if done_t else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("bounces", bounces, o.t)
o.close()
