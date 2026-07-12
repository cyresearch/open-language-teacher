#!/usr/bin/env python3
"""Discord 值班员：常驻守信箱，让老师从手机随叫随到。

流程：学生的语音/文字/手写图片 → 听写(本地 Whisper)、图片交给大脑看图
      → 回复拆成「口语部分」+「◆メモ→课堂笔记」 → 文字先回、语音条跟上 → 记 lessons/
设计：轮询 0 token（本地 curl 带退避 5s/10s/20s）；只在真有消息时花一次大脑请求；
      思考期间每 8 秒续一次「正在输入」，学生知道消息已接单。
配置：.env 里的 DISCORD_BOT_TOKEN / DISCORD_CHANNEL_ID / DISCORD_OWNER_ID（见 .env.example）。
用法：duty_daemon.py [--announce]   （不会自己退出，杀掉即下班）
"""
import datetime
import json
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import time

import brain
import common
import ideal_self

CHANNEL = common.env("DISCORD_CHANNEL_ID")
HW_CHANNEL = common.env("HANDWRITING_CHANNEL_ID")  # 可选: 手写投递箱频道(iPad 快捷指令经 webhook 投图)
OWNER = common.env("DISCORD_OWNER_ID")
TOK = common.env("DISCORD_BOT_TOKEN")
TEACHER_NAME = common.env("TEACHER_NAME", "先生")
CLAUDE_MODEL = common.env("CLAUDE_MODEL", "sonnet")

HERE = pathlib.Path(__file__).resolve().parent
PIPE = HERE / "pipeline.py"
STATE = common.RUNTIME / "duty_state.json"
DUTY_CWD = common.RUNTIME / "duty_cwd"
INBOX = common.RUNTIME / "duty_inbox"
LESSONS = common.LESSONS

# 人设归配置档案 (config/*.md, 每句话现读, 改完即生效); 代码只管机械协议
FORMAT_RULES = (
    "\n【入力】生徒のメッセージは音声の文字起こしで、誤字がありえます。文脈で判断する。\n"
    f"【過去の授業】{LESSONS} に授業記録があり、Read で読み返せる。\n"
    "【出力形式】まず返事の本文だけを書く（読み上げられるため、絵文字・記号・箇条書き・"
    "マークダウンは禁止）。その後、新しい行に「◆メモ」と書き、その下に今回のレッスンメモを"
    "生徒の母語の箇条書きで書く：生词（读音+意思）、语法点、纠错（原句→自然说法）、话题。"
    "特に無い項目は書かなくてよい。メモが全く無ければ「◆メモ」の下に「なし」と書く。"
)


def time_note():
    # 老师的时间感全靠这里注入: CLI 只给日期不给钟点, 不注入就会把早上当晚上
    now = common.now_local()
    wd = "月火水木金土日"[now.weekday()]
    return (f"\n【今の日時】{now.strftime('%Y-%m-%d')}（{wd}曜）{now.strftime('%H:%M')}"
            f"（{now.strftime('%Z')}）。挨拶や時間帯の判断は必ずこの時刻に合わせる"
            f"（朝＝おはよう、昼＝こんにちは、夕方・夜＝こんばんは）。"
            f"これはシステム情報。返事に書かない・読み上げない。")


def persona():
    parts = []
    for name in ("teacher.md", "student.md", "omoide.md", "curriculum.md"):
        try:
            parts.append((common.CONFIG / name).read_text())
        except Exception:
            pass
    if not parts:
        parts = ["あなたは優しい言語の先生です。生徒に短く自然な話し言葉で答えます。"]
    extra = common.extra_rules()
    if extra:
        parts.append("【追加ルール】\n" + extra)
    rules = FORMAT_RULES
    if ideal_self.configured():
        rules += ideal_self.PROTOCOL
    return "\n\n".join(parts) + rules + time_note()


def log(*a):
    print(common.now_local().strftime("%H:%M:%S"), *a, flush=True)


