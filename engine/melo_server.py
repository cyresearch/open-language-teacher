#!/usr/bin/env python
"""MeloTTS 常驻小服务（开机待命，省掉每次 1-30 秒的模型装载）。

用法: melo_server.py <语言 ZH|KR|EN|...> <端口>
接口: GET /  → "ok <语言>"（健康检查）
      POST /tts  {"text": "..."}  → wav 音频
注意: 要用装了对应语言依赖的 venv 的 python 来跑
     （中文 venv 与韩语 venv 必须分开——见 docs/known-issues.md 的 MeCab 冲突条目）。
"""
import json
import pathlib
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer

LANG = sys.argv[1] if len(sys.argv) > 1 else "ZH"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 50022

print(f"loading MeloTTS {LANG} ...", flush=True)
from melo.api import TTS

tts = TTS(language=LANG, device="auto")
SPK = list(tts.hps.data.spk2id.values())[0]
print(f"ready on 127.0.0.1:{PORT}", flush=True)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        body = f"ok {LANG}".encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            text = json.loads(self.rfile.read(n))["text"]
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                tmp = tf.name
            tts.tts_to_file(text, SPK, tmp, speed=1.0)
            wav = pathlib.Path(tmp).read_bytes()
            pathlib.Path(tmp).unlink(missing_ok=True)
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(wav)))
            self.end_headers()
            self.wfile.write(wav)
        except Exception as e:
            msg = str(e).encode()[:500]
            self.send_response(500)
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)


HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
