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
    p = {"seed": rnd.randrange(1, 10**9), "tamko": rnd.random() < 0.4}
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
    elif fmt == "rockets":
        p.update(n=rnd.choice([6, 7, 8]), fin=rnd.choice([5800, 6400, 7000]), ast_gap=rnd.choice([200, 230, 270]), hue=rnd.random(),
                 title=rnd.choice(["WHICH ROCKET REACHES SPACE?", "ROCKET RACE!", "PICK YOUR ROCKET!"]))
    elif fmt == "cars":
        p.update(n=rnd.choice([6, 8]), laps=rnd.choice([2, 3, 4]), crash=rnd.uniform(.001, .0025), hue=rnd.random(),
                 title=rnd.choice(["WHO WINS THE RACE?", "GRAND PRIX!", "PICK YOUR CAR!"]))
    elif fmt == "rps":
        p.update(n=rnd.choice([20, 25, 30]), speed=rnd.uniform(.55, .7), title=rnd.choice(["ROCK PAPER SCISSORS", "WHO TAKES OVER?"]))
    elif fmt == "meteors":
        p.update(n=rnd.choice([14, 18, 22]), hue=rnd.random(), title=rnd.choice(["SURVIVE THE METEORS!", "METEOR SHOWER!", "WHO SURVIVES?"]))
    elif fmt == "grow":
        p.update(tfill=rnd.uniform(50, 56), g=rnd.uniform(.4, .6), hue=rnd.random(),
                 title=rnd.choice(["IT GROWS EVERY BOUNCE", "+1 SIZE EVERY BOUNCE", "CAN IT FILL THE CIRCLE?"]))
    elif fmt == "dominoes":
        p.update(n=rnd.choice([400, 450, 500]), shape=rnd.choice(["spiral", "snake"]), hue=rnd.random(), tstep=rnd.uniform(.095, .11))
    elif fmt == "vision":
        p.update(hue=rnd.random(), tend=rnd.uniform(52, 56), r=rnd.choice([22, 26, 30]))
    elif fmt == "escape":
        p.update(rule=rnd.choice(["spawn", "shrink", "freeze"]), n=rnd.choice([8, 10, 12]), gap=rnd.uniform(.8, 1.0), hue=rnd.random())
    elif fmt == "press":
        p.update(slams=rnd.choice([8, 9, 10]), hue=rnd.random())
    elif fmt == "melody":
        p.update(beat=rnd.uniform(.38, .46))
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
CAPS["rockets"] = ["Rocket race to space! 🚀 Pick your rocket before liftoff 👇", "Asteroids, boosts and 1 winner 🚀 Which rocket? 👇", "Which rocket reaches space first? 🚀 Comment! 👇"]
CAPS["cars"] = ["Grand Prix time! 🏎️ Pick your car before the final lap 👇", "Crashes, overtakes, 1 winner 🏁 Who's your pick? 👇", "Which car wins the race? 🏎️ Comment now! 👇"]
CAPS["rps"] = ["Rock vs Paper vs Scissors ✂️ Who takes over? Comment before the end 👇", "3 armies, 1 winner ✂️ Pick your side! 👇", "Rock, paper or scissors? Who wins this war? 👇"]
CAPS["meteors"] = ["Meteor shower! ☄️ Only 1 survives. Pick your survivor 👇", "Dodge or die ☄️ Who makes it? Comment! 👇", "Who survives the meteors? ☄️ Choose now 👇"]
CAPS["grow"] = ["It grows every bounce 😳 How many bounces to fill the circle? Guess 👇", "Tiny ball → giant ball 🤯 Guess the bounces! 👇", "Can it fill the whole circle? 😳 Comment your guess 👇"]
CAPS["dominoes"] = ["Will they ALL fall? 😬 Watch till the end 👇", "Hundreds of dominoes, 1 chain reaction 😮 Will it make it? 👇", "The most satisfying chain reaction? 🤩 Comment YES or NO 👇"]
CAPS["vision"] = ["How old is your vision? 👀 Comment the age when you lost the ball 👇", "Can you still see it? 👀 Tell us your vision age 👇", "Vision test! 👀 When did the ball disappear for you? 👇"]
CAPS["escape"] = ["New rule, new chaos 🤯 Can the ball escape? Comment YES or NO 👇", "Can it break every ring? 👀 Guess before the end 👇"]
CAPS["press"] = ["Every slam splits the balls 🔨 How many at the end? Guess 👇", "1 ball vs the hydraulic press 🔨 Guess the final count 👇"]
CAPS["melody"] = ["Every bounce plays a note 🎵 Guess the song before the reveal 👇", "Can you name this song? 🎵 Comment before the end 👇", "Guess the song! 🎵 No cheating 👀👇"]
TAGS = {"vision": "#visiontest #eyetest #satisfyingvideo #challenge", "escape": "#ballescape #satisfyingvideo #physicssimulation",
        "press": "#hydraulicpress #satisfyingvideo #physicssimulation", "melody": "#guessthesong #musicchallenge #satisfyingvideo #classicalmusic",
        "rockets": "#rocketrace #space #whowillwin #cuteanimation", "cars": "#carrace #grandprix #racesimulation #whowillwin",
        "rps": "#rockpaperscissors #simulation #whowillwin #battle", "meteors": "#meteorshower #survivalgame #lastmanstanding #whowillwin",
        "grow": "#satisfyingvideo #bouncingball #physicssimulation", "dominoes": "#dominoes #chainreaction #satisfyingvideo #oddlysatisfying",
        "dup": "#satisfyingvideo #physicssimulation #bouncingballs #chaos",
        "battle": "#countryballs #countrybattle #countrywars #whowillwin",
        "race": "#marblerace #racesimulation #cuteanimation #whowillwin",
        "rings": "#ballescape #satisfyingvideo #physicssimulation",
        "survival": "#lastmanstanding #survivalgame #elimination #whowillwin",
        "ducks": "#duckrace #rubberduck #cuteanimation #whowillwin"}

