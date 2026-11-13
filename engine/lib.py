import numpy as np, subprocess, wave, math, os
from PIL import ImageFont
W, H, FPS, SR = 720, 1280, 30, 44100
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(s): return ImageFont.truetype(FB, s)

def hsv(h, s=1, v=1):
    h %= 1; i = int(h*6) % 6; f = h*6 - int(h*6)
    p, q, t = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
    r, g, b = [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][i]
    return (int(r*255), int(g*255), int(b*255))

class Out:
    def __init__(self, name):
        self.name = name; self.ev = []; self.n = 0
        self.p = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
            "-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20",
            "-pix_fmt","yuv420p",f"/tmp/{name}_v.mp4"], stdin=subprocess.PIPE)
    def frame(self, img): self.p.stdin.write(img.tobytes()); self.n += 1
    @property
    def t(self): return self.n/FPS
    def sound(self, freq, dur=0.15, vol=0.3, decay=18, kind="sine"):
        self.ev.append((self.t, freq, dur, vol, decay, kind))
    def close(self):
        self.p.stdin.close(); self.p.wait()
        L = int(SR*(self.t+1)); a = np.zeros(L)
        for t, fr, d, v, dc, k in self.ev:
            n = int(SR*d); tt = np.arange(n)/SR; env = np.exp(-tt*dc)
            if k == "sine": s = np.sin(2*np.pi*fr*tt) + 0.3*np.sin(4*np.pi*fr*tt)
            elif k == "noise": s = np.random.uniform(-1, 1, n)
            else: s = np.sign(np.sin(2*np.pi*fr*tt))*0.5
            i0 = int(t*SR); seg = a[i0:i0+n]; seg += (s*env*v)[:len(seg)]
        a = np.tanh(a*1.2)*0.8
        with wave.open(f"/tmp/{self.name}.wav", "w") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((a*32767).astype(np.int16).tobytes())
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"/tmp/{self.name}_v.mp4","-i",f"/tmp/{self.name}.wav",
            "-c:v","copy","-c:a","aac","-b:a","160k","-shortest",os.path.join(os.environ.get("OUTDIR", "."), f"{self.name}.mp4")])
