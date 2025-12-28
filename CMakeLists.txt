cmake_minimum_required(VERSION 3.10)
project(ImgProc VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")

file(GLOB SOURCES "src/common/*.cpp")
file(GLOB ENTRYPOINTS "src/*.cpp")

foreach(MAIN_FILE ${ENTRYPOINTS})
    get_filename_component(EXEC_NAME ${MAIN_FILE} NAME_WE)
    add_executable(${EXEC_NAME} ${MAIN_FILE} ${SOURCES})
endforeach()
