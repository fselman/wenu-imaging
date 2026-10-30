cmake_minimum_required(VERSION 3.29)
project(mefpp_native LANGUAGES C)
include(CTest)
include(CheckTypeSize)
include(CheckIncludeFile)
include(CheckSymbolExists)
include(CheckCSourceCompiles)
include(TestBigEndian)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
  message(FATAL_ERROR "Use an out-of-source build: cmake -S . -B <fresh-directory>")
endif()
set(MEFPP_C_STANDARD "90" CACHE STRING "Explicit C language mode: 90 or 17")
set_property(CACHE MEFPP_C_STANDARD PROPERTY STRINGS 90 17)
if(NOT MEFPP_C_STANDARD MATCHES "^(90|17)$")
  message(FATAL_ERROR "MEFPP_C_STANDARD must be 90 or 17")
endif()
set(CMAKE_C_STANDARD ${MEFPP_C_STANDARD})
set(CMAKE_C_STANDARD_REQUIRED YES)
set(CMAKE_C_EXTENSIONS NO)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
option(MEFPP_BUILD_RESOURCES "Decompress required runtime BPM resources" ON)
set(MEFPP_SOURCE_REVISION "unknown" CACHE STRING "Exact source revision for exported source builds")
if(WIN32)
  message(FATAL_ERROR "Native Windows adapters are not qualified yet; see roadmap stage 7")
endif()
if(NOT CMAKE_SYSTEM_NAME MATCHES "^(Linux|Darwin)$")
  message(FATAL_ERROR "This candidate currently qualifies Linux and Darwin only")
endif()

# Explicit feature checks replace generated configuration from historical hosts.
# glibc 2.17 predates _DEFAULT_SOURCE; retain its equivalent default interfaces
# in explicit ISO language modes without changing the numerical source (#89).
set(MEFPP_FEATURE_DEFINITIONS _DEFAULT_SOURCE=1 _DARWIN_C_SOURCE=1)
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  list(APPEND MEFPP_FEATURE_DEFINITIONS _BSD_SOURCE=1 _SVID_SOURCE=1 _POSIX_C_SOURCE=200809L)
endif()
set(CMAKE_REQUIRED_DEFINITIONS "")
foreach(definition IN LISTS MEFPP_FEATURE_DEFINITIONS)
  list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${definition}")
endforeach()
foreach(type IN ITEMS char short int long float double)
  string(TOUPPER "${type}" upper)
  check_type_size("${type}" SIZEOF_${upper} LANGUAGE C)
endforeach()
foreach(header IN ITEMS unistd.h sys/mman.h sys/resource.h sys/socket.h sys/shm.h sys/time.h)
  string(MAKE_C_IDENTIFIER "${header}" key)
  check_include_file("${header}" HAVE_${key})
  if(NOT HAVE_${key})
    message(FATAL_ERROR "Required legacy header missing: ${header}")
  endif()
endforeach()
check_c_source_compiles("#include <limits.h>\nint main(void) { typedef char require8[(CHAR_BIT == 8) ? 1 : -1]; return sizeof(require8) != 1; }" HAVE_EIGHT_BIT_BYTES)
if(NOT HAVE_EIGHT_BIT_BYTES OR NOT SIZEOF_SHORT EQUAL 2 OR NOT SIZEOF_INT EQUAL 4 OR NOT SIZEOF_FLOAT EQUAL 4 OR NOT SIZEOF_DOUBLE EQUAL 8)
  message(FATAL_ERROR "Unsupported legacy numeric representation")
endif()
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  check_symbol_exists(M_PI "math.h" HAVE_REQUIRED_M_PI)
  check_symbol_exists(shmget "sys/types.h;sys/ipc.h;sys/shm.h" HAVE_REQUIRED_SHMGET)
  if(NOT HAVE_REQUIRED_M_PI OR NOT HAVE_REQUIRED_SHMGET)
    message(FATAL_ERROR "Required legacy math/System V interfaces are unavailable; check feature-test definitions")
  endif()
endif()
foreach(symbol IN ITEMS mmap munmap)
  check_symbol_exists(${symbol} "sys/mman.h" HAVE_${symbol})
  if(NOT HAVE_${symbol})
    message(FATAL_ERROR "Required memory service missing: ${symbol}")
  endif()
