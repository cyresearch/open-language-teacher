"""理想の私(Ideal L2 Self):用学生自己的声音,说出改好的句子。

可选功能,整套走 .env 配置(见 .env.example 的 IDEAL_SELF 段);没配就完全不参与。
声音模型用 GPT-SoVITS 微调(教程见 README「听见更流利的自己」),推理服务
**用时才启动**,闲置超时自动退出,不常驻吃内存。
"""
import json
import pathlib
import subprocess
import time
import urllib.request

import common

ENABLED = common.env("IDEAL_SELF", "").lower() in ("on", "1", "true", "yes")
CLONE_DIR = common.env_path("CLONE_DIR")        # GPT-SoVITS 安装目录
CLONE_PY = common.env_path("CLONE_PY")          # 它的 venv python
CLONE_CONFIG = common.env("CLONE_CONFIG")       # 推理配置(相对 CLONE_DIR)
CLONE_REF = str(common.env_path("CLONE_REF_AUDIO") or "")  # 参考音频(3-10 秒, 学生本人); env_path 会展开 ~
CLONE_REF_TEXT = common.env("CLONE_REF_TEXT")   # 参考音频里说的话
PORT = common.env("CLONE_PORT", "9880")
IDLE_EXIT = int(common.env("CLONE_IDLE_EXIT", "600"))  # 闲置多少秒后关服务

URL = f"http://127.0.0.1:{PORT}"
LAST_USED = common.RUNTIME / "clone_last_used"
LOGF = common.RUNTIME / "clone_api.log"


def configured():
    return ENABLED and CLONE_DIR and CLONE_PY and CLONE_CONFIG and CLONE_REF


def _ping(timeout=2):
    try:
        urllib.request.urlopen(URL + "/tts", timeout=timeout)
        return True
    except urllib.error.HTTPError:
        return True   # 有 HTTP 响应(哪怕报参数错)=服务在
    except Exception:
        return False


def _ensure_server(timeout=240):
    """服务不在就拉起(装载模型约 1 分钟),在就直接用。"""
    if _ping():
        return True
    with LOGF.open("a") as fh:
        subprocess.Popen(
            [str(CLONE_PY), "api_v2.py", "-a", "127.0.0.1", "-p", PORT,
             "-c", CLONE_CONFIG],
            cwd=str(CLONE_DIR), stdout=fh, stderr=subprocess.STDOUT)
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(4)
        if _ping():
            return True
    return False


def synth(text, out_ogg, lang="ja"):
    """合成一句"理想の私"。成功返回 ogg 路径,失败返回 None(不打断主流程)。"""
    if not configured():
        return None
    try:
        if not _ensure_server():
            print("ideal_self: 克隆服务没起来, 跳过", flush=True)
            return None
        payload = {
            "text": text, "text_lang": lang,
            "ref_audio_path": CLONE_REF,
            "prompt_text": CLONE_REF_TEXT, "prompt_lang": lang,
            "text_split_method": "cut5", "batch_size": 1,
            "media_type": "wav", "streaming_mode": False,
        }
        req = urllib.request.Request(URL + "/tts",
                                     data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            wav = r.read()
        if wav[:4] != b"RIFF":
            print("ideal_self: 合成返回非音频, 跳过", flush=True)
            return None
        tmp_wav = pathlib.Path(out_ogg).with_suffix(".wav")
        tmp_wav.write_bytes(wav)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_wav),
                        "-c:a", "libopus", "-b:a", "48k", out_ogg],
                       check=True, timeout=60)
        tmp_wav.unlink(missing_ok=True)
        LAST_USED.write_text(str(time.time()))
        return out_ogg
    except Exception as e:
        print(f"ideal_self: {e}", flush=True)
        return None


def maybe_shutdown_idle():
    """闲置超时就把克隆服务关掉释放内存(值班员主循环里每轮叫一次)。"""
    if not configured():
        return
    try:
        last = float(LAST_USED.read_text())
    except Exception:
        return
    if time.time() - last > IDLE_EXIT and _ping():
        subprocess.run(["pkill", "-f", f"api_v2.py -a 127.0.0.1 -p {PORT}"],
                       capture_output=True)
        LAST_USED.unlink(missing_ok=True)
        print("ideal_self: 闲置超时, 克隆服务已下班", flush=True)


PROTOCOL = (
    "\n【理想の私】生徒の発話に不自然な表現があって直した場合、または生徒が"
    "「理想の自分の声で」「Ideal L2 Self」などと頼んだ場合は、返事の一番最後に"
    "新しい行で「◆理想の私」と書き、その次の行に、生徒が言いたかった内容を"
    "自然な日本語で一〜二文だけ書く(説明・記号・翻訳は書かない)。"
    "該当しない時はこのブロック自体を書かない。"
)
