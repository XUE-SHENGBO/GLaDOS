# BTTwas 文件入口

本目录用于整理 BTTwas 的测试、练习与资料。对应 GitHub 分支：`BTTwas-improve`。

## 文件放哪里

| 目录 | 用途 | 例子 |
| --- | --- | --- |
| [tests/](tests/README.md) | 测试脚本、测试输入与结果说明 | `tests/emotion/test_emotion.py` |
| [exercises/](exercises/README.md) | 学习练习、独立实验和个人改进草稿 | `exercises/python/d03_emotion/main.py` |
| [notes/](notes/README.md) | 学习笔记、截图、硬件接线和问题说明 | `notes/oled/README.md` |
| [inbox/](inbox/README.md) | 暂时不知道如何分类的上传文件 | `inbox/2026-10-11_emotion/` |
| [templates/](templates/test-record.md) | 可以复制的测试记录模板 | `templates/test-record.md` |

每个主题建一个小文件夹，代码、输入数据和说明放在一起。推荐使用小写英文加下划线命名，避免长期使用 `test1`、`新建文件夹` 等不容易辨认的名称。

例如：

```text
BTTwas/
  tests/
    emotion/
      README.md         # 测什么、怎么运行、需要什么环境
      test_emotion.py   # 测试脚本
      fixtures/         # 小型测试输入（需要时再创建）
      results.md        # 实际结果与问题（需要时再创建）
```

以上是命名示例，具体测试代码等你上传后再添加。项目已有的 ROS 2 包和包内测试仍位于 `src/`；个人实验验证后，正式项目修改放入对应的包。

## 在 GitHub 网页上传

1. 打开仓库，先把分支选择为 **BTTwas-improve**。
2. 进入 `BTTwas`，再进入对应的分类目录。
3. 选择 **Add file → Upload files**，上传文件。
4. 提交说明写清用途，例如“添加 emotion 的 D03 测试”，并提交到 **BTTwas-improve**。

不确定分类时，可以直接上传到 `BTTwas/inbox/`，之后告诉我文件名或主题。

## 从本地上传

本地项目路径：`C:\Users\Baitan\Desktop\xsb-GLaDOS`。

在项目根目录执行；暂存前先检查文件列表：

```powershell
git branch --show-current
# 确认输出是 BTTwas-improve
git status --short
git add BTTwas/
git diff --cached --stat
git commit -m "Add emotion test files"
git push origin BTTwas-improve
```

提交说明根据实际内容修改。每次开始工作前检查分支；切换分支时先处理当前未提交的文件。

## 怎样让我快速找到文件

告诉我相对路径和任务，例如：

> 帮我检查 BTTwas-improve 分支的 BTTwas/tests/emotion/test_emotion.py，运行报错写在同目录的 results.md。

测试说明至少写清：用途、依赖环境、运行命令、预期结果、实际结果。可以复制 `templates/test-record.md`。

只提交需要共享的源码和小型资料；密码、API 密钥、虚拟环境、构建产物和大型录音不放入本目录。已有 `.gitignore` 会过滤常见的本地产物。
