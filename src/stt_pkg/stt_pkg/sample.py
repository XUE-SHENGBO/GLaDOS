import argparse
from gc import is_finalized
from pathlib import Path
from pyexpat import model
import re
from faster_whisper import WhisperModel

def load_model():
    #模型缓存->项目的根目录下的 models 文件夹
    models_dir = Path(__file__).resolve().parents[3] / "models"

    print("GLaDOS:正在加载模型,请稍等......")

    model = WhisperModel(
        'base', 
        device="cpu", 
        compute_type="int8", 
        download_root=str(models_dir),
    )

    print("GLaDOS:模型加载完成~OvO!")
    return model

def transcribe_audio(audio_path,model=None):
    #没有传入模型时加载模型;传入后复用现有模型
    if model is None:
        model = load_model()

    print("GLaDOS:开始识别音频......")
    
    segments, info = model.transcribe(
        str(audio_path),
        language="zh",
        vad_filter=True,
    )
    #拼接识别出来的各段文字
    return " ".join([segment.text for segment in segments]).strip()

def main():
    parser = argparse.ArgumentParser(description="把语音识别成文字")
    parser.add_argument("audio_path", type=Path, help="录音文件路径")
    args = parser.parse_args()

    audio_path = args.audio_path

    if not audio_path.is_file():
        print(f"GLaDOS:音频文件不存在: {audio_path}")
        return

    try:
        transcription = transcribe_audio(audio_path)
        print(f"GLaDOS:识别结果:\n{transcription}")
    except Exception as e:
        print(f"GLaDOS:音频识别失败: {e}")


if __name__ == "__main__":
    main()