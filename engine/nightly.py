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
    "（システム指示：今夜は日曜、週に一度の「振り返りの夜」——一週間に一度の大事な儀式です。"
    "あなたの方から会話を始めてください。\n"
    "手を抜かないこと。まず今週の授業記録を Read で**全部**読み返し、"
    "日付と生徒の原文を引用できる状態になってから書くこと：\n{files}\n"
    "復盘の方針は {cfg} にもあります（Read で読める）。\n"
    "出力は二つ、どちらも省略不可：\n"
    "・読み上げ本文＝先生からの小さな手紙（6〜9文）。今週の具体的な場面を最低ふたつ引きながら"
    "（あの日のあの一言、あの言い間違いからの成長など）、心を込めて振り返る。"
    "終わりに来週そっと意識してほしい点をひとつと、今日一日どうだったかの問いかけ。"
    "定型文やその場で書けそうな一般論は書かない——記録を読んだ人にしか書けない手紙にする。\n"
    "・◆メモ＝生徒の母語で書く構造化した週次復盘。「なし」は禁止。各項目に"
    "**生徒の原文の引用と日付**を付けること：\n"
    "【本周概况】聊了几天、每天的主要话题各一行\n"
    "【高频错误】反复出现的单词/语法/句式 3〜5 条，每条＝原句引用（几号说的）→ 正确说法 → 一句为什么\n"
    "【新掌握】本周学过、之后真的用对了的词和语法，各标出处日期\n"
    "【夸夸】引用 2〜3 个具体的进步瞬间原句\n"
    "【下周小目标】只写一个，要具体到可以执行）"
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
    spoken, notes, _, _ = dd.split_reply(raw)
    if dry:
        print("DRY:", spoken)
        if notes:
            print("MEMO:", notes)
        return
    dd.INBOX.mkdir(parents=True, exist_ok=True)
    ogg = str(dd.INBOX / f"nightly_{now.date().isoformat()}.ogg")
    voice = None
    try:
        voice = dd.tts(spoken, ogg)
    except Exception as e:
        print("tts failed:", e)
    dd.send(f"🌙 {spoken}", voice)
    if notes:
        # 周复盘的结构化メモ单独成条发出(过长就分段, Discord 单条上限 2000 字)
        head = "📝 **今週の復盘**\n"
        chunk = 1800
        for i in range(0, len(notes), chunk):
            dd.send((head if i == 0 else "") + notes[i:i + chunk])
    dd.lesson_log("（夜の夜談、先生から）", spoken, notes)
    print("nightly check-in sent")


if __name__ == "__main__":
    main()
