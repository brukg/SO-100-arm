from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from controller_manager_msgs.srv import SwitchController
import os

def get_robot_description(context, *args, **kwargs):
    dof = LaunchConfiguration('dof').perform(context)
    pkg_share = FindPackageShare('so_100_arm').find('so_100_arm')
    urdf_path = os.path.join(pkg_share, 'urdf', f'so_100_arm_{dof}dof.urdf')
    controller_path = os.path.join(pkg_share, 'config', f'controllers_{dof}dof.yaml')
    
    with open(urdf_path, 'r') as file:
        urdf_content = file.read()
        # Convert package:// to model:// for Gazebo
        replace_str = f'package://so_100_arm/models/so_100_arm_{dof}dof/meshes'
        with_str = f'model://so_100_arm_{dof}dof/meshes'
        gazebo_urdf_content = urdf_content.replace(replace_str, with_str)
        return {
            'robot_description': ParameterValue(urdf_content, value_type=str),
            'gazebo_description': ParameterValue(gazebo_urdf_content, value_type=str),
            'controller_path': controller_path
        }

def generate_launch_description():
    # Declare the DOF argument
    dof_arg = DeclareLaunchArgument(
        'dof',
        default_value='5',
        description='DOF configuration - either 5 or 7'
    )

    pkg_share = FindPackageShare('so_100_arm').find('so_100_arm')
    model_path = os.path.join(os.path.dirname(os.path.dirname(pkg_share)), 'models')

    # Set the package path for Gazebo
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        os.environ['GZ_SIM_RESOURCE_PATH'] += f":{model_path}"
    else:
        os.environ['GZ_SIM_RESOURCE_PATH'] = model_path

    def launch_setup(context, *args, **kwargs):
        descriptions = get_robot_description(context)
        
        spawn_robot = Node(
            package='ros_gz_sim',
            executable='create',
            name='spawn_model',
            arguments=[
                '-string', descriptions['gazebo_description'].value,
                '-name', 'so_100_arm',
                '-allow_renaming', 'true',
                '-x', '0',
                '-y', '0',
                '-z', '0'
            ],
            output='screen'
        )

        # Define the controller spawner nodes
        joint_state_broadcaster_spawner = ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                'joint_state_broadcaster'],
            output='screen'
        )

        joint_trajectory_controller_spawner = ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                'joint_trajectory_controller'],
            output='screen'
        )

        # Add gripper controller spawner
        gripper_controller_spawner = ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                'gripper_controller'],
            output='screen'
        )

        nodes = [
            # Start robot_state_publisher
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot_state_publisher',
                output='screen',
                parameters=[{'robot_description': descriptions['robot_description']}]
            ),
            
            # Launch Gazebo
            ExecuteProcess(
                cmd=['gz', 'sim', '-r', 'empty.sdf'],
                output='screen',
                additional_env={'GZ_SIM_RESOURCE_PATH': os.environ['GZ_SIM_RESOURCE_PATH']}
            ),

            # Bridge
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                name='bridge',
                parameters=[{
                    'qos_overrides./tf_static.publisher.durability': 'transient_local',
                }],
                arguments=[
                    '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
                    '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
                    '/tf_static@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
                ],
            ),

            # Spawn robot
            spawn_robot,

            # Spawn joint_state_broadcaster after robot spawns
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=spawn_robot,
                    on_exit=[joint_state_broadcaster_spawner]
                )
            ),

            # Spawn joint_trajectory_controller after joint_state_broadcaster
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster_spawner,
                    on_exit=[joint_trajectory_controller_spawner]
                )
            ),

            # Add gripper controller after joint_trajectory_controller
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_trajectory_controller_spawner,
                    on_exit=[gripper_controller_spawner]
                )
            )
        ]
        return nodes

    return LaunchDescription([
        dof_arg,
        OpaqueFunction(function=launch_setup)
    ])