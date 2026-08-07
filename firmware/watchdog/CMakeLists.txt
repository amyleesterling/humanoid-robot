cmake_minimum_required(VERSION 3.13)

if(NOT DEFINED ENV{PICO_SDK_PATH})
    message(FATAL_ERROR "PICO_SDK_PATH must identify the pinned Raspberry Pi Pico SDK checkout")
endif()

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(project_button_watchdog C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(PICO_BOARD pico CACHE STRING "Raspberry Pi Pico 1 / RP2040")

pico_sdk_init()

add_compile_options(
    "-ffile-prefix-map=${CMAKE_SOURCE_DIR}=project-button-watchdog"
    "-fmacro-prefix-map=${CMAKE_SOURCE_DIR}=project-button-watchdog"
    "-ffile-prefix-map=${PICO_SDK_PATH}=pico-sdk"
    "-fmacro-prefix-map=${PICO_SDK_PATH}=pico-sdk"
    "-ffile-prefix-map=${CMAKE_BINARY_DIR}=watchdog-build"
    "-fmacro-prefix-map=${CMAKE_BINARY_DIR}=watchdog-build"
)

add_executable(project_button_watchdog
    platform/pico/main.c
    src/pb_watchdog.c
)

target_include_directories(project_button_watchdog PRIVATE include)
target_link_libraries(project_button_watchdog PRIVATE
    pico_stdlib
    hardware_gpio
    hardware_watchdog
)

set_source_files_properties(
    platform/pico/main.c
    src/pb_watchdog.c
    PROPERTIES COMPILE_OPTIONS
        "-Wall;-Wextra;-Werror;-Wformat=2;-Wshadow;-Wstrict-prototypes;-Wundef;-fstack-usage;-Wstack-usage=256"
)

target_link_options(project_button_watchdog PRIVATE -Wl,--build-id=none)

pico_enable_stdio_usb(project_button_watchdog 0)
pico_enable_stdio_uart(project_button_watchdog 0)
pico_set_program_name(project_button_watchdog "Project Button HR-V0 Watchdog")
pico_set_program_version(project_button_watchdog "P0.2")
pico_set_program_description(project_button_watchdog "PRELIMINARY ordinary diagnostic watchdog; no safety credit")
pico_add_extra_outputs(project_button_watchdog)
