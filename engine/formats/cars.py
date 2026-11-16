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
N = P.get("n", 8); L0, L1 = 70, 610; LANES = 5; LW = (L1-L0)/LANES
TOP, BOT = 480, 1280
names = list(rng.choice(CP, N, replace=False))
if P.get("tamko"): names[0] = "Tamko"
hue = P.get("hue", rng.random())
cars = [dict(n=names[i], c=YEL if names[i] == "Tamko" else hsv(hue+i/N, .75, 1), x=L0+LW*(i % LANES+.5), tx=None,
             y=900+(i//LANES)*110+rng.uniform(-30, 30), alive=True, spin=0, num=i) for i in range(N)]
for c in cars: c['tx'] = c['x']
# elimination plan: N-1 crashes spread between 5s and 57s
plan = sorted(rng.uniform(5, 57, N-1)); plan = [5+(57-5)*k/(N-2) + rng.uniform(-2, 2) for k in range(N-1)]
victims = []; obs = []; smoke = []; scroll = 0.0; nxt = 1.2; order = []; doomed = None
KINDS = ["cone", "oil", "truck", "rock", "barrel"]
music(o, 64, bpm=P.get("bpm", 150), seed=P.get("seed", 1))
def car_draw(dr, c, t):
    x, y = c['x'], c['y']; h = (t*16 if c['spin'] else 0) + (c['tx']-c['x'])*-0.01
    if not c['alive']:
        h = 0.6
    body = rot([(-17, -30), (17, -30), (17, 30), (-17, 30)], x, y, h)
    col = c['c'] if c['alive'] else (90, 90, 95)
    dr.polygon(body, fill=col, outline=INK)
    for wx, wy in [(-19, -18), (19, -18), (-19, 18), (19, 18)]:
        dr.polygon(rot([(wx-4, wy-7), (wx+4, wy-7), (wx+4, wy+7), (wx-4, wy+7)], x, y, h), fill=(20, 20, 25))
    dr.polygon(rot([(-13, -18), (13, -18), (13, -6), (-13, -6)], x, y, h), fill=(30, 40, 60))
    dr.polygon(rot([(-13, 14), (13, 14), (13, 22), (-13, 22)], x, y, h), fill=(30, 40, 60))
    if c['alive']: out(dr, (x, y-46), c['n'], fredoka(17), "white", sw=3)
def obs_draw(dr, ob):
    x, y, k = ob['x'], ob['y'], ob['k']
    if k == "cone":
        dr.polygon([(x, y-26), (x-18, y+18), (x+18, y+18)], fill=(255, 130, 30), outline=INK); dr.rectangle([x-12, y-2, x+12, y+5], fill="white")
    elif k == "oil":
        dr.ellipse([x-34, y-20, x+34, y+20], fill=(15, 15, 20)); dr.ellipse([x-14, y-12, x+4, y-4], fill=(70, 60, 110))
    elif k == "truck":
        dr.rectangle([x-26, y-70, x+26, y+60], fill=(200, 205, 215), outline=INK, width=3); dr.rectangle([x-22, y+40, x+22, y+70], fill=(220, 70, 70), outline=INK, width=3)
    elif k == "rock":
        dr.polygon([(x-28, y+18), (x-20, y-16), (x+4, y-26), (x+26, y-8), (x+24, y+20)], fill=(130, 120, 110), outline=INK)
    else:
        dr.ellipse([x-22, y-22, x+22, y+22], fill=(220, 60, 60), outline=INK, width=3); dr.ellipse([x-8, y-8, x+8, y+8], fill=(255, 220, 60))
while True:
    t = o.t
    alive = [c for c in cars if c['alive']]
    if len(alive) == 1 and not order: order = [alive[0]['n']]; fanfare(o, t); win_t = t
    if order and t > win_t+4 and t > 61: break
    if t > 75: break
    spd = 9 + 9*min(1, t/50)
    scroll = (scroll + spd) % 80
    # plan: pick a victim, send obstacle at it
    if plan and t >= plan[0] - 1.6 and doomed is None and len(alive) > 1:
        plan.pop(0); doomed = alive[rng.integers(len(alive))]
        obs.append(dict(x=doomed['x'], y=TOP-80, k=rng.choice(KINDS), target=doomed))
    if t >= nxt and not order:
        nxt = t + max(.35, 1.1 - t*0.012)
        lane = rng.integers(LANES); obs.append(dict(x=L0+LW*(lane+.5), y=TOP-80, k=rng.choice(KINDS), target=None))
    for ob in obs: ob['y'] += spd*(0.6 if ob['k'] == "truck" else 1)
    obs = [ob for ob in obs if ob['y'] < BOT+100]
    for c in alive:
        if c['spin']: c['spin'] -= 1; continue
        threat = [ob for ob in obs if ob['target'] is not c and abs(ob['x']-c['x']) < 50 and 0 < c['y']-ob['y'] < 260]
        if threat and c is not doomed:
            best = min(range(LANES), key=lambda l: (sum(1 for ob in obs if abs(ob['x']-(L0+LW*(l+.5))) < 50 and 0 < c['y']-ob['y'] < 320)*10 + abs(L0+LW*(l+.5)-c['x'])/LW + rng.random()*.5))
            c['tx'] = L0+LW*(best+.5)
        elif rng.random() < .01: c['tx'] = L0+LW*(rng.integers(LANES)+.5)
        if c is doomed and threat: c['tx'] = c['x']
        c['x'] += (c['tx']-c['x'])*.16
        c['y'] += (870 + 60*math.sin(t*.6+c['num']*1.9) + (c['num'] % 3)*70 - c['y'])*.02
        for other in alive:
            if other is not c and abs(other['x']-c['x']) < 40 and abs(other['y']-c['y']) < 70: c['y'] += 2 if c['y'] > other['y'] else -2
        for ob in obs:
            hw = 40 if ob['k'] != "truck" else 45; hh = 50 if ob['k'] != "truck" else 95
            if abs(ob['x']-c['x']) < hw and abs(ob['y']-c['y']) < hh and (ob['target'] is c or (c is not doomed and rng.random() < 0) ):
                c['alive'] = False; ob['y'] = BOT+200; doomed = None
                o.sound(160, .4, .5, 6, "noise"); o.sound(90, .3, .4, 8, "sine")
                for _ in range(22): smoke.append([c['x'], c['y'], rng.uniform(-4, 4), rng.uniform(-2, 6), 1.0])
                break
    if doomed is not None and not any(ob['target'] is doomed for ob in obs): doomed = None
    for c in cars:
        if not c['alive']: c['y'] += spd
    img = Image.new("RGB", (W, H), (60, 150, 80)); dr = ImageDraw.Draw(img)
    for k in range(-1, 12):
        yy = TOP + k*80 + scroll
        dr.rectangle([0, yy, L0-14, yy+40], fill=(70, 165, 90)); dr.rectangle([L1+14, yy+40, W, yy+80], fill=(70, 165, 90))
    dr.rectangle([L0-14, 0, L1+14, H], fill=(68, 68, 80))
    for k in range(-1, 12):
        yy = TOP + k*80 + scroll
        for e in (L0-14, L1+4):
            dr.rectangle([e, yy, e+10, yy+40], fill=RED); dr.rectangle([e, yy+40, e+10, yy+80], fill="white")
        for l in range(1, LANES):
            lx = L0+LW*l; dr.rectangle([lx-3, yy, lx+3, yy+40], fill=(235, 235, 235))
    for ob in obs: obs_draw(dr, ob)
    for sm in smoke:
        sm[0] += sm[2]; sm[1] += sm[3]+spd*.5; sm[4] -= .025
        if sm[4] > 0: g = int(110+110*sm[4]); r_ = 10+(1-sm[4])*22; dr.ellipse([sm[0]-r_, sm[1]-r_, sm[0]+r_, sm[1]+r_], fill=(g, g, g))
    smoke = [s for s in smoke if s[4] > 0]
    for c in cars:
        if c['y'] < BOT+80: car_draw(dr, c, t)
    for c in alive:
        if c['n'] == "Tamko": tamko_sprite(img, int(c['x']), int(c['y']), 26, t)
    dr.rectangle([0, 0, W, 470], fill=BG)
    header(img, P.get("title", "LAST CAR STANDING WINS"), None, y=240)
    podium(dr, order + [c['n'] for c in sorted(alive, key=lambda c: c['y'])] if not order else order)
    cta(img, f"{order[0]} WINS!" if order else f"{len(alive)} CARS LEFT  •  Pick your car!", y=440, col=YEL if order else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("done", order, o.t)
o.close()
