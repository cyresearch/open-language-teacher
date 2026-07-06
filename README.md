# AI Language Teacher (name TBD)

**English** | [中文](README.zh.md)

> An open-source, local-first AI language teacher you can actually *talk* to — at your desk and from your phone.

**Status: alpha · verified on macOS (Apple Silicon) only · docs under construction**

## Why this exists

The author has lived in Japan for four years and passed the JLPT N1 early on — yet still could not speak Japanese naturally. Living inside a language environment and reading it fluently do not add up to speaking it. Skill Acquisition Theory in second language acquisition research offers a clear account: practice effects are highly specific to the skill practiced — comprehension practice improves comprehension, and only production practice improves production (DeKeyser & Suzuki, 2025). If you want to speak, the only way is to speak.

This project exists so that speaking can actually happen: a teacher with a name, a personality, and a memory of every lesson. She lives on your own machine, talks with you through local open-source voices, and reaches out on her own — say, every evening at nine — to ask about your day. Speaking practice, arranged so that it simply happens.

## Features

- 🗣️ **Real voice conversation** — local Whisper transcription + multilingual speech synthesis; desk lessons are push-to-talk
- 📱 **Reachable from your phone** — a Discord duty daemon sits in your DM channel; send a voice message, class begins (polling costs zero tokens)
- 🌐 **Multilingual teaching persona** — whichever language you speak to her, she becomes a teacher *of that language* — except your native language, which stays a cozy chat-and-explanation channel; pace adapts to the level in your profile
- 🎭 **Persona as config** — the teacher's name, personality, teaching style, your language profile, textbook progress, voice cast: all plain Markdown files; save and it takes effect on the next utterance
- 🔊 **All-local, open-source voices, zero monthly cost** — Japanese via VOICEVOX · English via Kokoro · Chinese & Korean via MeloTTS; online engines serve only as fallback; per-language voice choice in `config/voices.md`
- 🌙 **Evening chats instead of homework** — at a set hour each night the teacher opens the conversation and asks about your day; no nagging, no checking up
- 📝 **Lesson memory** — every exchange is distilled into vocabulary, grammar points, and corrections in `lessons/`; she remembers next time

## Quick start

```bash
# 1. Install dependencies and voice engines (setup/README.md; read docs/known-issues.md first)
# 2. Birth ritual: answer a short interview, and your teacher is born 🐣
python3 setup/birth.py
# 3. Start class
~/.venvs/ai-teacher/bin/python engine/desktop_class.py   # desk lesson
python3 setup/services.py                                # background services & nightly timer
```

```
repo/
  setup/             ← birth ritual (birth.py) · service installer (services.py) · requirements
  config/examples/   ← config templates (the birth ritual generates your live copies in config/)
  engine/            ← brain (3 providers) · pipeline · duty daemon · nightly · desk class · MeloTTS server
  audition/          ← voice audition tool (audition.py <lang>)
  deploy/launchd/    ← macOS service templates
  docs/              ← Discord setup, FAQ, known issues
  lessons/           ← your lesson logs (auto-generated, never committed)
```

## The brain: three providers

Set `BRAIN_PROVIDER` in `.env`: **claude-code** (your own Claude Code CLI — first-party, within your subscription, fullest feature set) · **api** (your own Anthropic API key) · **ollama** (local model, fully offline, free). This project does not and will never piggyback on anyone's subscription through unofficial third-party channels.

## Security

See [SECURITY.md](SECURITY.md). Core principles: config is data, not code · least-privilege brain · secrets never enter the repo · chat channel denies strangers by default.

## Docs

- [Discord bot setup, step by step](docs/discord-setup.md)
- [FAQ](docs/faq.md)
- [Known issues / battle scars](docs/known-issues.md) (Chinese; English translation planned)

## Credits

- Voices: [VOICEVOX](https://voicevox.hiroshiba.jp/) (observe each character's terms of use), [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M), [MeloTTS](https://github.com/myshell-ai/MeloTTS)
- Transcription: [mlx-whisper](https://github.com/ml-explore/mlx-examples)
- Design philosophy inspired by [OpenClaw](https://openclaw.ai)'s workspace-as-markdown approach

## License

TBD (will be settled before the first public release).
