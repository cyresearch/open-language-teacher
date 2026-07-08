"""共用地基：仓库根定位 + .env 加载 + 标准目录。

所有机器相关的路径/密钥都住在仓库根的 `.env`（gitignore，永不入库），
样板见 `.env.example`。代码里不允许出现任何写死的个人路径。
"""
import datetime
import os
import pathlib

ROOT = pathlib.Path(os.environ.get("TEACHER_HOME",
                                   pathlib.Path(__file__).resolve().parent.parent))
CONFIG = ROOT / "config"
LESSONS = ROOT / "lessons"
RUNTIME = ROOT / "runtime"  # 状态文件、收件箱、临时音频（gitignore）

_loaded = False


def load_env():
    """把仓库根 .env 的 KEY=VALUE 读进环境变量（不覆盖已存在的）。"""
    global _loaded
    if _loaded:
        return
    _loaded = True
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.split("#", 1)[0].strip()
        if k and v and k not in os.environ:
            os.environ[k] = v


def env(key, default=""):
    load_env()
    return os.environ.get(key, default).strip()


def env_path(key, default=""):
    v = env(key, default)
    return pathlib.Path(v).expanduser() if v else None


def now_local():
    """当前时间，按 .env 的 TIMEZONE（IANA 名，如 Asia/Tokyo）；没配就跟随系统时区。

    老师的时间感（早晚问候）、lessons 的时间戳与天数划分都以此为准，这样即使
    机器时区和你居住地不一致，也能对齐你居住地的时间。返回 tz-aware datetime。
    """
    tzname = env("TIMEZONE")
    if tzname:
        try:
            from zoneinfo import ZoneInfo
            return datetime.datetime.now(ZoneInfo(tzname))
        except Exception:
            pass
    return datetime.datetime.now().astimezone()


def extra_rules():
    """config/protocol.md 里「## 追加ルール」之后的部分（用户的自由加料区）。"""
    try:
        text = (CONFIG / "protocol.md").read_text()
        _, _, tail = text.partition("## 追加ルール")
        return tail.strip()
    except Exception:
        return ""
