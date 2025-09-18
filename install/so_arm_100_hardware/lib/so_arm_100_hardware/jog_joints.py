#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger
import curses
import sys
import math
import yaml
import os
from datetime import datetime
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from ament_index_python.packages import get_package_share_directory

class JogTool(Node):
    def __init__(self):
        super().__init__('jog_tool')
        
        # Split joints into arm and gripper
        self.arm_joints = [
            'Shoulder_Rotation',
            'Shoulder_Pitch',
            'Elbow',
            'Wrist_Pitch',
            'Wrist_Roll'
        ]
        self.gripper_joint = 'Gripper'
        
        # For tracking current positions
        self.joint_positions = {}
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10)
            
        # Separate clients for arm and gripper
        self.arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/so_100_arm_controller/follow_joint_trajectory'
        )
        
        # For gripper control
        self.gripper_pub = self.create_publisher(
            JointTrajectory,
            '/so_100_arm_gripper_controller/commands',
            10)
        
        # For toggling torque
        self.torque_client = self.create_client(Trigger, '/toggle_torque')
        while not self.torque_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for toggle_torque service...')
        
        self.selected_joint = 0
        self.step_size = 0.1  # radians
        self.status_message = ""
        self.torque_enabled = True
        self.torque_future = None  # Track the service call future
        
        # Set up poses directory in package share
        self.poses_dir = os.path.join(
            get_package_share_directory('so_arm_100_hardware'),
            'config',
            'poses'
        )
        os.makedirs(self.poses_dir, exist_ok=True)
        
    def joint_state_callback(self, msg):
        for i, name in enumerate(msg.name):
            if name in self.arm_joints or name == self.gripper_joint:
                self.joint_positions[name] = msg.position[i]
                
    def move_joint(self, delta):
        # Get the correct joint name and index
        if self.selected_joint < len(self.arm_joints):
            joint_name = self.arm_joints[self.selected_joint]
            joint_index = self.selected_joint
            # self.get_logger().info(f'Moving arm joint: {joint_name} at index {joint_index}')
        else:
            joint_name = self.gripper_joint
            # self.get_logger().info(f'Moving gripper joint: {joint_name}')
        
        current_pos = self.joint_positions.get(joint_name, 0.0)
        new_pos = current_pos + delta
        
        if joint_name in self.arm_joints:
            # Send arm trajectory
            goal_msg = FollowJointTrajectory.Goal()
            goal_msg.trajectory.joint_names = self.arm_joints
            
            point = JointTrajectoryPoint()
            # Initialize with current positions
            point.positions = [self.joint_positions.get(j, 0.0) for j in self.arm_joints]
            # Only modify the selected joint
            point.positions[joint_index] = new_pos

            point.velocities = [0.0] * len(self.arm_joints)
            point.accelerations = [0.0] * len(self.arm_joints)
            point.time_from_start.sec = 0
            point.time_from_start.nanosec = 100_000_000
            
            goal_msg.trajectory.points = [point]
            self.arm_client.send_goal_async(goal_msg)
        else:
            # Send gripper command
            msg = JointTrajectory()
            msg.joint_names = [self.gripper_joint]
            
            point = JointTrajectoryPoint()
            point.positions = [new_pos]
            point.time_from_start.sec = 0
            point.time_from_start.nanosec = 100_000_000
            
            msg.points = [point]
            self.gripper_pub.publish(msg)
            
        # self.get_logger().info(f'Moving {joint_name} from {current_pos:.3f} to {new_pos:.3f}')
        
    def save_pose(self, pose_name):
        pose_data = {
            'name': pose_name,
            'timestamp': datetime.now().isoformat(),
            'positions': self.joint_positions.copy()
        }
        
        filepath = os.path.join(self.poses_dir, f'{pose_name}.yaml')
        with open(filepath, 'w') as f:
            yaml.dump(pose_data, f, default_flow_style=False)
            
        self.status_message = f"Saved pose to {filepath}"
        
    def load_pose(self, pose_name):
        filepath = os.path.join(self.poses_dir, f'{pose_name}.yaml')
        
        try:
            with open(filepath, 'r') as f:
                pose_data = yaml.safe_load(f)

            # Send arm trajectory
            arm_goal = FollowJointTrajectory.Goal()
            arm_goal.trajectory.joint_names = self.arm_joints  # Only arm joints
            
            point = JointTrajectoryPoint()
            # Get positions only for arm joints
            point.positions = [pose_data['positions'][joint] for joint in self.arm_joints]
            point.velocities = [0.0] * len(self.arm_joints)
            point.accelerations = [0.0] * len(self.arm_joints)
            point.time_from_start.sec = 2
            
            arm_goal.trajectory.points = [point]
            self.arm_client.send_goal_async(arm_goal)

            # Send gripper command separately
            gripper_msg = JointTrajectory()
            gripper_msg.joint_names = [self.gripper_joint]
            
            gripper_point = JointTrajectoryPoint()
            gripper_point.positions = [pose_data['positions'][self.gripper_joint]]
            gripper_point.time_from_start.sec = 2
            
            gripper_msg.points = [gripper_point]
            self.gripper_pub.publish(gripper_msg)
            
            self.status_message = f"Loaded pose '{pose_name}'"
            
        except Exception as e:
            self.status_message = f"Failed to load pose: {str(e)}"
        
    def toggle_torque(self):
        request = Trigger.Request()
        self.torque_future = self.torque_client.call_async(request)
        
        # Add callback to handle response
        self.torque_future.add_done_callback(self._torque_callback)
        
    def _torque_callback(self, future):
        try:
            response = future.result()
            if response.success:
                self.torque_enabled = not self.torque_enabled
                state = "enabled" if self.torque_enabled else "disabled"
                self.status_message = f"Torque {state}"
            else:
                self.status_message = f"Failed to toggle torque: {response.message}"
        except Exception as e:
            self.status_message = f"Error toggling torque: {str(e)}"
        finally:
            self.torque_future = None

