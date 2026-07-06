# macOS 常驻服务（launchd）

把 `template.plist` 复制成每个服务的文件，替换三个占位符后装入 `~/Library/LaunchAgents/`：

- `__LABEL__`：服务名（建议 `com.<你的老师名>.<服务>`）
- `__PYTHON__`：对应 venv 的 python 绝对路径
- `__ARGS__`：脚本与参数（见下表，每个参数一行 `<string>`）

| 服务 | python | 参数 | 说明 |
|---|---|---|---|
| voicevox | （随便，不用 python 时直接把引擎 run 当第一个 ProgramArguments） | `--host 127.0.0.1 --port 50021` | 日语引擎 |
| melo-zh | `~/.venvs/melo/bin/python` | `<repo>/engine/melo_server.py ZH 50022` | 中文服务 |
| melo-ko | `~/.venvs/melo-ko/bin/python` | `<repo>/engine/melo_server.py KR 50023` | 韩语服务 |
| duty | `~/.venvs/ai-teacher/bin/python` | `<repo>/engine/duty_daemon.py` | Discord 值班员 |
| nightly | `~/.venvs/ai-teacher/bin/python` | `<repo>/engine/nightly.py` | 夜谈（用 StartCalendarInterval 替换 KeepAlive，见模板注释） |

装载与管理：

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<label>.plist   # 装载
launchctl kickstart -k gui/$(id -u)/<label>                             # 重启
launchctl bootout gui/$(id -u)/<label>                                  # 卸载
```

> 注意：plist 里的 PATH 要包含 claude 命令所在目录（launchd 不读你的 shell 配置）。