def dget(path):
    # 用 curl 而不是 urllib: Discord 前面的 Cloudflare 会拒掉 Python 默认 UA (403)
    r = subprocess.run(["curl", "-s", "--max-time", "15",
                        "-H", f"Authorization: Bot {TOK}",
                        "https://discord.com/api/v10" + path],
                       capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)


def send(text, ogg=None, reply_to=None, channel=None):
    payload = {"content": text[:1900]}
    if reply_to:
        payload["message_reference"] = {"message_id": reply_to,
                                        "fail_if_not_exists": False}
    cmd = ["curl", "-s", "--max-time", "30",
           "-H", f"Authorization: Bot {TOK}",
           "-F", "payload_json=" + json.dumps(payload, ensure_ascii=False)]
    if ogg:
        cmd += ["-F", f"files[0]=@{ogg};type=audio/ogg"]
    cmd.append(f"https://discord.com/api/v10/channels/{channel or CHANNEL}/messages")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    ok = '"id"' in r.stdout
    log("send", "ok" if ok else f"FAIL {r.stdout[:120]}")
    return ok


def typing(channel=None):
    # 让手机上显示「正在输入…」, 表示消息已接单 (指示器约 10 秒, 处理各阶段各点一次)
    subprocess.run(["curl", "-s", "-X", "POST", "-d", "",
                    "-H", f"Authorization: Bot {TOK}",
                    f"https://discord.com/api/v10/channels/{channel or CHANNEL}/typing"],
                   capture_output=True, timeout=15)


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st))


def _sync_session_keys(st):
    # 定时任务(早间新闻/夜谈)是独立进程, 会在状态文件里更新 claude 会话标记。
    # 常驻值班员内存里的标记会过时→误判"该翻篇"另起新会话, 就看不到早间新闻了。
    # 每次处理消息前, 把会话标记从文件同步过来(只同步 claude_*, last_id 仍归自己管)。
    try:
        disk = load_state()
    except Exception:
        return
    for k, v in disk.items():
        if k.startswith("claude_"):
            st[k] = v


def stt(path):
    r = subprocess.run([sys.executable, str(PIPE), "stt", path],
                       capture_output=True, text=True, timeout=300)
    return r.stdout.strip().splitlines()[-1].strip() if r.stdout.strip() else ""


def tts(text, out):
    subprocess.run([sys.executable, str(PIPE), "tts", text, out],
                   capture_output=True, text=True, timeout=300, check=True)
    return out


def think(text, st):
    # 大脑走 brain.py 三通道 (claude-code / api / ollama, 由 .env 的 BRAIN_PROVIDER 定)
    return brain.think(text, persona(), session="duty", st=st,
                       model=CLAUDE_MODEL,
                       tools=("WebSearch", "WebFetch", "Read"), cwd=DUTY_CWD)


def think_with_typing(text, st, channel=None):
    # 思考期间每 8 秒续一次「正在输入」(指示器约 10 秒灭), 学生知道老师还在想
    stop = threading.Event()

    def keepalive():
        while not stop.wait(8):
            typing(channel)

    typing(channel)
    t = threading.Thread(target=keepalive, daemon=True)
    t.start()
    try:
        return think(text, st)
    finally:
        stop.set()


MARKERS = ("◆メモ", "◆理想の私", "◆思い出")


def split_reply(raw):
    # 三个块顺序不定(人设与协议各有偏好), 按出现位置切, 谁先谁后都能拆对
    found = sorted((raw.find(m), m) for m in MARKERS if raw.find(m) != -1)
    spoken = raw[:found[0][0]] if found else raw
    parts = {}
    for k, (pos, m) in enumerate(found):
        end = found[k + 1][0] if k + 1 < len(found) else len(raw)
        parts[m] = raw[pos + len(m):end].strip().lstrip("：:").strip()
    notes = parts.get("◆メモ", "")
    if notes in ("なし", "なし。", "无", "無し", "None"):
        notes = ""
    return (spoken.strip(), notes,
            parts.get("◆理想の私", ""), parts.get("◆思い出", ""))


