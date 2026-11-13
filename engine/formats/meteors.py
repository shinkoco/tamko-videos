import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
N = P.get("n", 18); X0, Y0, X1, Y1 = 50, 500, 620, 975; BR = 16; HUE0 = P.get("hue", 0)
names = list(rng.choice(NPOOL, N, replace=False))
pl = [dict(n=names[i], c=hsv(HUE0+i/N, .6, 1), x=rng.uniform(X0+30, X1-30), y=rng.uniform(Y0+30, Y1-30),
           vx=rng.uniform(-2, 2), vy=rng.uniform(-2, 2), alive=True) for i in range(N)]
mets = []; booms = []; parts = []; nxt = 2.5; win_t = None; last_out = []
while True:
    t = o.t
    alive = [p for p in pl if p['alive']]
    if win_t and t > max(win_t+4, 61): break
    if t > 85: break
    if not win_t and t >= nxt and len(alive) > 1:
        frac = 1 - (len(alive)-1)/(N-1)
        gap = max(0.55, 2.4 - 1.6*min(1, t/50))
        tg = alive[rng.integers(len(alive))]
        aim = 0.6 + 0.4*min(1, t/55)  # meteors get more accurate
        mx = tg['x'] + rng.normal(0, 60*(1-aim)+10); my = tg['y'] + rng.normal(0, 60*(1-aim)+10)
        mets.append(dict(x=min(X1-20, max(X0+20, mx)), y=min(Y1-20, max(Y0+20, my)), t0=t, r=rng.uniform(34, 52), tg=tg))
        nxt = t + gap; o.sound(660, .08, .12, 25)
    for m in mets:
        if t - m['t0'] < 0.8 and m.get('tg') and m['tg']['alive']: m['x'] += (m['tg']['x']-m['x'])*.08; m['y'] += (m['tg']['y']-m['y'])*.08
    for m in mets[:]:
        if t - m['t0'] >= 1.3:
            mets.remove(m); booms.append([m['x'], m['y'], m['r'], 1.0]); o.sound(80, .45, .5, 6, "square"); o.sound(0, .3, .35, 10, "noise")
            hit = [p for p in alive if math.hypot(p['x']-m['x'], p['y']-m['y']) < m['r']+BR]
            plan = N - (N-1)*min(1, max(0, t-3)/50)
            if not hit and len(alive) > plan + 1:
                hit = [min(alive, key=lambda p: math.hypot(p['x']-m['x'], p['y']-m['y']))]
            if len(hit) >= len(alive): hit = hit[:len(alive)-1]
            for v in hit:
                v['alive'] = False; last_out = ([v['n']] + last_out)[:4]
                for _ in range(24):
                    th = rng.uniform(0, 6.28); s = rng.uniform(2, 7); parts.append([v['x'], v['y'], s*math.cos(th), s*math.sin(th), 1.0, v['c']])
            alive = [p for p in pl if p['alive']]
            if len(alive) == 1 and not win_t: win_t = t; fanfare(o, t)
    for p in alive:
        for m in mets:  # dodge
            dx, dy = p['x']-m['x'], p['y']-m['y']; d = math.hypot(dx, dy) or 1
            if d < m['r']+30: p['vx'] += dx/d*.15; p['vy'] += dy/d*.15
        if rng.random() < .03: p['vx'] += rng.uniform(-1.5, 1.5); p['vy'] += rng.uniform(-1.5, 1.5)
        sp = math.hypot(p['vx'], p['vy'])
        if sp > 3.8: p['vx'] *= 3.8/sp; p['vy'] *= 3.8/sp
        p['x'] += p['vx']; p['y'] += p['vy']
        if p['x'] < X0+BR or p['x'] > X1-BR: p['vx'] *= -1; p['x'] = min(X1-BR, max(X0+BR, p['x']))
        if p['y'] < Y0+BR or p['y'] > Y1-BR: p['vy'] *= -1; p['y'] = min(Y1-BR, max(Y0+BR, p['y']))
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([X0-8, Y0-8, X1+8, Y1+8], 20, fill=(34, 40, 30), outline=(120, 90, 60), width=6)
    for m in mets:
        k = (t-m['t0'])/1.3; rr = m['r']*(.4+.6*k)
        dr.ellipse([m['x']-rr, m['y']-rr*.6, m['x']+rr, m['y']+rr*.6], outline=RED if int(t*10) % 2 else (255, 160, 60), width=4)
        fy = m['y'] - (1-k)*700; fx = m['x'] + (1-k)*180
        if fy > Y0-200:
            dr.line([fx, fy, fx+40, fy-120], fill=(255, 150, 40), width=10)
            dr.ellipse([fx-16, fy-16, fx+16, fy+16], fill=(140, 90, 70), outline=(255, 120, 40), width=4)
    for b in booms:
        b[3] -= .06; rr = b[2]*(1.6-b[3]*.6)
        if b[3] > 0: dr.ellipse([b[0]-rr, b[1]-rr, b[0]+rr, b[1]+rr], fill=(255, int(140+100*b[3]), 40))
    booms = [b for b in booms if b[3] > 0]
    for q in parts:
        q[0] += q[2]; q[1] += q[3]; q[3] += .2; q[4] -= .035
        if q[4] > 0: dr.ellipse([q[0]-4, q[1]-4, q[0]+4, q[1]+4], fill=tuple(int(v*q[4]) for v in q[5]))
    parts = [q for q in parts if q[4] > 0]
    for p in alive:
        blob(dr, p['x'], p['y'], BR*(1.6 if win_t else 1), p['c'], p['vx'], p['vy'], p['n'] if (len(alive) <= 8 or win_t) else None)
    header(img, P.get("title", "SURVIVE THE METEORS!"), f"{len(alive)} left")
    if last_out and not win_t: out(dr, (AX, 438), "OUT: " + "  ".join(last_out), fit("OUT: " + "  ".join(last_out), 540, 26, fredoka), RED, sw=4)
    cta(img, f"{alive[0]['n']} SURVIVES!" if win_t else "Pick your survivor!", col=YEL if win_t else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("winner", [p['n'] for p in pl if p['alive']], o.t)
o.close()
