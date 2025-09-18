from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    use_fake_hardware_arg = DeclareLaunchArgument(
        'use_fake_hardware',
        default_value='true',
        description='Use fake hardware'
    )

    moveit_config = MoveItConfigsBuilder("so_100_arm", package_name="so_100_arm").to_moveit_configs()
    # Add the use_fake_hardware parameter
    moveit_config.robot_description = {
        "use_fake_hardware": LaunchConfiguration('use_fake_hardware')
    }

    return LaunchDescription([
        use_fake_hardware_arg,
        generate_demo_launch(moveit_config)
    ])