ALL = ["dup", "battle", "race", "rings", "survival", "ducks", "rockets", "cars", "rps", "meteors", "grow", "dominoes", "vision", "escape", "press", "melody"]
YT = {"dup": ["Every bounce = +1 ball 🤯", "1 ball becomes chaos 😳", "How many balls at the end? 🤯"],
      "battle": ["8 countries, only 1 survives 🏆", "Which country wins? 🌍", "Country battle royale 🏆"],
      "race": ["Who reaches the bottom first? 🏁", "Tiny race, big drama 🏁", "Pick your runner! 🏁"],
      "vision": ["How old is your vision? 👀 Eye test", "Can you still see the ball? 👀 Vision test"],
      "escape": ["Can the ball escape the rings? 🤯 New rule", "Ball escape with a twist 🤯"],
      "press": ["Hydraulic press splits every ball 🔨", "1 ball vs a hydraulic press 🔨 How many?"],
      "melody": ["Guess the song 🎵 Every bounce plays a note", "Can you name this song? 🎵 Bouncing ball music"],
      "rockets": ["Which rocket reaches space? 🚀 Rocket race", "Rocket race to space 🚀"],
      "cars": ["Grand Prix: who wins? 🏎️ Car race", "Car race simulation 🏁"],
      "rps": ["Rock vs Paper vs Scissors ✂️ Who wins?", "Rock Paper Scissors war ✂️"],
      "meteors": ["Survive the meteors ☄️ Who's last?", "Meteor shower survival ☄️"],
      "grow": ["It grows every bounce 😳 Satisfying", "Can it fill the circle? 😳"],
      "dominoes": ["Will ALL the dominoes fall? 😬", "Giant domino chain reaction 🤩"],
      "rings": ["Can the ball escape? 👀", "Ball vs rings 💥", "Will it make it out? 🔥"],
      "survival": ["Only 1 survives the traps 💀", "Last one standing wins 🏆", "Who survives? 😱"],
      "ducks": ["Duck race! Pick your duck 🦆", "Which duck wins? 🦆", "The cutest race ever 🦆"]}
