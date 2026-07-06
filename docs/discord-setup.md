# Discord Setup, Step by Step

This connects your teacher to your phone: you send text or a voice message in a private
Discord channel, the duty daemon transcribes it, thinks, and replies with text + a voice note.

Time required: ~10 minutes. Cost: free (Discord bots are free; polling costs zero LLM tokens).

## 1. Create the bot

1. Open https://discord.com/developers/applications → **New Application** → name it after your teacher
2. Left sidebar → **Bot**
3. Click **Reset Token** → copy the token **now** (it is shown only once). This goes into `.env` as `DISCORD_BOT_TOKEN`
4. Still on the Bot page, scroll to **Privileged Gateway Intents** and switch **MESSAGE CONTENT INTENT** on
   — without it, Discord hides message text from your bot and every message arrives empty

## 2. Give it a home

1. In the Discord app, create a **new private server** just for you (plus icon in the server list). One default channel is enough
2. Back in the developer portal: **OAuth2 → URL Generator**
   - Scopes: `bot`
   - Bot permissions: `View Channels`, `Send Messages`, `Read Message History`, `Attach Files`
3. Open the generated URL in a browser → invite the bot into your private server

## 3. Collect the two IDs

1. Discord **User Settings → Advanced → Developer Mode: ON**
2. Right-click the channel you'll chat in → **Copy Channel ID** → `.env` `DISCORD_CHANNEL_ID`
3. Right-click your own name in any message → **Copy User ID** → `.env` `DISCORD_OWNER_ID`
   — the daemon answers **only** this user; everyone else is ignored by design (see SECURITY.md)

## 4. Fill `.env` and test

```bash
# .env (repo root)
DISCORD_BOT_TOKEN=xxxxx
DISCORD_CHANNEL_ID=xxxxx
DISCORD_OWNER_ID=xxxxx

# fire a test — the teacher announces herself in the channel:
~/.venvs/ai-teacher/bin/python engine/duty_daemon.py --announce
```

You should see a 📻 greeting in the channel within seconds. Now send her a message —
text first, then try holding the microphone button (mobile) for a voice message.

To keep her on duty permanently, register the service: `python3 setup/services.py`.

## Good to know

- **The bot appears "offline" — that is normal.** The daemon uses REST polling, never the
  realtime gateway; presence is a gateway feature. She answers anyway.
- **Voice messages work from the mobile app** (hold the mic button). The daemon downloads
  the audio attachment and transcribes it locally with Whisper.
- **Reply rhythm**: polling backs off when idle (5s → 20s → 60s), so a reply can take up to
  a minute after a long quiet period; the first message wakes it back to 5s.

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| No 📻 announce message | Wrong token or channel ID; check `/tmp/com.aiteacher.duty.log` |
| Bot replies to text but says it heard nothing | MESSAGE CONTENT INTENT is off (step 1.4) |
| Replies but no voice note attached | A voice engine is down — run `python3 audition/audition.py ja` to test; check engine services |
| `403` errors in the log | Discord's CDN rejects Python's default user agent; the daemon already routes everything through `curl` — if you patched networking code, keep it that way |
| Messages from friends ignored | By design. Only `DISCORD_OWNER_ID` is answered |
