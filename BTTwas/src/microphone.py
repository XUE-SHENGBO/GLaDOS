from email.mime import audio
import wave
from datetime import datetime
from pathlib import Path
import sounddevice as sd

def record_audio():
    duration = 5  # seconds
    channels = 1  # mono

    #初代使用默认麦克风的采样率，有修改后面完善
    device = sd.query_devices(kind='input')
    samplerate = int(device['default_samplerate'])

    with sd.RawInputStream(
        samplerate=samplerate,
        channels=channels,
        dtype="int16" ,
        ) as stream:
        print(f'GLaDOS:OvO~开始录音,请说话{duration}秒后自动结束...')
        audio,overflowed = stream.read(int(duration * samplerate))

    if overflowed:
        raise RuntimeError("GLaDOS:录音时有声音丢失,请主人重新录制:")

    #保存到项目目录下的 recordings 文件夹
    recordings_dir = Path(__file__).resolve().parent.parent / "recordings"
    recordings_dir.mkdir(exist_ok=True)

    filename = datetime.now().strftime('recording_%Y%m%d_%H%M%S.wav')
    recording_path = recordings_dir / filename

    with wave.open(str(recording_path), 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(samplerate)
        wf.writeframes(bytes(audio))
    return recording_path

def main():
    print("————————————欢迎使用 GLaDOS ————————————")
    input("GLaDOS:主人您好!按回车键开始录音......")

    try:
        recording_path = record_audio()
        print(f"GLaDOS:录音已保存到: {recording_path}")
    except Exception as e:
        print(f"GLaDOS:录音失败: {e}") 
        return
    
    print(f'GLaDOS:录音已完成~OvO!\n如有需要,请主人检查录音文件: {recording_path}')

if __name__ == "__main__":
    main()