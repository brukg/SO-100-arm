# SO-100 Robot Arm ROS2 Package

This package provides ROS2 support for the SO-100 robot arm, available in 5-DOF configuration. It is based on the open-source 3D printable [SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) project by The Robot Studio. This implementation includes URDF models, Gazebo simulation support, and MoveIt2 integration.

The original ROS1 implementation can be found at: https://github.com/TheRobotStudio/SO-ARM100

## Features

- Robot arm URDF models
  - 5-DOF configuration with gripper
- Gazebo Harmonic simulation support
- ROS2 Control integration
  - Joint trajectory controller
  - Gripper action controller
- MoveIt2 motion planning capabilities (In Progress)
  - Basic configuration generated
  - Integration with Gazebo pending
  - Motion planning testing pending

## Prerequisites

### ROS2 and Dependencies

- ROS2 Humble
- Gazebo Garden
- MoveIt2
- ros2_control
- gz_ros2_control

### Hardware Requirements

For using the physical robot:

- SO-ARM-100 robot arm (5-DOF)
- Feetech SMS/STS series servos
- USB-to-Serial converter (CH340 chip)
- so_arm_100_hardware package installed:

  ```bash
  cd ~/ros2_ws/src
  git clone git@github.com:brukg/so_arm_100_hardware.git
  cd ~/ros2_ws
  colcon build --packages-select so_arm_100_hardware
  source install/setup.bash
  ```

## Installation

### Create a ROS2 workspace (if you don't have one)

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

### Clone the repository

```bash
git clone git@github.com:brukg/SO-100-arm.git
```

### Install dependencies

```bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
```

### Build the package

```bash
colcon build --packages-select so_100_arm
source install/setup.bash
```

## Usage

### Launch the Hardware Interface

```bash
## Launch the hardware interface
ros2 launch so_100_arm hardware.launch.py
```

### Test Servo Communication

To verify servo connections and read their status:

```bash
# Build the test program
cd ~/ros2_ws
colcon build --packages-select so_arm_100_hardware
source install/setup.bash

# Set USB permissions
sudo chmod 666 /dev/ttyUSB0

# Run the servo test
ros2 run so_arm_100_hardware test_servo
```

This will:

- Test communication with each servo (ID 1-6)
- Read current position, voltage, temperature
- Verify position control mode
- Show any communication errors

Example output for working servos:

```

Testing servo 1...
  Servo 1 responded to ping
  Set to position control mode
  Position: 1963
  Voltage: 7.4V
  Temperature: 29°C
  Load: -24
```

### Test Hardware Interface

Send a test trajectory to move the physical arm:

```bash
ros2 action send_goal /so_100_arm_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{
  trajectory: {
    joint_names: [Shoulder_Rotation, Shoulder_Pitch, Elbow, Wrist_Pitch, Wrist_Roll],
    points: [
      {
        positions: [-0.5, -1.0, 0.5, 0.0, 0.0],
        velocities: [0.0, 0.0, 0.0, 0.0, 0.0],
        time_from_start: {sec: 2, nanosec: 0}
      },
      {
        positions: [-0.5, 0.50, 0.0, 0.0, 0.0],
        velocities: [0.0, 0.0, 0.0, 0.0, 0.0],
        time_from_start: {sec: 4, nanosec: 0}
      }
    ]
  }
}"
```

This will move the arm through two positions:

- First point (2 sec): Shoulder down with elbow bent
- Second point (4 sec): Shoulder up with arm extended

Note: Ensure the arm has clear space to move before sending commands.

### Launch the robot in Gazebo

```bash
ros2 launch so_100_arm gz.launch.py dof:5
```

### Launch the robot in RVIZ

```bash
ros2 launch so_100_arm rviz.launch.py
```

### Launch MoveIt2 Demo

```bash
ros2 launch so_100_arm demo.launch.py
```

### Test Joint Movement


#### Send a test position command for 5dof arm

```bash
ros2 topic pub /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory '{joint_names: ["Shoulder_Rotation", "Shoulder_Pitch", "Elbow", "Wrist_Roll", "Wrist_Pitch"], points: [{positions: [1.0, 1.0, 1.0, 1.0, 1.0], velocities: [], accelerations: [], effort: [], time_from_start: {sec: 1, nanosec: 0}}]}'
```