CAPS["rockets"] = ["Rocket race to space! 🚀 Pick your rocket before liftoff 👇", "Asteroids, boosts and 1 winner 🚀 Which rocket? 👇", "Which rocket reaches space first? 🚀 Comment! 👇"]
CAPS["cars"] = ["Grand Prix time! 🏎️ Pick your car before the final lap 👇", "Crashes, overtakes, 1 winner 🏁 Who's your pick? 👇", "Which car wins the race? 🏎️ Comment now! 👇"]
CAPS["rps"] = ["Rock vs Paper vs Scissors ✂️ Who takes over? Comment before the end 👇", "3 armies, 1 winner ✂️ Pick your side! 👇", "Rock, paper or scissors? Who wins this war? 👇"]
CAPS["meteors"] = ["Meteor shower! ☄️ Only 1 survives. Pick your survivor 👇", "Dodge or die ☄️ Who makes it? Comment! 👇", "Who survives the meteors? ☄️ Choose now 👇"]
CAPS["grow"] = ["It grows every bounce 😳 How many bounces to fill the circle? Guess 👇", "Tiny ball → giant ball 🤯 Guess the bounces! 👇", "Can it fill the whole circle? 😳 Comment your guess 👇"]
CAPS["dominoes"] = ["Will they ALL fall? 😬 Watch till the end 👇", "Hundreds of dominoes, 1 chain reaction 😮 Will it make it? 👇", "The most satisfying chain reaction? 🤩 Comment YES or NO 👇"]
CAPS["vision"] = ["How old is your vision? 👀 Comment the age when you lost the ball 👇", "Can you still see it? 👀 Tell us your vision age 👇", "Vision test! 👀 When did the ball disappear for you? 👇"]
CAPS["escape"] = ["New rule, new chaos 🤯 Can the ball escape? Comment YES or NO 👇", "Can it break every ring? 👀 Guess before the end 👇"]
CAPS["press"] = ["Every slam splits the balls 🔨 How many at the end? Guess 👇", "1 ball vs the hydraulic press 🔨 Guess the final count 👇"]
CAPS["melody"] = ["Every bounce plays a note 🎵 Guess the song before the reveal 👇", "Can you name this song? 🎵 Comment before the end 👇", "Guess the song! 🎵 No cheating 👀👇"]
TAGS.update({"vision": "#visiontest #eyetest #satisfyingvideo #challenge", "escape": "#ballescape #satisfyingvideo #physicssimulation",
        "press": "#hydraulicpress #satisfyingvideo #physicssimulation", "melody": "#guessthesong #musicchallenge #satisfyingvideo #classicalmusic",
        "rockets": "#rocketrace #space #whowillwin #cuteanimation", "cars": "#carrace #grandprix #racesimulation #whowillwin",
        "rps": "#rockpaperscissors #simulation #whowillwin #battle", "meteors": "#meteorshower #survivalgame #lastmanstanding #whowillwin",
        "grow": "#satisfyingvideo #bouncingball #physicssimulation", "dominoes": "#dominoes #chainreaction #satisfyingvideo #oddlysatisfying"})
YTAGS = {"dup": ["oddly satisfying", "physics", "bouncing balls", "chaos"], "battle": ["countryballs", "country battle", "countries"],
         "race": ["marble race", "race", "cute"], "rings": ["oddly satisfying", "ball escape", "physics"],
         "survival": ["survival", "last one standing", "elimination"], "ducks": ["duck race", "rubber duck", "cute"],
         "vision": ["vision test", "eye test", "challenge"], "escape": ["ball escape", "physics", "oddly satisfying"],
         "press": ["hydraulic press", "physics", "oddly satisfying"], "melody": ["guess the song", "music", "classical music", "bouncing ball"],
         "rockets": ["rocket race", "space", "cute"], "cars": ["car race", "grand prix", "racing"], "rps": ["rock paper scissors", "battle"],
         "meteors": ["meteor", "survival", "last one standing"], "grow": ["bouncing ball", "physics", "oddly satisfying"],
         "dominoes": ["dominoes", "chain reaction", "oddly satisfying"]}
