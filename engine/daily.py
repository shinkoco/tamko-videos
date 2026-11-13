"""Generate N Tamko videos with fresh random variants.
Usage: python3 daily.py OUTDIR [count]
Writes OUTDIR/<name>.mp4 and OUTDIR/manifest.json [{file, format, caption}].
Keeps engine/history.json so consecutive runs rotate formats."""
import os, sys, json, random, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "out")
COUNT = int(sys.argv[2]) if len(sys.argv) > 2 else 2
os.makedirs(OUT, exist_ok=True)
HIST = os.path.join(HERE, "history.json")
hist = json.load(open(HIST)) if os.path.exists(HIST) else []
rnd = random.Random()

def params(fmt):
    p = {"seed": rnd.randrange(1, 10**9)}
    if fmt == "dup":
        p.update(max=rnd.choice([1000, 1500, 2000, 2500, 3000]), g=rnd.uniform(0.35, 0.55), hue=rnd.random(),
                 title=rnd.choice(["EVERY BOUNCE = +1 BALL", "1 BOUNCE = 1 NEW BALL", "HOW MANY BALLS?"]))
    elif fmt == "battle":
        p.update(R=rnd.choice([240, 255, 270]), spin=rnd.uniform(0.6, 1.3))
    elif fmt == "race":
        p.update(sx=rnd.choice([84, 92, 100]), sy=rnd.choice([110, 120, 130]), gaprow=rnd.choice([7, 9, 11]),
                 hue=rnd.random(), fin=rnd.choice([8800, 9600, 10400]),
                 title=rnd.choice(["WHO REACHES THE BOTTOM?", "WHO WINS THE RACE?", "PICK YOUR RUNNER!"]))
    elif fmt == "survival":
        p.update(n=rnd.choice([16, 20, 24]), hue=rnd.random(), round=rnd.uniform(4.0, 4.8),
                 title=rnd.choice(["WHO SURVIVES?", "LAST ONE STANDING", "SURVIVE THE TRAPS!"]))
    elif fmt == "ducks":
        p.update(n=rnd.choice([6, 8]), fin=rnd.choice([5600, 6200, 6800]), rock_gap=rnd.choice([220, 260, 300]),
                 pool_gap=rnd.choice([1200, 1500, 1800]), title=rnd.choice(["WHICH DUCK WINS?", "DUCK RACE!", "PICK YOUR DUCK!"]))
    elif fmt == "rings":
        p.update(n=rnd.choice([10, 12, 14, 16]), gap=rnd.uniform(0.85, 1.1), g=rnd.uniform(0.45, 0.6),
                 spin=rnd.uniform(0.7, 1.2), hue=rnd.random())
    return p

CAPS = {
    "dup": ["Every bounce = +1 ball 🤯 How many at the end? Guess below! 👇",
            "1 ball becomes chaos 😳 Drop your guess for the final count 👇",
            "Watch it multiply... how many balls do you think? 👇"],
    "battle": ["8 countries enter. Only 1 survives 🏆 Comment your country! 👇",
               "Which country wins this time? 🌍 Pick yours before the end 👇",
               "Country battle! Last one standing wins 🏆 Who's your pick? 👇"],
    "race": ["10 tiny runners, 1 winner 🏁 Pick your runner in the comments! 👇",
             "Who reaches the bottom first? 🏁 Choose now, no cheating 👀👇",
             "Tiny race, big drama 🏁 Comment your champion! 👇"],
    "rings": ["Can the ball escape every ring? 👀 Comment YES or NO! 👇",
              "Ring after ring... will it make it out? 🔥 Guess below 👇",
              "The ball vs the rings 💥 Who wins? Comment before the end 👇"],
}
CAPS["survival"] = ["Traps every round. Only 1 survives 💀 Pick your survivor! 👇",
    "Who makes it to the end? 😱 Comment your pick before round 1 👇",
    "Last one standing wins 🏆 Choose wisely 👇"]
CAPS["ducks"] = ["Duck race! 🦆 Pick your duck before the finish line 👇",
    "Rocks, whirlpools and 1 winner 🦆 Which duck do you pick? 👇",
    "The cutest race on TikTok 🦆 Comment your champion! 👇"]
