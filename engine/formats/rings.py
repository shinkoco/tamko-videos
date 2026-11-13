import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
from PIL import Image, ImageDraw
CX, CY = AX, 700
N = P.get('n', 14); SP = 200/(N-1); HUE0 = P.get('hue', 0.0)
rings = [dict(r=62+i*SP, gap=P.get('gap', 0.95), ang=rng.uniform(0, 6.28), spd=(P.get('spin', 0.9)+0.05*i)*(1 if i % 2 else -1),
              hue=HUE0+i/N, alive=True) for i in range(N)]
ball = dict(x=CX, y=CY-15, vx=3.0, vy=0.0, r=9)
G = P.get('g', 0.55); trail = []; particles = []; escaped = 0; done_t = None
notes = [261.6, 293.7, 329.6, 392.0, 440.0, 523.3, 587.3, 659.3]; ni = 0
while True:
    t = o.t
    if done_t and t > max(done_t+4, 61): break
    if t > 75: break
    for _ in range(4):
        ball['vy'] += G/4; ball['x'] += ball['vx']/4; ball['y'] += ball['vy']/4
        dx, dy = ball['x']-CX, ball['y']-CY; d = math.hypot(dx, dy)
        inner = next((rg for rg in rings if rg['alive']), None)
        if inner and d + ball['r'] >= inner['r']:
            a = (math.atan2(dy, dx) - inner['ang']) % (2*math.pi)
            if a < inner['gap'] and t >= escaped*52/N:
                if d > inner['r'] + ball['r']:
                    inner['alive'] = False; escaped += 1
                    o.sound(700 + 50*escaped, .35, .45, 8)
                    col = hsv(inner['hue'])
                    for k in range(70):
                        th = rng.uniform(0, 6.28); sp = rng.uniform(2, 9)
                        particles.append([CX+inner['r']*math.cos(th), CY+inner['r']*math.sin(th), sp*math.cos(th), sp*math.sin(th), 1.0, col])
                    if escaped == N:
                        done_t = t
                        for k, fr in enumerate([523, 659, 784, 1047]): o.ev.append((t+.12*k, fr, .4, .35, 5, "sine"))
            else:
                nx, ny = dx/d, dy/d; vn = ball['vx']*nx + ball['vy']*ny
                if vn > 0:
                    ball['vx'] -= 2.0*vn*nx; ball['vy'] -= 2.0*vn*ny
                    sp = math.hypot(ball['vx'], ball['vy'])
                    if sp > 13: ball['vx'] *= 13/sp; ball['vy'] *= 13/sp
                    ball['x'] = CX + nx*(inner['r']-ball['r']-0.5); ball['y'] = CY + ny*(inner['r']-ball['r']-0.5)
                    o.sound(notes[ni % 8], .15, .3); ni += 1
        if not inner:
            if ball['y'] > H+50 or ball['x'] < -50 or ball['x'] > W+50:
                ball.update(x=CX, y=CY-15, vx=rng.uniform(-4, 4), vy=0)
    for rg in rings: rg['ang'] += rg['spd']/FPS
    trail.append((ball['x'], ball['y'])); trail = trail[-12:]
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    first = next((rg for rg in rings if rg['alive']), None)
    for rg in rings:
        if not rg['alive']: continue
        if rg is first and t < escaped*52/N:
            dr.ellipse([CX-rg['r'], CY-rg['r'], CX+rg['r'], CY+rg['r']], outline=hsv(rg['hue'], .8), width=6); continue
        a0 = math.degrees(rg['ang'] + rg['gap']); a1 = math.degrees(rg['ang']) + 360
        dr.arc([CX-rg['r'], CY-rg['r'], CX+rg['r'], CY+rg['r']], a0, a1, fill=hsv(rg['hue'], .8), width=6)
    for i, (x, y) in enumerate(trail):
        rr = ball['r']*(i+1)/len(trail)*0.8
        dr.ellipse([x-rr, y-rr, x+rr, y+rr], fill=(int(255*i/len(trail)), int(205*i/len(trail)), int(60*i/len(trail))))
    for p in particles:
        p[0] += p[2]; p[1] += p[3]; p[3] += 0.15; p[4] -= 0.03
        if p[4] > 0:
            c = tuple(int(v*p[4]) for v in p[5]); dr.ellipse([p[0]-3, p[1]-3, p[0]+3, p[1]+3], fill=c)
    particles = [p for p in particles if p[4] > 0]
    x, y, r = ball['x'], ball['y'], ball['r']
    dr.ellipse([x-r, y-r, x+r, y+r], fill=YEL, outline="white", width=2)
    header(img, "CAN THE BALL ESCAPE?", f"Rings left: {N-escaped}/{N}")
    if done_t: cta(img, "ESCAPED!", col=YEL)
    else: cta(img, "Will it make it? Comment!")
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("escaped", escaped, o.t)
o.close()
