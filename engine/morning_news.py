#!/usr/bin/env python3
"""早间新闻：老师每天早上主动来讲当天的新闻（定时器触发，时间在 .env 的 MORNING_TIME）。

讲什么领域由 config/morning-news.md 决定（每次现读，改完即生效）。
新闻靠 WebSearch 现查，不编造；用学习语言短短地讲，顺便教生词。
用法：morning_news.py [--dry]   （--dry 只打印不发送，测试用）
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import duty_daemon as dd

DEFAULT_FIELDS = "世界大事（国际重要新闻）"


def news_fields():
    try:
        text = (dd.common.CONFIG / "morning-news.md").read_text()
        return text.strip() or DEFAULT_FIELDS
    except Exception:
        return DEFAULT_FIELDS


PROMPT = (
    "（システム指示：今は朝の定例「朝のニュース」の時間です。あなたの方から会話を始めてください。"
    "まず WebSearch で今日の最新ニュースを実際に調べること。作り話は絶対にしない——"
    "調べられなかったら正直にそう言って、代わりに朝の挨拶だけでいい。"
    "下記の生徒の興味分野から、大きなニュースを1〜2件選んで、朝の挨拶と一緒に、"
    "短く簡単な言葉で教えてあげてください。難しい言葉は簡単に言い換える。"
    "最後に、生徒が一言返したくなるような軽い問いかけを。"
    "読み上げられるので本文は短く（4〜7文くらい）。◆メモには出てきた生词・表現を整理する。\n"
    "【生徒の興味分野（config/morning-news.md より）】\n{fields}）"
)


def main():
    dry = "--dry" in sys.argv
    now = dd.common.now_local()
    st = dd.load_state()
    raw = dd.think(PROMPT.format(fields=news_fields()), st)
    dd.save_state(st)
    spoken, notes = dd.split_reply(raw)
    if dry:
        print("DRY:", spoken)
        if notes:
            print("MEMO:", notes)
        return
    dd.INBOX.mkdir(parents=True, exist_ok=True)
    ogg = str(dd.INBOX / f"morning_{now.date().isoformat()}.ogg")
    voice = None
    try:
        voice = dd.tts(spoken, ogg)
    except Exception as e:
        print("tts failed:", e)
    dd.send(f"☀️ {spoken}", voice)
    dd.lesson_log("（朝のニュース、先生から）", spoken, notes)
    print("morning news sent")


if __name__ == "__main__":
    main()