endforeach()
set(CMAKE_EXTRA_INCLUDE_FILES sys/types.h)
check_type_size("off_t" SIZEOF_OFF_T LANGUAGE C)
unset(CMAKE_EXTRA_INCLUDE_FILES)
if(NOT SIZEOF_OFF_T OR SIZEOF_OFF_T LESS 8)
  message(FATAL_ERROR "Required 64-bit off_t unavailable")
endif()
test_big_endian(WORDS_BIGENDIAN)
set(OS_LINUX 0)
set(OS_DARWIN 0)
if(APPLE)
  set(OS_DARWIN 1)
else()
  set(OS_LINUX 1)
endif()
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(CONFIG_GUARD MEFPP_PLATFORM_CONFIG_H)
configure_file(cmake/platform_config.h.in generated/mefpp_platform_config.h @ONLY)
set(CONFIG_GUARD QFITS_PLATFORM_CONFIG_H)
configure_file(cmake/platform_config.h.in generated/qfits_platform_config.h @ONLY)

include(cmake/QfitsSources.cmake)
include(cmake/EclipseSources.cmake)
add_library(qfits STATIC ${QFITS_SOURCES})
target_include_directories(qfits PUBLIC qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
# Preserve the legacy default allocator policy and its table size.
target_compile_definitions(qfits PRIVATE XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
add_library(eclipse STATIC ${ECLIPSE_SOURCES})
target_include_directories(eclipse PUBLIC src/include)
target_compile_definitions(eclipse PRIVATE _ECLIPSE_)
target_link_libraries(eclipse PUBLIC qfits)
add_library(mefpp_common STATIC ins/mef/common/mefp_lib.c
  ins/mef/common/mef_bias_kernel.c)
target_include_directories(mefpp_common PUBLIC ins/mef/common)
target_link_libraries(mefpp_common PUBLIC eclipse)
add_executable(mefpp ins/mef/recipes/mefpp.c)
target_link_libraries(mefpp PRIVATE mefpp_common)
foreach(target IN ITEMS qfits eclipse mefpp_common mefpp)
  target_compile_definitions(${target} PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(${target} PRIVATE -Wall -Wextra)
  endif()
endforeach()
check_symbol_exists(sqrt "math.h" HAVE_SQRT_WITHOUT_LIBM)
if(NOT HAVE_SQRT_WITHOUT_LIBM)
  set(CMAKE_REQUIRED_LIBRARIES m)
  check_symbol_exists(sqrt "math.h" HAVE_SQRT_WITH_LIBM)
  unset(CMAKE_REQUIRED_LIBRARIES)
  if(NOT HAVE_SQRT_WITH_LIBM)
    message(FATAL_ERROR "Cannot link required math library")
  endif()
  target_link_libraries(eclipse PUBLIC m)
endif()


# M1 inspection is opt-in. The legacy executable and installed payload do not
# depend on the snapshot library, which is not yet a supported public ABI.
option(MEFPP_BUILD_CONFIG_PROBES "Build isolated M1 configuration probes" OFF)
if(MEFPP_BUILD_CONFIG_PROBES)
  add_library(mefpp_config_snapshot STATIC ins/mef/common/mef_config.c
    ins/mef/common/mef_runtime.c ins/mef/common/mef_cli_request.c
    ins/mef/common/mef_input_request.c ins/mef/common/mef_cal_bias.c)
  target_include_directories(mefpp_config_snapshot PUBLIC ins/mef/common
    PRIVATE src/include qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(mefpp_config_snapshot PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(mefpp_config_snapshot PRIVATE -Wall -Wextra -pedantic-errors)
  endif()
  target_link_libraries(mefpp_config_snapshot PUBLIC mefpp_common)
  # M2 parser exception: unmodified dependency and its private shim only.
  # Neither target is linked to mefpp or installed. Other code stays C90/C17.
  add_library(mefpp_config_domains STATIC ins/mef/common/mef_config_domains.c)
  target_include_directories(mefpp_config_domains PUBLIC ins/mef/common)
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(mefpp_config_domains PRIVATE -Wall -Wextra -pedantic-errors)
  endif()
  add_library(mefpp_tomlc17 STATIC ../third_party/tomlc17/tomlc17.c
    ins/mef/common/mef_toml_bridge.c)
  target_link_libraries(mefpp_tomlc17 PRIVATE mefpp_config_domains)
  set_target_properties(mefpp_tomlc17 PROPERTIES C_STANDARD 99 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_tomlc17 PRIVATE ../third_party/tomlc17 ins/mef/common)
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(mefpp_tomlc17 PRIVATE -Wall -Wextra -pedantic-errors)
  endif()
  add_library(mefpp_config_toml STATIC ins/mef/common/mef_config_toml.c
    ins/mef/common/mef_toml_bundle.c)
  target_include_directories(mefpp_config_toml PRIVATE ins/mef/common)
  target_link_libraries(mefpp_config_toml PUBLIC mefpp_config_snapshot mefpp_tomlc17)
  target_compile_definitions(mefpp_config_toml PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(mefpp_config_toml PRIVATE -Wall -Wextra -pedantic-errors)
  endif()
  add_executable(mef_config_read ins/mef/common/mef_config_read.c)
  target_link_libraries(mef_config_read PRIVATE mefpp_config_toml)
  target_compile_definitions(mef_config_read PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  add_executable(config_domains_probe tests/config_domains_probe.c)
  target_link_libraries(config_domains_probe PRIVATE mefpp_config_toml mefpp_config_domains)
  target_compile_options(config_domains_probe PRIVATE -UNDEBUG)
  add_executable(config_toml_snapshot tests/config_toml_snapshot.c)
  target_link_libraries(config_toml_snapshot PRIVATE mefpp_config_toml)
  target_compile_options(config_toml_snapshot PRIVATE -UNDEBUG)
  add_executable(config_paf_snapshot tests/config_paf_snapshot.c)
  target_link_libraries(config_paf_snapshot PRIVATE mefpp_config_snapshot mefpp_common)
  target_compile_definitions(config_paf_snapshot PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  add_executable(cli_capture_probe tests/cli_capture_probe.c)
  target_link_libraries(cli_capture_probe PRIVATE mefpp_config_snapshot mefpp_common)
  target_compile_definitions(cli_capture_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  add_executable(bias_service_probe tests/bias_service_probe.c tests/bias_legacy_reference.c)
  target_link_libraries(bias_service_probe PRIVATE mefpp_config_snapshot)
  target_compile_definitions(bias_service_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(bias_service_probe PRIVATE -UNDEBUG -Wall -Wextra)
  endif()
  add_executable(input_request_probe tests/input_request_probe.c)
  target_link_libraries(input_request_probe PRIVATE mefpp_config_snapshot eclipse)
  target_compile_definitions(input_request_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(cli_capture_probe PRIVATE -UNDEBUG -Wall -Wextra)
    target_compile_options(input_request_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  endif()
endif()

if(MEFPP_BUILD_RESOURCES)
  find_program(MEFPP_FUNPACK NAMES funpack REQUIRED)
  if(NOT EXISTS "${MEFPP_FUNPACK}" OR IS_DIRECTORY "${MEFPP_FUNPACK}")
    message(FATAL_ERROR "MEFPP_FUNPACK must identify an existing executable file")
  endif()
  file(SHA256 "${MEFPP_FUNPACK}" MEFPP_FUNPACK_SHA256)
  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/resources")
  foreach(mask IN ITEMS OCAM_BPM_1x1 WFI_BPM_1x1)
    add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/resources/${mask}.fits"
      COMMAND "${CMAKE_COMMAND}" "-DFUNPACK=${MEFPP_FUNPACK}" "-DOUTPUT=${CMAKE_CURRENT_BINARY_DIR}/resources/${mask}.fits" "-DINPUT=${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/static_cal/${mask}.fits.fz" -P "${CMAKE_CURRENT_SOURCE_DIR}/cmake/unpack_bpm.cmake"
      DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/static_cal/${mask}.fits.fz" "${CMAKE_CURRENT_SOURCE_DIR}/cmake/unpack_bpm.cmake"
      VERBATIM)
    list(APPEND resource_outputs "${CMAKE_CURRENT_BINARY_DIR}/resources/${mask}.fits")
  endforeach()
  add_custom_target(mefpp_resources ALL DEPENDS ${resource_outputs})
endif()

if(BUILD_TESTING)
  find_package(Python3 COMPONENTS Interpreter REQUIRED)
  add_test(NAME native_frontend_contract
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/frontend_contract.py"
      "${CMAKE_CURRENT_SOURCE_DIR}")
  add_test(NAME native_install_contract
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/install_contract.py"
      "${CMAKE_COMMAND}" "${CMAKE_CURRENT_SOURCE_DIR}/cmake/install_runtime.cmake.in")
  add_executable(native_smoke tests/native_smoke.c)
  target_link_libraries(native_smoke PRIVATE eclipse)
  if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    target_compile_definitions(native_smoke PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  endif()
  target_compile_options(native_smoke PRIVATE -Wall -Wextra -pedantic-errors)
  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/test-work")
  if(MEFPP_BUILD_CONFIG_PROBES)
    set(config_probe_sdk_args "")
    if(APPLE AND CMAKE_OSX_SYSROOT)
      list(APPEND config_probe_sdk_args --sysroot "${CMAKE_OSX_SYSROOT}")
    endif()
    add_test(NAME native_config_toml
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/config_toml_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --toml-probe "$<TARGET_FILE:config_toml_snapshot>"
        --paf-probe "$<TARGET_FILE:config_paf_snapshot>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_config_toml PROPERTIES TIMEOUT 300 LABELS "native;configuration;toml")
    add_test(NAME native_config_toml_subsets
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/config_toml_subsets_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --toml-probe "$<TARGET_FILE:config_toml_snapshot>"
        --paf-probe "$<TARGET_FILE:config_paf_snapshot>"
        --cli-probe "$<TARGET_FILE:cli_capture_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_config_toml_subsets PROPERTIES TIMEOUT 300 LABELS "native;configuration;toml;composition")
    add_test(NAME native_config_toml_domains
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/config_toml_domains_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --probe "$<TARGET_FILE:config_domains_probe>"
        --paf-probe "$<TARGET_FILE:config_paf_snapshot>"
        --cli-probe "$<TARGET_FILE:cli_capture_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_config_toml_domains PROPERTIES TIMEOUT 300 LABELS "native;configuration;toml;domains;provenance")
    add_test(NAME native_config_migration
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/config_migration_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --reader "$<TARGET_FILE:mef_config_read>"
        --paf-probe "$<TARGET_FILE:config_paf_snapshot>"
        --cli-probe "$<TARGET_FILE:cli_capture_probe>"
        --domain-probe "$<TARGET_FILE:config_domains_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_config_migration PROPERTIES TIMEOUT 300 LABELS "native;configuration;migration;provenance")
    add_test(NAME native_config_snapshot
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/config_snapshot_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --cc "${CMAKE_C_COMPILER}" --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work"
        --c-standard "${MEFPP_C_STANDARD}"
        --paf-probe "$<TARGET_FILE:config_paf_snapshot>" ${config_probe_sdk_args})
    set_tests_properties(native_config_snapshot PROPERTIES TIMEOUT 180 LABELS "native;configuration")
    add_test(NAME native_runtime_lifecycle
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/runtime_lifecycle_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --cc "${CMAKE_C_COMPILER}" --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work"
        --c-standard "${MEFPP_C_STANDARD}" ${config_probe_sdk_args})
    set_tests_properties(native_runtime_lifecycle PROPERTIES TIMEOUT 180 LABELS "native;configuration;ownership")
    add_test(NAME native_cli_capture
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/cli_capture_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --probe "$<TARGET_FILE:cli_capture_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_cli_capture PROPERTIES TIMEOUT 300 LABELS "native;configuration;cli;ownership")
    add_test(NAME native_bias_service
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/bias_service_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --probe "$<TARGET_FILE:bias_service_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_bias_service PROPERTIES TIMEOUT 300 LABELS "native;bias;ownership")
    add_test(NAME native_input_request
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/input_request_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --probe "$<TARGET_FILE:input_request_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_input_request PROPERTIES TIMEOUT 300 LABELS "native;inputs;ownership")
  endif()
  add_test(NAME native_primitives COMMAND native_smoke)
  set_tests_properties(native_primitives PROPERTIES WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/test-work")
  add_test(NAME native_failure_contract
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/failure_contract.py"
      "$<TARGET_FILE:mefpp>" "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/omegacam.paf")
  # Preserve the Mac/Chapman3-qualified response-ratio fixture unchanged.
  set(MEFPP_SOURCE_BRANCH "unknown" CACHE STRING "Source branch for test provenance")
  add_executable(shared_normalization_probe
    tests/fixtures/shared-normalization/shared_normalization_probe.c)
  target_link_libraries(shared_normalization_probe PRIVATE mefpp_common)
  target_compile_definitions(shared_normalization_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  foreach(kind IN ITEMS dome sky)
    foreach(order IN ITEMS 0 1)
      add_test(NAME native_shared_normalization_${kind}_order${order}
        COMMAND "${Python3_EXECUTABLE}"
          "${CMAKE_CURRENT_SOURCE_DIR}/tests/shared_normalization_contract.py"
          "$<TARGET_FILE:shared_normalization_probe>"
          "${CMAKE_CURRENT_SOURCE_DIR}/tests/fixtures/shared-normalization"
          "${kind}" "${order}"
          "${CMAKE_CURRENT_BINARY_DIR}/test-work/shared-normalization"
          "${MEFPP_SOURCE_REVISION}" "${MEFPP_SOURCE_BRANCH}")
      set_tests_properties(native_shared_normalization_${kind}_order${order}
        PROPERTIES TIMEOUT 90 LABELS "native;normalization")
    endforeach()
  endforeach()
  add_test(NAME native_cli_usage COMMAND "${CMAKE_COMMAND}" -DEXECUTABLE=$<TARGET_FILE:mefpp> -P "${CMAKE_CURRENT_SOURCE_DIR}/tests/cli_usage.cmake")
endif()

# Installation validates every required file before writing a private prefix.
set(MEFPP_BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}")
set(MEFPP_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
# Hash all native inputs, including headers and compressed resources, for provenance.
file(GLOB_RECURSE manifest_inputs CONFIGURE_DEPENDS RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}"
  "src/*.c" "src/*.h" "ins/mef/*.c" "ins/mef/*.h" "ins/mef/*.def"
  "ins/mef/config/*.paf" "ins/mef/static_cal/*.fits.fz"
  "qfits5/src/*.c" "qfits5/src/*.h" "qfits5/include/*.h"
  "CMakeLists.txt" "Makefile" "configure" "cmake/*" "tests/*" "LICENSE" "qfits5/LICENSE")
set(source_inventory "")
if(MEFPP_BUILD_CONFIG_PROBES)
  list(APPEND manifest_inputs ../third_party/tomlc17/tomlc17.c
    ../third_party/tomlc17/tomlc17.h ../third_party/tomlc17/LICENSE
    ../third_party/tomlc17/upstream.json)
  list(SORT manifest_inputs)
endif()
foreach(input IN LISTS manifest_inputs)
  file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/${input}" digest)
  string(APPEND source_inventory "${input} ${digest}\n")
endforeach()
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/source-sha256.txt" "${source_inventory}")
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/source-sha256.txt" MEFPP_SOURCE_INVENTORY_SHA256)
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/generated/mefpp_platform_config.h" MEFPP_CONFIG_SHA256)
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/generated/qfits_platform_config.h" QFITS_CONFIG_SHA256)
# Escape strings used in the JSON record, including paths with spaces/quotes.
foreach(json_key IN ITEMS MEFPP_SOURCE_REVISION CMAKE_C_COMPILER CMAKE_C_COMPILER_ID
    CMAKE_C_COMPILER_VERSION CMAKE_VERSION MEFPP_C_STANDARD CMAKE_SYSTEM_NAME
    CMAKE_SYSTEM_PROCESSOR CMAKE_OSX_ARCHITECTURES CMAKE_OSX_SYSROOT CMAKE_AR
    CMAKE_RANLIB CMAKE_LINKER CMAKE_INSTALL_PREFIX CMAKE_BUILD_TYPE CMAKE_C_FLAGS
    CMAKE_EXE_LINKER_FLAGS MEFPP_FUNPACK)
  set(JSON_${json_key} "${${json_key}}")
  string(REPLACE "\\" "\\\\" JSON_${json_key} "${JSON_${json_key}}")
  string(REPLACE "\"" "\\\"" JSON_${json_key} "${JSON_${json_key}}")
  string(REPLACE "\n" "\\n" JSON_${json_key} "${JSON_${json_key}}")
  string(REPLACE "\r" "\\r" JSON_${json_key} "${JSON_${json_key}}")
  string(REPLACE "\t" "\\t" JSON_${json_key} "${JSON_${json_key}}")
endforeach()
configure_file(cmake/build-info.json.in build-info.json @ONLY)
file(GENERATE OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/mefpp-path-$<CONFIG>.cmake" CONTENT "set(MEFPP_EXECUTABLE [==[$<TARGET_FILE:mefpp>]==])\n")
configure_file(cmake/install_runtime.cmake.in install_runtime.cmake @ONLY)
install(SCRIPT "${CMAKE_CURRENT_BINARY_DIR}/install_runtime.cmake")
message(STATUS "Candidate mefpp: C${MEFPP_C_STANDARD}; ${CMAKE_C_COMPILER}; resources=${MEFPP_BUILD_RESOURCES}")
