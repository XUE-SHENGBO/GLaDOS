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

class TUINode(Node):
    def __init__(self):
        super().__init__('TUI_node')

        self.action_group = ReentrantCallbackGroup()
        self.client = ActionClient(self,GenerateText,'gen_msg',callback_group=self.action_group)
        self.goal_handle = None
        self.result_future = None
        self.cancel_future = None

        self.user_input = None
        self.history = {0: []}
        self.conversation_id = 0
        self.is_receiving = False
        self.get_logger().info(f'ai_tui_node startup!')
        

    
    async def receive_input(self):#接受输入和发起goal
        session = PromptSession()
        print()
        self.user_input = await session.prompt_async('user:')

        self.analysis_input()

    def analysis_input(self):
        user_input = self.user_input.strip()
        parts = user_input.split()     

        if user_input =='/exit':
            self.request_cancel()
            raise SystemExit(0)
        
        elif user_input == '/new':
            self.conversation_id+=1

            if self.conversation_id not in self.history:
                self.history[self.conversation_id] = []
            self.history[self.conversation_id].append(self.user_input)
            self.get_logger().info('new conversation started!')
            print('new conversation started!')
            return

        elif parts[0] == '/shift':
            number = int(parts[1])
            if number not in self.history:
                self.get_logger().error(f'the conversation you asked does not exist:{number}')
                print(f'the conversation you asked does not exist:{number}')
                return
            self.conversation_id = number
            self.get_logger().info(f'Shift to conversation id={number}')
            print(f'Shift to conversation id={number}')
            return
        elif not user_input:
            return
        else:
            self.history[self.conversation_id].append(self.user_input)
            self.send_goal()


    def send_goal(self):#处理发送
        if not self.client.server_is_ready():
            self.get_logger().warning('Server has not been ready, please try agian later.')
            return
        
        goal = GenerateText.Goal()
        goal.prompt = '\n'.join(self.history[self.conversation_id])
        goal.conversation_id = str(self.conversation_id)

        self.send_future = self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback,
        )
        self.send_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self,future):#处理服务端是否接受goal
        try:
            handle = future.result()
        except Exception as exc:
            self.get_logger().error(f'failed to send goal:{exc}')
            return

        if not handle.accepted:
            self.get_logger().warning('goal is rejected by action server!')
            return

        self.goal_handle = handle
        self.is_receiving = True
        self.result_future = handle.get_result_async()
        self.result_future.add_done_callback(self.result_callback)

    def feedback_callback(self,feedback_msg):#打印feedback
        feedback = feedback_msg.feedback
        print(feedback.delta,end='',flush=True)

    def result_callback(self,future):#返回result后返回全部内容和成功失败消息
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f'error when getting result:{exc}')
            self.is_receiving = False
            return
        result = response.result
        status = response.status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().debug(f'mission success:{result}')
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error(f'server aborted:{result}')

        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info(f'mission canceled:{result}')
        else:
            self.get_logger().warning(f'unkown status:{result}')
        self.is_receiving = False

    def request_cancel(self):#请求取消任务
        if self.goal_handle is None:
            return
        if self.result_future is not None and self.result_future.done():
            return
        if self.cancel_future is not None:
            return

        self.cancel_future = self.goal_handle.cancel_goal_async()
        self.cancel_future.add_done_callback(self.cancel_response_callback)

    def cancel_response_callback(self,future):#获取请求取消任务的返回
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f'cancel failed:{exc}')
            return
        if response.goal_canceling:
            self.get_logger().info('server allows canceling')
            self.is_receiving = False
        else:
            self.get_logger().warning('cancel rejected!')



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