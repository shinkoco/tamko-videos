"""Maze 'Trapped or free?': Tamko explores a random maze (depth-first, dead ends greyed out) against a timer.
Exit found before 0:00 = FREE, otherwise TRAPPED."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
GW, GH = P.get("gw", 14), P.get("gh", 16); X0, Y0 = 80, 490; CS = 560/GW
TIMER = P.get("timer", 54.0); T0 = 2.0
# perfect maze (recursive backtracker)
walls = np.ones((GH, GW, 4), bool)  # N E S W
DIRS = [(0, -1, 0, 2), (1, 0, 1, 3), (0, 1, 2, 0), (-1, 0, 3, 1)]
seen = np.zeros((GH, GW), bool); st = [(0, 0)]; seen[0, 0] = True
while st:
    cx, cy = st[-1]; opts = [(dx, dy, a, b) for dx, dy, a, b in DIRS if 0 <= cx+dx < GW and 0 <= cy+dy < GH and not seen[cy+dy, cx+dx]]
    if not opts: st.pop(); continue
    dx, dy, a, b = opts[rng.integers(len(opts))]; walls[cy, cx, a] = False; walls[cy+dy, cx+dx, b] = False
    seen[cy+dy, cx+dx] = True; st.append((cx+dx, cy+dy))
EXIT = (GW-1, GH-1)
# Tamko's exploration: random depth-first search, recorded as a list of moves
path = [(0, 0)]; vis = {(0, 0)}; stack = [(0, 0)]; moves = [(0, 0, False)]
while stack and stack[-1] != EXIT:
    cx, cy = stack[-1]
    opts = [(cx+dx, cy+dy) for dx, dy, a, b in DIRS if not walls[cy, cx, a] and (cx+dx, cy+dy) not in vis]
    if opts:
        n = opts[rng.integers(len(opts))]; vis.add(n); stack.append(n); moves.append((n[0], n[1], False))
    else:
        stack.pop()
        if stack: moves.append((stack[-1][0], stack[-1][1], True))
# speed chosen so that the finish lands somewhere around the deadline: sometimes free, sometimes trapped
finish = rng.uniform(TIMER*.9, TIMER*1.15); step = finish/len(moves)
trail = []; dead = set(); i_mv = 0; res = None; res_t = None
music(o, 70, bpm=P.get("bpm", 140), seed=P.get("seed", 1) + 21, vol=.75)
def cc(x, y): return X0 + (x + .5)*CS, Y0 + (y + .5)*CS
while True:
    t = o.t
    if res_t and t > max(res_t + 4, 61): break
    if res is None and t > T0:
        target = min(len(moves) - 1, int((t - T0)/step))
        while i_mv < target:
            i_mv += 1; x, y, back = moves[i_mv]
            if back and trail: dead.add(trail.pop())
            elif not back: trail.append((x, y))
            o.sound(330 if back else 660 + 20*(len(trail) % 12), .04, .08, 40, "sine")
        if moves[i_mv][:2] == EXIT:
            res, res_t = "FREE", t; fanfare(o, t)
        elif t - T0 >= TIMER:
            res, res_t = "TRAPPED", t; o.sound(110, .8, .5, 3, "square")
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    for (x, y) in dead:
        cx_, cy_ = cc(x, y); dr.rectangle([cx_ - CS/2 + 2, cy_ - CS/2 + 2, cx_ + CS/2 - 2, cy_ + CS/2 - 2], fill=(45, 50, 75))
    ex, ey = cc(*EXIT); dr.rectangle([ex - CS/2 + 3, ey - CS/2 + 3, ex + CS/2 - 3, ey + CS/2 - 3], fill=(60, 170, 90))
    pts = [cc(0, 0)] + [cc(x, y) for x, y in trail]
    if len(pts) > 1: dr.line(pts, fill=(255, 196, 40), width=7, joint="curve")
    wc = (60, 200, 245) if res != "TRAPPED" else (255, 90, 110)
    for y in range(GH):
        for x in range(GW):
            x0, y0 = X0 + x*CS, Y0 + y*CS
            if walls[y, x, 0]: dr.line([(x0, y0), (x0 + CS, y0)], fill=wc, width=4)
            if walls[y, x, 3]: dr.line([(x0, y0), (x0, y0 + CS)], fill=wc, width=4)
    dr.rectangle([X0, Y0, X0 + GW*CS, Y0 + GH*CS], outline=wc, width=6)
    hx, hy = pts[-1]; tamko_sprite(img, hx, hy, CS*.95, t)
    out(dr, (ex, ey + CS*.9), "EXIT", fredoka(20), (120, 230, 120), sw=3)
    left = max(0.0, TIMER - max(0, t - T0)) if res is None else max(0.0, TIMER - (res_t - T0))
    col = "white" if left > 10 else RED
    out(dr, (AX, Y0 + GH*CS + 60), f"0:{int(left):02d}", lilita(64), col, sw=6)
    header(img, P.get("title", "TRAPPED OR FREE?"), f"Tamko needs the exit in {int(TIMER)} seconds")
    cta(img, ("FREE!" if res == "FREE" else "TRAPPED!") if res else "Comment TRAPPED or FREE!", col=YEL if res != "TRAPPED" else RED)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("maze", res, len(moves), round(finish, 1), o.t)
o.close()
