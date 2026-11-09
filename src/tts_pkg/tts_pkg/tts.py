import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import SetBool

from .glados_tts_toolkit import GLaDOS_TTS

class TTSNode(Node):
    def __init__(self):
        super().__init__('TTSNode')
        self.sub = self.create_subscription(String,'tts/text',self.tts_callback,10)
        # Service responses run in a separate group while playback waits for them.
        self.mute_group = MutuallyExclusiveCallbackGroup()
        self.mute_client = self.create_client(
            SetBool, 'stt/set_muted', callback_group=self.mute_group
        )
        self.tts = GLaDOS_TTS(self)
        self.get_logger().info('TTSNode startup!')

    def tts_callback(self, message):
        text = message.data.strip()
        if not text:
            return
        has_stt = self.mute_client.service_is_ready()
        try:
            if has_stt:
                self.set_stt_muted(True)
            self.tts.tts(text)
        except Exception as exc:
            self.get_logger().error(f'TTS failed: {exc}')
        finally:
            if has_stt and rclpy.ok():
                try:
                    self.set_stt_muted(False)
                except Exception as exc:
                    self.get_logger().error(f'Could not resume STT: {exc}')

    def set_stt_muted(self, muted):
        response = self.mute_client.call(SetBool.Request(data=muted), timeout_sec=2.0)
        if response is None or not response.success:
            raise RuntimeError(f'STT did not acknowledge muted={muted}')


def main(args=None):
    rclpy.init(args=args)
    node = None
    executor = MultiThreadedExecutor(num_threads=2)
    try:
        node = TTSNode()
        executor.add_node(node)
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()
if __name__ == '__main__':
    main()
