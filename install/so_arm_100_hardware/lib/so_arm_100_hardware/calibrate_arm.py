#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
import yaml
import os
from datetime import datetime
import asyncio
from threading import Thread
from ament_index_python.packages import get_package_share_directory
class CalibrationTool(Node):
    def __init__(self):
        super().__init__('calibration_tool')
        self.calib_client = self.create_client(Trigger, 'record_position')
        self.torque_client = self.create_client(Trigger, 'toggle_torque')
        
        # Wait for services to be available
        while not self.torque_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for toggle_torque service...')
        while not self.calib_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for record_position service...')
            
        self.joints = [
            'Shoulder_Rotation',
            'Shoulder_Pitch', 
            'Elbow',
            'Wrist_Pitch',
            'Wrist_Roll',
            'Gripper'
        ]
        self.config_dir = os.path.join(
            get_package_share_directory('so_arm_100_hardware'),
            'config',
        )
        
    async def disable_torque(self):
        print("\nDisabling torque to allow manual movement...")
        try:
            # Wait for service to be available
            if not self.torque_client.wait_for_service(timeout_sec=1.0):
                print("Torque service not available!")
                return False
            
            future = self.torque_client.call_async(Trigger.Request())
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(future, timeout=2.0)
                self.get_logger().info(f'Service response: {response.message}')
                if response.success:
                    print("Torque disabled - you can now move the joints")
                    await asyncio.sleep(1.0)  # Give time for servos to fully disable
                    return True
                else:
                    print(f"Failed to disable torque: {response.message}")
                    return False
            except asyncio.TimeoutError:
                print("Service call timed out!")
                return False
            
        except Exception as e:
            self.get_logger().error(f'Service call failed: {str(e)}')
            return False

    async def enable_torque(self):
        print("\nRe-enabling torque...")
        try:
            if not self.torque_client.wait_for_service(timeout_sec=1.0):
                print("Torque service not available!")
                return False
            
            future = self.torque_client.call_async(Trigger.Request())
            response = await asyncio.wait_for(future, timeout=2.0)
            
            if response.success:
                print("Torque enabled")
                await asyncio.sleep(1.0)  # Give time for servos to fully enable
                return True
            else:
                print(f"Failed to enable torque: {response.message}")
                return False
        except Exception as e:
            self.get_logger().error(f'Service call failed: {str(e)}')
            return False

    async def record_joint_limits(self, joint_name, joint_idx):
        limits = {}
        
        print(f"\n=== Calibrating {joint_name} ===")
        print(f"1. Move ONLY the {joint_name} joint")
        
        print("\nMove to minimum position (mechanical stop)")
        input("Press Enter when ready...")
        response = await self.calib_client.call_async(Trigger.Request())
        if response.success:
            try:
                data = yaml.safe_load(response.message)
                if joint_name in data:
                    limits['min'] = data[joint_name]
                else:
                    print(f"Warning: No data for {joint_name} in response: {response.message}")
                    return None
            except Exception as e:
                print(f"Failed to parse response: {e}")
                print(f"Response was: {response.message}")
                return None
            
        print("\nMove to center/neutral position")
        input("Press Enter when ready...")
        response = await self.calib_client.call_async(Trigger.Request())
        if response.success:
            data = yaml.safe_load(response.message)
            if joint_name in data:
                limits['center'] = data[joint_name]
            else:
                print(f"Warning: No data for {joint_name}")
                return None
            
        print("\nMove to maximum position (mechanical stop)")
        input("Press Enter when ready...")
        response = await self.calib_client.call_async(Trigger.Request())
        if response.success:
            data = yaml.safe_load(response.message)
            if joint_name in data:
                limits['max'] = data[joint_name]
            else:
                print(f"Warning: No data for {joint_name}")
                return None
            
        return limits

    async def calibrate_all_joints(self):
        # Disable torque first
        if not await self.disable_torque():
            print("Failed to disable torque!")
            return

        calibration_data = {
            'timestamp': datetime.now().isoformat(),
            'joints': {}
        }
        
        for idx, joint in enumerate(self.joints):
            limits = await self.record_joint_limits(joint, idx)
            if limits:
                # Ensure consistent format
                calibration_data['joints'][joint] = {
                    'min': {
                        'ticks': limits['min']['ticks'],
                        'speed': limits['min']['speed'],
                        'load': limits['min']['load']
                    },
                    'center': {
                        'ticks': limits['center']['ticks'],
                        'speed': limits['center']['speed'],
                        'load': limits['center']['load']
                    },
                    'max': {
                        'ticks': limits['max']['ticks'],
                        'speed': limits['max']['speed'],
                        'load': limits['max']['load']
                    }
                }
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Save calibration data with explicit formatting
        filepath = os.path.join(self.config_dir, "calibration.yaml")
        with open(filepath, 'w') as f:
            yaml.dump(calibration_data, f, default_flow_style=False, sort_keys=False)
        print(f"\nCalibration data saved to: {filepath}")
        
        # Print a summary
        print("\nCalibration Summary:")
        for joint, limits in calibration_data['joints'].items():
            if limits:  # Check if we have data for this joint
                print(f"\n{joint}:")
                print(f"  Min: {limits['min']['ticks']} ticks")
                print(f"  Center: {limits['center']['ticks']} ticks")
                print(f"  Max: {limits['max']['ticks']} ticks")
                print(f"  Range: {limits['max']['ticks'] - limits['min']['ticks']} ticks")
                print(f"  Speed: {limits['min']['speed']}")
                print(f"  Load: {limits['min']['load']}")
            else:
                print(f"\n{joint}: No calibration data")

        # Re-enable torque when done
        await self.enable_torque()

async def main():
    rclpy.init()
    
    # Create and spin the node in a separate thread
    tool = CalibrationTool()
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(tool)
    
    # Spin executor in a separate thread
    executor_thread = Thread(target=executor.spin)
    executor_thread.start()
    
    try:
        await tool.calibrate_all_joints()
    finally:
        # Cleanup
        executor.shutdown()
        rclpy.shutdown()
        executor_thread.join()
    
    print("\nCalibration complete!")

if __name__ == '__main__':
    # Import here to avoid circular imports
    asyncio.run(main()) 