import rclpy
from rclpy.node import Node
from ai_interfaces.action import GenerateText
from prompt_toolkit import PromptSession
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from rclpy.callback_groups import ReentrantCallbackGroup
from threading import Thread
from concurrent.futures import Future
class AIClient:
    def __init__(self,node):
        self.node = node
        self.action_group = ReentrantCallbackGroup()
        self.client = ActionClient(node,GenerateText,'gen_msg',callback_group=self.action_group)
        self.goal_handle = None
        self.result_future = None
        self.cancel_future = None

        self.user_input = None
        self.conversation_id = 0
        self.is_receiving = False

    def send_goal(self,prompt,conversation_id, on_delta,result_future,instructions):#处理发送
        if not self.client.server_is_ready():
            self.node.get_logger().warning('Server has not been ready, please try agian later.')
            result_future.set_exception(RuntimeError('Server has not been ready, please try again later.'))
            return
        
        goal = GenerateText.Goal()
        goal.prompt = prompt
        goal.instructions = instructions
        if conversation_id is not None:
            goal.conversation_id = conversation_id
        else:
            goal.conversation_id = ''

        self.send_future = self.client.send_goal_async(
            goal,
            feedback_callback=on_delta,
        )
        self.send_future.add_done_callback(
            lambda future: self.goal_response_callback(future, result_future)
        )

    def goal_response_callback(self,future,result_future):#处理服务端是否接受goal
        try:
            handle = future.result()

            if not handle.accepted:
                self.node.get_logger().warning('goal is rejected by action server!')
                result_future.set_exception(RuntimeError('goal is rejected by action server!'))
                return

            self.goal_handle = handle
            self.cancel_future = None
            self.is_receiving = True
            self.result_future = handle.get_result_async()
            self.result_future.add_done_callback(
                lambda future: self.result_callback(future, result_future)
            )
        except Exception as exc:
            self.node.get_logger().error(f'failed to send goal:{exc}')
            result_future.set_exception(exc)
            self.is_receiving = False
            return        

    def result_callback(self,future,result_future):#返回result后返回全部内容和成功失败消息
        self.is_receiving = False
        if result_future.done():
            return
        try:
            response = future.result()
        except Exception as exc:
            self.node.get_logger().error(f'error when getting result:{exc}')
            self.is_receiving = False
            result_future.set_exception(exc)
            return

        result = response.result
        status = response.status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.node.get_logger().debug(f'mission success:{result}')
            result_future.set_result(result)
        elif status == GoalStatus.STATUS_ABORTED:
            self.node.get_logger().error(f'server aborted:{result}')
            result_future.set_exception(RuntimeError(f'server aborted:{result}'))
        elif status == GoalStatus.STATUS_CANCELED:
            self.node.get_logger().info(f'mission canceled:{result}')
            result_future.set_exception(RuntimeError(f'mission canceled:{result}'))
        else:
            self.node.get_logger().warning(f'unkown status:{result}')
            result_future.set_exception(RuntimeError(f'unknown status {status}:{result}'))
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
            self.node.get_logger().error(f'cancel failed:{exc}')
            return
        if response.goals_canceling:
            self.node.get_logger().info('server allows canceling')
            self.node.is_receiving = False
        else:
            self.node.get_logger().warning('cancel rejected!')


    def generate(self,prompt,conversation_id=None,on_delta=None,instructions = ''):
        result_future = Future()
        try:
            self.send_goal(prompt,conversation_id,on_delta,result_future,instructions)
        except Exception as exc:
            if not result_future.done():
                result_future.set_exception(exc)
        return result_future

    def cancel(self):
        return self.request_cancel()


