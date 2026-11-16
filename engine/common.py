"""Shared drawing helpers for formats."""
import math
from brand import INK, fredoka, out

NPOOL = ["Mochi","Pip","Bloop","Tofu","Kiwi","Bean","Zuzu","Nugget","Waffle","Gizmo","Taro","Yuzu","Miso","Boba","Peanut","Sushi",
         "Dango","Nori","Pudding","Bubbles","Pickle","Noodle","Biscuit","Pebble","Sprout","Cocoa","Maple","Ziggy","Bolt","Ramen",
         "Wasabi","Kibo","Momo","Fuzzy","Jelly","Coco","Rocket","Pixel","Squish","Toffee"]

def blob(dr, x, y, r, col, vx=0, vy=0, name=None, nsize=18):
    dr.ellipse([x-r, y-r, x+r, y+r], fill=col, outline=INK, width=3)
    k = r/17; lx = max(-2, min(2, vx*.5))*k; ly = max(-2, min(2, vy*.5))*k
    for ex in (-6*k, 6*k):
        dr.ellipse([x+ex-4*k, y-7*k, x+ex+4*k, y+1*k], fill="white")
        dr.ellipse([x+ex+lx-2*k, y-5*k+ly, x+ex+lx+2*k, y-1*k+ly], fill="black")
    if name: out(dr, (x, y-r-12), name, fredoka(nsize), "white", sw=3)

def rot(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + px*c - py*s, cy + px*s + py*c) for px, py in pts]

def podium(dr, ranking, y=305):
    from brand import YEL, AX
    for i, nm in enumerate(ranking[:3]):
        out(dr, (AX, y+i*36), f"{i+1}. {nm}", fredoka(30), [YEL, (200, 200, 215), (230, 140, 70)][i], sw=4)

def fanfare(o, t):
    for k, fr in enumerate([523, 659, 784, 1047]): o.ev.append((t+.12*k, fr, .4, .35, 5, "sine"))

def music(o, dur, bpm=150, seed=0, vol=1.0):
    """Original chiptune loop: kick, hat, square bass, arpeggio."""
    import random
    r = random.Random(seed); b = 60/bpm
    root = r.choice([110, 98, 123.5, 104])
    prog = r.choice([[0, 5, 3, 4], [0, 3, 4, 4], [0, 5, 4, 3], [0, 4, 5, 3]])
    deg = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]
    def st(n): return root*2**(n/12)
    k = 0; t = 0.0
    while t < dur:
        bar = (k//8) % 4; ch = deg[prog[bar]]
        if k % 2 == 0: o.ev.append((t, 55, .12, .5*vol, 25, "sine"))
        o.ev.append((t+b/4, 8000, .03, .06*vol, 60, "noise"))
        o.ev.append((t, st(ch-12) if k % 2 == 0 else st(ch), b*.45, .11*vol, 6, "sq"))
        arp = [0, 4, 7, 12][k % 4] if prog[bar] in (0, 3) else [0, 3, 7, 12][k % 4]
        o.ev.append((t+b/2, st(ch+arp+12), b*.4, .07*vol, 9, "sine"))
        k += 1; t = k*b/2
