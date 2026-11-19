"""Plinko 'Pick 1 to 6': 6 numbered balls drop through pegs each round. OUT slot = eliminated,
other slots give points. Last ball standing (or most points) wins."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
X0, X1 = 60, 620; PY0, ROWS, DY = 560, 9, 50; SLOT_Y = PY0 + ROWS*DY + 20; FLOOR = SLOT_Y + 120
NB = 6; RB = 19; RP = 6
COLS = [(255, 90, 110), (255, 196, 40), (60, 200, 245), (120, 230, 120), (200, 120, 255), (255, 150, 60)]
pegs = []
for row in range(ROWS):
    n = 9 if row % 2 == 0 else 8
    for c in range(n): pegs.append((X0 + 30 + c*62.5 + (31 if row % 2 else 0), PY0 + row*DY))
pegs = np.array(pegs)
NS = 7; SW = (X1 - X0)/NS
layout = P.get("slots") or list(rng.permutation(["+1", "+3", "+2", "OUT", "+5", "+1", "+2"]))
pts = [0]*NB; alive = [True]*NB; elim_order = []
balls = []; rnd_n = 0; state = "drop"; t_state = 0.0; win = None; win_t = None; msg = ""; flash = {}
music(o, 70, bpm=P.get("bpm", 150), seed=P.get("seed", 1) + 3, vol=.8)
def new_round():
    global balls, rnd_n
    rnd_n += 1; balls = []
    ids = [i for i in range(NB) if alive[i]]
    for k, i in enumerate(ids):
        balls.append(dict(i=i, x=X0 + 40 + (k + .5)*(X1 - X0 - 80)/len(ids) + rng.uniform(-8, 8), y=480.0 + rng.uniform(0, 20),
                          vx=rng.uniform(-1, 1), vy=0.0, done=False, delay=k*.25))
new_round(); t_state = 0.0
while True:
    t = o.t
    if win_t and t > max(win_t + 4, 61): break
    if t > 85: break
    if win is None:
        for b in balls:
            if b['done'] or t - t_state < b['delay']: continue
            b['vy'] += .45; b['x'] += b['vx']; b['y'] += b['vy']; b['vx'] *= .995
            d = np.hypot(pegs[:, 0] - b['x'], pegs[:, 1] - b['y']); j = int(d.argmin())
            if d[j] < RB + RP:
                nx, ny = (b['x'] - pegs[j, 0])/d[j], (b['y'] - pegs[j, 1])/d[j]
                b['x'] = pegs[j, 0] + nx*(RB + RP); b['y'] = pegs[j, 1] + ny*(RB + RP)
                vn = b['vx']*nx + b['vy']*ny
                if vn < 0:
                    b['vx'] -= 1.5*vn*nx; b['vy'] -= 1.5*vn*ny; b['vx'] += rng.normal(0, .8)
                    if abs(vn) > 1.5: o.sound(600 + 40*b['i'], .05, .12, 40, "sine")
            if b['x'] < X0 + RB: b['x'] = X0 + RB; b['vx'] = abs(b['vx'])*.6
            if b['x'] > X1 - RB: b['x'] = X1 - RB; b['vx'] = -abs(b['vx'])*.6
            for c in balls:
                if c is b or c['done']: continue
                dx, dy = b['x'] - c['x'], b['y'] - c['y']; dd = math.hypot(dx, dy) or 1
                if dd < 2*RB: b['x'] += dx/dd*(2*RB - dd)/2; b['y'] += dy/dd*(2*RB - dd)/2
            if b['y'] > FLOOR - RB:
                b['y'] = FLOOR - RB; b['done'] = True
                s = min(NS - 1, max(0, int((b['x'] - X0)//SW))); b['slot'] = s; lab = layout[s]
                flash[s] = 1.0
                if lab == "OUT": o.sound(120, .4, .4, 6, "square")
                else: pts[b['i']] += int(lab[1:]); o.sound(880, .15, .25, 12, "sine")
        if balls and all(b['done'] for b in balls) and state == "drop":
            state, t_state2 = "show", t
            outs = [b['i'] for b in balls if layout[b['slot']] == "OUT"]
            left = [i for i in range(NB) if alive[i] and i not in outs]
            if left:  # if everyone falls OUT in the same round, nobody is eliminated
                for i in outs: alive[i] = False; elim_order.append(i)
                msg = ("OUT: " + " ".join(f"#{i+1}" for i in outs)) if outs else "Nobody out!"
            else: msg = "All OUT? Round replayed!"
            alive_ids = [i for i in range(NB) if alive[i]]
            if len(alive_ids) == 1 or (t > 52 and len(alive_ids) > 1):
                win = max(alive_ids, key=lambda i: pts[i]); win_t = t + .4; fanfare(o, t + .4)
        if state == "show" and t - t_state2 > 1.6 and win is None:
            state = "drop"; new_round(); t_state = t
    # draw
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    for (px, py) in pegs: dr.ellipse([px - RP, py - RP, px + RP, py + RP], fill=(210, 225, 255))
    for s in range(NS):
        x0 = X0 + s*SW; lab = layout[s]; f = flash.get(s, 0)
        col = RED if lab == "OUT" else YEL
        if f > 0: dr.rectangle([x0 + 3, SLOT_Y + 3, x0 + SW - 3, FLOOR], fill=tuple(int(c*f*.5) for c in col)); flash[s] = f - .04
        dr.line([(x0, SLOT_Y), (x0, FLOOR)], fill=(255, 196, 40), width=3)
        out(dr, (x0 + SW/2, FLOOR + 30), lab, lilita(32), col, sw=4)
    dr.line([(X1, SLOT_Y), (X1, FLOOR)], fill=(255, 196, 40), width=3); dr.line([(X0, FLOOR), (X1, FLOOR)], fill=(255, 196, 40), width=3)
    for b in balls:
        if t - t_state < b['delay'] and not b['done']: continue
        dr.ellipse([b['x'] - RB, b['y'] - RB, b['x'] + RB, b['y'] + RB], fill=COLS[b['i']], outline=INK, width=3)
        out(dr, (b['x'], b['y'] + 1), str(b['i'] + 1), lilita(22), "white", sw=3)
    # scoreboard
    for i in range(NB):
        x = X0 + 20 + i*((X1 - X0 - 40)/(NB - 1)); y = FLOOR + 80
        c = COLS[i] if alive[i] else (70, 75, 90)
        dr.ellipse([x - 20, y - 20, x + 20, y + 20], fill=c, outline=INK, width=3); out(dr, (x, y), str(i + 1), lilita(24), "white", sw=3)
        out(dr, (x, y + 36), "OUT" if not alive[i] else f"{pts[i]} pts", fredoka(20), RED if not alive[i] else "white", sw=3)
    header(img, P.get("title", "PICK 1 TO 6!"), f"Round {rnd_n}  •  " + (msg or "OUT = eliminated"))
    cta(img, f"#{win + 1} WINS!" if win is not None and t >= win_t else "Comment your number!", col=YEL)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("plinko", win, pts, o.t)
o.close()
