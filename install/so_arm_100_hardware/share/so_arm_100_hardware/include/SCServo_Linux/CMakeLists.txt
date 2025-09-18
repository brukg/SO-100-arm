cmake_minimum_required(VERSION 3.10)
project(SCServo)

# Add -fPIC flag for position independent code
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Get all source files in current directory
file(GLOB SOURCES 
    "*.cpp"
)

add_library(SCServo STATIC ${SOURCES})

target_include_directories(SCServo PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)