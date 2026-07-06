# Open Language Teacher · 开源语言老师

[English](README.md) | **中文**

> 一位跑在你自己电脑上的开源 AI 语言老师：能出声对话，还会主动来找你说话。

**状态：alpha，目前只在 macOS (Apple Silicon) 上验证过，文档还在长。**

## 为什么做这个

我在日本生活了四年，N1 早就过了，可我到现在还是没法自然地开口说日语。

我花了挺久才承认，我每天做的那些事（生活在日本、流畅地读文献、坐在讲座里听）其实都练不到「说」。这方面的研究结论很直白：练什么就只长什么，练理解只长理解，想会说就只能去说（Skill Acquisition Theory; DeKeyser & Suzuki, 2025）。

可是口语练习需要一个对象，真人对象要么忙、要么贵、要么让人紧张。所以我干脆造了一个。她有名字，性格是我自己写在文本文件里的，我们上过的每一课她都记得。她住在我自己的电脑上，用开源的声音说话，聊多久都不产生账单。每天晚上她会先来找我，问我今天做了什么，我用日语回答她。说穿了诀窍就一个：有人先开口，练习才会发生。

## 她是什么样的

- 你说，她出声回。听写是本地 Whisper，每种语言有自己的嗓子：日语 VOICEVOX、英语 Kokoro、中文和韩语 MeloTTS。零月费
- 手机上也找得到她。一个小值班程序守着你们的私人 Discord 频道，躺在床上发条语音，她回文字加语音条
- 用哪种语言跟她说话，她就当哪种语言的老师，深浅按你档案里写的水平来。唯独你的母语例外：母语只用来闲聊和讲解，不纠错
- 她的一切都是 markdown 文件。性格、教法、你的语言画像、教材进度、哪种语言用哪把嗓子，改完保存，下一句话她就变了。这也是项目叫 Open 的原因：声音开源，大脑可以开源，老师本人对你完全敞开，随你改写
- 每节课都留笔记。生词、语法点、纠错都进 `lessons/`，她之后真的会回头看，所以「上周学了什么」这种问题问得出答案
- 我自己最喜欢的是夜谈。到你定的钟点，她主动开场问你今天过得怎么样。没有作业，没有打卡，没有负罪感，今晚不回，她明天照常来

## 快速开始

```bash
# 1. 装依赖与声音引擎（见 setup/README.md；踩坑必读 docs/known-issues.md）
# 2. 出生仪式：回答几个问题，你的老师就此诞生 🐣
python3 setup/birth.py
# 3. 开课
~/.venvs/ai-teacher/bin/python engine/desktop_class.py   # 电脑口语课
python3 setup/services.py                                # 常驻服务与夜谈定时器
```

```
repo/
  setup/             ← 出生仪式 birth.py · 服务安装器 services.py · 依赖清单
  config/examples/   ← 配置样板（出生仪式会替你生成正式版到 config/）
  engine/            ← 大脑三通道·管线·值班员·夜谈·电脑课·MeloTTS 服务
  audition/          ← 声优海选工具（audition.py <语言>）
  deploy/launchd/    ← macOS 常驻服务模板
  docs/              ← Discord 教程、FAQ、踩坑记录
  lessons/           ← 你的课堂记录（自动生成，不入库）
```

## 大脑

给她装脑子有三条路，改 `.env` 里的 `BRAIN_PROVIDER`：

- **claude-code**：你自己的 Claude Code。第一方工具，跑在你的订阅里，也是唯一带联网搜索的模式
- **api**：你自己的 Anthropic API key
- **ollama**：本地模型，免费且完全离线

三条都是正门。这个项目永远不会从后门蹭任何人的订阅。

## 安全

见 [SECURITY.md](SECURITY.md)。一句话版本：配置是数据不是代码，大脑只能读和搜，密钥永不入库，聊天频道除了你谁都不理。

## 文档

- [Discord bot 保姆级搭建教程](docs/discord-setup.md)（英文）
- [FAQ](docs/faq.md)（英文）
- [已知坑 / 血泪实录](docs/known-issues.md)

## 致谢

- 声音：[VOICEVOX](https://voicevox.hiroshiba.jp/)（各角色的使用条款请自行遵守）、[Kokoro](https://huggingface.co/hexgrad/Kokoro-82M)、[MeloTTS](https://github.com/myshell-ai/MeloTTS)
- 听写：[mlx-whisper](https://github.com/ml-explore/mlx-examples)
- 「workspace 即 markdown」的点子来自玩 [OpenClaw](https://openclaw.ai) 时的启发

## License

[MIT](LICENSE) © 2026 Chen Ying。语音引擎与角色声音各有自己的使用条款（比如 VOICEVOX 的角色声音），本许可证只覆盖本仓库的代码。
