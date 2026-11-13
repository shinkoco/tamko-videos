import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
RP = ["Apollo","Comet","Nova","Zippy","Orbit","Blaze","Luna","Astro","Rocky","Spark","Meteor","Pluto","Vega","Jet","Cosmo","Starry"]
N = P.get("n", 7); FIN = P.get("fin", 6400); L, R = 40, 630
names = list(rng.choice(RP, N, replace=False))
cols = [hsv(P.get("hue", 0)+i/N, .55, 1) for i in range(N)]
rk = [dict(n=names[i], c=cols[i], x=L+50+i*(R-L-100)/(N-1), d=0.0, v=0.0, vx=0.0, stun=0, done=None) for i in range(N)]
ast = [(rng.uniform(L+40, R-40), d, rng.uniform(20, 42)) for d in np.arange(600, FIN-300, P.get("ast_gap", 230))]
boost = [(rng.uniform(L+60, R-60), d) for d in np.arange(900, FIN-400, 900)]
stars = [(rng.uniform(0, W), rng.uniform(0, 4000), rng.uniform(1, 3)) for _ in range(220)]
order = []; cam = 0; first_t = 1e9; snd = 0
while True:
    t = o.t
    if t > 61 and (len(order) == N or (order and t > first_t+7)): break
    if t > 80: break
    act = [r for r in rk if r['done'] is None]
    lead = max(r['d'] for r in rk)
    for r in act:
        tgt = 3.6 + 0.7*math.sin(t*0.9 + r['x']/90) + min(1.6, (lead-r['d'])*0.004)
        if r['stun'] > 0: r['stun'] -= 1; tgt = 0.6
        r['v'] += (tgt - r['v'])*0.06; r['vx'] += rng.uniform(-.3, .3); r['vx'] *= .95
        for (bx, bd) in boost:
            if abs(r['x']-bx) < 40 and abs(r['d']-bd) < 25: r['v'] = 10; o.sound(1175, .1, .15) if t-snd > .1 else None; snd = t
        for (ax, ad, ar) in ast:
            if math.hypot(r['x']-ax, r['d']-ad) < ar+16 and r['stun'] == 0:
                r['stun'] = 40; r['vx'] = 6 if r['x'] > ax else -6; o.sound(140, .25, .35, 8, "noise")
        r['d'] += r['v']; r['x'] = min(R-18, max(L+18, r['x']+r['vx']))
        if r['d'] >= FIN:
            r['done'] = t; order.append(r['n']); o.sound(784 if len(order) == 1 else 523, .3, .35, 6)
            if len(order) == 1: first_t = t; fanfare(o, t)
    target = (max(r['d'] for r in act) if act else FIN) - 230
    cam += (min(target, FIN-500) - cam)*0.08
    Y = lambda d: 960 - (d - cam)
    img = Image.new("RGB", (W, H), (8, 8, 26)); dr = ImageDraw.Draw(img)
    for (sx, sy, sz) in stars:
        yy = (sy + cam*0.3*sz/3) % 1400 - 60; dr.ellipse([sx-sz, yy-sz, sx+sz, yy+sz], fill=(200, 200, 255))
    fy = Y(FIN)
    if -40 < fy < H:
        for k in range(L, R, 40): dr.rectangle([k, fy-20, k+20, fy], fill="white"); dr.rectangle([k+20, fy-40, k+40, fy-20], fill="white")
    for (bx, bd) in boost:
        y = Y(bd)
        if -40 < y < H+40: dr.polygon([(bx-28, y+14), (bx+28, y+14), (bx, y-20)], fill=YEL)
    for (ax, ad, ar) in ast:
        y = Y(ad)
        if -60 < y < H+60:
            dr.ellipse([ax-ar, y-ar, ax+ar, y+ar], fill=(120, 105, 95), outline=(70, 60, 55), width=3)
            dr.ellipse([ax-ar*.4, y-ar*.3, ax-ar*.05, y+ar*.05], fill=(95, 82, 75))
    for r in rk:
        x = r['x']; y = Y(r['d'])
        if r['done'] is not None:
            i = order.index(r['n']); x = L+60+(i % 4)*140; y = Y(FIN)-110-(i//4)*90
        if -80 < y < H+80:
            a = (t*12 if r['stun'] else 0)
            fl = 18 + 10*abs(math.sin(t*30 + x))
            body = rot([(-11, -26), (11, -26), (11, 16), (-11, 16)], x, y, a)
            nose = rot([(-11, -26), (11, -26), (0, -44)], x, y, a)
            fins = rot([(-11, 6), (-22, 20), (-11, 16)], x, y, a) , rot([(11, 6), (22, 20), (11, 16)], x, y, a)
            flame = rot([(-8, 16), (8, 16), (0, 16+fl)], x, y, a)
            dr.polygon(flame, fill=(255, 150, 40)); dr.polygon(body, fill=r['c'], outline=INK)
            dr.polygon(nose, fill=RED, outline=INK); [dr.polygon(f, fill=RED, outline=INK) for f in fins]
            cx, cy = rot([(0, -10)], x, y, a)[0]; dr.ellipse([cx-6, cy-6, cx+6, cy+6], fill=(150, 220, 255), outline=INK)
            out(dr, (x, y+48+fl*.3), r['n'], fredoka(18), "white", sw=3)
    dr.rectangle([0, 0, W, 470], fill=BG)
    header(img, P.get("title", "WHICH ROCKET REACHES SPACE?"), None, y=240)
    podium(dr, order + [r['n'] for r in sorted(act, key=lambda r: -r['d'])])
    cta(img, f"{order[0]} WINS!" if order else "Pick your rocket!", y=440, col=YEL if order else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("done", order[:3], o.t)
o.close()
