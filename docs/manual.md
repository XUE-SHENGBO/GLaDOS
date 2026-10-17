# AI TUI使用说明
进入项目目录,编译项目
```bash
colcon build --symlink-install
```

启动两个终端窗口
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run ai_pkg ai_backend
```
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run ai_pkg TUI
```