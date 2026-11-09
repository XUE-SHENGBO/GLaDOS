"""Submit finalized speech to the existing AI action server."""

from ai_pkg.ai_client import AIClient
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from pathlib import Path
import os
from dotenv import load_dotenv

punctuation_list = ('!',',','?','.'
                    ,'。','，','？','！')
class VoiceChat(Node):
    def __init__(self):
        super().__init__('voice_chat')
        self.ai = AIClient(self)
        self.conversation_id = None
        self.pending = None
        self.create_subscription(String, '/stt/final', self.on_final,100)
        self.create_subscription(String,'/stt/partial',self.on_partial,100)
        self.last_word = ''

        env_path = Path(__file__).resolve().parents[3]/".env"
        load_dotenv(env_path)
        self.instructions = os.getenv("INSTRUCTIONS")
        self.partial_output = ''

        self.tts = self.create_publisher(String,'tts/text',10)
        
        self.get_logger().info('VoiceChat node startup! Speak to chat')

    def on_final(self, message):#用户说完后发送请求到AI backend
        print(flush=True)
        prompt = message.data.strip()
        if not prompt:
            return
        if self.pending is not None:
            self.get_logger().warning('AI is busy; ignoring this utterance')
            return

        self.get_logger().info(f'User: {prompt}')
        self.pending = self.ai.generate(
            prompt, conversation_id=self.conversation_id, on_delta=self.on_delta,
            instructions = self.instructions
        )
        self.pending.add_done_callback(self.on_result)

    def on_partial(self,message):#用户语音输入流式上屏
        delta = message.data[len(self.last_word):]
        print(delta,end='',flush=True)
        self.last_word = message.data

    def on_delta(self, message):#AI backend 输出流式发送到tts,在标点处断句
        print(message.feedback.delta, end='', flush=True)
        if any(punctuation in message.feedback.delta for punctuation in punctuation_list):
            tts_msg = String()
            tts_msg.data = self.partial_output
            self.tts.publish(tts_msg)
            self.partial_output = ''
        else:
            self.partial_output= self.partial_output + message.feedback.delta
        
    def on_result(self, future):#AI backend返回完毕后获取conversation_id
        print(flush=True)
        try:
            self.conversation_id = future.result().conversation_id
        except Exception as exc:
            self.get_logger().error(f'AI request failed: {exc}')
        finally:
            self.pending = None


def main(args=None):
    rclpy.init(args=args)
    node = VoiceChat()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
