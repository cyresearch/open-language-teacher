# AI Language Teacher (name TBD)

**English** | [中文](README.zh.md)

> An open-source, local-first AI language teacher you can actually talk to, at your desk and from your phone.

**Status: alpha. Verified on macOS (Apple Silicon) only. Docs under construction.**

## Why I built this

I have lived in Japan for four years and passed the JLPT N1 early on. I still cannot speak Japanese naturally. Living inside a language environment does not teach you to speak, and neither does reading well. Second language acquisition research describes this precisely: practice effects are specific to the skill you practice. Comprehension practice improves comprehension, and only production practice improves production (Skill Acquisition Theory; DeKeyser & Suzuki, 2025). If I want to speak, I have to speak.

So I built someone to speak with: a teacher who has a name, a personality, and a memory of every lesson. She lives on my own machine, talks with me through local open-source voices, and comes to find me every evening to ask about my day. Speaking practice stops being a chore I schedule and becomes something that simply happens.

## Features

- 🗣️ **Real voice conversation.** Local Whisper transcription plus multilingual speech synthesis. Desk lessons are push-to-talk.
- 📱 **Reachable from your phone.** A Discord duty daemon sits in your private channel. Send a voice message and class begins. Polling costs zero LLM tokens.
- 🌐 **Multilingual teaching persona.** Speak any language to her and she becomes a teacher of that language. Your native language is the one exception: it stays a relaxed channel for chat and explanations. Pace adapts to the level in your profile.
- 🎭 **Persona as config.** The teacher's name, personality, teaching style, your language profile, textbook progress, and voice cast are all plain Markdown files. Save, and it takes effect on the next utterance.
- 🔊 **All-local, open-source voices, zero monthly cost.** Japanese via VOICEVOX, English via Kokoro, Chinese and Korean via MeloTTS. Online engines serve only as fallback. Pick voices per language in `config/voices.md`.
- 🌙 **Evening chats instead of homework.** At a set hour each night the teacher opens the conversation and asks about your day. No nagging, no checking up.
- 📝 **Lesson memory.** Every exchange is distilled into vocabulary, grammar points, and corrections in `lessons/`. She remembers next time.

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

Set `BRAIN_PROVIDER` in `.env`:

- **claude-code**: your own Claude Code CLI. First-party, within your subscription, fullest feature set.
- **api**: your own Anthropic API key.
- **ollama**: a local model. Fully offline and free.

This project does not and will never piggyback on anyone's subscription through unofficial third-party channels.

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
