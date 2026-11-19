# Tamko daily run

Daily routine for @tamkoplay (TikTok + YouTube Shorts), run by a scheduled Claude session.

1. Clone the repo: `git clone --depth 1 https://github.com/shinkoco/tamko-videos /home/claude/tamko-videos`.
2. Check the tools: `python3 -c "import numpy, PIL"` and `which ffmpeg`. If one is missing: `pip install --break-system-packages numpy pillow`.
3. Generate: `cd /home/claude/tamko-videos/engine && python3 daily.py ../videos 2`.
   This writes 2 videos plus `../videos/manifest.json` (file, format, caption) and updates `engine/history.json`.
4. Clean up: delete every `videos/tamko_*.mp4` whose date stamp (`tamko_YYYYMMDD_...`) is more than 3 days old.
5. Commit and push to `main`: `git -c push.negotiate=true push`.
6. For each manifest entry, publish on TWO tools (Tamko YouTube now lives on Buffer, NOT Zernio; Zernio keeps only the TikTok accounts):
   6a. TikTok via Zernio: `call_tool` name `posts_create_post` with:
```json
{"content": "<caption>",
 "media_items": [{"type": "video", "url": "https://raw.githubusercontent.com/shinkoco/tamko-videos/main/videos/<file>"}],
 "scheduled_for": "<TIKTOK_TIME>", "timezone": "Europe/Paris",
 "platforms": [{"platform": "tiktok", "accountId": "6af7635df038e4d78c1b8569", "scheduledFor": "<TIKTOK_TIME>"}],
 "tiktok_settings": {"privacyLevel": "PUBLIC_TO_EVERYONE", "allowComment": true, "allowDuet": true, "allowStitch": true,
   "contentPreviewConfirmed": true, "expressConsentGiven": true, "videoCoverTimestampMs": 20000}}
```
   6b. YouTube Short via Buffer: `create_post` with channelId "6afc52e4ece6dfde5ff748bf" (Tamko Arcade, org 6afa0ec6b734c24f5af94d04 — shared with Partners in Vice, never touch its channels), schedulingType "automatic", mode "customScheduled", dueAt "<YOUTUBE_TIME>" as ISO with Paris offset (e.g. 2026-11-18T17:00:00+01:00), text "<yt_caption>", assets [{"video": {"url": "<same raw URL>"}}], metadata {"youtube": {"title": "<yt_title>", "categoryId": "24", "madeForKids": false, "privacy": "public", "isAiGenerated": false}}.
   Buffer free plan: max 10 scheduled posts for the whole org (shared with Partners in Vice) — only schedule the current day's 2 Shorts.
   Times are local Paris time written as "YYYY-MM-DDTHH:MM:00" (timezone Europe/Paris), optimised per platform:
   - Video 1 (morning slot): TikTok 08:00, YouTube 17:00 the same day.
   - Video 2 (evening slot): TikTok 20:00, YouTube 22:00 the same day.
   If a TikTok time has already passed (or is less than 20 minutes away), use the next day for both times of that video.
   WARNING: when updating an existing Zernio post with `platforms`, always resend the FULL platform objects, otherwise Zernio wipes them.
   Visual charter (2026-11-19, freelance avatar+banner, option B light): starry night backdrop replaces flat BG (brand_bg in watermark), glossy cyan titles with gold rim, new flat mascot, small gold/cyan clouds in corners, endcard = mascot + TAMKO logo + "Follow for a new game every day!". Priority to the game: no big mascot in the header. Header block lifted 55 px (lift_header) right under the TikTok top bar (~150 px hidden).
   Hashtags & tags: vidIQ list in engine/daily.py (TAGS, BROAD, YTAGS, GENTAGS) and in the HUB data.json keywords.tamko — keep both in sync.
   Stats: TikTok from Zernio analytics; YouTube from Buffer (get_aggregated_post_metrics / list_posts on the Tamko channel).
7. Report: the files, their formats, and the Zernio post IDs with their times.

Format engine: `engine/formats/*.py — 16 formats: dup, battle, race, rings, survival, ducks, rockets (top-down space-invaders survival), cars (top-down highway survival; the old circuit race is retired), rps, meteors, grow, dominoes, vision, escape, press, melody (melody uses PUBLIC-DOMAIN tunes only) (rotation: no format from the last 8 videos)`. Settings are passed in the `TP` environment variable (JSON).
Brand: Lilita One (titles), Fredoka (body text), palette A (night background #0E101E, yellow #FFCD3C, blue #3CAAFF, red #FF5A6E), watermark on the left at mid-height.

Seasonal themes: engine/brand.py switches automatically by date (THEME). Christmas = 1–26 December: snowy night-blue background, gold title, icy-blue call to action, animated falling snow and a blinking garland, plus 🎄 and #christmas in the TikTok caption. Can be forced with the env var TAMKO_THEME=christmas.

Quality check: after ANY change to the engine, run `python3 engine/qa.py /tmp/qa` (renders all 16 formats, ~11 min) and only push if it prints ALL GOOD. daily.py now switches to another format if one keeps failing, instead of stopping the day.
