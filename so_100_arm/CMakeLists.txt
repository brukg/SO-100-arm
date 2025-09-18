cmake_minimum_required(VERSION 3.22)
project(so_100_arm)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY 
    models
    urdf
    launch
    config
  DESTINATION share/${PROJECT_NAME}
  PATTERN "setup_assistant.launch" EXCLUDE)
install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})

ament_package()
