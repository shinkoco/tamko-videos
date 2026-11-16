import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
NM = ["Apollo","Nova","Comet","Orbit","Luna","Astro","Zenith","Pulsar","Quasar","Vega","Rigel","Titan","Cosmo","Halley","Sirius","Atlas"]
N = P.get("n", 8); L0, L1 = 60, 620; COLS = 6; CW = (L1-L0)/COLS; TOP, BOT = 480, 1280
names = list(rng.choice(NM, N, replace=False))
if P.get("tamko"): names[0] = "Tamko"
hue = P.get("hue", rng.random())
ships = [dict(n=names[i], c=YEL if names[i] == "Tamko" else hsv(hue+i/N, .7, 1), x=L0+CW*(i % COLS+.5), y=1000+(i//COLS)*110,
              alive=True, num=i) for i in range(N)]
for s in ships: s['tx'] = s['x']
plan = [5+(57-5)*k/(N-2)+rng.uniform(-2, 2) for k in range(N-1)]
stars = [[rng.uniform(0, W), rng.uniform(TOP, H), rng.uniform(1, 3)] for _ in range(90)]
obs = []; boom = []; order = []; doomed = None; nxt = 1.0; win_t = 0
INV = ["..X.....X..", "...X...X...", "..XXXXXXX..", ".XX.XXX.XX.", "XXXXXXXXXXX", "X.XXXXXXX.X", "X.X.....X.X", "...XX.XX..."]
INV2 = ["...XXXX...", ".XXXXXXXX.", "XXXXXXXXXX", "XXX.XX.XXX", "XXXXXXXXXX", "..XX..XX..", ".XX.XX.XX.", "X........X"]
music(o, 66, bpm=P.get("bpm", 155), seed=P.get("seed", 1)+7)
def inv_draw(dr, x, y, col, t, alt):
    g = INV if alt else INV2; px = 7
    for j, row in enumerate(g):
        for i, ch in enumerate(row):
            if ch == "X": dr.rectangle([x+(i-len(row)/2)*px, y+(j-4)*px, x+(i-len(row)/2+1)*px-1, y+(j-3)*px-1], fill=col)
def ship_draw(img, dr, s, t):
    x, y = s['x'], s['y']
    if s['n'] == "Tamko":
        tamko_sprite(img, int(x), int(y), 40, t)
    else:
        dr.polygon([(x, y-34), (x-15, y+10), (x+15, y+10)], fill=s['c'], outline=INK)
        dr.polygon([(x-15, y+2), (x-26, y+22), (x-12, y+18)], fill=RED, outline=INK)
        dr.polygon([(x+15, y+2), (x+26, y+22), (x+12, y+18)], fill=RED, outline=INK)
        dr.ellipse([x-7, y-16, x+7, y-2], fill=(150, 220, 255), outline=INK)
    fl = 12+6*math.sin(t*40+s['num'])
    dr.polygon([(x-8, y+18), (x+8, y+18), (x, y+18+fl)], fill=(255, 170, 40)); dr.polygon([(x-4, y+18), (x+4, y+18), (x, y+10+fl)], fill=(255, 240, 160))
    out(dr, (x, y-50), s['n'], fredoka(17), "white", sw=3)
def spawn(target=None):
    k = rng.choice(["inv", "inv2", "ast", "laser"], p=[.35, .25, .25, .15])
    x = target['x'] if target else L0+CW*(rng.integers(COLS)+.5)
    obs.append(dict(x=x, y=TOP-60, k=k, target=target, col=hsv(rng.random(), .6, 1), r=rng.uniform(28, 44), a=rng.uniform(0, 6)))
while True:
    t = o.t
    alive = [s for s in ships if s['alive']]
    if len(alive) == 1 and not order: order = [alive[0]['n']]; fanfare(o, t); win_t = t
    if order and t > win_t+4 and t > 61: break
    if t > 85: break
    spd = 8 + 9*min(1, t/50)
    if not plan and len(alive) > 1 and doomed is None: plan.append(t+1.6)
    if plan and t >= plan[0]-1.6 and doomed is None and len(alive) > 1:
        plan.pop(0); doomed = alive[rng.integers(len(alive))]; spawn(doomed)
    if t >= nxt and not order: nxt = t+max(.22, .7-t*.008); spawn()
    for ob in obs:
        ob['y'] += spd*(1.6 if ob['k'] == "laser" else 1); ob['a'] += .05
        if ob['k'] in ("inv", "inv2") and ob['target'] is None: ob['x'] += math.sin(t*4+ob['a'])*2
    obs = [ob for ob in obs if ob['y'] < BOT+80]
    for s in alive:
        threat = [ob for ob in obs if ob['target'] is not s and abs(ob['x']-s['x']) < 55 and 0 < s['y']-ob['y'] < 280]
        if s is doomed:
            s['tx'] = next((ob['x'] for ob in obs if ob['target'] is s), s['tx'])
        elif threat:
            best = min(range(COLS), key=lambda l: sum(1 for ob in obs if abs(ob['x']-(L0+CW*(l+.5))) < 55 and 0 < s['y']-ob['y'] < 340)*10 + abs(L0+CW*(l+.5)-s['x'])/CW + rng.random()*.5)
            s['tx'] = L0+CW*(best+.5)
        elif rng.random() < .012: s['tx'] = L0+CW*(rng.integers(COLS)+.5)
        s['x'] += (s['tx']-s['x'])*.17
        for q in alive:
            if q is not s and abs(q['x']-s['x']) < 46 and abs(q['y']-s['y']) < 80:
                s['y'] += 3 if s['y'] >= q['y'] else -3
                if s is not doomed: s['x'] += 2 if s['x'] >= q['x'] else -2
        s['x'] = min(L1-20, max(L0+20, s['x']))
        s['y'] += (930+60*math.sin(t*.7+s['num']*2.1)+(s['num'] % 3)*75 - s['y'])*.02
        for ob in obs:
            if ob['target'] is s and abs(ob['x']-s['x']) < 40 and abs(ob['y']-s['y']) < 45:
                s['alive'] = False; ob['y'] = BOT+300; doomed = None
                o.sound(140, .5, .5, 5, "noise"); o.sound(70, .4, .4, 6, "sine")
                for _ in range(30): boom.append([s['x'], s['y'], rng.uniform(-6, 6), rng.uniform(-6, 6), 1.0, hsv(rng.uniform(.0, .15), .9, 1)])
                break
    if doomed is not None and not any(ob['target'] is doomed for ob in obs): doomed = None
    img = Image.new("RGB", (W, H), (8, 6, 24)); dr = ImageDraw.Draw(img)
    for st in stars:
        st[1] += spd*st[2]*.25
        if st[1] > H: st[1] = TOP; st[0] = rng.uniform(0, W)
        g = int(120+40*st[2]); dr.rectangle([st[0], st[1], st[0]+st[2], st[1]+st[2]*3], fill=(g, g, 255))
    for ob in obs:
        x, y = ob['x'], ob['y']
        if ob['k'] in ("inv", "inv2"): inv_draw(dr, x, y, ob['col'], t, (int(t*4) % 2 == 0) ^ (ob['k'] == "inv2"))
        elif ob['k'] == "ast":
            pts = [(x+ob['r']*(1+.25*math.sin(i*2.3))*math.cos(ob['a']+i*math.pi/4), y+ob['r']*(1+.25*math.sin(i*2.3))*math.sin(ob['a']+i*math.pi/4)) for i in range(8)]
            dr.polygon(pts, fill=(140, 120, 110), outline=INK)
        else:
            dr.rectangle([x-5, y-34, x+5, y+34], fill=(255, 60, 120)); dr.rectangle([x-2, y-30, x+2, y+30], fill="white")
    for b in boom:
        b[0] += b[2]; b[1] += b[3]; b[4] -= .03
        if b[4] > 0: r_ = 4+10*b[4]; dr.ellipse([b[0]-r_, b[1]-r_, b[0]+r_, b[1]+r_], fill=b[5])
    boom = [b for b in boom if b[4] > 0]
    for s in alive: ship_draw(img, dr, s, t)
    dr.rectangle([0, 0, W, 470], fill=BG)
    header(img, P.get("title", "LAST ROCKET STANDING WINS"), None, y=240)
    podium(dr, order if order else [s['n'] for s in sorted(alive, key=lambda s: s['y'])])
    cta(img, f"{order[0]} WINS!" if order else f"{len(alive)} ROCKETS LEFT  •  Pick yours!", y=440, col=YEL if order else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("done", order, o.t)
o.close()
