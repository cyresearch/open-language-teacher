#!/usr/bin/env python3
"""声优海选：一键试听某种语言的候选音色，听完把心水的写进 config/voices.md。

用法：python3 audition/audition.py <ja|en|zh|ko>
样本落在 runtime/audition/，macOS 上自动播放（其他系统打印路径自己放）。
注意：要用主 venv 的 python 跑（需要 numpy 等）；melo 候选需要对应服务在线。
"""
import pathlib
import subprocess
import sys
import wave

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
import common  # noqa: E402
import pipeline  # noqa: E402

LINES = {
    "ja": "こんばんは！今日も一緒に、楽しくおしゃべりしましょうね。",
    "en": "Hi there! Let's have a fun little chat together today, shall we?",
    "zh": "晚上好呀！今天也一起开开心心地聊聊天吧。",
    "ko": "안녕하세요! 오늘도 같이 즐겁게 이야기해요.",
}
CANDIDATES = {
    "ja": [("voicevox", {"speaker": 0}, "四国めたん あまあま (0)"),
           ("voicevox", {"speaker": 3}, "ずんだもん (3)"),
           ("voicevox", {"speaker": 8}, "春日部つむぎ (8)"),
           ("voicevox", {"speaker": 10}, "雨晴はう (10)"),
           ("voicevox", {"speaker": 16}, "九州そら (16)")],
    "en": [("kokoro", {"voice": "af_heart"}, "af_heart 温暖"),
           ("kokoro", {"voice": "af_bella"}, "af_bella 活泼"),
           ("kokoro", {"voice": "af_sarah"}, "af_sarah 沉稳"),
           ("kokoro", {"voice": "af_sky"}, "af_sky 清爽"),
           ("kokoro", {"voice": "af_nicole"}, "af_nicole 气声")],
    "zh": [("melo", {"port": 50022}, "MeloTTS 中文（本地）"),
           ("edge", {"voice": "zh-CN-XiaoxiaoNeural"}, "晓晓（在线）"),
           ("edge", {"voice": "zh-CN-XiaoyiNeural"}, "晓伊（在线）")],
    "ko": [("melo", {"port": 50023}, "MeloTTS 韩语（本地）"),
           ("edge", {"voice": "ko-KR-SunHiNeural"}, "SunHi（在线）")],
}


def save_wav(arr, path):
    import numpy as np
    pcm = (np.clip(arr, -1, 1) * 32767).astype("<i2")
    w = wave.open(str(path), "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(pipeline.SR)
    w.writeframes(pcm.tobytes())
    w.close()


def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else ""
    if lang not in CANDIDATES:
        sys.exit(f"用法：audition.py <{'|'.join(CANDIDATES)}>")
    outdir = common.RUNTIME / "audition"
    outdir.mkdir(parents=True, exist_ok=True)
    text = LINES[lang]
    made = []
    for i, (engine, params, label) in enumerate(CANDIDATES[lang], 1):
        print(f"  [{i}/{len(CANDIDATES[lang])}] {label} 合成中...", flush=True)
        try:
            arr = pipeline.synth_sentence(text, voices={lang: {"engine": engine, **params}})
            f = outdir / f"{lang}-{i}-{engine}.wav"
            save_wav(arr, f)
            made.append((label, f))
        except Exception as e:
            print(f"      ✗ 失败：{e}")
    if not made:
        sys.exit("一个都没合成出来——检查引擎是否在线（见 setup/README.md）")
    print(f"\n  🎧 开始试听（样本在 {outdir}）：")
    for label, f in made:
        print(f"    ▶ {label}")
        if sys.platform == "darwin":
            subprocess.run(["afplay", str(f)])
        else:
            print(f"      （自行播放：{f}）")
    print("\n  心水哪个？把它写进 config/voices.md 的 JSON 块即刻生效。")


if __name__ == "__main__":
    main()
