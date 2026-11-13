import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
X0, Y0, X1, Y1 = 40, 480, 630, 975; N = P.get("n", 25); SP = P.get("speed", 0.6); RR = 14
NAMES = ["ROCK", "PAPER", "SCISSORS"]; COL = [(160, 160, 175), (245, 245, 235), (255, 90, 110)]
EATS = {0: 2, 1: 0, 2: 1}  # rock beats scissors, paper beats rock, scissors beats paper
u = []
for k in range(3):
    cx = [X0+100, X1-100, (X0+X1)/2][k]; cy = [Y1-90, Y1-90, Y0+90][k]
    for _ in range(N): u.append(dict(k=k, x=cx+rng.normal(0, 40), y=cy+rng.normal(0, 40), vx=0.0, vy=0.0))
win_t = None; snd = 0
def icon(dr, x, y, k):
    if k == 0: dr.ellipse([x-RR, y-RR*.85, x+RR, y+RR*.85], fill=COL[0], outline=INK, width=3); dr.ellipse([x-6, y-6, x-1, y-1], fill=(120, 120, 135))
    elif k == 1:
        dr.rectangle([x-RR*.8, y-RR, x+RR*.8, y+RR], fill=COL[1], outline=INK, width=3)
        for j in (-5, 0, 5): dr.line([x-7, y+j, x+7, y+j], fill=(150, 150, 170), width=2)
    else:
        dr.line([x-RR, y-RR, x+RR, y+RR], fill=COL[2], width=6); dr.line([x-RR, y+RR, x+RR, y-RR], fill=COL[2], width=6)
        dr.ellipse([x-RR-4, y+RR-8, x-RR+6, y+RR+2], outline=INK, width=3, fill=COL[2]); dr.ellipse([x+RR-6, y+RR-8, x+RR+4, y+RR+2], outline=INK, width=3, fill=COL[2])
while True:
    t = o.t
    counts = [sum(1 for a in u if a['k'] == k) for k in range(3)]
    if win_t and t > max(win_t+4, 61): break
    if t > 85: break
    sp = SP*(1 + max(0, t-30)*0.06)
    lead_k = counts.index(max(counts)); lead_frac = max(counts)/len(u)
    for a in u:
        prey = EATS[a['k']]; pred = [k for k, v in EATS.items() if v == a['k']][0]
        best = None; bd = 1e9; fx = fy = 0.0
        for b in u:
            if b is a: continue
            dx, dy = b['x']-a['x'], b['y']-a['y']; d = dx*dx+dy*dy
            if b['k'] == prey and d < bd: bd, best = d, b
            if b['k'] == pred and d < 120**2: dd = math.sqrt(d) or 1; fx -= dx/dd*(120-dd)/120; fy -= dy/dd*(120-dd)/120
        if best: dd = math.sqrt(bd) or 1; fx += (best['x']-a['x'])/dd; fy += (best['y']-a['y'])/dd
        fx += rng.normal(0, .35); fy += rng.normal(0, .35)
        if a['k'] == lead_k and lead_frac > .5 and t < 50: fx *= .4; fy *= .4
        a['vx'] = a['vx']*.85 + fx*.4; a['vy'] = a['vy']*.85 + fy*.4
        v = math.hypot(a['vx'], a['vy']) or 1
        if v > sp: a['vx'] *= sp/v; a['vy'] *= sp/v
        a['x'] = min(X1-RR, max(X0+RR, a['x']+a['vx'])); a['y'] = min(Y1-RR, max(Y0+RR, a['y']+a['vy']))
    for a in u:
        for b in u:
            if a['k'] != b['k'] and EATS[a['k']] == b['k'] and abs(a['x']-b['x']) < 2*RR and abs(a['y']-b['y']) < 2*RR:
                cnt = sum(1 for q in u if q['k'] == b['k']); kinds = len({q['k'] for q in u})
                if cnt == 1 and t < (42 if kinds == 3 else 52): continue  # last one standing is protected for drama
                b['k'] = a['k']
                if t-snd > .05: o.sound([220, 330, 440][a['k']]*2, .1, .25, 20); snd = t
    counts = [sum(1 for a in u if a['k'] == k) for k in range(3)]
    if not win_t and max(counts) == len(u):
        win_t = t; fanfare(o, t)
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([X0-8, Y0-8, X1+8, Y1+8], 20, fill=(24, 28, 50), outline=BLUE, width=6)
    for a in u:
        if counts[a['k']] == 1 and not win_t: dr.ellipse([a['x']-26, a['y']-26, a['x']+26, a['y']+26], outline=YEL, width=4)
        icon(dr, a['x'], a['y'], a['k'])
    header(img, P.get("title", "ROCK PAPER SCISSORS"), f"🪨 {counts[0]}   📄 {counts[1]}   ✂ {counts[2]}".replace("🪨", "Rock").replace("📄", "Paper").replace("✂", "Scissors"))
    if win_t: cta(img, f"{NAMES[counts.index(max(counts))]} WINS!", col=YEL)
    else: cta(img, "Who takes over? Comment!")
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
print("winner", counts, win_t, o.t)
o.close()
