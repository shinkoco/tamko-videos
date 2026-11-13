import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
NPOOL = ["Mochi","Pip","Bloop","Tofu","Kiwi","Bean","Zuzu","Nugget","Waffle","Gizmo","Taro","Yuzu","Miso","Boba","Peanut","Sushi",
         "Dango","Nori","Pudding","Bubbles","Pickle","Noodle","Biscuit","Pebble","Sprout","Cocoa","Maple","Ziggy","Bolt","Ramen",
         "Wasabi","Kibo","Momo","Fuzzy","Jelly","Coco","Rocket","Pixel","Squish","Toffee"]
N = P.get("n", 20); HUE0 = P.get("hue", 0.0)
CX, CY, R, BR = AX, 745, 255, 17
names = list(rng.choice(NPOOL, N, replace=False))
pl = []
for i in range(N):
    a = rng.uniform(0, 6.28); d = rng.uniform(0, R-40)
    sp = rng.uniform(2, 3.5); th = rng.uniform(0, 6.28)
    pl.append(dict(n=names[i], c=hsv(HUE0+i/N, .6, 1), x=CX+d*math.cos(a), y=CY+d*math.sin(a),
                   vx=sp*math.cos(th), vy=sp*math.sin(th), alive=True))
TRAPS = [("BOMB!", (255, 90, 110)), ("METEOR!", (255, 150, 40)), ("TRAPDOOR!", (160, 90, 255)), ("LIGHTNING!", (255, 230, 60))]
ROUND = P.get("round", 4.6); WARN = 2.0
plan = []  # victims per round, summing to N-1
left = N - 1
while left > 0:
    k = 3 if left > 12 else (2 if left > 4 else 1); k = min(k, left); plan.append(k); left -= k
