"""Hydraulic press v2: the plate slams on the pile, every ball it touches splits in two.
The pile grows each slam; when it crosses the red line the glass shatters. Viewers bet on the slam number."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
X0, X1, FLOOR, JTOP = 110, 570, 1190, 560      # glass jar (everything stays below y=470)
LINE = P.get("line", 860)                        # red break line
PERIOD = P.get("period", 4.6)                    # seconds between slams
HUE0 = P.get("hue", rng.random())
RB = P.get("rb", 22.0)
x = np.array([float(AX)]); y = np.array([FLOOR - RB]); r = np.array([RB]); hue = np.array([HUE0])
vx = np.zeros(1); vy = np.zeros(1)
plate = 540.0; slam = 0; state = "wait"; t_state = 0.0; done_t = None; flash = 0.0; cracks = []; shards = []
def pile_top():
    return float((y - r).min()) if len(y) else FLOOR
while True:
    t = o.t
    if done_t and t > max(done_t + 4, 61): break
    # press cycle: wait -> down -> hold -> up
    if done_t is None:
        if state == "wait" and t - t_state > PERIOD * .55: state, t_state = "down", t
        elif state == "down":
            target = pile_top()
            plate = min(target, plate + 22)
            if plate >= target - 1:
                state, t_state = "hold", t; slam += 1; flash = 1.0
                o.sound(55, .6, .7, 5, "square"); o.sound(0, .3, .5, 10, "noise")
                hit = rng.random(len(y)) < P.get("p", .55)  # each ball has a chance to split: the count is unpredictable
                if hit.any():
                    xs, ys, hs = x[hit], y[hit], hue[hit]; rs = np.full(len(xs), RB)
                    x = np.r_[x, xs + rng.uniform(-3, 3, len(xs))]; y = np.r_[y, ys - 2]; r = np.r_[r, rs]; hue = np.r_[hue, hs + .05]
                    vx = np.r_[vx, rng.normal(0, 2, len(xs))]; vy = np.r_[vy, rng.uniform(-6, -2, len(xs))]
                    for _i in range(len(xs)): o.sound(400 + 30 * (len(x) % 20), .05, .15, 30, "sine")
                cracks.append((rng.uniform(X0, X1), rng.uniform(LINE, FLOOR)))
        elif state == "hold" and t - t_state > .25: state, t_state = "up", t
        elif state == "up":
            plate = max(540, plate - 14)
            if plate <= 540: state, t_state = "wait", t
    else:
        plate = max(540, plate - 14)
    # physics
    vy = np.minimum(vy + .7, 9); x += vx; y += vy; vx *= .97
    y += rng.normal(0, .6, len(y)); x += rng.normal(0, .3, len(x))
    for _ in range(8):
        dx = x[:, None] - x[None, :]; dy = y[:, None] - y[None, :]; d = np.hypot(dx, dy) + 1e-6
        ov = np.clip((r[:, None] + r[None, :]) - d, 0, None); np.fill_diagonal(ov, 0)
        cnt = (ov > 0).sum(1) + 1
        x += (dx / d * ov).sum(1) / cnt * 1.0; y += (dy / d * ov).sum(1) / cnt * 1.0
        # hard walls: nothing ever leaves the jar
        if done_t is not None and t >= done_t: x = np.clip(x, r, W - r); y = np.minimum(y, np.where((x > X0 - 12) & (x < X1 + 12), FLOOR, H + 200) - r)
        else: x = np.clip(x, X0 + r, X1 - r); y = np.minimum(y, FLOOR - r)
        y = np.maximum(y, (plate if state in ("down", "hold") else (JTOP if done_t is None else 0)) + r)
    m = y >= FLOOR - r - .5; vy[m] *= -.2; vx[m] *= .85
    vy[np.abs(vy) < 1.5] *= .5
    top = pile_top()
    if done_t is None and slam > 0 and state == "wait" and t - t_state > 1.0 and top < LINE and np.abs(vy).max() < 3:
        done_t = t + .3; fanfare(o, t + .3); o.sound(900, .5, .5, 4, "noise")
        vx += rng.normal(0, 6, len(vx)); vy -= rng.uniform(4, 12, len(vy))
        for _ in range(60): shards.append([rng.uniform(X0, X1), rng.uniform(LINE, FLOOR), rng.uniform(-9, 9), rng.uniform(-14, -2), 1.0])
    if t > 80 and done_t is None: done_t = t
    # draw
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    broken = done_t is not None and t >= done_t
    glass = (150, 200, 255) if not broken else (90, 110, 140)
    if not broken:
        dr.rectangle([X0 - 12, JTOP, X0, FLOOR + 12], fill=glass); dr.rectangle([X1, JTOP, X1 + 12, FLOOR + 12], fill=glass)
    dr.rectangle([X0 - 12, FLOOR, X1 + 12, FLOOR + 12], fill=glass)
    for (cx, cy) in cracks[:12]:
        if not broken:
            for k in range(4):
                a = k * 1.6 + cx; dr.line([(X0 - 6 if cx < AX else X1 + 6, cy), (X0 - 6 + 30 * math.cos(a) if cx < AX else X1 + 6 - 30 * math.cos(a), cy + 30 * math.sin(a))], fill="white", width=2)
    for i in range(len(x)):
        dr.ellipse([x[i] - r[i], y[i] - r[i], x[i] + r[i], y[i] + r[i]], fill=hsv(hue[i], .7, 1), outline=INK if r[i] > 9 else None)
    # red break line
    for xx in range(X0, X1, 28): dr.line([(xx, LINE), (xx + 16, LINE)], fill=RED, width=5)
    out(dr, (X1 - 4, LINE - 22), "BREAK LINE", fredoka(22), RED, anc="rm", sw=3)
    # press
    if not broken:
        dr.rectangle([X0 + 6, plate - 30, X1 - 6, plate], fill=(200, 205, 215), outline=INK, width=3)
        dr.rectangle([AX - 26, 474, AX + 26, max(475, plate - 30)], fill=(150, 155, 170), outline=INK, width=3)
        if flash > 0: dr.rectangle([X0 + 6, plate, X1 - 6, plate + 8], fill=YEL); flash -= .12
    for s in shards:
        s[0] += s[2]; s[1] += s[3]; s[3] += .6; s[4] -= .02
        if s[4] > 0: dr.polygon([(s[0], s[1]), (s[0] + 10, s[1] + 4), (s[0] + 3, s[1] + 12)], fill=(180, 220, 255))
    header(img, P.get("title", "WHICH SLAM BREAKS THE GLASS?"), f"Slam {slam}  •  {len(x)} balls")
    cta(img, f"GLASS BROKE AT SLAM {slam}!" if broken else "Guess the slam number!", col=YEL if broken else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("press", slam, len(x), o.t)
o.close()
