"""Element duel: each side's balls bounce inside their own territory and convert every enemy cell they hit.
Biggest territory after the timer wins (fire vs water, ice vs lava...)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
DUELS = {"fire": (("FIRE", (235, 85, 40)), ("WATER", (40, 130, 230))), "ice": (("ICE", (150, 225, 255)), ("LAVA", (230, 70, 30))),
         "day": (("DAY", (255, 205, 60)), ("NIGHT", (40, 50, 110))), "grass": (("GRASS", (90, 200, 90)), ("SAND", (225, 190, 110)))}
(NA, CA), (NB_, CB) = DUELS[P.get("duel", "fire")]
G = 24; X0, Y0 = 80, 490; CS = 560/G; DUR = P.get("dur", 52)
grid = np.zeros((G, G), int); grid[:, G//2:] = 1  # 0 = side A (left), 1 = side B
NPER = P.get("per", 3); SPD = P.get("speed", 7.0); RB = 11
balls = []
for side in (0, 1):
    for k in range(NPER):
        a = rng.uniform(0, 2*math.pi)
        balls.append(dict(s=side, x=X0 + (G*CS*(.25 if side == 0 else .75)) + rng.uniform(-40, 40), y=Y0 + G*CS*(k + .5)/NPER,
                          vx=SPD*math.cos(a), vy=SPD*math.sin(a)))
win = None; win_t = None; boost = 1.0; power = None; p_until = 0; next_p = 8.0
music(o, 70, bpm=P.get("bpm", 150), seed=P.get("seed", 1) + 11, vol=.8)
def light(c, f): return tuple(min(255, int(v*f)) for v in c)
while True:
    t = o.t
    if win_t and t > max(win_t + 4, 61): break
    pa = (grid == 0).mean()
    if win is None:
        boost = 1 + max(0, t - 25)*.02
        if t >= next_p:
            power = int(rng.integers(0, 2)); p_until = t + 4.5; next_p = t + rng.uniform(8, 11)
            o.sound(700, .3, .35, 6, "square"); o.sound(1050, .3, .3, 6, "square")
        if power is not None and t > p_until: power = None
        for b in balls:
            for _ in range(2):  # sub-steps
                f = boost*(1.7 if power == b['s'] else 1.0)
                b['x'] += b['vx']*f/2; b['y'] += b['vy']*f/2
                if b['x'] < X0 + RB or b['x'] > X0 + G*CS - RB: b['vx'] *= -1; b['x'] = min(max(b['x'], X0 + RB), X0 + G*CS - RB)
                if b['y'] < Y0 + RB or b['y'] > Y0 + G*CS - RB: b['vy'] *= -1; b['y'] = min(max(b['y'], Y0 + RB), Y0 + G*CS - RB)
                for ox, oy in ((RB, 0), (-RB, 0), (0, RB), (0, -RB)):
                    gx, gy = int((b['x'] + ox - X0)//CS), int((b['y'] + oy - Y0)//CS)
                    if 0 <= gx < G and 0 <= gy < G and grid[gy, gx] != b['s']:
                        grid[gy, gx] = b['s']
                        if ox: b['vx'] = -b['vx']
                        else: b['vy'] = -b['vy']
                        o.sound(500 + 300*b['s'] + rng.integers(0, 60), .04, .1, 40, "sine")
                        break
            a = math.atan2(b['vy'], b['vx']) + rng.normal(0, .02); sp = math.hypot(b['vx'], b['vy'])
            b['vx'], b['vy'] = sp*math.cos(a), sp*math.sin(a)
        if t >= DUR:
            win = 0 if pa >= .5 else 1; win_t = t; fanfare(o, t)
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    for gy in range(G):
        for gx in range(G):
            c = CA if grid[gy, gx] == 0 else CB
            if (gx + gy) % 2: c = light(c, .9)
            dr.rectangle([X0 + gx*CS, Y0 + gy*CS, X0 + (gx + 1)*CS - 1, Y0 + (gy + 1)*CS - 1], fill=c)
    dr.rectangle([X0 - 4, Y0 - 4, X0 + G*CS + 3, Y0 + G*CS + 3], outline=(255, 196, 40), width=4)
    for b in balls:
        c = light(CB if b['s'] == 0 else CA, 1.0)  # each ball wears its side's colour with a white rim
        own = CA if b['s'] == 0 else CB
        rr = RB + (4 if power == b['s'] else 0)
        dr.ellipse([b['x'] - rr - 5, b['y'] - rr - 5, b['x'] + rr + 5, b['y'] + rr + 5], fill=INK)
        dr.ellipse([b['x'] - rr, b['y'] - rr, b['x'] + rr, b['y'] + rr], fill="white", outline=light(own, 1.2), width=6)
    # live percentage bar
    by = Y0 + G*CS + 40; bw = G*CS
    dr.rectangle([X0, by, X0 + bw*pa, by + 34], fill=CA); dr.rectangle([X0 + bw*pa, by, X0 + bw, by + 34], fill=CB)
    dr.rectangle([X0, by, X0 + bw, by + 34], outline="white", width=3)
    out(dr, (X0 + 8, by + 70), f"{NA} {pa*100:.0f}%", lilita(44), light(CA, 1.2), anc="lm", sw=5)
    out(dr, (X0 + bw - 8, by + 70), f"{(1 - pa)*100:.0f}% {NB_}", lilita(44), light(CB, 1.3), anc="rm", sw=5)
    left = max(0, DUR - t)
    header(img, P.get("title", f"{NA} VS {NB_}"), (f"{[NA, NB_][power]} SPEED BOOST!" if power is not None and win is None else f"Time left: {left:4.1f}s  •  biggest area wins"))
    cta(img, f"{[NA, NB_][win]} WINS!" if win is not None else "Pick your side!", col=YEL)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("territory", NA, NB_, win, round(pa, 3), o.t)
o.close()
