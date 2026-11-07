from getpass import getpass
from ai_chat import build_messages, ask_ai
from microphone import record_audio
from speech_to_text import transcribe_audio
from text_to_speech import speak


def main():
    print("————————————欢迎使用 GLaDOS ————————————")
    api_key = getpass("GLaDOS:主人你好呀~OvO请\n请输入您的 DeepSeek API Key:").strip()

    if not api_key:
        print("GLaDOS:主人~ API Key 不能为空哦~请重新输入")
        return

    messages = build_messages()
    print("GLaDOS:来啦~按回车开始录音,输入 exit 退出")

    while True:
        command = input("准备好后按回车：").strip()

        if command == "exit":
            print("GLaDOS:=v=主人再见!")
            break

        try:
            #录音&识别本轮讲话内容
            audio_path = record_audio()
            user_text = transcribe_audio(audio_path)

            if not user_text:
                print("GLaDOS:本次没有识别到讲话内容TOT,请主人重新录音...")
                continue

            print(f"GLaDOS:~识别内容为:{user_text}")

            #将本轮问题和历史对话 一起发送给AI模型,获取回答.
            request_messages = messages + [
                {"role": "user", "content": user_text}
            ]

            print("GLaDOS:正在思考...请稍等~")
            reply = ask_ai(request_messages, api_key)

        except Exception as error:
            print(f"GLaDOS:本轮处理失败:{error}")
            continue

        #请求成功将会保存本轮对话:
        messages = request_messages + [
            {"role": "assistant", "content": reply}
        ]

        print(f"GLaDOS:{reply}")

        #播放本轮 AI 回答(后面声音可以换)
        try:
            speak(reply)
        except Exception as error:
            print(f"GLaDOS:o-O?!语音播放失败:{error}")


if __name__ == "__main__":
    main()