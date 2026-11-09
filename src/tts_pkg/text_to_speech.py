import pyttsx3


def speak(text):
    """将文字转换为语音,通过当前音频输出设备播放."""
    if not text.strip():
        return

    #初始化当前系统的语音引擎
    engine = pyttsx3.init()

    try:
        #查找已安装的中文声音
        '''
        for voice in engine.getProperty("voices"):
            voice_info = (
                f"{voice.id} {voice.name} {voice.languages}"
            ).lower()
            print(voice_info)

            if any(
                tag in voice_info
                for tag in ("zh", "cmn", "mandarin", "chinese")
            ):
                print(f'chose this:{voice_info}')
                engine.setProperty("voice", voice.id)
                break
        else:
            raise RuntimeError("GLaDOS:Sorry~TOT~未找到中文声音,请主人先安装中文语音包~")
        '''
        engine.setProperty("voice", "gmw/en")#sit/yue  sit/cmn-latn-pinyin gmw/en
        #设置语速和音量
        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)

        #将文字加入朗读列表后,等待播放,再结束
        engine.say(text)

        engine.runAndWait()
        
    finally:
        engine.stop()


def main():
    #text = "您好主人,我是GLaDOS!现在开始语音播放测试."
    text = 'hi, I am GLaDOS! This is a speak test now.'
    print(f"GLaDOS:准备朗读:\n{text}")

    try:
        speak(text)
    except Exception as error:
        print(f"GLaDOS:o-O?!语音播放失败:{error}")
        return

    print("GLaDOS:朗读结束!OvO~")


if __name__ == "__main__":
    main()