"""Generate N Tamko videos with fresh random variants.
Usage: python3 daily.py OUTDIR [count]
Writes OUTDIR/<name>.mp4 (TikTok, 60 s+), OUTDIR/<name>_yt.mp4 (YouTube Short, 2x speed) and OUTDIR/manifest.json [{file, yt_file, format, caption, yt_title, yt_caption}].
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
        p.update(n=rnd.choice([6, 7, 8]), hue=rnd.random(), bpm=rnd.choice([145, 155, 165]),
                 title=rnd.choice(["LAST ROCKET STANDING WINS", "SPACE INVASION!", "PICK YOUR ROCKET!"]))
    elif fmt == "cars":
        p.update(n=rnd.choice([6, 7, 8]), hue=rnd.random(), bpm=rnd.choice([140, 150, 160]),
                 title=rnd.choice(["LAST CAR STANDING WINS", "HIGHWAY SURVIVAL!", "PICK YOUR CAR!"]))
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
    elif fmt == "plinko":
        p.update(bpm=rnd.choice([140, 150, 160]), title=rnd.choice(["PICK 1 TO 6!", "WHICH NUMBER WINS?", "PLINKO: PICK YOUR BALL!"]))
    elif fmt == "territory":
        d = rnd.choice(["fire", "ice", "day", "grass"]); p.update(duel=d, per=rnd.choice([2, 3]), bpm=rnd.choice([140, 150, 160]))
    elif fmt == "maze":
        p.update(gw=rnd.choice([12, 14]), gh=rnd.choice([14, 16]), timer=rnd.choice([52.0, 55.0]), bpm=rnd.choice([130, 140, 150]))
    elif fmt == "press":
        p.update(p=rnd.uniform(.5, .62), hue=rnd.random(), title=rnd.choice(["WHICH SLAM BREAKS THE GLASS?", "WHEN WILL THE GLASS BREAK?", "GUESS THE SLAM NUMBER!"]))
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

CAPS["rockets"] = ["Alien invasion! 👾 Pick your rocket before the first hit 👇", "Invaders, asteroids, lasers… only 1 rocket survives 🚀 Who's your pick? 👇", "Which rocket survives the invasion? 👾 Comment now! 👇"]
CAPS["cars"] = ["Highway chaos! 🏎️ Pick your car before the first crash 👇", "Cones, oil, trucks… only 1 car survives 🏁 Who's your pick? 👇", "Which car makes it to the end? 🏎️ Comment now! 👇"]
CAPS["rps"] = ["Rock vs Paper vs Scissors ✂️ Who takes over? Comment before the end 👇", "3 armies, 1 winner ✂️ Pick your side! 👇", "Rock, paper or scissors? Who wins this war? 👇"]
CAPS["meteors"] = ["Meteor shower! ☄️ Only 1 survives. Pick your survivor 👇", "Dodge or die ☄️ Who makes it? Comment! 👇", "Who survives the meteors? ☄️ Choose now 👇"]
CAPS["grow"] = ["It grows every bounce 😳 How many bounces to fill the circle? Guess 👇", "Tiny ball → giant ball 🤯 Guess the bounces! 👇", "Can it fill the whole circle? 😳 Comment your guess 👇"]
CAPS["dominoes"] = ["Will they ALL fall? 😬 Watch till the end 👇", "Hundreds of dominoes, 1 chain reaction 😮 Will it make it? 👇", "The most satisfying chain reaction? 🤩 Comment YES or NO 👇"]
CAPS["vision"] = ["How old is your vision? 👀 Comment the age when you lost the ball 👇", "Can you still see it? 👀 Tell us your vision age 👇", "Vision test! 👀 When did the ball disappear for you? 👇"]
CAPS["escape"] = ["New rule, new chaos 🤯 Can the ball escape? Comment YES or NO 👇", "Can it break every ring? 👀 Guess before the end 👇"]
CAPS["press"] = ["Every slam adds more balls 🔨 Which slam breaks the glass? Guess 👇", "The glass breaks at the red line 🔨 Guess the slam number 👇", "Slam after slam 🔨 When does the glass break? Comment your number 👇"]
CAPS["melody"] = ["Every bounce plays a note 🎵 Guess the song before the reveal 👇", "Can you name this song? 🎵 Comment before the end 👇", "Guess the song! 🎵 No cheating 👀👇"]
TAGS = {"vision": "#visiontest #eyetest #satisfyingvideo #challenge", "escape": "#ballescape #satisfyingvideo #physicssimulation",
        "press": "#hydraulicpress #satisfyingvideo #physicssimulation", "melody": "#guessthesong #musicchallenge #satisfyingvideo #classicalmusic",
        "rockets": "#spaceinvaders #rocketrace #space #whowillwin", "cars": "#carrace #highway #racesimulation #whowillwin",
        "rps": "#rockpaperscissors #simulation #whowillwin #battle", "meteors": "#meteorshower #survivalgame #lastmanstanding #whowillwin",
        "grow": "#satisfyingvideo #physicssimulation #simulation", "dominoes": "#dominoes #chainreaction #satisfyingvideo #oddlysatisfying",
        "dup": "#satisfyingvideo #physicssimulation #simulation #chaos",
        "battle": "#countryballs #countrybattle #countrywars #whowillwin",
        "race": "#marblerace #racesimulation #cuteanimation #whowillwin",
        "rings": "#ballescape #satisfyingvideo #physicssimulation",
        "survival": "#lastmanstanding #survivalgame #elimination #whowillwin",
        "ducks": "#duckrace #rubberduck #cuteanimation #whowillwin"}

ALL = ["dup", "battle", "race", "rings", "survival", "ducks", "rockets", "cars", "rps", "meteors", "grow", "dominoes", "vision", "escape", "press", "melody", "plinko", "territory", "maze"]
YT = {"dup": ["Every bounce = +1 ball 🤯", "1 ball becomes chaos 😳", "How many balls at the end? 🤯"],
      "battle": ["8 countries, only 1 survives 🏆", "Which country wins? 🌍", "Country battle royale 🏆"],
      "race": ["Who reaches the bottom first? 🏁", "Tiny race, big drama 🏁", "Pick your runner! 🏁"],
      "vision": ["How old is your vision? 👀 Eye test", "Can you still see the ball? 👀 Vision test"],
      "escape": ["Can the ball escape the rings? 🤯 New rule", "Ball escape with a twist 🤯"],
      "press": ["Which slam breaks the glass? 🔨💀", "Hydraulic press vs glass 🔨 Guess the slam"],
      "melody": ["Guess the song 🎵 Every bounce plays a note", "Can you name this song? 🎵 Bouncing ball music"],
      "rockets": ["Alien invasion: which rocket survives? 👾", "Last rocket standing 🚀 Space invaders race"],
      "cars": ["Highway survival: who wins? 🏎️ Car race", "Last car standing 🏁 Car race simulation"],
      "rps": ["Rock vs Paper vs Scissors ✂️ Who wins?", "Rock Paper Scissors war ✂️"],
      "meteors": ["Survive the meteors ☄️ Who's last?", "Meteor shower survival ☄️"],
      "grow": ["It grows every bounce 😳 Satisfying", "Can it fill the circle? 😳"],
      "dominoes": ["Will ALL the dominoes fall? 😬", "Giant domino chain reaction 🤩"],
      "rings": ["Can the ball escape? 👀", "Ball vs rings 💥", "Will it make it out? 🔥"],
      "survival": ["Only 1 survives the traps 💀", "Last one standing wins 🏆", "Who survives? 😱"],
      "ducks": ["Duck race! Pick your duck 🦆", "Which duck wins? 🦆", "The cutest race ever 🦆"]}
# Competitor-style title hooks (Math Melody / Bump Theory / Satisfying Shapes analysis, 2026-11-19)
for _k, _v in {"dup": ["Wait for the last bounce 💀 How many balls?", "Every bounce = MORE balls 💀 Guess the count"],
    "battle": ["Only 1 country survives 💀 Pick yours", "Wait for the final 2 💀 Country battle"],
    "race": ["Wait for the photo finish 💀 Pick your runner", "Can your runner win? 🏁 (1 to 10)"],
    "vision": ["Your eyes will FAIL this test 👀", "Wait until the ball disappears 👀 How old is your vision?"],
    "escape": ["Can the ball escape all the rings? 💀", "Wait for the last ring 💀 Will it escape?"],
    "press": ["Wait for the glass to break 🔨💀", "Guess the slam number 🔨 (1 to 15)"],
    "melody": ["Guess the song before the last note 🎵💀", "Sound on 🔊 Can you name this song?"],
    "rockets": ["Only 1 rocket survives the invasion 💀👾", "Wait for the final boss wave 👾 Pick your rocket"],
    "cars": ["Only 1 car survives the highway 💀🏎️", "Wait for the last crash 💀 Pick your car"],
    "rps": ["Which side takes over? ✂️💀 Rock Paper Scissors", "Wait for the comeback 💀 Rock vs Paper vs Scissors"],
    "meteors": ["Only 1 survives the meteors 💀 Pick yours", "Wait for the last meteor ☄️💀"],
    "grow": ["How many bounces until it fills? 💀", "Wait for the last bounce 😳 It grows every hit"],
    "dominoes": ["Will ALL the dominoes fall? 💀 Wait for the end", "Can 500 dominoes make it? 😬💀"],
    "rings": ["Can the ball escape every ring? 💀", "Wait for ring 1 💀 Will it make it out?"],
    "survival": ["Only 1 survives the traps 💀 Pick yours", "Wait for the final 2 💀 Who survives?"],
    "ducks": ["Which duck wins? 🦆💀 Wait for the end", "Can your duck dodge everything? 🦆"]}.items():
    YT[_k] = YT[_k] + _v
QUESTION = {"dup": "What number did you guess?", "battle": "Which country did you pick?", "race": "Which runner did you pick?",
    "vision": "At what age did the ball disappear for you?", "escape": "Did you think it would escape?", "press": "Which slam did you pick?",
    "melody": "Did you guess the song before the reveal?", "rockets": "Which rocket did you pick?", "cars": "Which car did you pick?",
    "rps": "Rock, paper or scissors: who did you pick?", "meteors": "Who was your survivor?", "grow": "How many bounces did you guess?",
    "dominoes": "Did you think they'd all fall?", "rings": "Did you think it would escape?", "survival": "Who was your survivor?", "ducks": "Which duck did you pick?"}
def yt_description(fmt, cap_text, tags):
    tg = " ".join(dict.fromkeys(tags + ["#satisfying", "#physics", "#simulation", "#shorts"]))
    return f"{cap_text}\n\nSound on 🔊 100% code: our own physics, visuals and music. A new game every day!\n\n{QUESTION.get(fmt, 'Who did you pick?')} 👇\n\n{tg}"
CAPS["rockets"] = ["Alien invasion! 👾 Pick your rocket before the first hit 👇", "Invaders, asteroids, lasers… only 1 rocket survives 🚀 Who's your pick? 👇", "Which rocket survives the invasion? 👾 Comment now! 👇"]
CAPS["cars"] = ["Highway chaos! 🏎️ Pick your car before the first crash 👇", "Cones, oil, trucks… only 1 car survives 🏁 Who's your pick? 👇", "Which car makes it to the end? 🏎️ Comment now! 👇"]
CAPS["rps"] = ["Rock vs Paper vs Scissors ✂️ Who takes over? Comment before the end 👇", "3 armies, 1 winner ✂️ Pick your side! 👇", "Rock, paper or scissors? Who wins this war? 👇"]
CAPS["meteors"] = ["Meteor shower! ☄️ Only 1 survives. Pick your survivor 👇", "Dodge or die ☄️ Who makes it? Comment! 👇", "Who survives the meteors? ☄️ Choose now 👇"]
CAPS["grow"] = ["It grows every bounce 😳 How many bounces to fill the circle? Guess 👇", "Tiny ball → giant ball 🤯 Guess the bounces! 👇", "Can it fill the whole circle? 😳 Comment your guess 👇"]
CAPS["dominoes"] = ["Will they ALL fall? 😬 Watch till the end 👇", "Hundreds of dominoes, 1 chain reaction 😮 Will it make it? 👇", "The most satisfying chain reaction? 🤩 Comment YES or NO 👇"]
CAPS["vision"] = ["How old is your vision? 👀 Comment the age when you lost the ball 👇", "Can you still see it? 👀 Tell us your vision age 👇", "Vision test! 👀 When did the ball disappear for you? 👇"]
CAPS["escape"] = ["New rule, new chaos 🤯 Can the ball escape? Comment YES or NO 👇", "Can it break every ring? 👀 Guess before the end 👇"]
CAPS["press"] = ["Every slam adds more balls 🔨 Which slam breaks the glass? Guess 👇", "The glass breaks at the red line 🔨 Guess the slam number 👇", "Slam after slam 🔨 When does the glass break? Comment your number 👇"]
CAPS["melody"] = ["Every bounce plays a note 🎵 Guess the song before the reveal 👇", "Can you name this song? 🎵 Comment before the end 👇", "Guess the song! 🎵 No cheating 👀👇"]
TAGS.update({"vision": "#visiontest #eyetest #satisfyingvideo #challenge", "escape": "#ballescape #satisfyingvideo #physicssimulation",
        "press": "#hydraulicpress #satisfyingvideo #physicssimulation", "melody": "#guessthesong #musicchallenge #satisfyingvideo #classicalmusic",
        "rockets": "#spaceinvaders #rocketrace #space #whowillwin", "cars": "#carrace #highway #racesimulation #whowillwin",
        "rps": "#rockpaperscissors #simulation #whowillwin #battle", "meteors": "#meteorshower #survivalgame #lastmanstanding #whowillwin",
        "grow": "#satisfyingvideo #physicssimulation #simulation", "dominoes": "#dominoes #chainreaction #satisfyingvideo #oddlysatisfying"})
YTAGS = {"dup": ["oddly satisfying", "physics", "bouncing balls", "chaos"], "battle": ["countryballs", "country battle", "countries"],
         "race": ["marble race", "race", "cute"], "rings": ["oddly satisfying", "ball escape", "physics"],
         "survival": ["survival", "last one standing", "elimination"], "ducks": ["duck race", "rubber duck", "cute"],
         "vision": ["vision test", "eye test", "challenge"], "escape": ["ball escape", "physics", "oddly satisfying"],
         "press": ["hydraulic press", "physics", "oddly satisfying"], "melody": ["guess the song", "music", "classical music", "bouncing ball"],
         "rockets": ["space invaders", "rocket race", "space"], "cars": ["car race", "highway", "racing"], "rps": ["rock paper scissors", "battle"],
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
BLOCKED = {"#bouncingballs", "#balls", "#ballz", "#minigame", "#arcadegames", "#lastonestanding", "#lastmanstanding", "#oddlysatisfying"}
# vidIQ keyword research 2026-11-18 (also listed in the HUB, studiomgi.github.io data.json keywords.tamko)
BROAD = ["#arcade", "#gameplay", "#retrogames", "#mobilegames", "#simulatorgames", "#physics"]
TAGS = {"dup": "#satisfyingsimulation #bouncingball #2dphysics", "grow": "#bouncingball #satisfyingsimulation #physicssimulation",
        "press": "#satisfyingvideo #physicssimulation #2dphysics", "battle": "#countryballs #countrybattle #battleroyale",
        "survival": "#battleroyale #countryballs #whowouldwin", "meteors": "#battleroyale #survivalgame #whowouldwin",
        "race": "#marblerace #marblerun #algodoo", "ducks": "#marblerace #algodoo #whowouldwin",
        "rings": "#ballescape #spinningrings #willitescape", "escape": "#ballescape #willitescape #physicssimulation",
        "rps": "#rockpaperscissors #whowouldwin #satisfyingsimulation", "dominoes": "#domino #dominoesfalling #rubegoldberg",
        "rockets": "#spaceinvaders #spaceinvadersgameplay #classicarcade", "cars": "#cargame #carracinggame #whowouldwin",
        "vision": "#visiontest #eyetest #satisfyingvideo", "melody": "#guessthesong #bouncingball #satisfyingvideo"}
YTAGS = {"dup": ["satisfying simulation", "bouncing ball", "2d physics", "physics simulation"],
         "grow": ["bouncing ball", "satisfying simulation", "physics simulation"], "press": ["satisfying video", "physics simulation", "2d physics"],
         "battle": ["countryballs", "country battle", "countries marble race", "world war simulator"],
         "survival": ["battle royale", "countryballs", "who would win"], "meteors": ["battle royale", "survival game", "who would win"],
         "race": ["marble race", "marble run", "marble racing", "algodoo marble race"], "ducks": ["marble race", "algodoo", "who would win"],
         "rings": ["ball escape", "spinning rings", "escape the circle", "will it escape"], "escape": ["ball escape", "will it escape", "escape the circle"],
         "rps": ["rock paper scissors", "rock paper scissors simulation", "who would win"], "dominoes": ["domino", "dominoes falling", "rube goldberg"],
         "rockets": ["space invaders", "space invaders gameplay", "space invaders arcade"], "cars": ["car game", "car race game", "car racing game"],
         "vision": ["vision test", "eye test", "satisfying video"], "melody": ["guess the song", "bouncing ball", "satisfying video"]}
GENTAGS = ["arcade", "gameplay", "retro games", "classic arcade games", "mobile games", "simulator games", "satisfying video", "relaxing video", "physics simulation", "who would win"]
last = [h["format"] for h in hist[-8:]]
fmts = [f for f in ALL if f not in last]
rnd.shuffle(fmts); fmts = (fmts + [f for f in ALL if f not in fmts])[:COUNT]
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
CAPS["plinko"] = ["Pick 1 to 6 👇 OUT = eliminated. Which number survives?", "6 balls, 1 winner 🎯 Comment your number before the end 👇", "Plinko battle! Which number wins? Pick 1 to 6 👇"]
CAPS["territory"] = ["Pick your side 👇 Biggest area after the timer wins", "Each ball paints its color 🎨 Who takes over? Comment now 👇", "Element war! Which side wins? 👇"]
CAPS["maze"] = ["TRAPPED or FREE? 👀 Bet before the timer ends 👇", "Can Tamko find the exit in time? ⏱️ Comment TRAPPED or FREE 👇", "Will Tamko escape the maze? 🧩 Place your bet 👇"]
YT["plinko"] = ["Pick 1 to 6 🎯 Which ball survives?", "Plinko elimination 💀 Pick your number", "Wait for the last drop 💀 (1 to 6)"]
YT["territory"] = ["Which side takes over? 🎨💀", "Element war: pick your side 🔥💧", "Wait for the last second 💀 Who wins the map?"]
YT["maze"] = ["Trapped or free? 🧩💀", "Can Tamko escape the maze in time? ⏱️", "Wait for the timer 💀 Trapped or free?"]
TAGS.update({"plinko": "#plinko #pickanumber #whowouldwin", "territory": "#territorywar #satisfyingsimulation #whowouldwin", "maze": "#maze #mazegame #puzzle"})
YTAGS.update({"plinko": ["plinko", "pick a number", "who would win"], "territory": ["territory war", "pong wars", "satisfying simulation"], "maze": ["maze", "maze game", "maze solving"]})
FC.update({"plinko": ["Which number did you pick? 🎯 Comment below!"], "territory": ["Which side did you pick? 🎨 Comment below!"], "maze": ["Trapped or free? What was your bet? 🧩"]})
QUESTION.update({"plinko": "Which number did you pick?", "territory": "Which side did you pick?", "maze": "Trapped or free: what was your bet?"})
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
    tags = TAGS[fmt].split()[:3] + [rnd.choice(BROAD)]
    tags = [h for h in tags if h.lower() not in BLOCKED]  # hashtags TikTok already removed
    cap_text = rnd.choice(CAPS[fmt]); cap = cap_text + " " + " ".join(dict.fromkeys(tags))
    _d = datetime.date.today()
    if os.environ.get("TAMKO_THEME") == "christmas" or (_d.month == 12 and _d.day <= 26):
        cap = "🎄 " + cap + " #christmas"
    yt = rnd.choice(YT[fmt])
    ytags = YTAGS[fmt] + rnd.sample(GENTAGS, 4) + ["tamko"]
    fc = rnd.choice(FC[fmt])
    # YouTube Short version: 2x speed (~30-40 s), like the competitors' 15-30 s Shorts
    yfile = name + "_yt.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f, "-filter_complex", "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", os.path.join(OUT, yfile)], check=True)
    ytags_h = [t for t in tags if t != "#physics"]
    man.append({"file": name + ".mp4", "yt_file": yfile, "format": fmt, "caption": cap, "yt_title": yt, "yt_caption": yt_description(fmt, cap_text, ytags_h), "yt_tags": ytags, "yt_first_comment": fc, "duration": round(dur, 1), "params": p})
    hist.append({"format": fmt, "date": stamp})
json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
json.dump(hist[-200:], open(HIST, "w"), indent=0)
print(json.dumps(man, indent=1))
