import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
NPOOL = ["Quacky","Waddles","Puddles","Ducky","Bubbles","Nugget","Sunny","Mango","Peep","Splash","Biscuit","Noodle","Pickles",
         "Daisy","Lemon","Pebble","Taco","Chip","Muffin","Ziggy","Honey","Pancake","Sprinkle","Tofu","Coco","Mochi","Boba","Kiwi"]
N = P.get("n", 8); FIN = P.get("fin", 6200); L, Rb = 50, 620  # river banks
names = list(rng.choice(NPOOL, N, replace=False))
COLS = [(255, 205, 60), (255, 130, 160), (120, 220, 255), (150, 235, 140), (255, 160, 70), (200, 150, 255), (255, 255, 255), (255, 100, 100)]
rng.shuffle(COLS)
ducks = [dict(n=names[i], c=COLS[i % len(COLS)], x=L+40+i*(Rb-L-80)/(N-1), y=150.0, vx=0.0, vy=0.0, done=None, spin=0.0) for i in range(N)]
# obstacles
rocks = [(rng.uniform(L+40, Rb-40), y, rng.uniform(22, 40)) for y in np.arange(700, FIN-300, P.get("rock_gap", 260))]
pools = [(rng.uniform(L+80, Rb-80), y) for y in np.arange(1300, FIN-500, P.get("pool_gap", 1500))]
boosts = [(rng.uniform(L+60, Rb-60), y) for y in np.arange(1000, FIN-400, 1100)]
def current(x, y, t):
    mid = (L+Rb)/2; lane = 1 - ((x-mid)/((Rb-L)/2))**2  # faster in the middle
    return 2.3 + 1.8*max(0, lane) + 0.6*math.sin(y/300 + t*0.8)
order = []; cam = -350; snd_t = 0; first_t = 1e9
while True:
    t = o.t
    if t > 61 and (len(order) == N or (order and t > first_t + 7)): break
    if t > 80: break
    lead = max(d['y'] for d in ducks)
    for d in ducks:
        if d['done'] is not None: continue
        cur = current(d['x'], d['y'], t) + min(1.5, max(0, (lead - d['y'])*0.003))
        d['vy'] += (cur - d['vy'])*0.05; d['vx'] += rng.uniform(-0.25, 0.25) + 0.15*math.sin(t*1.3 + d['y']/200)
        d['vx'] *= 0.96
        for (bx, by) in boosts:
            if abs(d['x']-bx) < 45 and abs(d['y']-by) < 30: d['vy'] = 9; o.sound(988, .1, .15) if t-snd_t > .1 else None; snd_t = t
        for (px, py) in pools:
            dx, dy = d['x']-px, d['y']-py; dist = math.hypot(dx, dy)
            if dist < 90:  # whirlpool: swirl + slow
                d['vx'] += -dy/dist*0.9; d['vy'] = d['vy']*0.85 + dx/dist*0.9; d['spin'] += 0.3
        for (rx, ry, rr) in rocks:
            dx, dy = d['x']-rx, d['y']-ry; dist = math.hypot(dx, dy); m = rr+18
            if 0 < dist < m:
                nx, ny = dx/dist, dy/dist; vn = d['vx']*nx+d['vy']*ny
                if vn < 0: d['vx'] -= 1.6*vn*nx; d['vy'] -= 1.6*vn*ny
                d['x'], d['y'] = rx+nx*m, ry+ny*m
                if t-snd_t > .08: o.sound(330+rr*5, .12, .2); snd_t = t
        d['x'] += d['vx']; d['y'] += d['vy']; d['spin'] *= 0.95
        if d['x'] < L+18: d['x'] = L+18; d['vx'] = abs(d['vx'])
        if d['x'] > Rb-18: d['x'] = Rb-18; d['vx'] = -abs(d['vx'])
        if d['y'] >= FIN:
            d['done'] = t; order.append(d['n']); o.sound(523*(1.5 if len(order) == 1 else 1), .4, .4, 6)
            if len(order) == 1:
                first_t = t
                for k, fr in enumerate([523, 659, 784, 1047]): o.ev.append((t+.12*k, fr, .4, .35, 5, "sine"))
    act = [d for d in ducks if d['done'] is None]
    for i, a in enumerate(act):
        for b in act[i+1:]:
            dx, dy = b['x']-a['x'], b['y']-a['y']; dist = math.hypot(dx, dy)
            if 0 < dist < 36:
                nx, ny = dx/dist, dy/dist; ov = (36-dist)/2
                a['x'] -= nx*ov; a['y'] -= ny*ov; b['x'] += nx*ov; b['y'] += ny*ov
    target = (max(d['y'] for d in act) if act else FIN) - 700
    cam += (min(target, FIN-900) - cam)*0.08
    img = Image.new("RGB", (W, H), (30, 110, 170)); dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, L, H], fill=(70, 160, 90)); dr.rectangle([Rb, 0, W, H], fill=(70, 160, 90))
    for k in range(int(cam//60)-1, int((cam+H)//60)+2):  # waves scrolling with current
        yy = k*60 - cam + (t*90) % 60; xs = (k*137) % (Rb-L-120) + L+40
        dr.arc([xs, yy, xs+60, yy+20], 200, 340, fill=(120, 190, 235), width=3)
    for (px, py) in pools:
        y = py-cam
        if -100 < y < H+100:
            for rr in (80, 55, 30): dr.arc([px-rr, y-rr, px+rr, y+rr], (t*200 + rr*3) % 360, (t*200 + rr*3) % 360 + 260, fill=(200, 235, 255), width=4)
    for (bx, by) in boosts:
        y = by-cam
        if -60 < y < H+60: dr.polygon([(bx-30, y-15), (bx+30, y-15), (bx, y+20)], fill=(255, 205, 60))
    for (rx, ry, rr) in rocks:
        y = ry-cam
        if -60 < y < H+60: dr.ellipse([rx-rr, y-rr*.8, rx+rr, y+rr*.8], fill=(110, 110, 125), outline=(70, 70, 85), width=3)
    fy = FIN-cam+20
    for k in range(L, Rb, 40):
        dr.rectangle([k, fy, k+20, fy+20], fill="white"); dr.rectangle([k+20, fy+20, k+40, fy+40], fill="white")
    for d in ducks:
        x, y = d['x'], d['y']-cam
        if d['done'] is not None:
            i = order.index(d['n']); x = L+60+(i % 4)*140; y = FIN-cam+110+(i//4)*80
        if -60 < y < H+60:
            dr.ellipse([x-20, y-14, x+20, y+16], fill=d['c'], outline=INK, width=3)       # body
            dr.ellipse([x-12, y-32, x+10, y-10], fill=d['c'], outline=INK, width=3)       # head
            dr.polygon([(x+8, y-24), (x+22, y-20), (x+8, y-16)], fill=(255, 140, 40), outline=INK)  # beak
            dr.ellipse([x-2, y-26, x+4, y-20], fill="black")
            out(dr, (x, y-44), d['n'], fredoka(18), "white", sw=3)
    dr.rectangle([0, 0, W, 470], fill=BG)
    header(img, P.get("title", "WHICH DUCK WINS?"), None, y=240)
    rank = order + [d['n'] for d in sorted(act, key=lambda d: -d['y'])]
    for i, nm in enumerate(rank[:3]):
        out(dr, (AX, 305+i*36), f"{i+1}. {nm}", fredoka(30), [YEL, (200, 200, 215), (230, 140, 70)][i], sw=4)
    if order: cta(img, f"{order[0]} WINS!", y=440, col=YEL)
    else: cta(img, "Pick your duck!", y=440)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("finished", order, o.t)
o.close()
