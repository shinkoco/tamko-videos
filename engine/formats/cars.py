import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
CP = ["Turbo","Flash","Nitro","Bolt","Drift","Rocket","Blitz","Zoom","Racer","Dash","Vroom","Fury","Comet","Viper","Spark","Ace"]
N = P.get("n", 8); LAPS = P.get("laps", 3); CX, CY, RX, RY = AX, 715, 255, 215; TW = 70
names = list(rng.choice(CP, N, replace=False))
cars = [dict(n=names[i], c=hsv(P.get("hue", 0)+i/N, .7, 1), s=-0.04*i, lane=(i % 4 - 1.5)*15, v=0.0, spin=0, done=None, num=i+1) for i in range(N)]
order = []; first_t = 1e9; smoke = []; lap_shown = 1
def pos(s, lane):
    a = s*2*math.pi - math.pi/2
    return CX + (RX+lane)*math.cos(a), CY + (RY+lane)*math.sin(a), a
while True:
    t = o.t
    if t > 61 and (len(order) == N or (order and t > first_t+6)): break
    if t > 80: break
    act = [c for c in cars if c['done'] is None]
    lead = max(c['s'] for c in cars)
    base = LAPS/52/FPS*1.0
    for c in act:
        tgt = base*(1 + 0.18*math.sin(t*0.7 + c['num']*1.7) + min(0.25, (lead-c['s'])*0.6))
        if c['spin'] > 0: c['spin'] -= 1; tgt = base*0.15
        elif rng.random() < P.get("crash", 0.0016) and t > 4:
            c['spin'] = 45; o.sound(200, .35, .35, 7, "noise")
            x, y, _ = pos(c['s'], c['lane'])
            for _ in range(14): smoke.append([x, y, rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5), 1.0])
        c['v'] += (tgt - c['v'])*0.08; c['s'] += c['v']
        if c['s'] >= LAPS:
            c['done'] = t; order.append(c['n']); o.sound(784 if len(order) == 1 else 523, .3, .35, 6)
            if len(order) == 1: first_t = t; fanfare(o, t)
    lap = min(LAPS, int(max(c['s'] for c in act) if act else LAPS)+1)
    if lap > lap_shown: lap_shown = lap; o.sound(988, .15, .3); o.ev.append((t+.15, 1319, .2, .3, 10, "sine"))
    img = Image.new("RGB", (W, H), (40, 120, 70)); dr = ImageDraw.Draw(img)
    dr.ellipse([CX-RX-TW, CY-RY-TW, CX+RX+TW, CY+RY+TW], fill=(70, 70, 82))
    dr.ellipse([CX-RX+TW, CY-RY+TW, CX+RX-TW, CY+RY-TW], fill=(40, 120, 70))
    for k in range(0, 360, 12):
        a = math.radians(k); col = RED if (k//12) % 2 else (255, 255, 255)
        for rr in (TW, -TW):
            x1, y1 = CX+(RX+rr)*math.cos(a), CY+(RY+rr)*math.sin(a)
            dr.ellipse([x1-5, y1-5, x1+5, y1+5], fill=col)
    for k in range(-TW, TW, 14):
        dr.rectangle([CX-4, CY-RY+k, CX+4, CY-RY+k+7], fill="white" if (k//14) % 2 else (20, 20, 20))
    for sm in smoke:
        sm[0] += sm[2]; sm[1] += sm[3]; sm[4] -= .02
        if sm[4] > 0: g = int(120+100*sm[4]); r_ = 10+(1-sm[4])*16; dr.ellipse([sm[0]-r_, sm[1]-r_, sm[0]+r_, sm[1]+r_], fill=(g, g, g))
    smoke = [s for s in smoke if s[4] > 0]
    for c in sorted(cars, key=lambda c: c['lane']):
        x, y, a = pos(min(c['s'], LAPS), c['lane'])
        if c['done'] is not None:
            i = order.index(c['n']); x = CX-150+(i % 4)*100; y = CY-40+(i//4)*80; a = 0
        h = a + math.pi/2 + (t*14 if c['spin'] else 0)
        body = rot([(-11, -20), (11, -20), (11, 20), (-11, 20)], x, y, h)
        dr.polygon(body, fill=c['c'], outline=INK)
        wind = rot([(-8, -10), (8, -10), (8, -2), (-8, -2)], x, y, h); dr.polygon(wind, fill=(30, 40, 60))
        out(dr, (x, y-30), c['n'], fredoka(16), "white", sw=3)
    dr.rectangle([0, 0, W, 470], fill=BG)
    header(img, P.get("title", "WHO WINS THE RACE?"), None, y=240)
    act_sorted = [c['n'] for c in sorted(act, key=lambda c: -c['s'])]
    podium(dr, order + act_sorted)
    cta(img, f"{order[0]} WINS!" if order else f"LAP {lap}/{LAPS}  •  Pick your car!", y=440, col=YEL if order else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("done", order[:3], o.t)
o.close()