def main(stdscr):
    # Set up curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    
    rclpy.init()
    node = JogTool()
    
    # Print instructions
    stdscr.addstr(0, 0, "Joint Jog Control")
    stdscr.addstr(1, 0, "----------------")
    stdscr.addstr(2, 0, "Up/Down: Select joint")
    stdscr.addstr(3, 0, "Left/Right: Move joint")
    stdscr.addstr(4, 0, "+/-: Adjust step size")
    stdscr.addstr(5, 0, "t: Toggle torque (arm/disarm)")
    stdscr.addstr(6, 0, "s: Save current position")
    stdscr.addstr(7, 0, "l: Load saved position")
    stdscr.addstr(8, 0, "q: Quit")
    
    pose_name = ""
    entering_name = False
    
    while True:
        # Update display
        for i, joint in enumerate(node.arm_joints + [node.gripper_joint]):
            prefix = ">" if i == node.selected_joint else " "
            pos = node.joint_positions.get(joint, 0.0)
            stdscr.addstr(i+10, 0, f"{prefix} {joint:<15} {pos:6.3f}")
        
        stdscr.addstr(17, 0, f"Step size: {node.step_size:5.3f} rad")
        stdscr.addstr(18, 0, f"Torque: {'ON' if node.torque_enabled else 'OFF'}")
        stdscr.addstr(19, 0, f"Status: {node.status_message}")
        
        if entering_name:
            stdscr.addstr(19, 0, f"Enter pose name: {pose_name}_")
        else:
            stdscr.addstr(19, 0, " " * 50)  # Clear line
            
        stdscr.refresh()
        
        # Process input
        try:
            key = stdscr.getch()
            if entering_name:
                if key == ord('\n'):  # Enter key
                    if pose_name:
                        if node.status_message.startswith("Save"):
                            node.save_pose(pose_name)
                        else:
                            node.load_pose(pose_name)
                    entering_name = False
                    pose_name = ""
                elif key == 27:  # Escape key
                    entering_name = False
                    pose_name = ""
                elif key == curses.KEY_BACKSPACE or key == 127:  # Backspace
                    pose_name = pose_name[:-1]
                elif key >= 32 and key <= 126:  # Printable characters
                    pose_name += chr(key)
            else:
                if key == ord('q'):
                    break
                elif key == curses.KEY_UP:
                    node.selected_joint = (node.selected_joint - 1) % len(node.arm_joints + [node.gripper_joint])
                elif key == curses.KEY_DOWN:
                    node.selected_joint = (node.selected_joint + 1) % len(node.arm_joints + [node.gripper_joint])
                elif key == curses.KEY_LEFT:
                    node.move_joint(-node.step_size)
                elif key == curses.KEY_RIGHT:
                    node.move_joint(node.step_size)
                elif key == ord('+') or key == ord('='):
                    node.step_size = min(node.step_size * 1.5, 1.0)
                elif key == ord('-'):
                    node.step_size = max(node.step_size / 1.5, 0.01)
                elif key == ord('t'):
                    # Toggle torque without waiting
                    node.toggle_torque()
                    rclpy.spin_once(node)  # Process any pending callbacks
                elif key == ord('s'):
                    entering_name = True
                    node.status_message = "Save pose"
                elif key == ord('l'):
                    entering_name = True
                    node.status_message = "Load pose"
                
        except KeyboardInterrupt:
            break
            
        # Process any pending callbacks including torque response
        rclpy.spin_once(node, timeout_sec=0.1)
    
    rclpy.shutdown()

if __name__ == '__main__':
    curses.wrapper(main) 