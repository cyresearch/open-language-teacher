#!/usr/bin/env python3
"""晚间夜谈开场：老师主动问学生今天做了什么（定时器每晚触发，时间可配）。

开场白由老师带着课堂记忆现场生成，不是固定台词。规则详见 config/evening-chat.md。
用法：nightly.py [--dry]   （--dry 只打印不发送，测试用）
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import duty_daemon as dd

WEEKDAY_PROMPT = (
    "（システム指示：今は夜の定例「夜談」の時間です。あなたの方から会話を始めてください。"
    "生徒に、今日一日何をしたかを優しく聞いてください。最近の会話や授業の内容を覚えていれば、"
    "自然に踏まえて構いません。短くて温かい、話しかけたくなる一言にしてください。◆メモは「なし」で。）"
)
SUNDAY_PROMPT = (
    "（システム指示：今は日曜の夜、今週の小さな振り返りの時間です。あなたの方から会話を始めて、"
    "今週のレッスンで出てきた生词や表現を2〜3個だけ、軽く優しく振り返ってください。"
    "そのあと、今日一日何をしたかも聞いてください。短く温かく。◆メモは「なし」で。）"
)


def main():
    dry = "--dry" in sys.argv
    prompt = SUNDAY_PROMPT if datetime.date.today().weekday() == 6 else WEEKDAY_PROMPT
    st = dd.load_state()
    raw = dd.think(prompt, st)
    dd.save_state(st)
    spoken, _ = dd.split_reply(raw)
    if dry:
        print("DRY:", spoken)
        return
    dd.INBOX.mkdir(parents=True, exist_ok=True)
    ogg = str(dd.INBOX / f"nightly_{datetime.date.today().isoformat()}.ogg")
    voice = None
    try:
        voice = dd.tts(spoken, ogg)
    except Exception as e:
        print("tts failed:", e)
    dd.send(f"🌙 {spoken}", voice)
    dd.lesson_log("（夜の夜談、先生から）", spoken, "")
    print("nightly check-in sent")


if __name__ == "__main__":
    main()
