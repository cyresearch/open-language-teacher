#!/usr/bin/env python3
"""语音管线：本地听写 + 按 config/voices.md 路由的多语言合成。

声优归配置（config/voices.md 的 JSON 块，每次合成前现读，改完即生效）：
  ja → VOICEVOX（本地） / en → Kokoro（本地） / zh·ko → MeloTTS 常驻服务（本地）
  任何本地引擎失败自动落到该语言的在线兜底（微软 edge-tts），保证不哑火。

用法:
  pipeline.py stt <音频文件>            # 听写 → 打印文本
  pipeline.py tts <文本> <输出.ogg>     # 合成 → ogg 语音条（按句路由多语言）
"""
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import wave

import common

VOICEVOX = common.env("VOICEVOX_URL", "http://127.0.0.1:50021")
ENGINE_RUN = common.env_path("VOICEVOX_RUN")
KOKORO_DIR = common.env_path("KOKORO_DIR", "~/.local/opt/kokoro")
WHISPER_REPO = common.env("WHISPER_REPO", "mlx-community/whisper-large-v3-turbo")
VOICES_MD = common.CONFIG / "voices.md"
SR = 24000  # 各引擎输出统一重采样到 24kHz

DEFAULT_VOICES = {
    "ja": {"engine": "voicevox", "speaker": 0},
    "en": {"engine": "kokoro", "voice": "af_heart"},
    "zh": {"engine": "melo", "port": 50022},
    "ko": {"engine": "melo", "port": 50023},
}
EDGE_FALLBACK = {
    "ja": "ja-JP-NanamiNeural",
    "en": "en-US-JennyNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ko": "ko-KR-SunHiNeural",
}

_kokoro = None


def load_voices():
    try:
        m = re.search(r"```json\s*(\{.*?\})\s*```", VOICES_MD.read_text(), re.S)
        cfg = json.loads(m.group(1))
        return {**DEFAULT_VOICES, **cfg}
    except Exception as e:
        print(f"warn: voices.md 读取失败, 用默认配置 ({e})", file=sys.stderr)
        return DEFAULT_VOICES


def api(path, params=None, data=None, timeout=120):
    url = VOICEVOX + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, data=data, method="POST")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def ensure_engine():
    import time
    probe = urllib.request.Request(VOICEVOX + "/version")
    try:
        urllib.request.urlopen(probe, timeout=2)
        return
    except Exception:
        pass
    if not ENGINE_RUN or not ENGINE_RUN.exists():
        sys.exit("VOICEVOX 引擎不在线，且 .env 未配置 VOICEVOX_RUN（引擎可执行文件路径）")
    subprocess.Popen([str(ENGINE_RUN), "--host", "127.0.0.1",
                      "--port", VOICEVOX.rsplit(":", 1)[-1]],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    for _ in range(60):
        time.sleep(2)
        try:
            urllib.request.urlopen(probe, timeout=2)
            return
        except Exception:
            continue
    sys.exit("VOICEVOX engine did not come up")


def _collapse_repeats(text):
    """压掉 Whisper 结尾的重复幻觉：同一短语连续重复 3 次以上就压回 2 次。

    Whisper 在录音结尾的静音/呼吸段容易陷入重复循环（例：「買った道で」刷屏），
    是解码层的已知毛病。stt() 关掉 condition_on_previous_text 已能大幅减少，
    这里对漏网的连续重复再兜一道底。单元最长 40 字，避免长串正则回溯拖慢。
    """
    if not text:
        return text
    return re.sub(r"(.{1,40}?)\1{2,}", lambda m: m.group(1) * 2, text)


def stt(path):
    import mlx_whisper
    # condition_on_previous_text=False：不把已输出的文本喂回下一段解码，
    # 斩断「越重复越重复」的反馈循环（Whisper 结尾重复幻觉的主因）。
    # 温度回退 (0→1) + 压缩比阈值 2.4 走默认：重复度过高的解码会自动换温度重来。
    result = mlx_whisper.transcribe(
        path, path_or_hf_repo=WHISPER_REPO,
        condition_on_previous_text=False,
    )
    print(_collapse_repeats(result["text"].strip()))


def detect_lang(s):
    kana = len(re.findall(r"[ぁ-んァ-ヶー]", s))
    hangul = len(re.findall(r"[가-힣]", s))
    latin = len(re.findall(r"[A-Za-z]", s))
    cjk = len(re.findall(r"[一-鿿]", s))
    if kana:
        return "ja"
    if hangul:
        return "ko"
    if latin >= 3 and latin >= cjk:
        return "en"
    if cjk:
        return "zh"
    return "en" if latin else "ja"


def _resample(arr, sr_from, sr_to):
    import numpy as np
    if sr_from == sr_to:
        return arr
    x_old = np.linspace(0, 1, len(arr))
    x_new = np.linspace(0, 1, int(len(arr) * sr_to / sr_from))
    return np.interp(x_new, x_old, arr)


def _wav_bytes_to_pcm(wavb):
    import numpy as np
    w = wave.open(io.BytesIO(wavb), "rb")
    sr = w.getframerate()
    arr = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype("f4") / 32768
    w.close()
    return _resample(arr, sr, SR)


def _voicevox_pcm(text, speaker=0):
    ensure_engine()
    q = api("/audio_query", {"text": text, "speaker": speaker})
    wav = api("/synthesis", {"speaker": speaker}, q)
    return _wav_bytes_to_pcm(wav)


def _kokoro_pcm(text, voice="af_heart", lang="en"):
    import numpy as np
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(KOKORO_DIR / "kokoro-v1.0.onnx"),
                         str(KOKORO_DIR / "voices-v1.0.bin"))
    klang = "en-us" if lang == "en" else "cmn"
    samples, sr = _kokoro.create(text, voice=voice, speed=1.0, lang=klang)
    return _resample(np.asarray(samples, dtype="f4"), sr, SR)


