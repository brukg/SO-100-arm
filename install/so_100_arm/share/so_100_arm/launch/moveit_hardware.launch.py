from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Launch hardware (ros2_control + controllers) and MoveIt (move_group + RViz).

    This includes `hardware.launch.py` from this package to start the controller manager
    and spawners, then starts the MoveIt demo (move_group + rviz) using the package's
    MoveIt configuration. RViz launched by the hardware launch is disabled to avoid
    duplicates.
    """

    use_fake_hardware_arg = DeclareLaunchArgument(
        'use_fake_hardware',
        default_value='false',
        description='Use fake hardware (true for simulation, false for real hardware)'
    )

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Start RViz (MoveIt RViz)'
    )

    # Build MoveIt config and pass the use_fake_hardware flag into robot_description
    moveit_config = MoveItConfigsBuilder("so_100_arm", package_name="so_100_arm").to_moveit_configs()
    moveit_config.robot_description = {
        "use_fake_hardware": LaunchConfiguration('use_fake_hardware')
    }

    # Include hardware launch (starts ros2_control, controller_manager and spawners)
    hardware_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare('so_100_arm'), 'launch', 'hardware.launch.py'])
        ]),
        launch_arguments={
            # hardware.launch has its own rviz arg; disable it because MoveIt will start RViz
            'rviz': 'false',
            'zero_pose': 'false'
        }.items()
    )

    # Generate MoveIt demo launch (move_group + MoveIt RViz etc.)
    demo_launch = generate_demo_launch(moveit_config)

    # Combine into a single LaunchDescription
    ld = LaunchDescription([
        use_fake_hardware_arg,
        rviz_arg,
        hardware_launch,
    ])

    # Append entities from the demo launch so everything runs together
    ld.add_action(demo_launch)

    return ld
