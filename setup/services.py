#!/usr/bin/env python3
"""常驻服务安装器（macOS launchd）：渲染 plist 并给出装载命令。

渲染到 deploy/launchd/rendered/，默认只渲染不装载（命令打给你自己跑，透明可控）。
用法：python3 setup/services.py
"""
import pathlib
import plistlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
import common  # noqa: E402

OUT = ROOT / "deploy" / "launchd" / "rendered"
PREFIX = "com.aiteacher"


def ask(prompt, default=""):
    tip = f"（默认：{default}，输入 - 跳过）" if default else "（回车跳过）"
    val = input(f"  {prompt}{tip}: ").strip()
    if val == "-":
        return ""
    return val or default


def plist(label, args, nightly=None, path_extra=""):
    d = {
        "Label": label,
        "ProgramArguments": args,
        "RunAtLoad": True,
        "StandardOutPath": f"/tmp/{label}.log",
        "StandardErrorPath": f"/tmp/{label}.log",
        "EnvironmentVariables": {
            "PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"
                    + (f":{path_extra}" if path_extra else "")},
    }
    if nightly:
        h, m = nightly.split(":")
        d["StartCalendarInterval"] = {"Hour": int(h), "Minute": int(m)}
    else:
        d["KeepAlive"] = True
    return d


def main():
    if not sys.stdin.isatty():
        sys.exit("需要交互终端：python3 setup/services.py")
    print("=" * 46)
    print("  常驻服务安装器（launchd）")
    print("=" * 46)
    home = pathlib.Path.home()
    main_py = ask("主 venv 的 python", f"{home}/.venvs/ai-teacher/bin/python")
    vv_run = ask("VOICEVOX 引擎 run 路径", common.env("VOICEVOX_RUN"))
    zh_py = ask("MeloTTS 中文 venv 的 python", f"{home}/.venvs/melo/bin/python")
    ko_py = ask("MeloTTS 韩语 venv 的 python", f"{home}/.venvs/melo-ko/bin/python")
    nightly = common.env("NIGHTLY_TIME", "21:00")
    claude_dir = ""
    import shutil
    c = common.env("CLAUDE_BIN") or shutil.which("claude") or ""
    if c:
        claude_dir = str(pathlib.Path(c).parent)

    services = []
    if vv_run and pathlib.Path(vv_run).expanduser().exists():
        services.append((f"{PREFIX}.voicevox",
                         plist(f"{PREFIX}.voicevox",
                               [str(pathlib.Path(vv_run).expanduser()),
                                "--host", "127.0.0.1", "--port", "50021"])))
    if zh_py and pathlib.Path(zh_py).expanduser().exists():
        services.append((f"{PREFIX}.melo-zh",
                         plist(f"{PREFIX}.melo-zh",
                               [str(pathlib.Path(zh_py).expanduser()),
                                str(ROOT / "engine/melo_server.py"), "ZH", "50022"])))
    if ko_py and pathlib.Path(ko_py).expanduser().exists():
        services.append((f"{PREFIX}.melo-ko",
                         plist(f"{PREFIX}.melo-ko",
                               [str(pathlib.Path(ko_py).expanduser()),
                                str(ROOT / "engine/melo_server.py"), "KR", "50023"])))
    if main_py and pathlib.Path(main_py).expanduser().exists():
        mp = str(pathlib.Path(main_py).expanduser())
        if common.env("DISCORD_BOT_TOKEN"):
            services.append((f"{PREFIX}.duty",
                             plist(f"{PREFIX}.duty",
                                   [mp, str(ROOT / "engine/duty_daemon.py")],
                                   path_extra=claude_dir)))
            services.append((f"{PREFIX}.nightly",
                             plist(f"{PREFIX}.nightly",
                                   [mp, str(ROOT / "engine/nightly.py")],
                                   nightly=nightly, path_extra=claude_dir)))
        else:
            print("  （.env 没配 Discord —— 跳过值班员与夜谈服务）")

    if not services:
        sys.exit("没有可渲染的服务（路径都不存在？）")
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"\n  渲染到 {OUT}：")
    for label, d in services:
        f = OUT / f"{label}.plist"
        with f.open("wb") as fh:
            plistlib.dump(d, fh)
        print(f"    ✓ {f.name}")
    print("\n  装载命令（复制执行；plist 先拷到 ~/Library/LaunchAgents/）：\n")
    print(f"    cp {OUT}/*.plist ~/Library/LaunchAgents/")
    for label, _ in services:
        print(f"    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/{label}.plist")
    print("\n  卸载：launchctl bootout gui/$(id -u)/<label>；日志在 /tmp/<label>.log")


if __name__ == "__main__":
    main()
