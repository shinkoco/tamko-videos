import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
CX, CY, R = AX, 720, 250; BGC = np.array(BG, float)
COL = np.array(hsv(P.get("hue", rng.random()), .6, 1), float)
END = P.get("tend", 54); r = P.get("r", 26)
x, y, vx, vy = CX, CY-80, rng.uniform(3, 5), 0.0
AGES = [90, 80, 70, 60, 50, 40, 30, 20, 15, 10, 5]
done_t = None; pent = [523, 587, 659, 784, 880]
while True:
    t = o.t
    if t > END + 6: break
    k = min(1, max(0, (t-3)/(END-3)))           # 0 = full color, 1 = invisible
    vis = (1-k)**2.2                            # contrast falls faster near the end
    col = tuple(int(v) for v in BGC + (COL-BGC)*max(vis, 0.012))
    age = AGES[min(len(AGES)-1, int(k*len(AGES)))]
    for _ in range(2):
        vy += .22; x += vx/2; y += vy/2
        dx, dy = x-CX, y-CY; d = math.hypot(dx, dy)
        if d + r > R:
            nx, ny = dx/d, dy/d; vn = vx*nx + vy*ny
            if vn > 0:
                vx -= 2*vn*nx; vy -= 2*vn*ny; sp = math.hypot(vx, vy)
                if sp < 7: vx *= 7/sp; vy *= 7/sp
                o.sound(pent[int(t*3) % 5], .12, .25*max(vis, .15))
            x, y = CX+nx*(R-r-.5), CY+ny*(R-r-.5)
    if not done_t and k >= 1: done_t = t; o.sound(196, .8, .3, 3)
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    rc = tuple(int(v) for v in BGC + (np.array([90, 100, 140])-BGC)*max(vis, .25))
    dr.ellipse([CX-R, CY-R, CX+R, CY+R], outline=rc, width=4)
    dr.ellipse([x-r, y-r, x+r, y+r], fill=col)
    header(img, P.get("title", "HOW OLD IS YOUR VISION?"), "Can you still see the ball?" if not done_t else "Did you see it until the end?")
    d2 = ImageDraw.Draw(img)
    if not done_t:
        out(d2, (AX, 440), f"If you see it: {age} years old" if age > 5 else "If you see it: SUPER VISION 🦅"[:-2], fit("If you see it: 90 years old", 520, 40), YEL, sw=5)
    cta(img, "Comment your vision age!", y=1000 if False else 388, col=BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("vision", o.t)
o.close()