FC = {"vision": ["What age did you get? 👀 Comment below!"], "escape": ["Did you think it would escape? 👀 Comment!"],
      "press": ["What was your guess? 🔨 Comment the number!"], "melody": ["Did you guess the song before the reveal? 🎵"], "rockets": ["Which rocket did you pick? 🚀 Comment below!"], "cars": ["Which car did you pick? 🏎️ Comment below!"],
      "rps": ["Rock, paper or scissors? ✂️ What did you pick?"], "meteors": ["Who was your survivor? ☄️ Comment below!"],
      "grow": ["How many bounces did you guess? 😳"], "dominoes": ["Did you think they'd all fall? 😬 Comment!"], "dup": ["What was your guess? 🤯 Comment the number!", "Did you guess right? 👀 Drop your number below!"],
      "battle": ["Which country did you pick? 🌍 Comment yours!", "Did your country win? 🏆 Tell us below!"],
      "race": ["Who did you pick? 🏁 Drop your runner below!", "Did your runner win? 🏁 Comment!"],
      "rings": ["Did you say YES or NO? 👀 Comment below!", "Called it? 🔥 Tell us below!"],
      "survival": ["Who was your survivor? 💀 Comment below!", "Did your pick survive? 😱 Tell us!"],
      "ducks": ["Which duck did you pick? 🦆 Comment below!", "Did your duck win? 🦆 Tell us!"]}
FC = {k: [x + " Subscribe for a new game every day!" for x in v] for k, v in FC.items()}
last = [h["format"] for h in hist[-8:]]
fmts = [f for f in ALL if f not in last]
rnd.shuffle(fmts); fmts = (fmts + [f for f in ALL if f not in fmts])[:COUNT]
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
man = []
for i, fmt in enumerate(fmts):
    for attempt in range(4):
        if attempt == 2:  # this format keeps failing: switch to another one instead of aborting the day
            fmt = rnd.choice([f for f in ALL if f not in fmts]); fmts[i] = fmt
        p = params(fmt); name = f"tamko_{stamp}_{i}_{fmt}"
        env = dict(os.environ, TP=json.dumps(p), TOUT=name, OUTDIR=OUT)
        r = subprocess.run([sys.executable, os.path.join(HERE, "formats", fmt + ".py")], env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if r.returncode != 0:
            print(f"WARNING: {fmt} failed (attempt {attempt+1}): {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else '?'}", file=sys.stderr)
            continue
        f = os.path.join(OUT, name + ".mp4")
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                   capture_output=True, text=True).stdout or 0)
        if dur >= 60: break
        os.remove(f)
    else:
        sys.exit(f"ERROR: could not produce video {i}")
    cap = rnd.choice(CAPS[fmt]) + " " + TAGS[fmt]
    _d = datetime.date.today()
    if os.environ.get("TAMKO_THEME") == "christmas" or (_d.month == 12 and _d.day <= 26):
        cap = "🎄 " + cap + " #christmas"
    yt = rnd.choice(YT[fmt])
    ytags = YTAGS[fmt] + ["satisfying", "simulation", "who will win", "tamko"]
    fc = rnd.choice(FC[fmt])
    man.append({"file": name + ".mp4", "format": fmt, "caption": cap, "yt_title": yt, "yt_caption": cap + " #shorts", "yt_tags": ytags, "yt_first_comment": fc, "duration": round(dur, 1), "params": p})
    hist.append({"format": fmt, "date": stamp})
json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
json.dump(hist[-200:], open(HIST, "w"), indent=0)
print(json.dumps(man, indent=1))
