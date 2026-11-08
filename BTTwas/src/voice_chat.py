from getpass import getpass
from ai_chat import AIChat
from microphone import record_audio
from speech_to_text import load_model,transcribe_audio
from text_to_speech import speak
import logging
from pathlib import Path


def main():
    #运行日志会保存到项目根目录下的logs文件夹中
    log_dir=Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "voice_chat.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )
    logging.info("语音对话程序启动")

    print("————————————欢迎使用 GLaDOS ————————————")
    api_key = getpass("GLaDOS:主人你好呀~OvO~\n请输入您的 DeepSeek API Key:").strip()

    if not api_key:
        print("GLaDOS:主人~ API Key 不能为空哦~请重新输入")
        return

    chat=AIChat(api_key)
    #没有传入模型时加载模型;传入后复用现有模型
    try:
        model = load_model()
        logging.info("语音识别模型加载成功")
    except Exception as e:
        logging.exception("语音识别模型加载失败")
        print(f"GLaDOS:模型加载失败:{e}")
        return

    print("GLaDOS:来啦~按回车开始录音,输入 exit 退出")

    while True:
        command = input("准备好后按回车：").strip()

        if command == "exit":
            logging.info("用户请求退出")
            print("GLaDOS:=v=主人再见!")
            break

        try:
            #录音&识别本轮讲话内容
            audio_path = record_audio()
            user_text = transcribe_audio(audio_path, model)

            if not user_text:
                print("GLaDOS:本次没有识别到讲话内容TOT,请主人重新录音...")
                continue

            print(f"GLaDOS:~识别内容为:{user_text}")

            #将本轮问题和历史对话 一起发送给AI模型,获取回答.
            print("GLaDOS:正在思考...请稍等~")
            reply = chat.chat(user_text)

        except Exception as error:
            logging.exception("本轮语音对话处理失败")
            print(f"GLaDOS:本轮处理失败:{error}")
            continue

        #请求成功将会保存本轮对话:

        print(f"GLaDOS:{reply}")

        #播放本轮 AI 回答(后面声音可以换)
        try:
            speak(reply)
        except Exception as error:
            logging.exception("语音播放失败")
            print(f"GLaDOS:o-O?!语音播放失败:{error}")


if __name__ == "__main__":
    main()