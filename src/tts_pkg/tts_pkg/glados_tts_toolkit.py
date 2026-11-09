from pathlib import Path
from math import gcd

import numpy as np
import sherpa_onnx
from piper.phonemize_espeak import ESPEAK_DATA_DIR, EspeakPhonemizer
from scipy.io.wavfile import write
from scipy.signal import resample_poly#重采样
import sounddevice as sd

MODEL_DIR = Path(__file__).resolve().parents[3] / "models" / "vits-piper-en_US-glados"
OUTPUT_DEVICE = "HECATE G1200"

MODEL_PATH = MODEL_DIR / "en_US-glados.onnx"
TOKENS_PATH = MODEL_DIR / "tokens.txt"


def play_audio(samples, sample_rate):
    samples = np.asarray(samples, dtype=np.float32)
    playback_rate = int(sample_rate)
    device = sd.query_devices(OUTPUT_DEVICE, "output")
    try:
        sd.check_output_settings(
            device=OUTPUT_DEVICE, samplerate=playback_rate, channels=1, dtype="int16"
        )
    except sd.PortAudioError as exc:
        if len(exc.args) < 2 or exc.args[1] != -9997:
            raise
        playback_rate = int(device["default_samplerate"])
        sd.check_output_settings(
            device=OUTPUT_DEVICE, samplerate=playback_rate, channels=1, dtype="int16"
        )
        divisor = gcd(playback_rate, int(sample_rate))
        samples = resample_poly(
            samples, playback_rate // divisor, int(sample_rate) // divisor
        )

    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    sd.play(pcm, playback_rate, device=OUTPUT_DEVICE, blocking=True)

class GLaDOS_TTS:
    def __init__(self,node):
        if not (MODEL_PATH.is_file() and TOKENS_PATH.is_file()):
            raise SystemExit(f"解压 vits-piper-en_US-glados 模型到 {MODEL_DIR}")     
        self.config = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=str(MODEL_PATH),
                    tokens=str(TOKENS_PATH),
                ),
                provider="cpu",
                num_threads=2,
            ),
        )
        self.node = node
        if not self.config.validate():
            raise SystemExit("sherpa-onnx 模型配置无效")

    def tts(self,text):
        tts = sherpa_onnx.OfflineTts(self.config)
        phonemes = EspeakPhonemizer(ESPEAK_DATA_DIR).phonemize(tts.lang or "en-us", text)
        generation = sherpa_onnx.GenerationConfig()
        generation.phoneme_codepoints = [
            [ord(phoneme) for phoneme in sentence] for sentence in phonemes
        ]
        audio = tts.generate("", generation)
        if len(audio.samples) == 0:
            raise SystemExit("未生成音频")
        self.node.get_logger().info(f'播放:{text}')
        play_audio(audio.samples, audio.sample_rate)

