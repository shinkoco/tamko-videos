"""Guess the song: every bounce plays the next note of a PUBLIC-DOMAIN melody, with the real rhythm."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import *
from brand import *
from common import *
from PIL import Image, ImageDraw
P = json.loads(os.environ.get("TP", "{}"))
rng = np.random.default_rng(P.get("seed", 1))
o = Out(os.environ.get("TOUT", "out"))
def f(n):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    return 440*2**((names[n[:-1]] + 12*(int(n[-1])-4))/12)
def S(s): return [(tok.split(":")[0], float(tok.split(":")[1]) if ":" in tok else 1.0) for tok in s.split()]
# Public-domain melodies only (all composers died more than 70 years ago / traditional).
SONGS = {
 "Ode to Joy (Beethoven)": S("E4 E4 F4 G4 G4 F4 E4 D4 C4 C4 D4 E4 E4:1.5 D4:.5 D4:2 E4 E4 F4 G4 G4 F4 E4 D4 C4 C4 D4 E4 D4:1.5 C4:.5 C4:2"),
 "Twinkle Twinkle Little Star": S("C4 C4 G4 G4 A4 A4 G4:2 F4 F4 E4 E4 D4 D4 C4:2 G4 G4 F4 F4 E4 E4 D4:2 G4 G4 F4 F4 E4 E4 D4:2 C4 C4 G4 G4 A4 A4 G4:2 F4 F4 E4 E4 D4 D4 C4:2"),
 "Jingle Bells": S("E4 E4 E4:2 E4 E4 E4:2 E4 G4 C4:1.5 D4:.5 E4:4 F4 F4 F4:1.5 F4:.5 F4 E4 E4 E4:.5 E4:.5 E4 D4 D4 E4 D4:2 G4:2"),
 "Korobeiniki (Tetris theme)": S("E5 B4:.5 C5:.5 D5 C5:.5 B4:.5 A4 A4:.5 C5:.5 E5 D5:.5 C5:.5 B4:1.5 C5:.5 D5 E5 C5 A4 A4:2 D5:1.5 F5:.5 A5 G5:.5 F5:.5 E5:1.5 C5:.5 E5 D5:.5 C5:.5 B4 B4:.5 C5:.5 D5 E5 C5 A4 A4:2"),
 "Für Elise (Beethoven)": S("E5:.5 D#5:.5 E5:.5 D#5:.5 E5:.5 B4:.5 D5:.5 C5:.5 A4:1.5 C4:.5 E4:.5 A4:.5 B4:1.5 E4:.5 G#4:.5 B4:.5 C5:1.5 E4:.5 E5:.5 D#5:.5 E5:.5 D#5:.5 E5:.5 B4:.5 D5:.5 C5:.5 A4:1.5 C4:.5 E4:.5 A4:.5 B4:1.5 E4:.5 C5:.5 B4:.5 A4:2"),
 "In the Hall of the Mountain King (Grieg)": S("B3:.5 C#4:.5 D4:.5 E4:.5 F#4:.5 D4:.5 F#4 F4:.5 C#4:.5 F4 E4:.5 C4:.5 E4 B3:.5 C#4:.5 D4:.5 E4:.5 F#4:.5 D4:.5 F#4:.5 B4:.5 A4:.5 F#4:.5 D4:.5 F#4:.5 A4:2"),
}
names = list(SONGS); song = P.get("song") or names[rng.integers(len(names))]; MEL = SONGS[song]
CX, CY, R, r = AX, 720, 255, 16
BEAT0 = P.get("beat", 0.42)
# play the melody 3 times, each faster; reveal at the end
seq = []
k = 1.0
while sum(d for _, d in seq) < 50:
    seq += [(n, d*BEAT0*k) for n, d in MEL] + [(None, 1.0)]
    k = max(0.5, k*0.85)
x, y = CX, CY; a = rng.uniform(0, 6.28); dx, dy = math.cos(a), math.sin(a)
idx = 0; seg_t = 1.5; t_next = 1.5; trail = []; ripples = []; reveal_t = None; hue = rng.random()
def dist_to_wall(px, py, dx, dy):
    b = (px-CX)*dx + (py-CY)*dy; c = (px-CX)**2 + (py-CY)**2 - (R-r)**2
    return -b + math.sqrt(max(0, b*b - c))
sx, sy = x, y; ex, ey = x, y; t0 = 0
while True:
    t = o.t
    if reveal_t and t > reveal_t + 6: break
    if t > 85: break
    if t >= t_next and idx < len(seq):
        n, d = seq[idx]; idx += 1
        x, y = ex, ey
        if n:
            o.sound(f(n), min(.6, d*1.3), .45, 5); hue += .07; ripples.append([x, y, 1.0])
            nx, ny = (x-CX)/(R-r), (y-CY)/(R-r); dn = dx*nx + dy*ny
            if dn > 0: dx, dy = dx-2*dn*nx, dy-2*dn*ny
            th = rng.normal(0, .25); c, s = math.cos(th), math.sin(th); dx, dy = dx*c-dy*s, dx*s+dy*c
            nn = math.hypot(dx, dy); dx, dy = dx/nn, dy/nn
            if dx*nx + dy*ny > -0.2: dx, dy = -nx*0.8 + dy*0.2, -ny*0.8 - dx*0.2; nn = math.hypot(dx, dy); dx, dy = dx/nn, dy/nn
        L = dist_to_wall(x, y, dx, dy); sx, sy = x, y; ex, ey = x+dx*L, y+dy*L; t0 = t; t_next = t + d
        if idx == len(seq): reveal_t = t_next
    k = min(1, (t - t0)/max(1e-3, t_next - t0)) if idx < len(seq) or t < t_next else 1
    bx, by = sx + (ex-sx)*k, sy + (ey-sy)*k
    trail.append((bx, by)); trail = trail[-14:]
    img = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(img)
    dr.ellipse([CX-R-6, CY-R-6, CX+R+6, CY+R+6], fill=(22, 26, 46), outline=hsv(hue, .6, 1), width=6)
    for rp in ripples:
        rp[2] -= .05; rr = 50*(1-rp[2])
        if rp[2] > 0: dr.ellipse([rp[0]-rr, rp[1]-rr, rp[0]+rr, rp[1]+rr], outline=hsv(hue, .5, 1), width=3)
    ripples = [q for q in ripples if q[2] > 0]
    for i, (tx, ty) in enumerate(trail):
        rr = r*(i+1)/len(trail)*.8; dr.ellipse([tx-rr, ty-rr, tx+rr, ty+rr], fill=tuple(int(v*(i+1)/len(trail)*.6) for v in hsv(hue, .7, 1)))
    dr.ellipse([bx-r, by-r, bx+r, by+r], fill=hsv(hue, .7, 1), outline="white", width=3)
    header(img, P.get("title", "GUESS THE SONG!"), "Every bounce plays a note")
    if reveal_t and t >= reveal_t:
        d2 = ImageDraw.Draw(img); out(d2, (AX, 440), song, fit(song, 560, 44), YEL, sw=5)
        cta(img, "Did you get it?", col=BLUE)
    else: cta(img, "Comment the song before the reveal!", col=BLUE)
    o.frame(watermark(img))
for fr in outro_frames(): o.frame(fr)
print("melody", song, o.t)
o.close()
