#!/usr/bin/env python3
"""Relay output from a joint_state_topic_interface controller to individual commands

Parameters
- prefix (str): a string prefixed to link and joint names.

Subscriptions
- sensor_msgs.msg.JointState on /robot_joint_commands

Publications
- std_msgs.msg.Float64 on /{prefix}{joint_name}/cmd_pos
"""

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

JOINT_TOPICS = {
    "Shoulder_Rotation": "shoulder_rotation/cmd_pos",
    "Shoulder_Pitch": "shoulder_pitch/cmd_pos",
    "Elbow": "elbow/cmd_pos",
    "Wrist_Pitch": "wrist_pitch/cmd_pos",
    "Wrist_Roll": "wrist_roll/cmd_pos",
    "Gripper": "gripper/cmd_pos",
}


class SOARM1005DofCommandRelay(Node):
    def __init__(self):
        super().__init__("so_arm_100_5dof_joint_relay")
        self.get_logger().info("Starting node {}".format(self.get_name()))

        # Declare and retrieve params
        self.declare_parameter("prefix", "")
        prefix = self.get_parameter("prefix").get_parameter_value().string_value
        self.get_logger().info("prefix: {}".format(prefix))

        # Create publishers and subscriptions
        self.pubs = {}
        for joint_name, topic in JOINT_TOPICS.items():
            prefixed_joint_name = f"{prefix}{joint_name}"
            prefixed_topic = f"{prefix}{topic}"
            self.pubs[prefixed_joint_name] = self.create_publisher(
                Float64, prefixed_topic, 10
            )
        self.create_subscription(
            JointState, "robot_joint_commands", self.on_joint_command, 10
        )

    def on_joint_command(self, msg):
        for i, name in enumerate(msg.name):
            if name in self.pubs:
                cmd = Float64()
                if msg.position and not math.isnan(msg.position[i]):
                    # position command
                    cmd.data = msg.position[i]
                elif msg.velocity and not math.isnan(msg.velocity[i]):
                    # velocity command
                    cmd.data = msg.velocity[i]
                self.pubs[name].publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = SOARM1005DofCommandRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
