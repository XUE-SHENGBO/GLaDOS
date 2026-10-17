cmake_minimum_required(VERSION 3.8)
project(ai_interfaces)

find_package(ament_cmake REQUIRED)#找到 ROS 2 的构建工具
find_package(rosidl_default_generators REQUIRED)#找到接口代码生成工具

rosidl_generate_interfaces(${PROJECT_NAME}#把列出的接口文件生成 Python/C++ 代码
  "action/GenerateText.action"
  "srv/GenerateText.srv"
)

ament_export_dependencies(rosidl_default_runtime)#声明使用这个包时需要接口运行支持
ament_package()