TAGS = {"survival": "#satisfying #survival #whowillwin #lastonestanding #fyp",
        "ducks": "#duckrace #satisfying #whowillwin #cute #fyp","dup": "#satisfying #oddlysatisfying #physics #chaos #fyp",
        "battle": "#countryballs #satisfying #whowillwin #countries #fyp",
        "race": "#marblerace #satisfying #whowillwin #race #fyp",
        "rings": "#satisfying #oddlysatisfying #ballgame #physics #fyp"}

ALL = ["dup", "battle", "race", "rings", "survival", "ducks"]
YT = {"dup": ["Every bounce = +1 ball 🤯", "1 ball becomes chaos 😳", "How many balls at the end? 🤯"],
      "battle": ["8 countries, only 1 survives 🏆", "Which country wins? 🌍", "Country battle royale 🏆"],
      "race": ["Who reaches the bottom first? 🏁", "Tiny race, big drama 🏁", "Pick your runner! 🏁"],
      "rings": ["Can the ball escape? 👀", "Ball vs rings 💥", "Will it make it out? 🔥"],
      "survival": ["Only 1 survives the traps 💀", "Last one standing wins 🏆", "Who survives? 😱"],
      "ducks": ["Duck race! Pick your duck 🦆", "Which duck wins? 🦆", "The cutest race ever 🦆"]}
YTAGS = {"dup": ["oddly satisfying", "physics", "bouncing balls", "chaos"], "battle": ["countryballs", "country battle", "countries"],
         "race": ["marble race", "race", "cute"], "rings": ["oddly satisfying", "ball escape", "physics"],
         "survival": ["survival", "last one standing", "elimination"], "ducks": ["duck race", "rubber duck", "cute"]}
FC = {"dup": ["What was your guess? 🤯 Comment the number!", "Did you guess right? 👀 Drop your number below!"],
      "battle": ["Which country did you pick? 🌍 Comment yours!", "Did your country win? 🏆 Tell us below!"],
      "race": ["Who did you pick? 🏁 Drop your runner below!", "Did your runner win? 🏁 Comment!"],
      "rings": ["Did you say YES or NO? 👀 Comment below!", "Called it? 🔥 Tell us below!"],
      "survival": ["Who was your survivor? 💀 Comment below!", "Did your pick survive? 😱 Tell us!"],
      "ducks": ["Which duck did you pick? 🦆 Comment below!", "Did your duck win? 🦆 Tell us!"]}
FC = {k: [x + " Subscribe for a new game every day!" for x in v] for k, v in FC.items()}
last = [h["format"] for h in hist[-4:]]
fmts = [f for f in ALL if f not in last]
rnd.shuffle(fmts); fmts = (fmts + [f for f in ALL if f not in fmts])[:COUNT]
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
man = []
for i, fmt in enumerate(fmts):
    for attempt in range(3):
        p = params(fmt); name = f"tamko_{stamp}_{i}_{fmt}"
        env = dict(os.environ, TP=json.dumps(p), TOUT=name, OUTDIR=OUT)
        subprocess.run([sys.executable, os.path.join(HERE, "formats", fmt + ".py")], env=env, check=True,
                       stdout=subprocess.DEVNULL)
        f = os.path.join(OUT, name + ".mp4")
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                   capture_output=True, text=True).stdout or 0)
        if dur >= 60: break
        os.remove(f)
    cap = rnd.choice(CAPS[fmt]) + " " + TAGS[fmt]
    yt = rnd.choice(YT[fmt]) + " #shorts"
    ytags = YTAGS[fmt] + ["satisfying", "simulation", "who will win", "tamko"]
    fc = rnd.choice(FC[fmt])
    man.append({"file": name + ".mp4", "format": fmt, "caption": cap, "yt_title": yt, "yt_caption": cap.replace("#fyp", "#shorts"), "yt_tags": ytags, "yt_first_comment": fc, "duration": round(dur, 1), "params": p})
    hist.append({"format": fmt, "date": stamp})
json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
json.dump(hist[-200:], open(HIST, "w"), indent=0)
print(json.dumps(man, indent=1))
