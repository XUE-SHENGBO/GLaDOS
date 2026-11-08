#->接deepseek
import json
from getpass import getpass
from urllib.error import URLError
from urllib.request import Request, urlopen

SYSTEM_PROMPT =(
     "你是 GLaDOS,一个具身智能助手。"
     "请使用中文回答,保持简洁准确,有条理。"
)
#身份可修改

def build_messages():
    """创建对话,先放入助手的身份设定"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

def ask_ai(messages, api_key):
    payload = {
        "model": "deepseek-flash",
        "messages": messages,
        "stream": False,
        "thinking": {"type": "disabled"},
        "max_tokens": 512,
    }

    request = Request(
        url="https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    with urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["choices"][0]["message"]["content"]
#默认deepseek-flash模型,可修改.(量大便宜)

class AIChat:
    def __init__(self, api_key):
        self.api_key = api_key
        self.messages = build_messages()

    def chat(self, user_text):
        request_messages = self.messages + [
            {"role": "user", "content": user_text}
        ]
        reply = ask_ai(request_messages, self.api_key)
        self.messages = request_messages + [
            {"role": "assistant", "content": reply}
        ]
        return reply
    
    def reset(self):
        self.messages = build_messages()

def main():
    print("————————————欢迎使用 GLaDOS ————————————")
    print("GLaDOS:主人我在TOT\nGLaDOS:qwq~请您先登录")

    api_key = getpass("请输入您的 DeepSeek API Key:").strip()

    if not api_key:
        print("API Key 不能为空")
        return

    chat=AIChat(api_key)

    print("————————————————登录成功————————————————")
    print("GLaDOS:主人我已登录成功~请问有什么吩咐呢!\n(输入 exit 结束聊天)\n")

    while True:
        user_text = input("你：").strip()

        if user_text == "exit":
            print("GLaDOS:主人再见~")
            break

        if not user_text:
            print("输入不能为空")
            continue

        print("GLaDOS:正在思考中...")
        try:
            reply = chat.chat(user_text)
        except URLError as e:
            print(f"GLaDOS:我请求失败了TOT:{e}")
            continue
        print(f"GLaDOS:{reply}")


if __name__ == "__main__":
    main()