rnd_i, trap, parts, win_t, last_out = 0, None, [], None, []
pent = [392, 440, 523, 587, 659]
while True:
    t = o.t
    if (win_t and t > max(win_t+4, 61)) or t > 85: break
    alive = [p for p in pl if p['alive']]
    # start a trap
    if not win_t and trap is None and t >= 3 + rnd_i*ROUND:
        k = min(plan[rnd_i] if rnd_i < len(plan) else 1, len(alive)-1); tgt = alive[rng.integers(len(alive))]
        ds = sorted(alive, key=lambda p: (p['x']-tgt['x'])**2 + (p['y']-tgt['y'])**2)
        rad = math.hypot(ds[k-1]['x']-tgt['x'], ds[k-1]['y']-tgt['y']) + BR + 6
        name, col = TRAPS[rng.integers(len(TRAPS))]
        trap = dict(x=tgt['x'], y=tgt['y'], r=max(rad, 40), t0=t, k=k, name=name, col=col)
        o.sound(880, .12, .2); o.ev.append((t+.5, 880, .12, .2, 18, "sine")); o.ev.append((t+1.0, 988, .12, .2, 18, "sine"))
    if trap and t >= trap['t0'] + WARN:
        inside = [p for p in alive if math.hypot(p['x']-trap['x'], p['y']-trap['y']) < trap['r']]
        inside.sort(key=lambda p: math.hypot(p['x']-trap['x'], p['y']-trap['y']))
        victims = inside[:trap['k']] if inside else sorted(alive, key=lambda p: math.hypot(p['x']-trap['x'], p['y']-trap['y']))[:trap['k']]
        if len(victims) >= len(alive): victims = victims[:len(alive)-1]
        for v in victims:
            v['alive'] = False; last_out = ([v['n']] + last_out)[:4]
            for _ in range(30):
                th = rng.uniform(0, 6.28); s = rng.uniform(2, 8)
                parts.append([v['x'], v['y'], s*math.cos(th), s*math.sin(th), 1.0, v['c']])
        o.sound(90, .5, .6, 5, "square"); o.sound(0, .35, .4, 9, "noise")
        trap = None; rnd_i += 1
        if len([p for p in pl if p['alive']]) == 1:
            win_t = t
            for k, fr in enumerate([523, 659, 784, 1047]): o.ev.append((t+.15*k, fr, .4, .35, 5, "sine"))
    alive = [p for p in pl if p['alive']]
    for p in alive:
        if rng.random() < 0.02:
            th = rng.uniform(0, 6.28); s = math.hypot(p['vx'], p['vy']); p['vx'], p['vy'] = s*math.cos(th), s*math.sin(th)
        if trap:  # panic: flee from the danger zone
            dx, dy = p['x']-trap['x'], p['y']-trap['y']; d = math.hypot(dx, dy) or 1
            if d < trap['r']+40: p['vx'] += dx/d*0.25; p['vy'] += dy/d*0.25
        sp = math.hypot(p['vx'], p['vy'])
        if sp > 4.5: p['vx'] *= 4.5/sp; p['vy'] *= 4.5/sp
        p['x'] += p['vx']; p['y'] += p['vy']
        dx, dy = p['x']-CX, p['y']-CY; d = math.hypot(dx, dy)
        if d > R-BR:
            nx, ny = dx/d, dy/d; vn = p['vx']*nx+p['vy']*ny
            if vn > 0: p['vx'] -= 2*vn*nx; p['vy'] -= 2*vn*ny
            p['x'], p['y'] = CX+nx*(R-BR), CY+ny*(R-BR)
    for i in range(len(alive)):
        for j in range(i+1, len(alive)):
            a, b = alive[i], alive[j]; dx, dy = b['x']-a['x'], b['y']-a['y']; d = math.hypot(dx, dy)
            if 0 < d < 2*BR:
                nx, ny = dx/d, dy/d; ov = (2*BR-d)/2
                a['x'] -= nx*ov; a['y'] -= ny*ov; b['x'] += nx*ov; b['y'] += ny*ov
                a['vx'], b['vx'] = b['vx'], a['vx']; a['vy'], b['vy'] = b['vy'], a['vy']
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    dr.ellipse([CX-R-8, CY-R-8, CX+R+8, CY+R+8], fill=(26, 30, 52), outline=(60, 170, 255), width=8)
    if trap:
        k = (t-trap['t0'])/WARN; blink = int(t*8) % 2
        c = trap['col'] if blink else tuple(v//2 for v in trap['col'])
        rr = trap['r']*min(1, k*1.5)
        dr.ellipse([trap['x']-rr, trap['y']-rr, trap['x']+rr, trap['y']+rr], outline=c, width=6)
        out(dr, (AX, 500), trap['name'], lilita(60), trap['col'])
    for p in parts:
        p[0] += p[2]; p[1] += p[3]; p[3] += .2; p[4] -= .035
        if p[4] > 0: dr.ellipse([p[0]-4, p[1]-4, p[0]+4, p[1]+4], fill=tuple(int(v*p[4]) for v in p[5]))
    parts = [p for p in parts if p[4] > 0]
    for p in alive:
        x, y = p['x'], p['y']; big = 1.6 if win_t else 1
        r = BR*big
        dr.ellipse([x-r, y-r, x+r, y+r], fill=p['c'], outline=INK, width=3)
        lx = max(-2, min(2, p['vx']*.5)); ly = max(-2, min(2, p['vy']*.5))
        for ex in (-6*big, 6*big):
            dr.ellipse([x+ex-4*big, y-7*big, x+ex+4*big, y+1*big], fill="white")
            dr.ellipse([x+ex+lx-2*big, y-5*big+ly, x+ex+lx+2*big, y-1*big+ly], fill="black")
        if len(alive) <= 8 or win_t:
            out(dr, (x, y-r-12), p['n'], fredoka(18 if not win_t else 28), "white", sw=3)
    nleft = len(alive)
    header(img, P.get("title", "WHO SURVIVES?"), f"{nleft} left  •  Round {rnd_i+1}")
    if last_out and not win_t:
        txt = "OUT: " + "  ".join(last_out)
        out(dr, (AX, 436), txt, fit(txt, 540, 26, fredoka), RED, sw=4)
    if win_t: cta(img, f"{alive[0]['n']} SURVIVES!", col=YEL)
    else: cta(img, "Pick your survivor!")
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("winner", [p['n'] for p in pl if p['alive']], o.t)
o.close()
