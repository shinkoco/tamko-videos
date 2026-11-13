"""Ring escape with a special rule: spawn / shrink / freeze."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
RULE = P.get("rule", "spawn"); CX, CY = AX, 720; N = P.get("n", 10); HUE0 = P.get("hue", 0.0)
TITLES = {"spawn": ("EVERY ESCAPE = +2 BALLS", "Can they break all the rings?"),
          "shrink": ("BALL SHRINKS EVERY BOUNCE", "Can it escape before it vanishes?"),
          "freeze": ("BALLS FREEZE AFTER 3 SEC", "Frozen balls become walls!")}
title, sub = TITLES[RULE]
SP = 190/(N-1)
rings = [dict(r=70+i*SP, gap=P.get("gap", 0.9), ang=rng.uniform(0, 6.28), spd=(0.8+0.05*i)*(1 if i % 2 else -1), hue=HUE0+i/N, alive=True) for i in range(N)]
def newball(x=CX, y=CY-10, r=None):
    return dict(x=x, y=y, vx=rng.uniform(-4, 4), vy=rng.uniform(-3, 0), r=r or (34 if RULE == "shrink" else 9), born=o.t, frozen=False, out=False)
balls = [newball()]; esc = 0; done_t = None; parts = []; notes = [261.6, 293.7, 329.6, 392, 440, 523.3]; ni = 0; snd = 0
while True:
    t = o.t
    if done_t and t > max(done_t+4, 61): break
    if t > 80: break
    inner = next((rg for rg in rings if rg['alive']), None)
    unlocked = t >= esc*52/N
    for b in balls:
        if b['frozen'] or b['out']: continue
        if RULE == "freeze" and t - b['born'] > 3 and inner:
            b['frozen'] = True; o.sound(1568, .2, .2, 12); balls.append(newball())
            fz = [q for q in balls if q['frozen']]
            if len(fz) > 6: balls.remove(fz[0])
            continue
        for _ in range(3):
            b['vy'] += .45/3; b['x'] += b['vx']/3; b['y'] += b['vy']/3
            if RULE == "freeze":
                for f in balls:
                    if f['frozen']:
                        dx, dy = b['x']-f['x'], b['y']-f['y']; d = math.hypot(dx, dy)
                        if 0 < d < b['r']+f['r']:
                            nx, ny = dx/d, dy/d; vn = b['vx']*nx+b['vy']*ny
                            if vn < 0: b['vx'] -= 2*vn*nx; b['vy'] -= 2*vn*ny
                            b['x'], b['y'] = f['x']+nx*(b['r']+f['r']), f['y']+ny*(b['r']+f['r'])
            if not inner:
                continue
            dx, dy = b['x']-CX, b['y']-CY; d = math.hypot(dx, dy)
            if d + b['r'] >= inner['r']:
                a = (math.atan2(dy, dx) - inner['ang']) % (2*math.pi)
                if a < inner['gap'] and unlocked and b['r']*2 < inner['gap']*inner['r']:
                    if d > inner['r'] + b['r']:
                        inner['alive'] = False; esc += 1; o.sound(700+40*esc, .35, .45, 8)
                        for _ in range(60):
                            th = rng.uniform(0, 6.28); s = rng.uniform(2, 8)
                            parts.append([CX+inner['r']*math.cos(th), CY+inner['r']*math.sin(th), s*math.cos(th), s*math.sin(th), 1.0, hsv(inner['hue'])])
                        if RULE == "spawn": balls += [newball(), newball()]
                        if esc == N: done_t = t; fanfare(o, t)
                        inner = next((rg for rg in rings if rg['alive']), None)
                else:
                    nx, ny = dx/d, dy/d; vn = b['vx']*nx + b['vy']*ny
                    if vn > 0:
                        b['vx'] -= 2*vn*nx; b['vy'] -= 2*vn*ny; sp = math.hypot(b['vx'], b['vy'])
                        if sp > 13: b['vx'] *= 13/sp; b['vy'] *= 13/sp
                        if sp < 6: b['vx'] *= 6/sp; b['vy'] *= 6/sp
                        if RULE == "shrink": b['r'] = max(5, b['r']*0.985)
                        if t-snd > .05: o.sound(notes[ni % 6], .14, .25); ni += 1; snd = t
                    b['x'] = CX + nx*(inner['r']-b['r']-.5); b['y'] = CY + ny*(inner['r']-b['r']-.5)
    if RULE == "spawn" and len(balls) > 60: balls = balls[-60:]
    for rg in rings: rg['ang'] += rg['spd']/FPS
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    for rg in rings:
        if not rg['alive']: continue
        if rg is inner and not unlocked:
            dr.ellipse([CX-rg['r'], CY-rg['r'], CX+rg['r'], CY+rg['r']], outline=hsv(rg['hue'], .8), width=6); continue
        dr.arc([CX-rg['r'], CY-rg['r'], CX+rg['r'], CY+rg['r']], math.degrees(rg['ang']+rg['gap']), math.degrees(rg['ang'])+360, fill=hsv(rg['hue'], .8), width=6)
    for q in parts:
        q[0] += q[2]; q[1] += q[3]; q[3] += .15; q[4] -= .03
        if q[4] > 0: dr.ellipse([q[0]-3, q[1]-3, q[0]+3, q[1]+3], fill=tuple(int(v*q[4]) for v in q[5]))
    parts = [q for q in parts if q[4] > 0]
    for b in balls:
        c = (150, 220, 255) if b['frozen'] else YEL
        dr.ellipse([b['x']-b['r'], b['y']-b['r'], b['x']+b['r'], b['y']+b['r']], fill=c, outline="white", width=2)
    header(img, P.get("title", title), f"Rings left: {N-esc}/{N}" + (f"  •  Balls: {len(balls)}" if RULE != "shrink" else ""))
    cta(img, "ESCAPED!" if done_t else sub, col=YEL if done_t else BLUE)
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("escape", RULE, esc, o.t)
o.close()
