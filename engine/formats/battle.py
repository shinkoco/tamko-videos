import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
from PIL import Image, ImageDraw
POOL = [("FRA",(0,85,164)),("BRA",(0,156,59)),("JPN",(235,235,235)),("USA",(178,34,52)),("ITA",(0,146,70)),("ESP",(241,191,0)),
("GER",(40,40,40)),("MEX",(206,17,38)),("ARG",(116,172,223)),("CAN",(216,6,33)),("UK",(1,33,105)),("POR",(0,102,0)),("NED",(255,102,0)),
("BEL",(253,218,36)),("SUI",(213,43,30)),("SWE",(0,106,167)),("NOR",(186,12,47)),("POL",(220,20,60)),("TUR",(227,10,23)),("KOR",(205,46,58)),
("CHN",(222,41,16)),("IND",(255,153,51)),("AUS",(0,0,139)),("MAR",(193,39,45)),("ALG",(0,98,51)),("SEN",(0,133,63)),("EGY",(206,17,38)),
("COL",(252,209,22)),("CHI",(213,43,30)),("PER",(217,16,35)),("GRE",(13,94,175)),("UKR",(0,87,183)),("IRL",(22,155,98)),("CRO",(23,23,150)),
("NGA",(0,135,81)),("KSA",(0,108,53)),("THA",(45,42,74)),("VIE",(218,37,29)),("PHI",(0,56,168)),("IDN",(206,17,38))]
idx = rng.choice(len(POOL), 8, replace=False); C = [POOL[i] for i in idx]
def lum(c): return 0.3*c[0]+0.59*c[1]+0.11*c[2]
CX, CY, R, BR = AX, 735, P.get('R', 255), 34
balls = []
for i, (nm, c) in enumerate(C):
    a = i/8*6.28
    balls.append(dict(n=nm, c=c, x=CX+130*math.cos(a), y=CY+130*math.sin(a),
                      vx=rng.uniform(-6, 6), vy=rng.uniform(-6, 6), alive=True, out=False))
ang, last, out_list, win_t = 0.0, 0.0, [], None
F1, F2, F3 = font(52), fredoka(24), font(34)
while True:
    t = o.t
    if win_t and t > max(win_t+5, 61): break
    gap = 0.2 if win_t else (0.0 if t-last < 4 else 0.25+0.25*(t-last-4))
    ang += P.get('spin', 0.9)/FPS
    al = [b for b in balls if b['alive']]
    for b in balls:
        b['vy'] += 0.35; b['x'] += b['vx']; b['y'] += b['vy']
        if not b['alive'] or b['out']: continue
        dx, dy = b['x']-CX, b['y']-CY; d = math.hypot(dx, dy)
        if d > R-BR:
            a = (math.atan2(dy, dx)-ang) % 6.28
            if a < gap and len(al) > 1:
                if d > R+BR:
                    b['alive'] = False; b['out'] = True; last = t; out_list.append(b['n'])
                    o.sound(120, 0.5, 0.5, 6, "square"); o.sound(0, 0.3, 0.3, 12, "noise")
                    if len([q for q in balls if q['alive']]) == 1:
                        win_t = t
                        for k, fr in enumerate([523, 659, 784, 1047]): o.ev.append((t+0.15*k, fr, .4, .35, 5, "sine"))
            else:
                nx, ny = dx/d, dy/d; vn = b['vx']*nx+b['vy']*ny
                if vn > 0:
                    b['vx'] -= 2*vn*nx; b['vy'] -= 2*vn*ny
                    b['x'], b['y'] = CX+nx*(R-BR-1), CY+ny*(R-BR-1)
                    o.sound(330 + 40*C.index((b['n'], b['c'])), 0.1, 0.12)
    for i in range(len(al)):
        for j in range(i+1, len(al)):
            a, b = al[i], al[j]; dx, dy = b['x']-a['x'], b['y']-a['y']; d = math.hypot(dx, dy)
            if 0 < d < 2*BR:
                nx, ny = dx/d, dy/d; rv = (a['vx']-b['vx'])*nx + (a['vy']-b['vy'])*ny
                if rv > 0:
                    a['vx'] -= rv*nx; a['vy'] -= rv*ny; b['vx'] += rv*nx; b['vy'] += rv*ny
                    o.sound(700, 0.08, 0.2, 30)
                ov = (2*BR-d)/2; a['x'] -= nx*ov; a['y'] -= ny*ov; b['x'] += nx*ov; b['y'] += ny*ov
    for b in al:
        sp = math.hypot(b['vx'], b['vy'])
        if sp < 7: b['vx'] *= 7/max(sp, .1); b['vy'] *= 7/max(sp, .1)
        if sp > 15: b['vx'] *= 15/sp; b['vy'] *= 15/sp
    img = Image.new("RGB", (W, H), (14, 16, 30)); dr = ImageDraw.Draw(img)
    dr.arc([CX-R, CY-R, CX+R, CY+R], math.degrees(ang+gap), math.degrees(ang)+360, fill=(255, 255, 255), width=8)
    for b in balls:
        if b['y'] > H+100: continue
        x, y = b['x'], b['y']
        dr.ellipse([x-BR, y-BR, x+BR, y+BR], fill=b['c'], outline="white", width=3)
        tc = "black" if lum(b['c']) > 150 else "white"
        dr.text((x, y), b['n'], font=F2, fill=tc, anchor="mm")
    header(img, "WHO WILL WIN?", f"{len([b for b in balls if b['alive']])} countries left")
    d2 = ImageDraw.Draw(img)
    if out_list: out(d2, (AX, 438), "OUT: " + "  ".join(out_list), fit("OUT: " + "  ".join(out_list), 540, 26, fredoka), RED, sw=4)
    if win_t:
        w = [b for b in balls if b['alive']][0]
        cta(img, f"{w['n']} WINS! 🏆"[:-2], col=YEL)
    else: cta(img, "Comment your country!")
    o.frame(watermark(img))
for f in outro_frames(): o.frame(f)
o.close()
