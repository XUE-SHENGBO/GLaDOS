from rclpy.node import Node
import rclpy

import time
import board
import digitalio
from PIL import Image,ImageDraw
from adafruit_rgb_display import st7789

import os
from dotenv import load_dotenv
from pathlib import Path


class ST7789V2(st7789.ST7789):
    # Let the controller finish resetting and waking before the next command.
    _COMMAND_DELAY = {0x01: 0.150, 0x11: 0.120}

    def write(self, command=None, data=None):
        super().write(command, data)
        delay = self._COMMAND_DELAY.get(command)
        if delay is not None:
            time.sleep(delay)


class ScreenTest(Node):
    def __init__(self):
        super().__init__('ScreenTestNode')
        env_path = Path(__file__).resolve().parents[3] / ".env"
        load_dotenv(env_path)
        WIDTH = int(os.getenv("WIDTH", "240"))
        HEIGHT = int(os.getenv("HEIGHT", "280"))
        X_OFFSET = int(os.getenv("X_OFFSET", "0"))
        Y_OFFSET = int(os.getenv("Y_OFFSET", "20"))

        spi = board.SPI()
        # SPI0 owns CE0. The display driver controls CS on a separate GPIO.
        cs = digitalio.DigitalInOut(board.D23)
        dc = digitalio.DigitalInOut(board.D25)
        rst = digitalio.DigitalInOut(board.D22)

        display = ST7789V2(
            spi,
            cs=cs,
            dc=dc,
            rst=rst,
            width=WIDTH,
            height=HEIGHT,
            x_offset=X_OFFSET,
            y_offset=Y_OFFSET,
            rotation=0,
            baudrate=int(os.getenv("BAUDRATE","16_000_000")),
        )

        try:
            # 依次显示红、绿、蓝，检查颜色和显示范围
            for color in ("red", "green", "blue"):
                display.image(Image.new("RGB", (WIDTH, HEIGHT), color))#
                time.sleep(1)

            image = Image.new("RGB", (WIDTH, HEIGHT), "black")#新建画布对象,颜色RGB,指定宽高,背景色
            draw = ImageDraw.Draw(image)#draw绑定到这个画布

            draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline="white")#画矩形
            draw.text((20, 30), "Hello, Raspberry Pi 4B!", fill="white")#画字:位置,内容,填充
            draw.text((20, 55), "ST7789V2 display test", fill="yellow")

            display.image(image)#推送到显示屏显示
            print("测试画面已显示。按 Ctrl+C 退出。")

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            pass
        finally:
            cs.deinit()
            dc.deinit()
            rst.deinit()
            spi.deinit()


def main(args=None):
    rclpy.init(args=args)
    node = ScreenTest()

    try:
        rclpy.spin(Node)
    except SystemExit:
        print('Shutting down')
    finally:
        rclpy.shutdown()
        node.destroy_node()
        rclpy.shutdown()
if __name__ == '__main__':
    main()