def _melo_pcm(text, port=50022):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/tts",
                                 data=json.dumps({"text": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return _wav_bytes_to_pcm(r.read())


def _edge_pcm(text, voice):
    # 在线兜底 (微软 edge-tts, 非官方通道)
    import numpy as np
    edge = common.env("EDGE_TTS_BIN") or shutil.which("edge-tts")
    if not edge:
        raise RuntimeError("edge-tts 不在 PATH，且 .env 未配置 EDGE_TTS_BIN")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        mp3 = tf.name
    wav = mp3.replace(".mp3", ".wav")
    try:
        subprocess.run([str(edge), "--voice", voice, "--text", text,
                        "--write-media", mp3], check=True, timeout=60,
                       capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3,
                        "-ar", str(SR), "-ac", "1", wav], check=True, timeout=60)
        w = wave.open(wav, "rb")
        arr = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype("f4") / 32768
        w.close()
        return arr
    finally:
        pathlib.Path(mp3).unlink(missing_ok=True)
        pathlib.Path(wav).unlink(missing_ok=True)


def synth_sentence(s, voices=None):
    lang = detect_lang(s)
    cfg = (voices or load_voices()).get(lang, DEFAULT_VOICES[lang])
    try:
        engine = cfg.get("engine")
        if engine == "voicevox":
            return _voicevox_pcm(s, cfg.get("speaker", 0))
        if engine == "kokoro":
            return _kokoro_pcm(s, cfg.get("voice", "af_heart"), lang)
        if engine == "melo":
            return _melo_pcm(s, cfg.get("port", 50022))
        if engine == "edge":
            return _edge_pcm(s, cfg["voice"])
        raise ValueError(f"unknown engine: {engine}")
    except Exception as e:
        print(f"warn: {lang} 主引擎失败({e}), 落在线兜底", file=sys.stderr)
        return _edge_pcm(s, EDGE_FALLBACK[lang])


def split_sentences(text):
    parts = re.split(r"(?<=[。！？♪])|(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def tts(text, out_path):
    import numpy as np
    # 语音合成前清掉 markdown 记号（否则 ** * # ` 之类会被念成"星号"）
    text = re.sub(r"\*\*|__|\*|_|`+|#+", "", text)
    text = re.sub(r"(?m)^[ \t]*[-+]\s+", "", text)
    voices = load_voices()
    pieces = []
    gap = np.zeros(int(SR * 0.18), dtype="f4")
    for s in split_sentences(text):
        try:
            pieces.append(synth_sentence(s, voices))
            pieces.append(gap)
        except Exception as e:
            print(f"warn: 句子合成失败 ({e}): {s[:30]}", file=sys.stderr)
    if not pieces:
        sys.exit("nothing synthesized")
    audio = np.concatenate(pieces)
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        tmp = tf.name
    w = wave.open(tmp, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
    w.close()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp,
                    "-c:a", "libopus", "-b:a", "48k", out_path], check=True)
    pathlib.Path(tmp).unlink(missing_ok=True)
    print(out_path)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "stt":
        stt(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "tts":
        tts(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
