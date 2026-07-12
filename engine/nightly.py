#!/usr/bin/env python3
"""晚间夜谈开场：老师主动问学生今天做了什么（定时器每晚触发，时间可配）。

开场白由老师带着课堂记忆现场生成，不是固定台词。规则详见 config/evening-chat.md。
周日晚升级为「一周复盘」：老师读完本周课堂笔记，归纳高频错误、新掌握的词和
语法、值得夸的进步，规则在 config/weekly-review.md。
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
REVIEW_PROMPT = (
    "（システム指示：今夜は日曜、週に一度の「振り返りの夜」です。あなたの方から会話を始めてください。\n"
    "まず、今週の授業記録を Read で読み返すこと（全部）：\n{files}\n"
    "復盘の方針は {cfg} にもあります（Read で読める）。\n"
    "出力は二つ：\n"
    "・読み上げ本文＝3〜4文の温かい日本語の総括。今週いちばんの進歩を具体的に褒めて、"
    "来週そっと意識してほしい点をひとつだけ。数字の羅列や説教はしない。最後に今日一日どうだったかも軽く聞く。\n"
    "・◆メモ＝生徒の母語で書く構造化した週次復盘：\n"
    "【本周概况】聊了几天、主要话题一行\n"
    "【高频错误】反复出现的单词/语法/句式，各配正确说法，最多 5 条\n"
    "【新掌握】本周第一次学、之后能正确使用的词和语法\n"
    "【夸夸】引用具体的进步瞬间（比如纠正一次后马上用对了的）\n"
    "【下周小目标】只写一个）"
)


def week_files():
    """本周（含今天在内往前 7 天）实际存在的课堂笔记路径。"""
    today = dd.common.now_local().date()
    out = []
    for i in range(7):
        f = dd.LESSONS / f"{(today - datetime.timedelta(days=i)).isoformat()}-lesson.md"
        if f.exists():
            out.append(str(f))
    return out


def main():
    dry = "--dry" in sys.argv
    now = dd.common.now_local()
    if now.weekday() == 6:
        prompt = REVIEW_PROMPT.format(
            files="\n".join(week_files()) or "（今週の記録なし——その場合は普通の夜談に）",
            cfg=str(dd.common.CONFIG / "weekly-review.md"))
    else:
        prompt = WEEKDAY_PROMPT
    st = dd.load_state()
    raw = dd.think(prompt, st)
    dd.save_state(st)
    spoken, _, _, _ = dd.split_reply(raw)
    if dry:
        print("DRY:", spoken)
        return
    dd.INBOX.mkdir(parents=True, exist_ok=True)
    ogg = str(dd.INBOX / f"nightly_{now.date().isoformat()}.ogg")
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
