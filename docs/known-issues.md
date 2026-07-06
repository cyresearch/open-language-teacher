# 已知坑（血泪实录）

以下每一条都是在真机（macOS Apple Silicon）上踩过并验证过解法的。

## 1. MeloTTS 韩语 × 日语：MeCab 大小写目录互撞 ⭐ 最大的坑

**症状**：`import mecab` 报 `No module named 'mecab'`，但 `pip list` 明明显示 python-mecab-ko 已安装；或 melo 的日语模块报 `Japanese requires mecab-python3 and unidic-lite`，各种重装无效。

**根因**：macOS 默认文件系统**不区分大小写**。日语用的 `mecab-python3` 安装 `MeCab/` 包目录，韩语用的 `python-mecab-ko` 安装 `mecab/` 包目录——在 macOS 上这是**同一个物理目录**，两个包的文件互相覆盖，先装的目录名获胜，后装的包文件被搅进去、`RECORD` 清单与磁盘现实对不上。

**解法**（中文与韩语必须住不同 venv）：

1. 中文 venv（如 `~/.venvs/melo`）：只装 `melotts + mecab-python3 + unidic-lite`，正常工作
2. 韩语 venv（如 `~/.venvs/melo-ko`）：装 `melotts + python-mecab-ko` 后做三针手术：
   - 目录两步改名（case-insensitive 文件系统上必须走中转名）：
     `cd <venv>/lib/python3.11/site-packages && mv MeCab _tmp && mv _tmp mecab`
   - `melo/text/japanese.py`：把 `raise ImportError(...)` 改成 `MeCab = None`（软化导入）
   - 同文件 `_TAGGER = MeCab.Tagger()` 包成 `try/except`，失败置 `None`
     （韩语课永远用不到日语的分析器，装死无害）
3. 两个 venv 各起一个 `engine/melo_server.py`（ZH :50022 / KR :50023）

## 2. MeloTTS 首跑「假慢」

**症状**：第一次合成中文 82 秒、韩语 93 秒，像是不可用。
**根因**：首跑在合成步骤里静默下载各语言的 BERT 模型（数百 MB），不在进度条里显示。
**事实**：热身后中文约 2 秒/句、韩语约 4 秒/句（M 系列芯片）。用常驻服务（melo_server.py + launchd）把装载成本一次付清。

## 3. MeloTTS 安装本身的依赖三连坑

- `fugashi` 编译失败 → 先 `brew install mecab`
- 老 `tokenizers` 在 Python 3.12 无预编译包、源码编译撞 Rust → **用 Python 3.11 建 venv**（有现成 wheel）
- brew 的 python@3.11 建 venv 时 ensurepip 罢工 → 用 [uv](https://github.com/astral-sh/uv)：`uv venv --python 3.11 <路径>`（顺带快得多）

## 4. Qwen3-TTS / 大模型 TTS 在 Mac 上的双杀

0.5B+ 级别的 LLM-TTS（Qwen3-TTS、CosyVoice 等）在 Apple Silicon 上实测：MPS 后端可能产出**坏音频**（音素错乱，母语者听不懂），且速度约为实时的 2.5-3.5 倍慢（一句话 20+ 秒）。它们在 NVIDIA GPU 上是优秀选择，但**不适合 Mac 本地实时对话**。Mac 请用 VOICEVOX / Kokoro / MeloTTS 这个量级。

## 5. kokoro-onnx 的中文是「英文嘴念中文」

kokoro-onnx 运行时对中文文本走英文音素化，产出母语者无法理解的发音。中文请用 MeloTTS。（Kokoro 官方运行时 + misaki 中文注音理论上可修，未验证。）

## 6. Discord API 拒绝 Python 默认 UA

用 `urllib`/`requests` 直连 Discord REST 会被 Cloudflare 403。本项目全部 Discord 调用走 `curl` 子进程，绕开 UA 歧视。

## 7. edge-tts 是非官方通道

微软 edge-tts 免费、音质好，但走的是逆向的非官方接口：需要联网、随时可能失灵。本项目只把它当**兜底**，不当主力。

## 8. 消息游标的丢信风险

值班员如果「先记账后办事」，进程在处理途中被杀会永久吞掉那条消息。本项目的守则：**办完一件才记一件账**，同一条消息连败 3 次才跳过并明说。宁可偶尔重复，不吞消息。
