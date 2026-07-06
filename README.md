# AI Language Teacher（仓库名待定）

> An open-source, local-first AI language teacher you can actually *talk* to — on your desktop and from your phone.
> 一位开源、本地优先、真的能「开口对话」的 AI 语言老师——电脑上能聊，手机上也能随叫随到。

**状态：alpha · 目前仅在 macOS (Apple Silicon) 上验证 · 文档施工中**

## 为什么做这个

作者在日本生活了四年、早早通过了 JLPT N1——却依然无法自然地开口说日语。生活在语言环境里、能流畅阅读，都不等于会说。二语习得的 Skill Acquisition Theory 对此有清楚的解释：练习效果高度限定于所练的技能本身，练理解只提升理解，**练产出才提升产出**（DeKeyser & Suzuki, 2025）。想会说，只能去说。

这个项目就是为「去说」造的：一位有名字、有性格、记得你每一课的 AI 老师。她住在你自己的电脑上，用本地开源的声音和你对话，在你方便的时候（比如每晚九点）主动来找你聊今天发生的事——口语练习就这样自然发生。

## 特性

- 🗣️ **真语音对话**：本地 Whisper 听写 + 多语言语音合成，电脑课按回车就说
- 📱 **手机随叫随到**：Discord 值班员常驻，发语音条即上课（轮询零 token，不烧钱）
- 🌐 **多语言教学人格**：用哪种语言搭话，老师就变成那种语言的老师——唯独你的母语除外（母语只闲聊不教学）；每种语言按你档案里的水平调节奏
- 🎭 **人设即配置**：老师的名字、性格、教法、你的语言画像、教材进度、声优阵容——全部是 markdown 配置文件，改完保存即生效
- 🔊 **声音全本地开源、零月费**：日语 VOICEVOX · 英语 Kokoro · 中韩 MeloTTS，在线引擎只作兜底；每种语言的音色可自选（`config/voices.md`）
- 🌙 **夜谈代替作业**：每晚定时，老师主动来问你今天做了什么——不催促、不查岗
- 📝 **课堂记忆**：每次对话自动整理生词、语法点、纠错记录进 `lessons/`，老师下次记得

## 快速开始

> ⚠️ 安装向导（出生仪式）正在开发中。目前需要手动安装：见 `setup/README.md`。
> 踩坑必读：`docs/known-issues.md`（尤其是 MeloTTS 韩语的 MeCab 冲突）。

```
repo/
  config/examples/   ← 把这些复制到 config/ 并填成你自己的（人设·画像·课程·夜谈·声优）
  engine/            ← 管线·值班员·夜谈·电脑课·MeloTTS 服务
  setup/             ← 依赖清单与安装说明（向导施工中）
  deploy/launchd/    ← macOS 常驻服务模板
  docs/              ← 踩坑与专题文档
  lessons/           ← 你的课堂记录（自动生成，不入库）
```

## 大脑（LLM）接入

目前走 **Claude Code**（第一方 CLI，订阅内合规使用）。API key 与本地模型（Ollama）通道在路线图上。本项目不做、也永远不会做任何「订阅搭车」式的第三方接入。

## 安全

见 [SECURITY.md](SECURITY.md)。核心原则：配置是数据不是代码、老师大脑最小权限、密钥永不入库、聊天通道默认拒绝陌生人。

## 致谢

- 声音：[VOICEVOX](https://voicevox.hiroshiba.jp/)（四国めたん等角色请遵守各自的使用条款）、[Kokoro](https://huggingface.co/hexgrad/Kokoro-82M)、[MeloTTS](https://github.com/myshell-ai/MeloTTS)
- 听写：[mlx-whisper](https://github.com/ml-explore/mlx-examples)
- 设计哲学受 [OpenClaw](https://openclaw.ai) 「workspace 即 markdown」的启发

## License

待定（将在首个公开版本前确定）。
