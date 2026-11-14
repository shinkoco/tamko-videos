# Tamko daily run

Daily routine for @tamkoplay (TikTok + YouTube Shorts), run by a scheduled Claude session.

1. Clone the repo: `git clone --depth 1 https://github.com/shinkoco/tamko-videos /home/claude/tamko-videos`.
2. Check the tools: `python3 -c "import numpy, PIL"` and `which ffmpeg`. If one is missing: `pip install --break-system-packages numpy pillow`.
3. Generate: `cd /home/claude/tamko-videos/engine && python3 daily.py ../videos 2`.
   This writes 2 videos plus `../videos/manifest.json` (file, format, caption) and updates `engine/history.json`.
4. Clean up: delete every `videos/tamko_*.mp4` whose date stamp (`tamko_YYYYMMDD_...`) is more than 3 days old.
5. Commit and push to `main`: `git -c push.negotiate=true push`.
6. For each manifest entry, create ONE Zernio post covering both platforms. Use the `call_tool` tool with name `posts_create_post` and these arguments (fill in the values):
```json
{"content": "<caption>",
 "media_items": [{"type": "video", "url": "https://raw.githubusercontent.com/shinkoco/tamko-videos/main/videos/<file>"}],
 "scheduled_for": "<YYYY-MM-DD>T12:00:00",  "timezone": "Europe/Paris",
 "tags": <yt_tags>,
 "platforms": [
   {"platform": "tiktok", "accountId": "6af7635df038e4d78c1b8569"},
   {"platform": "youtube", "accountId": "6af76b7e636980181f23f59f", "customContent": "<yt_caption>",
    "platformSpecificData": {"title": "<yt_title>", "visibility": "public", "categoryId": "24",
      "madeForKids": false, "containsSyntheticMedia": false, "firstComment": "<yt_first_comment>"}}],
 "tiktok_settings": {"privacyLevel": "PUBLIC_TO_EVERYONE", "allowComment": true, "allowDuet": true, "allowStitch": true,
   "contentPreviewConfirmed": true, "expressConsentGiven": true, "videoCoverTimestampMs": 20000}}
```
   First video at 12:00, second at 19:00 (Paris time). If a slot has already passed, use the next day at the same time.
7. Report: the files, their formats, and the Zernio post IDs with their times.

Format engine: `engine/formats/*.py — 16 formats: dup, battle, race, rings, survival, ducks, rockets, cars, rps, meteors, grow, dominoes, vision, escape, press, melody (melody uses PUBLIC-DOMAIN tunes only) (rotation: no format from the last 8 videos)`. Settings are passed in the `TP` environment variable (JSON).
Brand: Lilita One (titles), Fredoka (body text), palette A (night background #0E101E, yellow #FFCD3C, blue #3CAAFF, red #FF5A6E), watermark on the left at mid-height.

Seasonal themes: engine/brand.py switches automatically by date (THEME). Christmas = 1–26 December: snowy night-blue background, gold title, icy-blue call to action, animated falling snow and a blinking garland, plus 🎄 and #christmas in the TikTok caption. Can be forced with the env var TAMKO_THEME=christmas.

Quality check: after ANY change to the engine, run `python3 engine/qa.py /tmp/qa` (renders all 16 formats, ~11 min) and only push if it prints ALL GOOD. daily.py now switches to another format if one keeps failing, instead of stopping the day.
