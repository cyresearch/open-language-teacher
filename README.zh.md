# Open Language Teacher · 开源语言老师

[English](README.md) | **中文**

> 一位跑在你自己电脑上的开源 AI 语言老师：能出声对话，还会主动来找你说话。

**这个项目还在开发阶段，会持续更新和维护。目前只在 macOS (Apple Silicon) 上验证过。**

## 为什么做这个

我在日本生活了四年，有通过N1，但没法自然地开口说日语。

生活在语言环境 但是不主动练习口语的话,依然不会说这一门语言; 其他语言同理. 如果想要提升口语能力,就必须要有口语练习这方面 (Skill Acquisition Theory; DeKeyser & Suzuki, 2025）。

AI就是很好的口语练习对象。她有名字，有性格,有记忆.你们上过的每一课她都记得。她住在你自己的电脑上，用开源的声音说话，聊多久都不产生账单。每天晚上她会先来找你，问你今天做了什么.

## 她是什么样的

- 能语音对话。听写用本地 Whisper，每种语言有自己的嗓子：日语 VOICEVOX、英语 Kokoro、中文和韩语 MeloTTS，零月费
- 手机上也能找到她。值班程序守着你们的私人 Discord 频道，发语音给她，她回文字加语音条
- 用哪种语言跟她说话，她就当哪种语言的老师，难度按你档案里写的水平调整。你的母语例外：母语只用来闲聊和讲解，不纠错
- 高度可定制。她的性格、教法、你的语言画像、教材进度、每种语言用哪把嗓子，全是 markdown 配置文件，改完保存就生效。这也是叫 Open 的原因：声音开源，大脑可以开源，老师本身也随你定制
- 每节课自动留笔记。生词、语法点、纠错都记在 `lessons/` 里，她之后会回头看
- 每晚定时夜谈。到点她主动来问你今天做了什么，不布置作业，也不打卡。今晚没回，她明天照常来
- 每天早上有新闻小课。她联网现查当天的真新闻，挑你感兴趣的领域讲一两条，用简单的目标语言，配母语大意和生词。领域写在配置里，时间随你定

## 快速开始

```bash
# 1. 装依赖与声音引擎（见 setup/README.md；踩坑必读 docs/known-issues.md）
# 2. 出生仪式：回答几个问题，生成你的老师
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

老师用哪个 LLM 思考，在 `.env` 里选 `BRAIN_PROVIDER`：

- **claude-code**：你自己的 Claude Code，跑在你的订阅里，也是唯一带联网搜索的模式
- **api**：你自己的 Anthropic API key
- **ollama**：本地模型，免费且完全离线

三条路都是正规接入，这个项目不会绕过服务条款去蹭订阅用量。

## 听见更流利的自己

她纠正你的句子之后，用**你自己的声音**把地道的说法读给你听。那个「说得流利的自己」是最强的学习动力之一（Ideal L2 Self；Dörnyei, 2009）。CHI 2026 的 AI Twin 研究先做出了这件事，这里是本地开源版。

- 素材就是你平时发她的 Discord 语音，聊几天就攒够（我用了约 30 分钟）。项目自动切片转写，你在审核页删掉转写错的
- 训练用 GPT-SoVITS 微调：云 GPU 几分钟、不到一美元；本地 CPU 也行，就是慢
- 合成全在本地跑，声音不出你的电脑。模型永远归你，占约 3.5GB
- 想更像：用 iPhone 语音备忘录录几分钟无损音频掺进去（设置里先开无损），有好麦克风更好。素材质量就是模型上限
- 预算充足可以用 ElevenLabs（AI Twin 论文同款），效果更好：Instant 克隆几十秒素材出声，$6/月起；Professional 档要一小时以上素材、训练数小时、忙时排队两到六小时，$22/月起。声音存在云端，停订即失效

## 安全

见 [SECURITY.md](SECURITY.md)。核心原则：配置是数据不是代码；大脑只能读和搜索；密钥不入库；聊天频道只认你一个人。

## 文档

- [Discord bot 搭建教程](docs/discord-setup.md)（英文）
- [FAQ](docs/faq.md)（英文）
- [已知坑](docs/known-issues.md)

## 致谢

- 声音：[VOICEVOX](https://voicevox.hiroshiba.jp/)（各角色的使用条款请自行遵守）、[Kokoro](https://huggingface.co/hexgrad/Kokoro-82M)、[MeloTTS](https://github.com/myshell-ai/MeloTTS)
- 听写：[mlx-whisper](https://github.com/ml-explore/mlx-examples)
- 配置文件化的设计受 [OpenClaw](https://openclaw.ai) 启发
- 「听见更流利的自己」的理论根基是 Zoltán Dörnyei 的 L2 Motivational Self System（Ideal L2 Self）
- 声音克隆功能的实现灵感来自 Park, M., Lee, S., Ma, J., & Yoon, D. (2026). AI Twin: Enhancing ESL Speaking Practice through AI Self-Clones of a Better Me. *CHI 2026*. https://doi.org/10.1145/3772318.3790266
- 本地声音克隆引擎：[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)（MIT）

## License

[MIT](LICENSE) © 2026 Chen Ying。语音引擎与角色声音各有自己的使用条款（比如 VOICEVOX 的角色声音），本许可证只覆盖本仓库的代码。
