#!/usr/bin/env python3
"""电脑口语课：按回车说话的本地对话课堂（零 API 费用）。

管线：按回车说话 → Whisper(本地) 转写 → claude 思考 → 多语言路由合成朗读
用法：desktop_class.py [device]      （device = 重新挑输出设备）
退出：Ctrl+C（课堂记录自动保存在 lessons/）
"""
import datetime
import json
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np
import sounddevice as sd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common
from pipeline import SR as PSR
from pipeline import WHISPER_REPO, ensure_engine, split_sentences, synth_sentence

CLAUDE_MODEL = common.env("DESKTOP_CLAUDE_MODEL", "haiku")  # 面对面对话求快
CLAUDE_BIN = common.env("CLAUDE_BIN") or shutil.which("claude")
LESSONS = common.LESSONS
SAMPLE_RATE = 16000
DEVCFG = common.RUNTIME / "desktop.json"


def persona():
    parts = []
    for name in ("teacher.md", "student.md", "curriculum.md"):
        try:
            parts.append((common.CONFIG / name).read_text())
        except Exception:
            pass
    if not parts:
        parts = ["あなたは優しい言語の先生です。生徒に短く自然な話し言葉で答えます。"]
    rules = ("\n【入力】生徒の発話は音声認識の文字起こしで、誤字がありえます。文脈で判断する。"
             "【出力】必ず1〜3文の短い話し言葉。読み上げられるので絵文字・記号・箇条書き・マークダウン禁止。")
    return "\n\n".join(parts) + rules


def list_output_devices():
    return [(i, d["name"]) for i, d in enumerate(sd.query_devices())
            if d["max_output_channels"] > 0]


def resolve_output_device(force_pick=False):
    devs = list_output_devices()
    cfg = json.loads(DEVCFG.read_text()) if DEVCFG.exists() else {}
    name = cfg.get("output_device")
    if not force_pick and name and any(n == name for _, n in devs):
        print(f"🔊 输出设备：{name}（想换：desktop_class.py device）")
        return name
    if not force_pick:
        for _, n in devs:  # 首选名字像耳机的
            if any(k in n for k in ("耳机", "AirPods", "Headphone", "headphone")):
                cfg["output_device"] = n
                DEVCFG.parent.mkdir(parents=True, exist_ok=True)
                DEVCFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
                print(f"🔊 自动选了输出设备：{n}（想换：desktop_class.py device）")
                return n
    print("可用输出设备：")
    for i, n in devs:
        print(f"  {i}. {n}")
    while True:
        raw = input("选哪个？输入编号: ").strip()
        try:
            name = dict(devs)[int(raw)]
            break
        except (ValueError, KeyError):
            print("再试一次~")
    cfg["output_device"] = name
    DEVCFG.parent.mkdir(parents=True, exist_ok=True)
    DEVCFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
    print(f"🔊 输出设备：{name}")
    return name


def record():
    frames = []

    def cb(indata, *_):
        frames.append(indata.copy())

    input("\n🎤 按回车开始说话...")
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                            dtype="float32", callback=cb)
    stream.start()
    input("   （说话中，说完再按回车）")
    stream.stop()
    stream.close()
    if not frames:
        return None
    audio = np.concatenate(frames)[:, 0]
    if len(audio) < SAMPLE_RATE * 0.5:  # 短于半秒当误触
        return None
    return audio


_whisper_loaded = False


def transcribe(audio):
    global _whisper_loaded
    import mlx_whisper
    if not _whisper_loaded:
        print("   （第一次转写要加载模型，稍等）")
        _whisper_loaded = True
    result = mlx_whisper.transcribe(audio, path_or_hf_repo=WHISPER_REPO)
    return result["text"].strip()


def think(text, first_turn):
    cmd = [CLAUDE_BIN, "-p", text, "--model", CLAUDE_MODEL,
           "--append-system-prompt", persona()]
    if not first_turn:
        cmd.append("--continue")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                       cwd=str(pathlib.Path(__file__).resolve().parent))
    reply = r.stdout.strip()
    if not reply:
        reply = "ごめんなさい、ちょっと聞こえませんでした。もう一度お願いします。"
    return reply


def speak(text, device=None):
    first_audio_at = None
    pending = False
    for s in split_sentences(text):
        try:
            arr = synth_sentence(s)
        except Exception as e:
            print(f"   （这句合成失败: {e}）")
            continue
        if pending:
            sd.wait()  # 等上一句放完 (下一句已在手上, 无缝衔接)
        if first_audio_at is None:
            first_audio_at = time.time()
        sd.play(arr, PSR, device=device)
        pending = True
    if pending:
        sd.wait()
    return first_audio_at


def main():
    if not CLAUDE_BIN:
        sys.exit("找不到 claude 命令：装 Claude Code，或在 .env 里配 CLAUDE_BIN")
    ensure_engine()
    out_dev = resolve_output_device(
        force_pick=(len(sys.argv) > 1 and sys.argv[1] == "device"))
    LESSONS.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    log = LESSONS / f"{today}-lesson.md"
    if not log.exists():
        log.write_text(f"# 口语课 {today}\n\n（本地引擎 · claude {CLAUDE_MODEL}）\n\n")
    print("=" * 46)
    print("  AI 语言老师 · 电脑口语课")
    print("  按回车说话，说完再按回车；Ctrl+C 下课")
    print(f"  课堂记录：{log}")
    print("=" * 46)

    first = True
    try:
        while True:
            audio = record()
            if audio is None:
                print("   （没录到声音，再试一次）")
                continue
            t0 = time.time()
            user_text = transcribe(audio)
            t1 = time.time()
            if not user_text:
                print("   （没听清，再说一次？）")
                continue
            print(f"\n私: {user_text}")
            reply = think(user_text, first)
            first = False
            t2 = time.time()
            print(f"先生: {reply}")
            first_audio_at = speak(reply, out_dev)
            t3 = time.time()
            lag = (first_audio_at - t2) if first_audio_at else (t3 - t2)
            print(f"   [听写 {t1-t0:.1f}s · 思考 {t2-t1:.1f}s · 开口 {lag:.1f}s]")
            with log.open("a") as f:
                stamp = datetime.datetime.now().strftime("%H:%M")
                f.write(f"**私** ({stamp}): {user_text}\n\n")
                f.write(f"**先生**: {reply}\n\n")
    except KeyboardInterrupt:
        print(f"\n\n今日はお疲れ様でした！课堂记录在：{log}")


if __name__ == "__main__":
    main()
