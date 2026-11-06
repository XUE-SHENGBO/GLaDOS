# 使用说明

## AI TUI
进入项目目录,编译项目
```bash
colcon build --symlink-install
```

启动
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch ai_pkg TUI.launch.py
```

## 树莓派 ST7789V2 屏幕

以下步骤适用于树莓派 4B、ROS 2 Jazzy 和中景园 ZJY169S0800TG01（240×280，4 线 SPI）。

### 接线

给树莓派断电后接线。表里的物理针脚号是 40 针排针上的位置，GPIO 编号对应代码中的 `board.Dxx`。

| 屏幕引脚 | 树莓派物理针脚 | 对应信号 |
| --- | --- | --- |
| `VCC` | 1 或 17 | 3.3 V |
| `GND` | 20 | GND |
| `SCL` / `SCK` | 23 | SPI0 SCLK（GPIO11） |
| `SDA` / `DIN` | 19 | SPI0 MOSI（GPIO10） |
| `CS` | 16 | GPIO23（`board.D23`） |
| `DC` | 22 | GPIO25（`board.D25`） |
| **`RES` / `RST`** | **15** | **GPIO22（`board.D22`）** |

这块屏幕只需写入数据，MISO（物理第 21 针）可以空着。屏幕驱动通过 GPIO23 控制片选，SPI0 的 CE0（物理第 24 针）留给系统。如果模块有独立的背光脚，按该模块的引脚说明接线。

### 安装依赖

在树莓派的项目根目录执行。已有 `.venv` 时，跳过创建命令，并确认 `.venv/pyvenv.cfg` 中的 `include-system-site-packages = true`，让虚拟环境可以读取系统安装的 ROS 2 和 colcon 依赖。

```bash
cd ~/Project/GLaDOS
/usr/bin/python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install adafruit-blinka adafruit-circuitpython-rgb-display Pillow python-dotenv
```

确认 SPI0 已启用，且当前用户能读写 `/dev/spidev0.0`。用 `ls -l /dev/spidev0.0` 查看设备所属组。实测的树莓派上，该设备属于 `dialout`。如果当前用户还不在这个组里，执行 `sudo usermod -aG dialout "$USER"`，然后退出 SSH 并重新登录。

### 构建和启动

在树莓派的项目根目录用 `.venv` 的 Python 调用系统的 colcon，使生成的节点入口默认使用 `.venv`。

```bash
source /opt/ros/jazzy/setup.bash
.venv/bin/python /usr/bin/colcon build --symlink-install \
  --base-paths src/screen_driver_pkg --packages-select screen_driver_pkg
source install/setup.bash
ros2 run screen_driver_pkg screen_test
```

启动后，屏幕会依次显示红、绿、蓝，再显示带白框和文字的测试画面。以后在新终端里加载 Jazzy 和工作区的 `setup.bash`，即可直接运行同一条 `ros2 run` 命令。
