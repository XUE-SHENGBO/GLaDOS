# BTTwas

[个人分支](https://github.com/XUE-SHENGBO/GLaDOS/tree/BTTwas-improve) · [项目首页](../README.md)

| 目录 | 内容 |
| :--- | :--- |
| [src](./src/) | 功能代码，目前包含终端文字聊天模块 |
| [tests](./tests/) | 测试代码和数据，预留目录 |

## 文字聊天

当前完成 F1 的独立终端聊天版本，支持 DeepSeek 调用、多轮上下文、空输入检查、请求失败后继续输入，以及输入 `exit` 退出。

使用 Python 3 和标准库运行。在 `BTTwas` 目录打开终端后执行：

```bash
python3 src/ai_chat.py
```

按提示在本机终端输入 DeepSeek API Key。密钥输入时隐藏，本程序将其保存在内存中。聊天上下文保留到本次程序退出。

密钥读取完成后，第一次发送问题时才会实际连接 DeepSeek。运行需要网络和可用的 DeepSeek API 额度。

后续功能代码继续放入 `src`，对应测试放入 `tests`。