### Test Gripper Control

The gripper can be controlled using ROS2 actions:

```bash
# Open gripper (full open position)
ros2 action send_goal /gripper_controller/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 1.57, max_effort: 50.0}}"

# Close gripper
ros2 action send_goal /gripper_controller/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 0.0, max_effort: 50.0}}"

# Half-open position
ros2 action send_goal /gripper_controller/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 0.5, max_effort: 50.0}}"
```

Monitor gripper state:

```bash
ros2 topic echo /gripper_controller/state
```

Note: The gripper position ranges from 0.0 (closed) to 0.085 (fully open). The max_effort parameter controls the gripping force.

## Demonstrations

### Gazebo Simulation

[![SO-100 Robot Arm Simulation](https://img.youtube.com/vi/ATuS6rOhYvI/0.jpg)](https://youtu.be/ATuS6rOhYvI?si=T6bOiCdqgBmSoSCu)

The video above shows the SO-100 robot arm in Gazebo Harmonic simulation:

- Joint trajectory execution
- Position control
- Dynamic simulation with gravity

## Package Structure

```bash
so_100_arm/
├── CMakeLists.txt                      # Build system configuration
├── config/  
│   ├── controllers_5dof.yaml           # 5DOF joint controller configuration
│   ├── initial_positions.yaml          # Default joint positions
│   ├── joint_limits.yaml               # Joint velocity and position limits
│   ├── kinematics.yaml                 # MoveIt kinematics configuration
│   ├── moveit_controllers.yaml         # MoveIt controller settings
│   ├── moveit.rviz                     # RViz configuration for MoveIt
│   ├── pilz_cartesian_limits.yaml      # Cartesian planning limits
│   ├── ros2_controllers.yaml           # ROS2 controller settings
│   ├── sensors_3d.yaml                 # Sensor configuration
│   ├── so_100_arm.ros2_control.xacro   # ROS2 Control macro
│   ├── so_100_arm.srdf                 # Semantic robot description
│   ├── so_100_arm.urdf.xacro          # Main robot description macro
│   └── urdf.rviz                       # RViz configuration for URDF
├── launch/  
│   ├── demo.launch.py                  # MoveIt demo with RViz
│   ├── gz.launch.py                    # Gazebo simulation launch
│   ├── move_group.launch.py            # MoveIt move_group launch
│   ├── moveit_rviz.launch.py           # RViz with MoveIt plugin
│   ├── rsp.launch.py                   # Robot state publisher
│   ├── rviz.launch.py                  # Basic RViz visualization
│   ├── setup_assistant.launch.py       # MoveIt Setup Assistant
│   ├── spawn_controllers.launch.py      # Controller spawning
│   ├── static_virtual_joint_tfs.launch.py
│   └── warehouse_db.launch.py          # MoveIt warehouse database
├── LICENSE
├── models/
│   ├── so_100_arm_5dof/               # 5DOF robot assets
│   │   ├── meshes/                    # STL files for visualization
│   │   └── model.config               # Model metadata
├── package.xml                         # Package metadata and dependencies
├── README.md                           # This documentation
└── urdf/
    ├── so_100_arm_5dof.csv            # Joint configuration data
    ├── so_100_arm_5dof.urdf           # 5DOF robot description

```

## Joint Configuration

### 5-DOF Configuration

1. Shoulder Rotation (-3.14 to 3.14 rad)
2. Shoulder Pitch    (-3.14 to 3.14 rad)
3. Elbow            (-3.14 to 3.14 rad)
4. Wrist Pitch      (-3.14 to 3.14 rad)
5. Wrist Roll       (-3.14 to 3.14 rad)

Note: The 5-DOF configuration uses continuous rotation joints with full range of motion (±π radians).

## Known Issues

- The MoveIt2 configuration is still in development
- Some joint limits may need fine-tuning
- Collision checking needs optimization

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License - see the LICENSE file for details

## Authors

Bruk G.

## Acknowledgments

- Based on the SO-ARM100 project by The Robot Studio
