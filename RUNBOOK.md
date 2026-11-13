# Tamko daily run

Daily routine for @tamkoplay (TikTok + YouTube Shorts), run by a scheduled Claude session.

1. Clone the repo: `git clone --depth 1 https://github.com/shinkoco/tamko-videos /home/claude/tamko-videos`.
2. Check the tools: `python3 -c "import numpy, PIL"` and `which ffmpeg`. If one is missing: `pip install --break-system-packages numpy pillow`.
3. Generate: `cd /home/claude/tamko-videos/engine && python3 daily.py ../videos 2`.
   This writes 2 videos plus `../videos/manifest.json` (file, format, caption) and updates `engine/history.json`.
4. Clean up: delete every `videos/tamko_*.mp4` whose date stamp (`tamko_YYYYMMDD_...`) is more than 3 days old.
5. Commit and push to `main`: `git -c push.negotiate=true push`.
6. For each manifest entry, create a scheduled Zernio post:
   - platform `tiktok`, account_id `6af7635df038e4d78c1b8569`
   - content = caption
   - media_urls = `https://raw.githubusercontent.com/shinkoco/tamko-videos/main/videos/<file>`
   - first video at 12:00 Europe/Paris, second at 19:00 Europe/Paris, same day. If a slot has already passed, use the next day at the same time.
     `schedule_minutes` = minutes from now until that time.
6b. Also cross-post each video as a YouTube Short at the same time: platform `youtube`, account_id `6af76b7e636980181f23f59f`,
   title = `yt_title`, content = `yt_caption`, same media_urls and schedule_minutes.
7. Report: the files, their formats, and the Zernio post IDs with their times.

Format engine: `engine/formats/{dup,battle,race,rings,survival,ducks}.py (rotation: no format from the last 4 videos)`. Settings are passed in the `TP` environment variable (JSON).
Brand: Lilita One (titles), Fredoka (body text), palette A (night background #0E101E, yellow #FFCD3C, blue #3CAAFF, red #FF5A6E), watermark on the left at mid-height.
