from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "so_100_arm", package_name="so_100_arm"
    ).to_moveit_configs()

    controller_mgr = moveit_config.trajectory_execution.get(
        "moveit_simple_controller_manager", {}
    )
    controller_names = controller_mgr.get("controller_names", [])

    # Find which controllers are set as default
    default_controllers = set()
    for name in controller_names:
        ctrl_config = controller_mgr.get(name, {})
        if ctrl_config.get("default", False):
            default_controllers.add(name)

    # Controllers sharing the same joints as a default controller
    # must be spawned inactive to avoid interface conflicts
    default_joints = set()
    for name in default_controllers:
        ctrl_config = controller_mgr.get(name, {})
        for joint in ctrl_config.get("joints", []):
            default_joints.add(joint)

    inactive_controllers = set()
    for name in controller_names:
        if name in default_controllers:
            continue
        ctrl_config = controller_mgr.get(name, {})
        joints = ctrl_config.get("joints", [])
        if any(j in default_joints for j in joints):
            inactive_controllers.add(name)

    ld = LaunchDescription()
    for controller in controller_names + ["joint_state_broadcaster"]:
        args = [controller]
        if controller in inactive_controllers:
            args.append("--inactive")
        ld.add_action(
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=args,
                output="screen",
            )
        )
    return ld
