import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from dotenv import load_dotenv#加载环境变量
import os
import asyncio
from pathlib import Path

from openai import OpenAI
import openai

from rclpy.logging import LoggingSeverity, set_logger_level
from rclpy.action import ActionServer,GoalResponse,CancelResponse
from ai_interfaces.action import GenerateText


class AIReplyNode(Node):
    def __init__(self):
        super().__init__('ai_reply_node')

        env_path = Path(__file__).resolve().parents[3]/".env"
        load_dotenv(env_path)
        logger_level = os.getenv("LOGGER_LEVEL")     

        ai_url = os.getenv('AI_URL')#read environment variable
        api_key = os.getenv("API_KEY")
        self.instructions = os.getenv("INSTRUCTIONS")
        self.model_name = os.getenv("MODEL_NAME")

        set_logger_level(self.get_logger().name, LoggingSeverity[logger_level])

        self.stream = None
        self.processing = False
        self.response_id = None
        self.conversation_id = None
        self.model = OpenAI(
            base_url=ai_url,
            api_key=api_key,
        )
        self.action_group = ReentrantCallbackGroup()
        self.ai_action_server = ActionServer(# action: allow stream reply and both server and client can cancel the execution
            self,
            GenerateText,
            'gen_msg',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.action_group
        )

        self.get_logger().info('ai reply service startup!')

    def goal_callback(self,request):
        if self.processing == True:
            return GoalResponse.REJECT

        prompt = request.prompt
        try:
            self.stream = self.model.responses.create(
                model=self.model_name,
                instructions=self.instructions,
                input=prompt,
                stream=True,
                background=True
            )

        except openai.APIConnectionError as e:
            self.get_logger().error("The server could not be reached")
            self.get_logger().error(str(e.__cause__))
            self.processing = False
            return GoalResponse.REJECT
        except openai.RateLimitError as e:
            self.get_logger().error("A 429 status code was received; we should back off a bit.")
            self.processing = False
            return GoalResponse.REJECT
        except openai.APIStatusError as e:
            self.get_logger().error("Another non-200-range status code was received")
            self.get_logger().error(str(e.status_code))
            self.get_logger().error(str(e.response))
            self.processing = False
            return GoalResponse.REJECT

        self.processing = True
        self.conversation_id = request.conversation_id
        return GoalResponse.ACCEPT
    
    def execute_callback(self,goal_handle):
        
        sequence = 0
        full_text = ''#保存这一轮生成的全文
        try:
            with self.stream:
                for event in self.stream:

                    if event.type == 'response.created':#开始流输出后先获取对话id
                        self.response_id = event.response.id
                        self.get_logger().info(f'AI API response ID{self.response_id}')
                    if goal_handle.is_cancel_requested:#检查客户端是否取消了action
                        result = GenerateText.Result()
                        result.text = full_text
                        result.error_message = 'generation aborted by client!'
                        goal_handle.canceled()
                        self.model.responses.cancel(self.response_id)
                        self.processing = False
                        return result
                    
                    if event.type in ('response.failed','response.incomplete'):#处理失败情况
                        self.get_logger().error(f"ai_gen_msg request error!{event.type}")
                        result = GenerateText.Result()
                        result.error_code = event.type
                        result.error_message = "ai_gen_msg request error!"
                        goal_handle.abort()
                        self.processing = False
                        return result
                    
                    if event.type == "response.output_text.delta":#正常接收,发布delta
                        feedback = GenerateText.Feedback()
                        feedback.delta = event.delta
                        full_text+=event.delta
                        feedback.sequence=sequence
                        goal_handle.publish_feedback(feedback)
                        sequence+=1

                    if event.type == "response.completed":#接受完毕,返回result
                        result = GenerateText.Result()
                        result.text = full_text
                        goal_handle.succeed()
                        self.processing = False
                        return result
                    
                if goal_handle.is_active:
                    goal_handle.abort()
                result = GenerateText.Result()
                result.text = full_text
                result.error_code = "stream_ended"
                result.error_message = "Stream ended without a terminal event"
                return result
            
        except Exception as exc:
            self.get_logger().error(str(exc))
            if goal_handle.is_active:
                goal_handle.abort()
            result = GenerateText.Result()
            result.text = full_text
            result.error_code = type(exc).__name__
            result.error_message = str(exc)
            return result
        finally:
            self.processing = False
            self.stream = None
            self.response_id = None
    def cancel_callback(self,goal_handle):
        if self.processing == False:
            result = GenerateText.Result()
            result.error_message = 'No request processing!cancel reject'
            return CancelResponse.REJECT
        return CancelResponse.ACCEPT

    
def main(args=None):
    rclpy.init(args=args)
    node = AIReplyNode()
    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)

    try:
        executor.spin()
    except SystemExit:
        print('Shutting down')
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
if __name__ == '__main__':
    main()
