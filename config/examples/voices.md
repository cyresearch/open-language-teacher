# 声优配置 · voices

> 老师每种语言用哪把嗓子。**改下面的 JSON 块保存即生效**（管线每次合成前现读，无需重启）。
> 用法：复制到 `config/voices.md`。想先试听再选：用 audition/ 里的海选工具。

## 当前配置

```json
{
  "ja": {"engine": "voicevox", "speaker": 0},
  "en": {"engine": "kokoro", "voice": "af_heart"},
  "zh": {"engine": "melo", "port": 50022},
  "ko": {"engine": "melo", "port": 50023}
}
```

## 可选音色目录

### 日语（engine: voicevox，本地开源，43 角色 127 种声线）

- 示例：`speaker: 0` = 四国めたん（あまあま）。ずんだもん(3)、春日部つむぎ(8)、雨晴はう(10)、九州そら(16) 等
- 全名单：引擎起来后 `curl http://127.0.0.1:50021/speakers`

### 英语（engine: kokoro，本地开源，54 种声线）

- 示例：`af_heart`（温暖）、af_bella（活泼明亮）、af_sarah（沉稳）、af_sky（清爽）
- 命名规律：af_ = 美音女声，bf_ = 英音女声，am_/bm_ = 男声

### 中文（engine: melo，本地开源，常驻服务默认 :50022）

- MeloTTS 中文为单声道模型（无同引擎替补）
- 在线备选：`{"engine": "edge", "voice": "zh-CN-XiaoxiaoNeural"}`（晓晓）或 XiaoyiNeural（晓伊）

### 韩语（engine: melo，本地开源，常驻服务默认 :50023）

- MeloTTS 韩语为单声道模型。安装有已知坑，见 docs/known-issues.md
- 在线备选：`{"engine": "edge", "voice": "ko-KR-SunHiNeural"}`

## 引擎说明

| engine | 本地/在线 | 参数 | 说明 |
|---|---|---|---|
| voicevox | 本地开源 | `speaker`（数字） | 日语专精，需 VOICEVOX 引擎在线 |
| kokoro | 本地开源 | `voice`（名字） | 英语强项；模型路径在 .env 的 KOKORO_DIR |
| melo | 本地开源 | `port` | MeloTTS 常驻服务（engine/melo_server.py） |
| edge | 在线 | `voice`（微软音色名） | 免费但走非官方通道，主用兜底皆可 |

- 任何本地引擎合成失败时，管线自动落到该语言的在线兜底（微软线），保证不哑火
- 想用 ElevenLabs 等付费引擎：属于扩展路线，见开源蓝图（接入自己的 key）
