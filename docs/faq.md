# FAQ

## How is this different from ChatGPT voice mode or a hosted voice agent?

Four things, by design:

1. **You own the teacher.** Her personality, your profile, the curriculum, the voice cast —
   all plain Markdown files on your disk. Edit any of them and the change takes effect on
   the next utterance. Nothing lives on someone else's server.
2. **She has a pedagogy.** The design follows skill specificity in Skill Acquisition Theory
   (production practice is what improves production): short natural turns, one correction at
   a time, vocabulary distilled into lesson logs she actually re-reads.
3. **She is proactive.** A nightly timer has her open the conversation and ask about your
   day — gentle, never nagging. Speaking practice happens because someone starts it.
4. **Voices are local and free.** No per-minute bill; usable offline; the online engine is
   only a fallback.

## What does it cost to run?

- **Voices & transcription**: $0 — VOICEVOX, Kokoro, MeloTTS, and Whisper all run locally
- **The brain**: your choice of provider — Claude Code (within your existing subscription),
  your own Anthropic API key (pay per use), or Ollama (free, local)
- **Discord**: free

## Which languages are supported?

Wired today: Japanese, English, Chinese, Korean — each with a local open-source voice.
The teacher can *understand and teach* any language your LLM speaks; adding a spoken voice
for a new language means adding a line to `config/voices.md` (the Microsoft edge fallback
covers dozens of languages online) or wiring another local engine.

## Whichever language I type, she becomes that teacher — how does she treat my native language?

Your native language is declared in `config/student.md` and is exempt from teacher mode:
she uses it for relaxed chat and explanations, never corrects it, never turns it into
vocabulary drills. Every other language in your profile gets a teaching mode tuned to the
level you wrote down.

## Does it run on Windows or Linux?

Not yet verified — alpha is macOS (Apple Silicon) only. The pieces are mostly portable:
VOICEVOX, Kokoro, and MeloTTS all have cross-platform builds; the transcription layer
(`mlx-whisper`) is Apple-only and would need swapping for `faster-whisper`; `launchd`
services would become systemd units or Task Scheduler jobs. Contributions welcome.

## What leaves my machine?

- Your voice and text are transcribed **locally** (Whisper runs on-device)
- LLM requests go to the brain **you** chose (Claude / your API key / local Ollama)
- Speech synthesis is local by default; only the edge **fallback** sends the text to be
  spoken to Microsoft's online service
- Lesson logs are written only to your local `lessons/`

See [SECURITY.md](../SECURITY.md) for the full threat model.

## Why Discord and not WhatsApp / Telegram / iMessage?

Discord gives bots first-class voice-message attachments, a free and stable REST API, and
private servers that make a clean 1:1 channel. The daemon is ~200 lines and channel-agnostic
in spirit — adapters for other messengers are a welcome contribution.

## The teacher's voice sounds robotic / I don't like it

Run the audition tool and pick with your own ears:

```bash
python3 audition/audition.py ja   # or en / zh / ko
```

Then write the winner into `config/voices.md`. If you want a premium multilingual voice,
wiring your own ElevenLabs key is on the roadmap.

## Can I change her personality after the birth ritual?

Any time. `config/teacher.md` is the single source of truth — edit and save; she reads it
before every reply. The same goes for your profile, the curriculum, evening-chat rules, and
the free-form extra rules section in `config/protocol.md`.

## She stopped replying on Discord

Check, in order: (1) `/tmp/com.aiteacher.duty.log`, (2) is the daemon process alive
(`launchctl list | grep aiteacher`), (3) voice engines up? (a synthesis failure only drops
the voice note, text still goes through), (4) [docs/discord-setup.md](discord-setup.md)
troubleshooting table.

## Why are some docs in Chinese?

The project grew out of a real bilingual workspace. `docs/known-issues.md` (the battle
scars) is Chinese-first for now; an English translation is planned before the first public
release. The code comments are being migrated gradually.
