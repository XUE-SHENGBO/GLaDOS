from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ld = LaunchDescription()

    # 1. Package installation directories
    ai_pkg = FindPackageShare('ai_pkg')
    tts_pkg = FindPackageShare('tts_pkg')
    stt_pkg = FindPackageShare('stt_pkg')

    # 2. Launch arguments

    # 3. Other launch files

    # 4. Nodes
    ai_backend = Node(
        package='ai_pkg',
        executable='ai_backend',
    )
    ld.add_action(ai_backend)
    tts_node = Node(
        package='tts_pkg',
        executable='tts',
    )
    ld.add_action(tts_node)
    stt_node = Node(
        package='stt_pkg',
        executable='stt'
    )
    ld.add_action(stt_node)
    voice_chat_node = Node(
        package='bringup_pkg',
        executable='voice_chat',
        output = 'screen',
        prefix=(
            'gnome-terminal --wait '
            '--title="GLaDOS 对话" '
            '--geometry=100x30 '
            '--zoom=1.3 --'
        ),
        ros_arguments=['--disable-stdout-logs'],
    )
    ld.add_action(voice_chat_node)
    return ld
