"""Stream microphone audio through Zipformer and publish recognized text."""

import os
from pathlib import Path
from threading import Event, Lock, Thread
from time import monotonic

from dotenv import load_dotenv
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import sherpa_onnx
import sounddevice as sd
from std_msgs.msg import String
from std_srvs.srv import SetBool


MODEL_NAME = 'sherpa-onnx-streaming-zipformer-small-bilingual-zh-en-2023-02-16'
MODEL_FILES = {
    'cpu': (
        'encoder-epoch-99-avg-1.int8.onnx',
        'decoder-epoch-99-avg-1.onnx',
        'joiner-epoch-99-avg-1.int8.onnx',
    ),
    'rknn': ('encoder.rknn', 'decoder.rknn', 'joiner.rknn'),
}


class STTNode(Node):
    def __init__(self):
        super().__init__('stt')
        env_path = Path(__file__).resolve().parents[3]/".env"
        load_dotenv(env_path)  # 加载当前工作目录下的 .env，供后面读取麦克风配置
        provider = 'cpu'                             #cpu or rknn

        model_dir = Path(self.declare_parameter(
            'model_dir', str(Path(__file__).resolve().parents[3] / 'models' / MODEL_NAME)
        ).value).expanduser()  # 取出 ROS 参数里的模型目录，并把路径开头的 ~ 展开为家目录

        silence = self.declare_parameter('trailing_silence', 0.7).value  # 读取句尾静音时长，单位为秒，默认 0.7 秒

        device = self.declare_parameter(
            'input_device', os.getenv('DEFAULT_DEVICE') or ''
        ).value

        device = int(device) if device.isdecimal() else device or None  # 纯数字转为设备编号，设备名保留为字符串，空值使用系统默认输入

        if provider not in MODEL_FILES:
            raise ValueError('provider must be cpu or rknn')
        if silence <= 0:
            raise ValueError('trailing_silence must be positive')

        encoder, decoder, joiner = (model_dir / name for name in MODEL_FILES[provider])#取出编解码器和融合模块路径
        tokens = model_dir / 'tokens.txt'#取出token列表
        for path in (encoder, decoder, joiner, tokens):
            if not path.is_file():
                raise FileNotFoundError(f'Model file missing: {path}. Set the model_dir parameter.')

        self.recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(  # 加载 Zipformer 模型并创建流式识别器
            encoder=str(encoder),
            decoder=str(decoder),
            joiner=str(joiner),
            tokens=str(tokens),
            provider=provider,
            sample_rate=16000,
            feature_dim=80,
            num_threads=2,
            enable_endpoint_detection=True,#启用断句识别(VAE)
            rule2_min_trailing_silence=silence,
        )
        self.device = device
        self.sample_rate = int(sd.query_devices(device, 'input')['default_samplerate'])
        self.partial = self.create_publisher(String, '/stt/partial', 100)  # 发布当前句子的识别预览
        self.final = self.create_publisher(String, '/stt/final', 100)  # 检测到句尾后，发布本句的最终识别结果
        self.capture_lock = Lock()
        self.capture_epoch = 0
        self.muted_until = 0.0
        self.mute_service = self.create_service(SetBool, 'stt/set_muted', self.set_muted)
        self.stop_event = Event()  # 创建停止信号，主线程退出时用它通知采音线程
        self.capture_error = None
        self.capture_failed = self.create_guard_condition(self.raise_capture_error)  # 采音线程触发此条件时，由 ROS 执行器调用错误处理函数
        self.worker = Thread(target=self.capture, name='stt-microphone')  # 创建采音和解码线程，让 ROS 执行器继续处理回调
        self.worker.start()

    def set_muted(self, request, response):
        with self.capture_lock:
            self.capture_epoch += 1
            self.muted_until = float('inf') if request.data else monotonic() + 0.1
        response.success = True
        return response

    def capture(self):
        try:
            self.decode_microphone()
        except Exception as exc:
            if not self.stop_event.is_set() and rclpy.ok():
                self.capture_error = exc
                self.capture_failed.trigger()

    def raise_capture_error(self):
        raise RuntimeError(f'Microphone recognition failed: {self.capture_error}')

    def decode_microphone(self):
        stream = self.recognizer.create_stream()  # 创建识别流，在连续的音频块之间保留解码状态
        last_partial = ''
        stream_epoch = 0
        with sd.InputStream(
            device=self.device, samplerate=self.sample_rate, channels=1, dtype='float32'
        ) as mic:
            self.get_logger().info(f'Listening at {self.sample_rate} Hz')
            while not self.stop_event.is_set():
                with self.capture_lock:
                    read_epoch = self.capture_epoch
                    read_muted = monotonic() < self.muted_until
                samples, overflowed = mic.read(int(self.sample_rate * 0.04))  # 每次读取约 40 毫秒音频，同时检查采音缓冲区是否溢出
                if self.stop_event.is_set() or not rclpy.ok():
                    break
                with self.capture_lock:
                    if overflowed or stream_epoch != self.capture_epoch:
                        if overflowed and not read_muted:
                            self.get_logger().warning('Microphone overflow; restarting utterance')
                        stream = self.recognizer.create_stream()
                        stream_epoch = self.capture_epoch
                        if last_partial:
                            self.partial.publish(String(data=''))
                            last_partial = ''

                    # Drain the input even while muted and discard blocks crossing a mute change.
                    if read_muted or read_epoch != stream_epoch:
                        continue

                    stream.accept_waveform(self.sample_rate, samples[:, 0])
                    while self.recognizer.is_ready(stream):
                        self.recognizer.decode_stream(stream)

                    text = self.recognizer.get_result(stream).strip()
                    if self.recognizer.is_endpoint(stream):
                        if text:
                            self.final.publish(String(data=text))
                        self.recognizer.reset(stream)
                        if last_partial:
                            self.partial.publish(String(data=''))
                        last_partial = ''
                    elif text != last_partial:
                        self.partial.publish(String(data=text))
                        last_partial = text

    def stop(self):
        self.stop_event.set()
        self.worker.join()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = STTNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.stop()
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
