# 安装（手动版）

> 自动化安装向导（出生仪式）正在开发中。以下是 macOS (Apple Silicon) 的手动步骤。
> 建议先通读 `docs/known-issues.md`，尤其要装韩语的话。

## 0. 系统依赖

```bash
brew install ffmpeg mecab
# 推荐 uv（快、且绕开 brew python venv 的坑）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 1. 主 venv（听写 + 英语声 + 兜底）

```bash
uv venv --python 3.12 ~/.venvs/ai-teacher
uv pip install --python ~/.venvs/ai-teacher/bin/python -r setup/requirements/main.txt
```

## 2. 声音引擎

- **VOICEVOX**（日语）：从 https://voicevox.hiroshiba.jp/ 下载引擎版（macOS arm64），
  解压后把 `run` 的路径填进 `.env` 的 `VOICEVOX_RUN`
- **Kokoro**（英语）：下载 `kokoro-v1.0.onnx` 和 `voices-v1.0.bin`
  （https://github.com/thewh1teagle/kokoro-onnx 的 releases），放进 `.env` 的 `KOKORO_DIR` 指向的目录
- **MeloTTS**（中文，可选）：
  ```bash
  uv venv --python 3.11 ~/.venvs/melo
  uv pip install --python ~/.venvs/melo/bin/python -r setup/requirements/melo-zh.txt
  ```
- **MeloTTS 韩语**（可选，有已知坑）：
  ```bash
  uv venv --python 3.11 ~/.venvs/melo-ko
  uv pip install --python ~/.venvs/melo-ko/bin/python -r setup/requirements/melo-ko.txt
  # 然后按 docs/known-issues.md 第 1 条做三针手术（必需！）
  ```

## 3. 配置

```bash
cp .env.example .env            # 填空
cp config/examples/*.md config/  # 逐份改成你自己的
```

## 4. 常驻服务（macOS launchd）

按 `deploy/launchd/README.md` 渲染并加载：VOICEVOX、MeloTTS 中/韩服务、Discord 值班员、夜谈定时器。

## 5. 开课

```bash
# 电脑口语课（用主 venv 的 python）
~/.venvs/ai-teacher/bin/python engine/desktop_class.py

# Discord 值班员（手机通道；Discord bot 创建教程见 docs/，施工中）
~/.venvs/ai-teacher/bin/python engine/duty_daemon.py --announce
```