def lesson_log(user_text, spoken, notes):
    LESSONS.mkdir(parents=True, exist_ok=True)
    now = common.now_local()
    f = LESSONS / f"{now.date().isoformat()}-lesson.md"
    stamp = now.strftime("%H:%M")
    with f.open("a") as fh:
        if not f.exists() or f.stat().st_size == 0:
            fh.write(f"# 口语课 {now.date().isoformat()}\n\n")
        fh.write(f"**私** ({stamp} 手机): {user_text}\n\n**先生**: {spoken}\n\n")
        if notes:
            fh.write(f"{notes}\n\n")


def handle(m, st, channel=None):
    ch = channel or CHANNEL
    _sync_session_keys(st)  # 同步定时任务(早间新闻/夜谈)可能更新过的会话标记
    text = (m.get("content") or "").strip()
    images = []
    for att in m.get("attachments", []):
        ct = att.get("content_type") or ""
        if ct.startswith("audio"):
            typing(ch)
            INBOX.mkdir(parents=True, exist_ok=True)
            dst = INBOX / f"{m['id']}.ogg"
            subprocess.run(["curl", "-s", "-L", "--max-time", "60",
                            "-o", str(dst), att["url"]], timeout=90, check=True)
            heard = stt(str(dst))
            if heard:
                text = (text + " " + heard).strip()
        elif ct.startswith("image") or ct == "application/pdf":
            # 手写练习/笔记照片: 存下来让大脑用 Read 亲眼看
            typing(ch)
            INBOX.mkdir(parents=True, exist_ok=True)
            suffix = pathlib.Path(att.get("filename") or "").suffix or ".png"
            dst = INBOX / f"{m['id']}_{att['id']}{suffix}"
            subprocess.run(["curl", "-s", "-L", "--max-time", "60",
                            "-o", str(dst), att["url"]], timeout=90, check=True)
            images.append(dst)
    if not text and not images:
        return
    shown = text if not images else \
        (f"{text}（+画像{len(images)}枚）" if text else "（画像を送りました）")
    ask = text
    if images:
        ask += ("\n【画像】生徒が画像を送りました。Read で開いて内容を読み取ってください。"
                "手書きの練習なら、まず読めた内容を確認してから添削・フィードバックを：\n"
                + "\n".join(str(p) for p in images))
        ask = ask.strip()
    log("heard:", shown[:70])
    spoken, notes, ideal, omoide = split_reply(think_with_typing(ask, st, ch))
    log("reply:", spoken[:70])
    msg = f"🎤 私：「{shown}」\n\n👩‍🏫 {TEACHER_NAME}：「{spoken}」"
    if notes:
        msg += f"\n\n📝 **今日のメモ**\n{notes}"
    send(msg, None, m["id"], channel=ch)  # 文字先行, 不等语音合成
    typing(ch)
    try:
        voice = tts(spoken, str(INBOX / f"reply_{m['id']}.ogg"))
        send("", voice, channel=ch)  # 语音条随后跟上
    except Exception as e:
        log("tts failed:", e)
    if ideal and ideal_self.configured():
        # 理想の私: 用学生自己的声音说出改好的句子(模型冷启动时这条会晚到 1 分钟左右)
        typing(ch)
        ogg = ideal_self.synth(ideal, str(INBOX / f"ideal_{m['id']}.ogg"))
        if ogg:
            send(f"✨ 理想の私：「{ideal}」", ogg, channel=ch)
            log("ideal-self sent:", ideal[:50])
    if omoide:
        # 思い出帳: 老师点名要记住的事, 由值班员代笔落盘(大脑保持只读)
        f = common.CONFIG / "omoide.md"
        if not f.exists():
            f.write_text("# 思い出帳\n\n> 老师的 ◆思い出 块由值班员自动写入这里, 手动整理也可以。\n\n")
        with f.open("a") as fh:
            fh.write(f"- {common.now_local().strftime('%Y-%m-%d')}: {omoide}\n")
        log("omoide +", omoide[:40])
    lesson_log(shown, spoken, notes)


