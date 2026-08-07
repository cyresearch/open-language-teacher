"""大脑三通道：老师的 LLM 接入层。

.env 的 BRAIN_PROVIDER 三选一：
  claude-code  你自己的 Claude Code（第一方 CLI，订阅内合规；默认，功能最全：
               会话记忆走 --continue，且支持 WebSearch/Read 工具）
  api          你自己的 Anthropic API key（无工具；会话记忆走本地滚动历史）
  ollama       本地模型（零成本全离线；无工具；会话记忆走本地滚动历史）
  openai-compat  任何 OpenAI 兼容 API（Gemini / OpenAI / DeepSeek 等；
               无工具；会话记忆走本地滚动历史）

本项目绝不做任何「订阅搭车」式第三方接入——四条通道全部是正规门。
"""
import datetime
import json
import shutil
import subprocess
import time
import urllib.request

import common

PROVIDER = common.env("BRAIN_PROVIDER", "claude-code")
FALLBACK_REPLY = ("ごめんなさい、ちょっと調子が悪いみたい。"
                  "もう一度話しかけてくれますか？◆メモ\nなし")
HIST_CAP = 40  # api/ollama 通道的滚动历史条数上限


def think(text, persona, *, session="duty", st=None, model=None,
          tools=(), cwd=None):
    """一次思考。session 区分会话线（duty/desktop 各自记忆）。"""
    st = st if st is not None else {}
    try:
        if PROVIDER == "api":
            return _api(text, persona, session) or FALLBACK_REPLY
        if PROVIDER == "ollama":
            return _ollama(text, persona, session) or FALLBACK_REPLY
        if PROVIDER in ("openai-compat", "gemini"):
            return _openai_compat(text, persona, session) or FALLBACK_REPLY
        return _claude_code(text, persona, session, st, model, tools, cwd) \
            or FALLBACK_REPLY
    except Exception as e:
        print(f"brain error ({PROVIDER}): {e}")
        return FALLBACK_REPLY


# ---------- 通道 1：Claude Code ----------

def _session_rolled_over(last_ts):
    """跨天且闲置超 4 小时 → 该开新会话了（半夜聊到一半不砍断）。

    --continue 的会话历史只增不减，放任不管会越聊越慢；按日翻篇给延迟
    加了上限，跨会话的连续性靠 lessons/ 的课堂笔记兜底（老师可 Read）。
    """
    if not last_ts:
        return False
    gap = time.time() - last_ts
    same_day = datetime.date.fromtimestamp(last_ts) == datetime.date.today()
    return gap > 4 * 3600 and not same_day


def _claude_code(text, persona, session, st, model, tools, cwd):
    binpath = common.env("CLAUDE_BIN") or shutil.which("claude")
    if not binpath:
        raise RuntimeError("找不到 claude 命令（装 Claude Code 或在 .env 配 CLAUDE_BIN）")
    key = "claude_started" if session == "duty" else f"claude_started_{session}"
    ts_key = key.replace("claude_started", "claude_last_ts")
    if st.get(key) and _session_rolled_over(st.get(ts_key)):
        st[key] = False
    cmd = [binpath, "-p", text,
           "--model", model or common.env("CLAUDE_MODEL", "sonnet"),
           "--append-system-prompt", persona]
    if tools:
        cmd += ["--allowedTools", *tools]
    if st.get(key):
        cmd.append("--continue")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                       cwd=str(cwd) if cwd else None)
    reply = r.stdout.strip()
    if not reply and st.get(key):  # 会话丢了就重开一条
        cmd.remove("--continue")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                           cwd=str(cwd) if cwd else None)
        reply = r.stdout.strip()
    st[key] = True
    st[ts_key] = time.time()
    return reply


# ---------- 通道 2/3 共用的滚动历史 ----------

def _hist_file(session):
    return common.RUNTIME / f"history_{session}.json"


def _load_hist(session):
    f = _hist_file(session)
    try:
        return json.loads(f.read_text())
    except Exception:
        return []


def _save_hist(session, hist):
    f = _hist_file(session)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(hist[-HIST_CAP:], ensure_ascii=False))


def _post_json(url, payload, headers, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json",
                                          **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


# ---------- 通道 2：Anthropic API ----------

def _api(text, persona, session):
    key = common.env("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("BRAIN_PROVIDER=api 但 .env 没填 ANTHROPIC_API_KEY")
    hist = _load_hist(session) + [{"role": "user", "content": text}]
    out = _post_json(
        "https://api.anthropic.com/v1/messages",
        {"model": common.env("ANTHROPIC_MODEL", "claude-opus-4-8"),
         "max_tokens": 1024, "system": persona, "messages": hist},
        {"x-api-key": key, "anthropic-version": "2023-06-01"})
    reply = "".join(b.get("text", "") for b in out.get("content", [])
                    if b.get("type") == "text").strip()
    if reply:
        _save_hist(session, hist + [{"role": "assistant", "content": reply}])
    return reply


# ---------- 通道 4：OpenAI 兼容 API（Gemini / OpenAI / DeepSeek 等） ----------

def _openai_compat(text, persona, session):
    base = common.env("OPENAI_COMPAT_URL")
    key = common.env("OPENAI_COMPAT_KEY")
    if not base or not key:
        raise RuntimeError("BRAIN_PROVIDER=openai-compat 需要在 .env 配 "
                           "OPENAI_COMPAT_URL 和 OPENAI_COMPAT_KEY")
    model = common.env("OPENAI_COMPAT_MODEL", "gemini-2.5-flash")
    hist = _load_hist(session) + [{"role": "user", "content": text}]
    out = _post_json(
        base.rstrip("/") + "/chat/completions",
        {"model": model,
         "messages": [{"role": "system", "content": persona}] + hist},
        {"Authorization": f"Bearer {key}"})
    reply = (out.get("choices") or [{}])[0].get("message", {})         .get("content", "").strip()
    if reply:
        _save_hist(session, hist + [{"role": "assistant", "content": reply}])
    return reply


# ---------- 通道 3：Ollama 本地模型 ----------

def _ollama(text, persona, session):
    base = common.env("OLLAMA_URL", "http://127.0.0.1:11434")
    model = common.env("OLLAMA_MODEL", "qwen3")
    hist = _load_hist(session) + [{"role": "user", "content": text}]
    out = _post_json(
        base + "/api/chat",
        {"model": model, "stream": False,
         "messages": [{"role": "system", "content": persona}] + hist},
        {})
    reply = (out.get("message") or {}).get("content", "").strip()
    if reply:
        _save_hist(session, hist + [{"role": "assistant", "content": reply}])
    return reply
