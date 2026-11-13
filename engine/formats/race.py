import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
from PIL import Image, ImageDraw
NPOOL = ["Mochi","Pip","Bloop","Tofu","Kiwi","Bean","Zuzu","Nugget","Waffle","Gizmo","Taro","Yuzu","Miso","Boba","Peanut","Sushi","Dango","Nori","Pudding","Bubbles","Pickle","Noodle","Biscuit","Pebble","Sprout","Cocoa","Maple","Ziggy","Bolt","Ramen","Wasabi","Tamtam","Kibo","Momo","Fuzzy","Jelly","Coco","Rocket","Pixel","Squish"]
NAMES = list(rng.choice(NPOOL, 10, replace=False)); HUE0 = P.get("hue", 0.0)
BR, PR, SX, SY, Y0, FIN = 22, 8, P.get('sx', 92), P.get('sy', 120), 400, P.get('fin', 9600)
pegs_off = {}
blobs = [dict(n=nm, c=hsv(HUE0+i/10, .65, 1), x=80+i*52, y=200+rng.uniform(0, 40), vx=0, vy=0, done=None)
         for i, nm in enumerate(NAMES)]
order = []; F1, F2, F3 = font(48), font(22), font(30)
def pegs_near(x, y):
    r0 = int((y-Y0)/SY)
    for r in range(r0-1, r0+2):
        if r < 0: continue
        py = Y0 + r*SY
        if py > FIN-150: continue
        off = SX/2 if r % 2 else 0
        if r % P.get('gaprow', 9) == 4: continue  # free-fall rows
        c0 = int((x-off-40)/SX)
        for c in range(c0-1, c0+2):
            px = 40+off+c*SX
            if 30 < px < 610: yield px, py
pent = [392, 440, 523, 587, 659, 784]; snd_t = 0; cam = -320
while True:
    t = o.t
    if (len(order) == 10 and t > 61) or t > 75: break
    for b in blobs:
        if b['done'] is not None: continue
        b['vy'] += 0.42; b['vx'] *= 0.995; b['x'] += b['vx']; b['y'] += b['vy']
        if b['x'] < BR: b['x'] = BR; b['vx'] = abs(b['vx'])
        if b['x'] > 630-BR: b['x'] = 630-BR; b['vx'] = -abs(b['vx'])
        for px, py in pegs_near(b['x'], b['y']):
            dx, dy = b['x']-px, b['y']-py; d = math.hypot(dx, dy)
            if 0 < d < BR+PR:
                nx, ny = dx/d, dy/d; vn = b['vx']*nx+b['vy']*ny
                if vn < 0:
                    b['vx'] -= 1.55*vn*nx; b['vy'] -= 1.55*vn*ny; b['vx'] += rng.uniform(-1.2, 1.2)
                    if t-snd_t > 0.07: o.sound(pent[int(px) % 6], .12, .15); snd_t = t
                b['x'], b['y'] = px+nx*(BR+PR), py+ny*(BR+PR)
        if b['vy'] > 7.5: b['vy'] = 7.5
        if b['y'] >= FIN:
            b['done'] = t; order.append(b['n'])
            o.sound(523*(1.5 if len(order) == 1 else 1), .4, .4, 6)
            if len(order) == 1:
                for k, fr in enumerate([523, 659, 784, 1047]): o.ev.append((t+.12*k, fr, .4, .35, 5, "sine"))
    for i, a in enumerate(blobs):
        for b in blobs[i+1:]:
            if a['done'] or b['done']: continue
            dx, dy = b['x']-a['x'], b['y']-a['y']; d = math.hypot(dx, dy)
            if 0 < d < 2*BR:
                nx, ny = dx/d, dy/d; ov = (2*BR-d)/2
                a['x'] -= nx*ov; a['y'] -= ny*ov; b['x'] += nx*ov; b['y'] += ny*ov
                rv = (a['vx']-b['vx'])*nx + (a['vy']-b['vy'])*ny
                if rv > 0: a['vx'] -= rv*nx; a['vy'] -= rv*ny; b['vx'] += rv*nx; b['vy'] += rv*ny
    run = [b for b in blobs if b['done'] is None]
    target = (max(b['y'] for b in run) if run else FIN) - 700
    cam += (min(target, FIN-900) - cam)*0.08
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    for k in range(int(cam//400)-1, int((cam+H)//400)+2):  # soft stripes
        yy = k*400-cam
        dr.rectangle([0, yy, W, yy+200], fill=(20, 23, 42))
    r0 = int((cam-Y0)/SY)
    for r in range(max(0, r0-1), r0+int(H/SY)+2):
        py = Y0+r*SY
        if py > FIN-150 or r % P.get('gaprow', 9) == 4: continue
        off = SX/2 if r % 2 else 0
        for c in range(0, 9):
            px = 40+off+c*SX
            if 30 < px < 610:
                dr.ellipse([px-PR, py-cam-PR, px+PR, py-cam+PR], fill=(60, 170, 255))
    fy = FIN-cam+BR
    for k in range(0, W, 40):
        dr.rectangle([k, fy, k+20, fy+20], fill="white"); dr.rectangle([k+20, fy+20, k+40, fy+40], fill="white")
    for b in blobs:
        x, y = b['x'], b['y']-cam
        if b['done'] is not None:
            i = order.index(b['n']); x = 60+(i % 5)*150; y = FIN-cam+90+(i//5)*90
        if -50 < y < H+50:
            dr.ellipse([x-BR, y-BR, x+BR, y+BR], fill=b['c'], outline=INK, width=3)
            lx = max(-3, min(3, b['vx']*0.6)); ly = max(-3, min(3, b['vy']*0.4))
            for ex in (-8, 8):
                dr.ellipse([x+ex-6, y-9, x+ex+6, y+3], fill="white")
                dr.ellipse([x+ex+lx-3, y-6+ly, x+ex+lx+3, y+ly], fill="black")
            dr.text((x, y-BR-14), b['n'], font=fredoka(20), fill="white", anchor="mm")
    dr.rectangle([0, 0, W, 470], fill=BG)
    header(img, P.get("title", "WHO REACHES THE BOTTOM?"), None, y=240)
    ranking = order + [b['n'] for b in sorted(run, key=lambda b: -b['y'])]
    for i, nm in enumerate(ranking[:3]):
        col = [YEL, (200, 200, 215), (230, 140, 70)][i]
        out(dr, (AX, 305+i*36), f"{i+1}. {nm}", fredoka(30), col, sw=4)
    if order: cta(img, f"{order[0]} WINS!", y=440, col=YEL)
    else: cta(img, "Pick your runner!", y=440)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("finished", order, o.t)
o.close()
