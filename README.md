# Open Language Teacher

**English** | [中文](README.zh.md)

> An open-source AI language teacher that runs on your own computer, talks out loud, and messages you first.

**This project is under active development and will keep being updated and maintained. Only tested on macOS (Apple Silicon) so far.**

## Why I built this

I have lived in Japan for four years and passed the JLPT N1, but I still can't speak Japanese naturally.

Living in a language environment doesn't make you a speaker if you don't practice speaking, and the same goes for any language. If you want better speaking skills, you need speaking practice (Skill Acquisition Theory; DeKeyser & Suzuki, 2025).

An AI is a good speaking partner. She has a name, a personality, and a memory: she remembers every lesson you've had together. She lives on your own computer and speaks with open-source voices, so chatting never adds to a bill. Every evening she messages you first and asks what you did today.

## What she's like

- Voice conversation. Transcription runs on local Whisper, and each language has its own voice: Japanese via VOICEVOX, English via Kokoro, Chinese and Korean via MeloTTS. Zero monthly cost
- Reachable from your phone. A duty daemon watches your private Discord channel; send her a voice message and she replies with text plus a voice note
- Whichever language you speak to her, she teaches that language, adjusted to the level in your profile. Your native language is the exception: it is only for chat and explanations, no corrections
- Highly customizable. Her personality, teaching style, your language profile, textbook progress, and which voice speaks which language are all Markdown config files; save and it takes effect. That is also why it is called Open: the voices are open source, the brain can be open source, and the teacher herself is yours to customize
- Every lesson leaves notes. New words, grammar points, and corrections go into `lessons/`, and she reads them back later
- A nightly chat at a set hour. She asks what you did today. No homework, no streaks. If you don't answer tonight, she comes back tomorrow as usual

## Quick start

```bash
# 1. Install dependencies and voice engines (setup/README.md; read docs/known-issues.md first)
# 2. Birth ritual: answer a few questions to generate your teacher
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

Pick the LLM in `.env` with `BRAIN_PROVIDER`:

- **claude-code**: your own Claude Code CLI, running within your subscription. The only mode with web search
- **api**: your own Anthropic API key
- **ollama**: a local model, free and fully offline

All three are legitimate access paths. This project does not work around terms of service to ride on anyone's subscription.

## Security

See [SECURITY.md](SECURITY.md). Core principles: config is data, not code; the brain can only read and search; secrets never enter the repo; the chat channel answers you and no one else.

## Docs

- [Discord bot setup](docs/discord-setup.md)
- [FAQ](docs/faq.md)
- [Known issues](docs/known-issues.md) (Chinese for now, English translation planned)

## Credits

- Voices: [VOICEVOX](https://voicevox.hiroshiba.jp/) (observe each character's terms of use), [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M), [MeloTTS](https://github.com/myshell-ai/MeloTTS)
- Transcription: [mlx-whisper](https://github.com/ml-explore/mlx-examples)
- The config-as-files design is inspired by [OpenClaw](https://openclaw.ai)

## License

[MIT](LICENSE) © 2026 Chen Ying. Voice engines and characters keep their own terms (VOICEVOX character voices, for example); this license covers the code in this repository.
