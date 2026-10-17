import rclpy
from rclpy.node import Node
class gen_msg_srv_node(Node):
    def __init__(self):
        super().__init__("gen_msg_srv")
        self.create_service()
def main(args = None):
    rclpy.init()
    node = gen_msg_srv_node()
    try:
        rclpy.spin(node)
    except SystemExit:
        print('shutting down')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()