def drain(chan, idkey, st, allow_webhook=False):
    """收一个频道的新消息逐条处理并记账。返回本轮是否有真消息(用于轮询提速)。

    allow_webhook: 手写投递箱频道除学生本人外, 也接收 webhook 投递的消息
    (iPad 快捷指令把 Notability 手写页经 webhook 发进来)。
    """
    try:
        msgs = dget(f"/channels/{chan}/messages?after={st[idkey]}&limit=5")
    except Exception as e:
        log("poll error:", e)
        return False
    got = False
    for m in sorted(msgs, key=lambda m: int(m["id"])):
        mine = not m["author"].get("bot") and m["author"].get("id") == OWNER
        hooked = allow_webhook and m.get("webhook_id")
        if mine or hooked:
            got = True
            try:
                handle(m, st, channel=chan)
                st.pop("retry_id", None)
                st.pop("retry_n", None)
            except Exception as e:
                log("handle error:", e)
                # 失败不记账, 下轮重试; 同一条连败 3 次才放弃并告知学生
                n = st.get("retry_n", 0) + 1 if st.get("retry_id") == m["id"] else 1
                st.update(retry_id=m["id"], retry_n=n)
                save_state(st)
                if n < 3:
                    break  # 不推进游标, 稍后重试这条
                send("😵 这条消息连续处理失败了三次，先跳过。"
                     "请查看 duty.log 排查。", reply_to=m["id"], channel=chan)
        # 办完一件才记一件账: 中途被杀就重做, 宁可偶尔重复不吞消息
        st[idkey] = m["id"]
        save_state(st)
    return got


def main():
    for key, val in (("DISCORD_BOT_TOKEN", TOK), ("DISCORD_CHANNEL_ID", CHANNEL),
                     ("DISCORD_OWNER_ID", OWNER)):
        if not val:
            sys.exit(f"缺配置：请在仓库根 .env 里填 {key}（样板见 .env.example）")
    if brain.PROVIDER == "claude-code" and not (common.env("CLAUDE_BIN")
                                                or shutil.which("claude")):
        sys.exit("找不到 claude 命令：装 Claude Code、在 .env 配 CLAUDE_BIN，"
                 "或把 BRAIN_PROVIDER 换成 api / ollama")
    DUTY_CWD.mkdir(parents=True, exist_ok=True)
    st = load_state()
    inits = [(CHANNEL, "last_id")] + ([(HW_CHANNEL, "last_id_hw")] if HW_CHANNEL else [])
    for chan, idkey in inits:
        if idkey not in st:
            msgs = dget(f"/channels/{chan}/messages?limit=1")
            st[idkey] = msgs[0]["id"] if msgs else "0"
            save_state(st)
    if "--announce" in sys.argv:
        send(f"📻 {TEACHER_NAME}、値班室に入りました！いつでも話しかけてくださいね。")
    log(f"on duty ({CLAUDE_MODEL}). last_id =", st["last_id"],
        f"| 手習い帖: {HW_CHANNEL or 'off'}")
    last_activity = time.time()
    while True:
        idle = time.time() - last_activity
        interval = 5 if idle < 600 else (10 if idle < 3600 else 20)
        active = drain(CHANNEL, "last_id", st)
        if HW_CHANNEL:
            active = drain(HW_CHANNEL, "last_id_hw", st, allow_webhook=True) or active
        if active:
            last_activity = time.time()
        ideal_self.maybe_shutdown_idle()  # 克隆服务闲置超时就下班, 不占内存
        time.sleep(interval)


if __name__ == "__main__":
    main()
