cmake_minimum_required(VERSION 3.10)
project(USRP_MPM)

# Define options for devices
set(MPM_DEVICE "n3xx" CACHE STRING "Target device (e.g., n3xx, x4xx)")

# Python installation path
set(PYTHON_INSTALL_PATH ${CMAKE_CURRENT_SOURCE_DIR}/mpm/python)

# Configure the periph_manager module
if(MPM_DEVICE STREQUAL "n3xx")
    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/mpm/python/usrp_mpm/periph_manager/n3xx.py
        ${PYTHON_INSTALL_PATH}/usrp_mpm/periph_manager/periph_manager.py
        COPYONLY
    )
elseif(MPM_DEVICE STREQUAL "x4xx")
    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/mpm/python/usrp_mpm/periph_manager/x4xx.py
        ${PYTHON_INSTALL_PATH}/usrp_mpm/periph_manager/periph_manager.py
        COPYONLY
    )
else()
    message(FATAL_ERROR "Unsupported MPM_DEVICE: ${MPM_DEVICE}")
endif()

message(STATUS "Configured periph_manager for device: ${MPM_DEVICE}")
