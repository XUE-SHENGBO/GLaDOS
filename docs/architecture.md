# 目录和结构：
```
src/ai_pkg/ #管理AI上下文，流输出
src/audio_pkg/#音频的输入u输出
src/bringup_pkg/#整合和调度，主逻辑
src/camera_pkg/#管理摄像头
src/motor_pkg/#管理电机
src/sim_pkg/#运行模拟器

tests/#自动化测试

docs/#项目文档
```

# ai_pkg
## ai_client
这个脚本写了一个ai_client类,包装了ai_action的错误处理,回应请求结果,取消等
新建实例:`client = AIClient(node)`需要传递引用它的节点self,来以这个节点为名发送日志
### generate
`client.generate(self,prompt,conversation_id=None,on_delta=None)`
返回一个result_future对象,其中是`src/ai_interfaces/action/GenerateText.action`里面这个result对象

prompt:此轮对话输入
conversation_id:对话id,留空会让result返回一个新的16进制conversation_id,填旧的conversation_id切换到那个对话
on_delta:流式回调,接受一个回调函数,会收到一个feedback_msg,里面有feedback_msg.feedback.delta,是每段小回答的内容
例:
```python
    def feedback_callback(self,feedback_msg):#打印feedback,接受feedback_msg,定义:src/ai_interfaces/action/GenerateText.action
        print(feedback_msg.feedback.delta,end='',flush=True)
```
### cancel
`client.cancel()`
请求取消此轮发送
