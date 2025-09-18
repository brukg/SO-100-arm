#ifndef SOARM100_INTERFACE_H
#define SOARM100_INTERFACE_H

#include <rclcpp/rclcpp.hpp>
#include "rclcpp/macros.hpp"
#include <hardware_interface/system_interface.hpp>

#include <rclcpp_lifecycle/state.hpp>
#include <rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp>

#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"

#include <vector>
#include <string>
#include <memory>
#include <termios.h>
#include <map>

#include <sensor_msgs/msg/joint_state.hpp>
#include <SCServo_Linux/SCServo.h>
#include "std_srvs/srv/trigger.hpp"
#include <yaml-cpp/yaml.h>

namespace so_arm_100_controller
{

using CallbackReturn = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

class SOARM100Interface : public hardware_interface::SystemInterface
{
public:
  SOARM100Interface();
  virtual ~SOARM100Interface();

  // LifecycleNodeInterface
  CallbackReturn on_init(const hardware_interface::HardwareInfo &hardware_info) override;
  CallbackReturn on_activate(const rclcpp_lifecycle::State &previous_state) override;
  CallbackReturn on_deactivate(const rclcpp_lifecycle::State &previous_state) override;

  // SystemInterface
  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;
  hardware_interface::return_type read(const rclcpp::Time & time, const rclcpp::Duration & period) override;
  hardware_interface::return_type write(const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  // Position command and state storage for all joints
  std::vector<double> position_commands_;
  std::vector<double> position_states_;

  // Keep these until we fully transition to calibration
  std::vector<int> zero_positions_{2048, 2048, 2048, 2048, 2048, 2048};  // Center positions
  std::vector<int> servo_directions_{1, 1, 1, 1, 1, 1};  // Direction multipliers

  // Calibration data
  struct JointCalibration {
    int min_ticks;
    int center_ticks;
    int max_ticks;
    double range_ticks;
  };
  std::map<std::string, JointCalibration> joint_calibration_;

  // Communication configuration
  bool use_serial_;
  std::string serial_port_;
  int serial_baudrate_;

  // Serial communication
  int SerialPort;
  struct termios tty;
  int WriteToSerial(const unsigned char* buf, int nBytes);
  int ReadSerial(unsigned char* buf, int nBytes);
  bool ConfigureSerialPort();

  // ROS interfaces
  rclcpp::Node::SharedPtr node_;
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr command_publisher_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr feedback_subscriber_;

  std::shared_ptr<rclcpp::executors::SingleThreadedExecutor> executor_;
  std::thread spin_thread_;

  // Store last received feedback message
  sensor_msgs::msg::JointState::SharedPtr last_feedback_msg_;
  std::mutex feedback_mutex_;

  SMS_STS st3215_;

  void feedback_callback(const sensor_msgs::msg::JointState::SharedPtr msg);

  // Calibration methods
  void calibrate_servo(uint8_t servo_id, int current_pos);
  double ticks_to_radians(int ticks, size_t servo_idx);
  int radians_to_ticks(double radians, size_t servo_idx);

  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr calib_service_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr torque_service_;

  void calibration_callback(
      const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
      std::shared_ptr<std_srvs::srv::Trigger::Response> response);
  
  void torque_callback(
      const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
      std::shared_ptr<std_srvs::srv::Trigger::Response> response);

  void record_current_position();
  void set_torque_enable(bool enable);

  std::string last_calibration_data_;
  bool torque_enabled_{true};

  bool load_calibration(const std::string& filepath);
  double normalize_position(const std::string& joint_name, int ticks);
};

}  // namespace so_arm_100_controller

#endif  // SOARM100_INTERFACE_H
