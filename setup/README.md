# 安装

> 顺序：先装依赖与声音引擎（下面 0-2 节）→ 然后跑**出生仪式** `python3 setup/birth.py`
> （采访生成老师人设、学生画像、.env）→ 最后 `python3 setup/services.py` 排常驻服务。
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

## 3. 配置（二选一）

```bash
python3 setup/birth.py           # 推荐：出生仪式（采访 → 生成全套配置 + .env）
# 或者手动：
cp .env.example .env             # 填空
cp config/examples/*.md config/  # 逐份改成你自己的
```

## 4. 常驻服务（macOS launchd）

```bash
python3 setup/services.py   # 渲染 plist + 给出装载命令（VOICEVOX/Melo/值班员/夜谈）
```

手工方式见 `deploy/launchd/README.md`。声优不合口味？`python3 audition/audition.py <ja|en|zh|ko>` 一键海选。

## 5. 开课

```bash
# 电脑口语课（用主 venv 的 python）
~/.venvs/ai-teacher/bin/python engine/desktop_class.py

# Discord 值班员（手机通道；Discord bot 创建教程见 docs/，施工中）
~/.venvs/ai-teacher/bin/python engine/duty_daemon.py --announce
```
