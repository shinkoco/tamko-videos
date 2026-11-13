import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
N = P.get("n", 500); SHAPE = P.get("shape", "spiral"); HUE0 = P.get("hue", 0.0)
CX, CY = AX, 735
# build a path of N points with roughly equal spacing
pts = []
if SHAPE == "spiral":
    a, rr = 0.0, 245.0
    while len(pts) < N and rr > 12:
        pts.append((CX + rr*math.cos(a), CY + rr*math.sin(a), a + math.pi/2)); step = 9.5/rr; a += step; rr -= 42*step/(2*math.pi)
else:  # zigzag snake
    rows = 12; per = N//rows + 1; x0, x1 = 70, 610; y0 = 500
    for rw in range(rows):
        for j in range(per):
            fx = j/(per-1); x = x0 + (x1-x0)*(fx if rw % 2 == 0 else 1-fx)
            pts.append((x, y0 + rw*40, 0.0 if rw % 2 == 0 else math.pi))
pts = pts[:N]; N = len(pts)
STEP = P.get("tstep", 0.1)  # seconds between falls
DUR = 2 + N*STEP
# suspense: a stall point where the chain pauses
stall_i = int(N*rng.uniform(.55, .7)); STALL = 2.2
fall_at = [2 + i*STEP + (STALL if i >= stall_i else 0) for i in range(N)]
snd = 0; done_t = None
while True:
    t = o.t
    fallen = sum(1 for f in fall_at if t >= f + 0.15)
    if not done_t and fallen == N: done_t = t; fanfare(o, t)
    if done_t and t > max(done_t+4, 61): break
    if t > 85: break
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    for i, (x, y, a) in enumerate(pts):
        k = min(1, max(0, (t - fall_at[i])/0.15)); col = hsv(HUE0 + i/N*1.5, .65, 1)
        if k <= 0: L, Wd = 9, 3; ang = a + math.pi/2; c = col
        else: L, Wd = 3 + 6*(1-k), 3 + 6*k; ang = a + math.pi/2; c = tuple(int(v*(1-.45*k)) for v in col)
        if k > 0 and i > 0 and t - fall_at[i] < 0.05 and t - snd > 0.03: o.sound(1400 + (i % 7)*60, .03, .12, 60); snd = t
        dx, dy = math.cos(ang), math.sin(ang); px, py = -dy, dx
        poly = [(x-dx*L-px*Wd/2, y-dy*L-py*Wd/2), (x+dx*L-px*Wd/2, y+dy*L-py*Wd/2), (x+dx*L+px*Wd/2, y+dy*L+py*Wd/2), (x-dx*L+px*Wd/2, y-dy*L+py*Wd/2)]
        dr.polygon(poly, fill=c)
    if 2 + stall_i*STEP < t < fall_at[stall_i] and not done_t:
        out(dr, (AX, 445), "...", lilita(60), RED)
    header(img, P.get("title", f"WILL ALL {N} FALL?"), f"Fallen: {fallen}/{N}")
    cta(img, "ALL DOWN!" if done_t else "Will it make it to the end?", col=YEL if done_t else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("dominoes", N, o.t)
o.close()
