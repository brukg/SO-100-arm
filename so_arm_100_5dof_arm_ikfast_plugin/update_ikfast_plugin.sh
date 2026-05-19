search_mode=OPTIMIZE_MAX_JOINT
srdf_filename=so_arm_100_5dof.srdf
robot_name_in_srdf=so_arm_100_5dof
moveit_config_pkg=so_arm_100_5dof_moveit_config
robot_name=so_arm_100_5dof
planning_group_name=arm
ikfast_plugin_pkg=so_arm_100_5dof_arm_ikfast_plugin
base_link_name=base_link
eef_link_name=End_Effector
ikfast_output_path=src/so_arm_100/so_arm_100_5dof_arm_ikfast_plugin/src/so_arm_100_5dof_arm_ikfast_solver.cpp

rosrun moveit_kinematics create_ikfast_moveit_plugin.py\
  --search_mode=$search_mode\
  --srdf_filename=$srdf_filename\
  --robot_name_in_srdf=$robot_name_in_srdf\
  --moveit_config_pkg=$moveit_config_pkg\
  $robot_name\
  $planning_group_name\
  $ikfast_plugin_pkg\
  $base_link_name\
  $eef_link_name\
  $ikfast_output_path
