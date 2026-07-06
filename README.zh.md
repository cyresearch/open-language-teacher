# AI 语言老师（仓库名待定）

[English](README.md) | **中文**

> 一位开源、本地优先、真的能「开口对话」的 AI 语言老师：电脑上能聊，手机上也能随叫随到。

**状态：alpha · 目前仅在 macOS (Apple Silicon) 上验证 · 文档施工中**

## 为什么做这个

我在日本生活了四年，早早通过了 JLPT N1，却依然无法自然地开口说日语。生活在语言环境里、能流畅阅读，都不等于会说。二语习得的 Skill Acquisition Theory 对此有清楚的解释：练习效果高度限定于所练的技能本身，练理解只提升理解，**练产出才提升产出**（DeKeyser & Suzuki, 2025）。想会说，只能去说。

所以我给自己造了一个可以说话的对象：一位有名字、有性格、记得我每一课的 AI 老师。她住在我自己的电脑上，用本地开源的声音和我对话，每天晚上主动来找我聊今天发生的事。口语练习不再是需要排进日程的任务，它就这样自然发生了。

## 特性

- 🗣️ **真语音对话**：本地 Whisper 听写 + 多语言语音合成，电脑课按回车就说
- 📱 **手机随叫随到**：Discord 值班员常驻，发语音条即上课（轮询零 token，不烧钱）
- 🌐 **多语言教学人格**：用哪种语言搭话，老师就变成那种语言的老师。唯独你的母语除外，母语只闲聊不教学；每种语言按你档案里的水平调节奏
- 🎭 **人设即配置**：老师的名字、性格、教法、你的语言画像、教材进度、声优阵容，全部是 markdown 配置文件，改完保存即生效
- 🔊 **声音全本地开源、零月费**：日语 VOICEVOX · 英语 Kokoro · 中韩 MeloTTS，在线引擎只作兜底；每种语言的音色可自选（`config/voices.md`）
- 🌙 **夜谈代替作业**：每晚定时，老师主动来问你今天做了什么。不催促、不查岗
- 📝 **课堂记忆**：每次对话自动整理生词、语法点、纠错记录进 `lessons/`，老师下次记得

## 快速开始

```bash
# 1. 装依赖与声音引擎（见 setup/README.md；踩坑必读 docs/known-issues.md）
# 2. 出生仪式：采访几个问题，你的老师就此诞生 🐣
python3 setup/birth.py
# 3. 开课
~/.venvs/ai-teacher/bin/python engine/desktop_class.py   # 电脑口语课
python3 setup/services.py                                # 常驻服务与夜谈定时器
```

```
repo/
  setup/             ← 出生仪式向导 birth.py · 服务安装器 services.py · 依赖清单
  config/examples/   ← 配置样板（出生仪式会替你生成正式版到 config/）
  engine/            ← 大脑三通道·管线·值班员·夜谈·电脑课·MeloTTS 服务
  audition/          ← 声优海选工具（audition.py <语言>）
  deploy/launchd/    ← macOS 常驻服务模板
  docs/              ← 踩坑与专题文档
  lessons/           ← 你的课堂记录（自动生成，不入库）
```

## 大脑（LLM）三通道

`.env` 的 `BRAIN_PROVIDER` 三选一：**claude-code**（你自己的 Claude Code，第一方 CLI 订阅内合规，功能最全）· **api**（你自己的 Anthropic API key）· **ollama**（本地模型，零成本全离线）。本项目不做、也永远不会做任何「订阅搭车」式的第三方接入。

## 安全

见 [SECURITY.md](SECURITY.md)。核心原则：配置是数据不是代码、老师大脑最小权限、密钥永不入库、聊天通道默认拒绝陌生人。

## 文档

- [Discord bot 保姆级搭建教程](docs/discord-setup.md)（英文）
- [FAQ](docs/faq.md)（英文）
- [已知坑 / 血泪实录](docs/known-issues.md)

## 致谢

- 声音：[VOICEVOX](https://voicevox.hiroshiba.jp/)（四国めたん等角色请遵守各自的使用条款）、[Kokoro](https://huggingface.co/hexgrad/Kokoro-82M)、[MeloTTS](https://github.com/myshell-ai/MeloTTS)
- 听写：[mlx-whisper](https://github.com/ml-explore/mlx-examples)
- 设计哲学受 [OpenClaw](https://openclaw.ai) 「workspace 即 markdown」的启发

## License

待定（将在首个公开版本前确定）。
