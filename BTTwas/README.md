# BTTwas

[个人分支](https://github.com/XUE-SHENGBO/GLaDOS/tree/BTTwas-improve) · [项目首页](../README.md)

| 目录 | 内容 |
| :--- | :--- |
| [src](./src/) | 功能代码 |
| [tests](./tests/) | 测试代码和数据，预留目录 |

后续功能代码继续放入 `src`，对应测试放入 `tests`。

# 一些说明

### 文件说明

| 文件 | 用途 |
| --- | --- |
| `src/ai_chat.py` | 文字对话 |
| `src/microphone.py` | 麦克风录音 |
| `src/speech_to_text.py` | 语音识别 |
| `src/text_to_speech.py` | 语音播放 |
| `src/voice_chat.py` | 完整语音对话入口 |

### 运行说明
使用 Python3.12 运行。以下命令适用于 macOS／Linux：

`python3 -m venv .venv`

`source .venv/bin/activate`

`python -m pip install -r requirements.txt`

`python src/voice_chat.py`

### 补充说明:
模型、录音和日志分别保存在 `models/、recordings/、logs/`里面，但是这类上内容已让 Git 忽略，不再上传。

# 目前初代内容存在(非完成)：
`F1`

`F2`

`F3`

* ps：
待完成python异步。
待完成F0树莓派环境配置、ros2接入与部署检验。