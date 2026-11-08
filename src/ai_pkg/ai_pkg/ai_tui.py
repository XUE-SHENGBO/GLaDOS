import rclpy
from rclpy.node import Node
from ai_interfaces.action import GenerateText
from prompt_toolkit import PromptSession
import asyncio
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from threading import Thread

from concurrent.futures import Future as ThreadFuture
from prompt_toolkit.patch_stdout import patch_stdout
from .ai_client import AIClient
class TUINode(Node):
    def __init__(self):
        super().__init__('TUI_node')
        self.client = AIClient(self)

        self.user_input = None
        self.conversation_id = None
        self.is_receiving = False
        self.get_logger().info(f'ai_tui_node startup!')

    async def receive_input(self):#接受输入和发起goal
        session = PromptSession()
        print()
        self.user_input = await session.prompt_async('user:')

        await self.analysis_input()

    async def analysis_input(self):
        user_input = self.user_input.strip()
        parts = user_input.split()

        if user_input =='/exit':
            self.client.cancel()
            raise SystemExit(0)

        elif user_input == '/new':
            self.conversation_id = None
            self.get_logger().info('new conversation started!')
            print('new conversation started!')
            return

        elif not user_input:
            return
        else:                                           #普通输出
            try:
                future = self.client.generate(
                    self.user_input.strip(),
                    self.conversation_id,
                    on_delta=self.feedback_callback,
                )

                result = await asyncio.wrap_future(future)
                self.conversation_id = result.conversation_id
                print()  # 流式输出结束后换行
            except Exception as exc:
                self.get_logger().error(f'生成失败：{exc}')

    def feedback_callback(self,feedback_msg):#打印feedback
        print(feedback_msg.feedback.delta,end='',flush=True)

async def run_tui(node):
    while rclpy.ok():
        try:
            if node.is_receiving == False:
                await node.receive_input()
            await asyncio.sleep(0.5)
        except EOFError:
            return

def main(args=None):
    rclpy.init()
    node = TUINode()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    spin_thread = Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    try:
        with patch_stdout():
            asyncio.run(run_tui(node))
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        spin_thread.join()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__=='__main__':
    main()