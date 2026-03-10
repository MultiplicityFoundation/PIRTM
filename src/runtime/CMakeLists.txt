cmake_minimum_required(VERSION 3.14)
project(pirtm_runtime 
    VERSION 0.4.0
    DESCRIPTION "PIRTM Phase 4 Standalone Runtime Library"
    LANGUAGES CXX C)

# ============================================================================
# Project Configuration
# ============================================================================

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Platform detection
if(UNIX AND NOT APPLE)
    set(LINUX TRUE)
endif()

if(APPLE)
    set(MACOS TRUE)
endif()

# ============================================================================
# Compiler Flags
# ============================================================================

# Release optimizations
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG" CACHE STRING "Release flags")

# Debug symbols
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0" CACHE STRING "Debug flags")

# Position-independent code for shared library
if(NOT WIN32)
    add_compile_options(-fPIC)
endif()

# Warnings
add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
    -Wno-unused-parameter
)

# ============================================================================
# Runtime Library Target
# ============================================================================

add_library(pirtm_runtime SHARED
    ${CMAKE_CURRENT_SOURCE_DIR}/libpirtm_runtime.cpp
)

# Set library output name
set_target_properties(pirtm_runtime PROPERTIES
    OUTPUT_NAME "pirtm_runtime"
    SOVERSION 0
    VERSION 0.4.0
)

# Include directories (for internal use)
target_include_directories(pirtm_runtime
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)

# ============================================================================
# Installation Configuration
# ============================================================================

# Install shared library
install(TARGETS pirtm_runtime
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
)

# Create header file for C API (for external users)
set(API_HEADER "${CMAKE_CURRENT_BINARY_DIR}/pirtm_runtime.h")
file(WRITE "${API_HEADER}"
"#ifndef PIRTM_RUNTIME_H
#define PIRTM_RUNTIME_H

#include <stdint.h>

#ifdef __cplusplus
extern \"C\" {
#endif

/* Opaque state handle */
typedef void* pirtm_state_t;

/* State creation/destruction */
pirtm_state_t pirtm_state_new(
    int32_t state_dim,
    double epsilon,
    const double* gain_matrix_data,
    int32_t gain_matrix_size
);
void pirtm_state_free(pirtm_state_t state);

/* State access */
int pirtm_get_state(pirtm_state_t state, double* output_vec, int32_t output_size);
int pirtm_set_state(pirtm_state_t state, const double* input_vec, int32_t input_size);

/* Execution */
double pirtm_step(pirtm_state_t state);
int pirtm_run(pirtm_state_t state, int32_t num_steps);

/* Witness validation */
int pirtm_verify_witness(pirtm_state_t state, const char* expected_hash);

/* Metadata access */
int32_t pirtm_get_dimension(pirtm_state_t state);
double pirtm_get_epsilon(pirtm_state_t state);

#ifdef __cplusplus
}
#endif

#endif // PIRTM_RUNTIME_H
")

install(FILES "${API_HEADER}" DESTINATION include)

# ============================================================================
# Build Options
# ============================================================================

option(BUILD_TESTS "Build runtime library tests" ON)
option(BUILD_SHARED_LIBS "Build shared library (default)" ON)

# ============================================================================
# Testing (if enabled)
# ============================================================================

if(BUILD_TESTS)
    enable_testing()
    
    # Add test executable (if test file exists)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/test_runtime.cpp")
        add_executable(test_pirtm_runtime
            ${CMAKE_CURRENT_SOURCE_DIR}/test_runtime.cpp
        )
        target_link_libraries(test_pirtm_runtime pirtm_runtime)
        add_test(NAME pirtm_runtime COMMAND test_pirtm_runtime)
    endif()
endif()

# ============================================================================
# Package Configuration
# ============================================================================

# Generate pkg-config file
set(PKGCONFIG_FILE "${CMAKE_CURRENT_BINARY_DIR}/pirtm_runtime.pc")
file(WRITE "${PKGCONFIG_FILE}"
"prefix=${CMAKE_INSTALL_PREFIX}
libdir=\${prefix}/lib
includedir=\${prefix}/include

Name: libpirtm_runtime
Description: PIRTM Phase 4 Standalone Runtime Library
Version: ${PROJECT_VERSION}
Libs: -L\${libdir} -lpirtm_runtime
Cflags: -I\${includedir}
")

install(FILES "${PKGCONFIG_FILE}" DESTINATION lib/pkgconfig)

# ============================================================================
# Summary
# ============================================================================

message(STATUS "")
message(STATUS "PIRTM Runtime Library Configuration:")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Position Independent Code: ON")
message(STATUS "  Build Tests: ${BUILD_TESTS}")
message(STATUS "")
message(STATUS "Targets:")
message(STATUS "  pirtm_runtime (shared library)")
message(STATUS "")
message(STATUS "Installation:")
message(STATUS "  Libraries: ${CMAKE_INSTALL_PREFIX}/lib")
message(STATUS "  Headers: ${CMAKE_INSTALL_PREFIX}/include")
message(STATUS "  pkg-config: ${CMAKE_INSTALL_PREFIX}/lib/pkgconfig")
message(STATUS "")
