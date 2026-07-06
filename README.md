# Open Language Teacher

**English** | [中文](README.zh.md)

> An open-source AI language teacher that runs on your own computer, talks out loud, and messages you first.

**Status: alpha. Only tested on macOS (Apple Silicon) so far. Docs are still growing.**

## Why I built this

I've lived in Japan for four years. I passed the JLPT N1 early on. And I still can't speak Japanese naturally.

It took me a while to admit that nothing I did every day (living here, reading fluently, sitting in lectures) was actually training my speaking. The research on this is pretty blunt: you improve at exactly the skill you practice, not the neighboring ones. Practicing comprehension makes you better at comprehension. Speaking only gets better when you speak (Skill Acquisition Theory; DeKeyser & Suzuki, 2025).

But speaking practice needs a partner, and human partners are busy, or expensive, or make you nervous. So I built one. She has a name, and a personality that I wrote myself in a text file. She remembers every lesson we've had. She lives on my own machine and speaks with open-source voices, so no meter is running while we chat. And every evening she messages me first, just to ask what I did today. I answer in Japanese. That's the whole trick, honestly: practice happens because someone starts it.

## What she's like

- You talk, she talks back, out loud. Transcription is local Whisper, and each language gets its own voice: Japanese via VOICEVOX, English via Kokoro, Chinese and Korean via MeloTTS. Zero monthly cost.
- She's on your phone too. A small daemon watches a private Discord channel, so you can send her a voice message from bed and she replies with text plus a voice note.
- Speak any language to her and she becomes a teacher of that language, pitched at the level you wrote in your profile. Your native language is the exception: that one stays a cozy channel for chatting and explanations, no corrections.
- Everything about her is a plain Markdown file. Personality, teaching style, your language profile, textbook progress, which voice speaks which language. Edit, save, and she's already different on the next sentence. This is also why the project is called Open: the voices are open source, the brain can be open source, and the teacher herself is completely open to being rewritten by you.
- Lessons leave notes. New words, grammar points, and corrections all land in `lessons/`, and she reads them back later, so asking "what did we learn last week?" actually works.
- My favorite part is the evening chat. At whatever hour you set, she opens the conversation and asks about your day. No homework, no streaks, no guilt. If you don't answer tonight, she just tries again tomorrow.

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

## The brain

Three ways to give her a mind. Set `BRAIN_PROVIDER` in `.env`:

- **claude-code**: your own Claude Code CLI. First-party, runs within your subscription, and it's the only mode with web search.
- **api**: your own Anthropic API key.
- **ollama**: a local model. Free and fully offline.

All three are front doors. This project never sneaks into anyone's subscription through a back door.

## Security

See [SECURITY.md](SECURITY.md). The short version: configs are data, not code. The brain can only read and search. Secrets never enter the repo. The chat channel ignores everyone but you.

## Docs

- [Discord bot setup, step by step](docs/discord-setup.md)
- [FAQ](docs/faq.md)
- [Known issues / battle scars](docs/known-issues.md) (Chinese for now, English translation planned)

## Credits

- Voices: [VOICEVOX](https://voicevox.hiroshiba.jp/) (mind each character's terms of use), [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M), [MeloTTS](https://github.com/myshell-ai/MeloTTS)
- Transcription: [mlx-whisper](https://github.com/ml-explore/mlx-examples)
- The workspace-as-markdown idea came from playing with [OpenClaw](https://openclaw.ai)

## License

[MIT](LICENSE) © 2026 Chen Ying. Voice engines and characters keep their own terms (VOICEVOX character voices, for example); this license covers the code in this repository.
