from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()
    ai_backend_node = Node(
        package='ai_pkg',
        executable='ai_backend',
        output='screen',
    )
    ld.add_action(ai_backend_node)

    TUI_node = Node(
        package='ai_pkg',
        executable='TUI',
        prefix=(
            'gnome-terminal --wait '
            '--title="GLaDOS 对话" '
            '--geometry=100x30 '
            '--zoom=1.3 --'
        ),
        ros_arguments=['--disable-stdout-logs'],
        output='screen',
    )
    ld.add_action(TUI_node)
    return ld