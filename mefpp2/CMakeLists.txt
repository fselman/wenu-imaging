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
option(MEFPP_BUILD_BIAS_RECIPE "Build uninstalled standalone MEF/native-ASDF bias recipe" OFF)
if(MEFPP_BUILD_BIAS_RECIPE)
  if(NOT MEFPP_C_STANDARD STREQUAL "17")
    message(FATAL_ERROR "The standalone bias recipe requires the selected C17 lane")
  endif()
  set(MEFPP_BUILD_MEF_ASSEMBLER ON CACHE BOOL "Native MEF assembly" FORCE)
  set(MEFPP_BUILD_BIAS_ADAPTER ON CACHE BOOL "Native bias service/reference adapter" FORCE)
endif()
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
check_c_source_compiles("#include <sys/types.h>\n#include <stddef.h>\n#include <limits.h>\nint main(void) { typedef char wide_io[(sizeof(long)>=8 && sizeof(off_t)<=sizeof(long) && sizeof(size_t)>=sizeof(off_t) && sizeof(ptrdiff_t)>=sizeof(off_t) && (off_t)-1<0) ? 1 : -1]; return sizeof(wide_io)!=1; }" HAVE_WIDE_IO_TYPES)
foreach(symbol IN ITEMS fseeko ftello)
  check_symbol_exists(${symbol} "stdio.h;sys/types.h" HAVE_${symbol})
  if(NOT HAVE_${symbol})
    message(FATAL_ERROR "Required wide file I/O interface unavailable: ${symbol}")
  endif()
endforeach()
if(NOT HAVE_WIDE_IO_TYPES)
  message(FATAL_ERROR "Wide I/O requires the selected signed-off_t LP64 representation")
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
option(MEFPP_BUILD_MEF_ASSEMBLER "Build isolated native MEF assembly (no recipe activation)" OFF)
if(MEFPP_BUILD_MEF_ASSEMBLER)
  add_library(mefpp_mef_assembly STATIC
    ins/mef/common/mef_mef_assemble.c ins/mef/common/mef_bpm_assembly_planes.c)
  target_include_directories(mefpp_mef_assembly PUBLIC ins/mef/common)
  target_link_libraries(mefpp_mef_assembly PUBLIC qfits)
  if(NOT APPLE)
    target_link_libraries(mefpp_mef_assembly PUBLIC m)
  endif()
  set_target_properties(mefpp_mef_assembly PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_compile_options(mefpp_mef_assembly PRIVATE -Wall -Wextra -Werror -pedantic-errors)
  add_executable(bpm_mef_assembly_probe tests/bpm_mef_assembly_probe.c)
  target_link_libraries(bpm_mef_assembly_probe PRIVATE mefpp_mef_assembly)
  set_target_properties(bpm_mef_assembly_probe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_compile_options(bpm_mef_assembly_probe PRIVATE -Wall -Wextra -Werror -pedantic-errors)
  add_executable(mef_assembly_probe tests/mef_assembly_probe.c)
  target_link_libraries(mef_assembly_probe PRIVATE mefpp_mef_assembly)
  set_target_properties(mef_assembly_probe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_compile_options(mef_assembly_probe PRIVATE -Wall -Wextra -Werror -pedantic-errors)
endif()
add_library(eclipse STATIC ${ECLIPSE_SOURCES})
target_include_directories(eclipse PUBLIC src/include)
target_compile_definitions(eclipse PRIVATE _ECLIPSE_)
target_link_libraries(eclipse PUBLIC qfits)
add_library(mefpp_common STATIC ins/mef/common/mefp_lib.c
  ins/mef/common/mef_bias_kernel.c ins/mef/common/mef_paths.c)
target_include_directories(mefpp_common PUBLIC ins/mef/common)
target_link_libraries(mefpp_common PUBLIC eclipse)
add_executable(mefpp ins/mef/recipes/mefpp.c ins/mef/common/mef_recipe_help.c)
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


# Configuration inspection is opt-in. The legacy executable and installed payload do not
# depend on the snapshot library, which is not yet a supported public ABI.
option(MEFPP_BUILD_CONFIG_PROBES "Build isolated configuration probes" OFF)
option(MEFPP_BUILD_BIAS_ADAPTER "Build uninstalled one-detector bias command" OFF)
if(MEFPP_BUILD_BIAS_ADAPTER)
  set(MEFPP_BUILD_CONFIG_PROBES ON)
endif()
if(MEFPP_BUILD_CONFIG_PROBES)
  add_library(mefpp_config_snapshot STATIC ins/mef/common/mef_config.c
    ins/mef/common/mef_runtime.c ins/mef/common/mef_cli_request.c
    ins/mef/common/mef_input_request.c ins/mef/common/mef_cal_bias.c
    ins/mef/common/mef_layout.c)
  target_include_directories(mefpp_config_snapshot PUBLIC ins/mef/common
    PRIVATE src/include qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(mefpp_config_snapshot PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(mefpp_config_snapshot PRIVATE -Wall -Wextra -pedantic-errors)
  endif()
  target_link_libraries(mefpp_config_snapshot PUBLIC mefpp_common)
  # Configuration parser exception: unmodified dependency and its private shim only.
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
  # Named ROI supplement: explicit C17, isolated from legacy settings/schema.
  add_library(mefpp_roi_config STATIC ins/mef/common/mef_roi_config.c)
  set_target_properties(mefpp_roi_config PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_roi_config PUBLIC ins/mef/common src/include
    PRIVATE ../third_party/tomlc17 qfits5/include)
  target_link_libraries(mefpp_roi_config PUBLIC mefpp_tomlc17 mefpp_common)
  target_compile_options(mefpp_roi_config PRIVATE -Wall -Wextra -pedantic-errors)
  add_executable(roi_config_probe tests/roi_config_probe.c)
  set_target_properties(roi_config_probe PROPERTIES C_STANDARD 17)
  target_link_libraries(roi_config_probe PRIVATE mefpp_roi_config)
  target_compile_options(roi_config_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  add_library(mefpp_linearity_samples STATIC ins/mef/common/mef_linearity_samples.c)
  set_target_properties(mefpp_linearity_samples PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_linearity_samples PUBLIC ins/mef/common src/include
    PRIVATE qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_link_libraries(mefpp_linearity_samples PUBLIC mefpp_config_snapshot)
  target_compile_definitions(mefpp_linearity_samples PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_compile_options(mefpp_linearity_samples PRIVATE -Wall -Wextra -pedantic-errors)
  add_executable(linearity_samples_probe tests/linearity_samples_probe.c)
  set_target_properties(linearity_samples_probe PROPERTIES C_STANDARD 17)
  target_link_libraries(linearity_samples_probe PRIVATE mefpp_linearity_samples)
  target_compile_options(linearity_samples_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  add_library(mefpp_linearity_pairs STATIC ins/mef/common/mef_linearity_pairs.c
    ins/mef/common/mef_linearity_pairs_export.c)
  set_target_properties(mefpp_linearity_pairs PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_linearity_pairs PRIVATE qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(mefpp_linearity_pairs PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_link_libraries(mefpp_linearity_pairs PUBLIC mefpp_linearity_samples)
  target_compile_options(mefpp_linearity_pairs PRIVATE -Wall -Wextra -pedantic-errors)
  add_executable(linearity_pairs_probe tests/linearity_pairs_probe.c)
  add_library(mefpp_linearity_prepare STATIC ins/mef/common/mef_linearity_prepare.c)
  set_target_properties(mefpp_linearity_prepare PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_linearity_prepare PRIVATE qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(mefpp_linearity_prepare PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_link_libraries(mefpp_linearity_prepare PUBLIC mefpp_linearity_pairs)
  target_compile_options(mefpp_linearity_prepare PRIVATE -Wall -Wextra -pedantic-errors)
  add_executable(linearity_prepare_probe tests/linearity_prepare_probe.c)
  set_target_properties(linearity_prepare_probe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_link_libraries(linearity_prepare_probe PRIVATE mefpp_linearity_prepare)
  target_compile_options(linearity_prepare_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  add_test(NAME native_linearity_prepare COMMAND linearity_prepare_probe)
  set_tests_properties(native_linearity_prepare PROPERTIES TIMEOUT 180 LABELS "native;linearity;overscan;ownership")
  set_target_properties(linearity_pairs_probe PROPERTIES C_STANDARD 17)
  target_link_libraries(linearity_pairs_probe PRIVATE mefpp_linearity_pairs)
  target_compile_options(linearity_pairs_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  add_executable(linearity_pairs_export_probe tests/linearity_pairs_export_probe.c)
  set_target_properties(linearity_pairs_export_probe PROPERTIES C_STANDARD 17)
  target_link_libraries(linearity_pairs_export_probe PRIVATE mefpp_linearity_pairs)
  target_compile_options(linearity_pairs_export_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  add_library(mefpp_detector_cube STATIC ins/mef/common/mef_detector_cube.c)
  target_link_libraries(mefpp_detector_cube PUBLIC mefpp_linearity_prepare mefpp_config_toml)
  target_compile_definitions(mefpp_detector_cube PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_compile_options(mefpp_detector_cube PRIVATE -Wall -Wextra -Wno-unused-function -pedantic-errors)
  set_target_properties(mefpp_detector_cube PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  add_library(mefpp_linearity_files STATIC ins/mef/common/mef_linearity_files.c
    ins/mef/common/mef_linearity_raw_files.c)
  set_target_properties(mefpp_linearity_files PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_linearity_files PRIVATE qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(mefpp_linearity_files PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_link_libraries(mefpp_linearity_files PUBLIC mefpp_detector_cube mefpp_linearity_samples mefpp_linearity_pairs mefpp_linearity_prepare)
  target_compile_options(mefpp_linearity_files PRIVATE -Wall -Wextra -pedantic-errors)
  add_executable(mefpp_pair_measure ins/mef/mefpp_pair_measure.c)
  add_executable(mefpp_linearity_prepare_command ins/mef/mefpp_linearity_prepare.c)
  set_target_properties(mefpp_linearity_prepare_command PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_linearity_prepare_command PRIVATE qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(mefpp_linearity_prepare_command PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_link_libraries(mefpp_linearity_prepare_command PRIVATE mefpp_linearity_files mefpp_roi_config mefpp_config_toml)
  target_compile_options(mefpp_linearity_prepare_command PRIVATE -Wall -Wextra -pedantic-errors)
  set_target_properties(mefpp_pair_measure PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_pair_measure PRIVATE qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(mefpp_pair_measure PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_link_libraries(mefpp_pair_measure PRIVATE mefpp_linearity_files mefpp_roi_config)
  target_compile_options(mefpp_pair_measure PRIVATE -Wall -Wextra -pedantic-errors)
  add_executable(mefpp_sample_extract ins/mef/mefpp_sample_extract.c)
  set_target_properties(mefpp_sample_extract PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_include_directories(mefpp_sample_extract PRIVATE qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(mefpp_sample_extract PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_link_libraries(mefpp_sample_extract PRIVATE mefpp_linearity_files mefpp_roi_config)
  target_compile_options(mefpp_sample_extract PRIVATE -Wall -Wextra -pedantic-errors)
  add_executable(linearity_raw_files_probe tests/linearity_raw_files_probe.c)
  set_target_properties(linearity_raw_files_probe PROPERTIES C_STANDARD 17)
  target_link_libraries(linearity_raw_files_probe PRIVATE mefpp_linearity_files)
  target_compile_options(linearity_raw_files_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  add_executable(linearity_files_probe tests/linearity_files_probe.c)
  set_target_properties(linearity_files_probe PROPERTIES C_STANDARD 17)
  target_link_libraries(linearity_files_probe PRIVATE mefpp_linearity_files)
  target_compile_options(linearity_files_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  add_library(mefpp_config_toml STATIC ins/mef/common/mef_config_toml.c
    ins/mef/common/mef_toml_bundle.c ins/mef/common/mef_toml_file.c
    ins/mef/common/mef_project.c)
  target_include_directories(mefpp_config_toml PUBLIC ../third_party/tomlc17 PRIVATE ins/mef/common)
  target_link_libraries(mefpp_config_toml PUBLIC mefpp_config_snapshot mefpp_tomlc17)
  add_library(mefpp_product_qc_records STATIC ins/mef/common/mef_product_qc_validate.c)
  add_library(mefpp_linearity_archive STATIC ins/mef/common/mef_linearity_archive.c)
  target_link_libraries(mefpp_linearity_archive PUBLIC mefpp_linearity_files mefpp_product_qc_records)
  target_compile_options(mefpp_linearity_archive PRIVATE -Wall -Wextra -Werror -pedantic-errors)
  set_target_properties(mefpp_linearity_archive PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_link_libraries(mefpp_linearity_prepare_command PRIVATE mefpp_linearity_archive)
  add_executable(linearity_archive_metadata_probe ins/mef/mefpp_linearity_prepare.c tests/linearity_archive_metadata.c)
  target_link_libraries(linearity_archive_metadata_probe PRIVATE mefpp_linearity_archive mefpp_roi_config mefpp_config_toml)
  target_include_directories(linearity_archive_metadata_probe PRIVATE qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(linearity_archive_metadata_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
    MEFPP_NATIVE_PRODUCT_QC=1 MEFPP_CANDIDATE_REVISION="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
  target_compile_options(linearity_archive_metadata_probe PRIVATE -Wall -Wextra -Werror -pedantic-errors)
  set_target_properties(linearity_archive_metadata_probe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_compile_definitions(mefpp_linearity_prepare_command PRIVATE MEFPP_CANDIDATE_REVISION="${MEFPP_SOURCE_REVISION}")
  target_include_directories(mefpp_product_qc_records PUBLIC ins/mef/common)
  target_compile_options(mefpp_product_qc_records PRIVATE -Wall -Wextra -Werror -pedantic-errors)
  set_target_properties(mefpp_product_qc_records PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  add_library(mefpp_recipe_run STATIC ins/mef/common/mef_recipe_run.c
    ins/mef/common/mef_product_paths.c ins/mef/common/mef_recipe_inputs.c)
  target_link_libraries(mefpp_recipe_run PUBLIC mefpp_config_snapshot)
  target_compile_definitions(mefpp_recipe_run PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_compile_options(mefpp_recipe_run PRIVATE -Wall -Wextra -Werror -pedantic-errors)
  set_target_properties(mefpp_recipe_run PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  add_executable(recipe_file_hash_probe tests/recipe_file_hash_probe.c
    ins/mef/common/mef_bpm_linearity_hash.c)
  target_include_directories(recipe_file_hash_probe PRIVATE ../third_party/tomlc17)
  target_link_libraries(recipe_file_hash_probe PRIVATE mefpp_recipe_run)
  target_compile_definitions(recipe_file_hash_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_compile_options(recipe_file_hash_probe PRIVATE -Wall -Wextra -Werror -pedantic-errors)
  set_target_properties(recipe_file_hash_probe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  add_executable(recipe_run_probe tests/recipe_run_probe.c)
  target_link_libraries(recipe_run_probe PRIVATE mefpp_recipe_run)
  target_compile_options(recipe_run_probe PRIVATE -UNDEBUG -Wall -Wextra -Werror -pedantic-errors)
  set_target_properties(recipe_run_probe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  if(MEFPP_BUILD_BIAS_ADAPTER)
    add_library(mefpp_bias_files STATIC ins/mef/common/mef_bias_files.c
      ins/mef/common/mef_operation_template.c)
    target_link_libraries(mefpp_bias_files PUBLIC mefpp_config_snapshot)
    add_library(mefpp_bpm_service STATIC ins/mef/common/mef_cal_bpm.c ins/mef/common/mef_bpm_files.c
      ins/mef/common/mef_bpm_publish.c)
    target_link_libraries(mefpp_bpm_service PUBLIC mefpp_bias_files mefpp_detector_cube)
    target_compile_definitions(mefpp_bpm_service PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
    target_compile_options(mefpp_bpm_service PRIVATE -Wall -Wextra -pedantic-errors)
    add_library(mefpp_bpm_product_qc STATIC ins/mef/common/mef_bpm_product_qc.c)
    target_link_libraries(mefpp_bpm_product_qc PUBLIC mefpp_bpm_service mefpp_product_qc_records)
    target_compile_options(mefpp_bpm_product_qc PRIVATE -Wall -Wextra -Werror -pedantic-errors)
    set_target_properties(mefpp_bpm_product_qc PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
    add_executable(bpm_native_qc_probe tests/bpm_files_probe.c)
    target_link_libraries(bpm_native_qc_probe PRIVATE mefpp_bpm_product_qc)
    target_compile_definitions(bpm_native_qc_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      BPM_PUBLICATION_CONTRACT=1 BPM_NATIVE_QC_CONTRACT=1)
    target_compile_options(bpm_native_qc_probe PRIVATE -UNDEBUG -Wall -Wextra -Werror -pedantic-errors)
    add_executable(bpm_service_probe tests/bpm_service_probe.c)
    target_link_libraries(bpm_service_probe PRIVATE mefpp_linearity_prepare mefpp_bpm_service)
    target_compile_definitions(bpm_service_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
    target_compile_options(bpm_service_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
    add_executable(bpm_files_probe tests/bpm_files_probe.c)
    target_link_libraries(bpm_files_probe PRIVATE mefpp_bpm_service)
    target_compile_definitions(bpm_files_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
    target_compile_options(bpm_files_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
    add_executable(bpm_publication_probe tests/bpm_files_probe.c)
    target_link_libraries(bpm_publication_probe PRIVATE mefpp_bpm_service)
    target_compile_definitions(bpm_publication_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS} BPM_PUBLICATION_CONTRACT=1)
    target_compile_options(bpm_publication_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
    target_compile_definitions(mefpp_bias_files PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
    target_compile_options(mefpp_bias_files PRIVATE -Wall -Wextra -pedantic-errors)
    add_executable(mefpp_m5 ins/mef/recipes/mefpp_bias_adapter.c ins/mef/recipes/mefpp_bpm_adapter.c)
    target_link_libraries(mefpp_m5 PRIVATE mefpp_bpm_service mefpp_config_toml)
    target_compile_definitions(mefpp_m5 PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      MEFPP_CANDIDATE_REVISION="${MEFPP_SOURCE_REVISION}")
    target_compile_options(mefpp_m5 PRIVATE -Wall -Wextra -pedantic-errors)
    if(MEFPP_BUILD_BIAS_RECIPE)
      # Length is checked separately because CMake regex repetition is limited.
      string(LENGTH "${MEFPP_SOURCE_REVISION}" recipe_revision_length)
      if(NOT MEFPP_SOURCE_REVISION MATCHES "^[0-9a-f]+$" OR NOT recipe_revision_length EQUAL 40)
        message(FATAL_ERROR "Standalone recipe requires an exact 40-character MEFPP_SOURCE_REVISION")
      endif()
      set(MEFPP_ASDF_PREFIX "" CACHE PATH "Existing qualified libasdf prefix; no installation")
      if(NOT IS_DIRECTORY "${MEFPP_ASDF_PREFIX}/include/asdf")
        message(FATAL_ERROR "Supply the retained qualified MEFPP_ASDF_PREFIX")
      endif()
      find_library(MEFPP_ASDF_LIBRARY NAMES asdf PATHS "${MEFPP_ASDF_PREFIX}/lib" NO_DEFAULT_PATH REQUIRED)
      add_library(mefpp_product_qc STATIC ins/mef/common/mef_product_qc_asdf.c)
      target_include_directories(mefpp_product_qc PUBLIC ins/mef/common)
      target_include_directories(mefpp_product_qc SYSTEM PRIVATE "${MEFPP_ASDF_PREFIX}/include")
      target_link_libraries(mefpp_product_qc PUBLIC "${MEFPP_ASDF_LIBRARY}" mefpp_recipe_run mefpp_product_qc_records)
      add_executable(mefpp_bpm_assemble ins/mef/mefpp_bpm_assemble.c)
      target_link_libraries(mefpp_bpm_assemble PRIVATE mefpp_mef_assembly mefpp_product_qc)
      target_compile_definitions(mefpp_bpm_assemble PRIVATE MEFPP_CANDIDATE_REVISION="${MEFPP_SOURCE_REVISION}")
      target_compile_options(mefpp_bpm_assemble PRIVATE -Wall -Wextra -Werror -pedantic-errors)
      set_target_properties(mefpp_bpm_assemble PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO
        BUILD_RPATH "${MEFPP_ASDF_PREFIX}/lib")
      target_link_libraries(mefpp_m5 PRIVATE mefpp_bpm_product_qc mefpp_product_qc)
      target_link_libraries(mefpp_linearity_prepare_command PRIVATE mefpp_product_qc)
      set_target_properties(mefpp_linearity_prepare_command PROPERTIES BUILD_RPATH "${MEFPP_ASDF_PREFIX}/lib")
      target_compile_definitions(mefpp_linearity_prepare_command PRIVATE MEFPP_NATIVE_PRODUCT_QC=1)
      target_compile_definitions(mefpp_m5 PRIVATE MEFPP_NATIVE_PRODUCT_QC=1)
      if(NOT APPLE)
        target_link_libraries(mefpp_product_qc PUBLIC m)
      endif()
      add_executable(bpm_native_asdf_probe tests/bpm_files_probe.c)
      target_link_libraries(bpm_native_asdf_probe PRIVATE mefpp_bpm_product_qc mefpp_product_qc)
      target_compile_definitions(bpm_native_asdf_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
        BPM_PUBLICATION_CONTRACT=1 BPM_NATIVE_QC_CONTRACT=1 BPM_NATIVE_ASDF_CONTRACT=1)
      target_compile_options(bpm_native_asdf_probe PRIVATE -UNDEBUG -Wall -Wextra -Werror -pedantic-errors)
      set_target_properties(bpm_native_asdf_probe PROPERTIES BUILD_RPATH "${MEFPP_ASDF_PREFIX}/lib")
      add_library(mefpp_bias_product_qc STATIC ins/mef/common/mef_bias_product_qc.c
        ins/mef/common/mef_bias_qc_fits.c)
      target_link_libraries(mefpp_bias_product_qc PUBLIC mefpp_bias_files mefpp_product_qc)
      add_executable(mefpp_bias_recipe ins/mef/recipes/mefpp_bias.c
        ins/mef/common/mef_bias_config.c
        ins/mef/common/mef_bias_prepare.c ins/mef/common/mef_bias_inputs.c
        ins/mef/common/mef_bias_process.c ins/mef/common/mef_bias_products.c)
      target_include_directories(mefpp_bias_recipe PRIVATE ../third_party/tomlc17)
      target_link_libraries(mefpp_bias_recipe PRIVATE mefpp_bias_product_qc mefpp_config_toml mefpp_mef_assembly)
      target_compile_definitions(mefpp_bias_recipe PRIVATE MEFPP_CANDIDATE_REVISION="${MEFPP_SOURCE_REVISION}")
      set_target_properties(mefpp_bias_recipe PROPERTIES BUILD_RPATH "${MEFPP_ASDF_PREFIX}/lib")
      add_executable(bias_product_qc_probe tests/bias_product_qc_probe.c)
      target_link_libraries(bias_product_qc_probe PRIVATE mefpp_bias_product_qc)
      target_compile_definitions(bias_product_qc_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
        MEFPP_CANDIDATE_REVISION="${MEFPP_SOURCE_REVISION}")
      target_compile_options(bias_product_qc_probe PRIVATE -UNDEBUG -Wall -Wextra -Werror -pedantic-errors)
      set_target_properties(bias_product_qc_probe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO
        BUILD_RPATH "${MEFPP_ASDF_PREFIX}/lib")
      option(MEFPP_BUILD_WARNING_PROBE "Build focused legacy warning checks with an explicit original reference" OFF)
      if(MEFPP_BUILD_WARNING_PROBE)
        set(MEFPP_WARNING_CORNER_REFERENCE "" CACHE FILEPATH "Retained pre-cleanup corner.c for comparison only")
        if(NOT EXISTS "${MEFPP_WARNING_CORNER_REFERENCE}")
          message(FATAL_ERROR "Supply the retained original MEFPP_WARNING_CORNER_REFERENCE")
        endif()
        add_library(warning_corner_reference OBJECT "${MEFPP_WARNING_CORNER_REFERENCE}")
        target_include_directories(warning_corner_reference PRIVATE src/include qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
        target_compile_definitions(warning_corner_reference PRIVATE ${MEFPP_FEATURE_DEFINITIONS} _ECLIPSE_=1
          image_detect_corners=mef_corner_warning_reference)
        set_target_properties(warning_corner_reference PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
        add_executable(native_warning_probe tests/native_warning_probe.c $<TARGET_OBJECTS:warning_corner_reference>)
        target_include_directories(native_warning_probe PRIVATE qfits5/src)
        target_link_libraries(native_warning_probe PRIVATE mefpp_bias_files)
        target_compile_definitions(native_warning_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
        target_compile_options(native_warning_probe PRIVATE -UNDEBUG -Wall -Wextra -Werror -pedantic-errors)
        set_target_properties(native_warning_probe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
      endif()
      add_executable(mefpp_bpm_linearity_recipe
        ins/mef/recipes/mefpp_bpm_linearity.c
        ins/mef/common/mef_bpm_linearity_config.c
        ins/mef/common/mef_bpm_linearity_compile.c
        ins/mef/common/mef_bpm_linearity_inputs.c
        ins/mef/common/mef_bpm_linearity_bindings.c
        ins/mef/common/mef_bpm_linearity_hash.c
        ins/mef/common/mef_bpm_linearity_process.c
        ins/mef/common/mef_bpm_linearity_products.c
        ins/mef/mefpp_linearity_prepare.c ins/mef/recipes/mefpp_bpm_adapter.c)
      target_include_directories(mefpp_bpm_linearity_recipe PRIVATE ../third_party/tomlc17)
      target_link_libraries(mefpp_bpm_linearity_recipe PRIVATE
        mefpp_recipe_run mefpp_bpm_product_qc mefpp_product_qc mefpp_config_toml
        mefpp_mef_assembly mefpp_linearity_files mefpp_linearity_archive mefpp_roi_config)
      target_compile_definitions(mefpp_bpm_linearity_recipe PRIVATE
        ${MEFPP_FEATURE_DEFINITIONS} MEFPP_RECIPE_LIBRARY=1 MEFPP_NATIVE_PRODUCT_QC=1
        MEFPP_CANDIDATE_REVISION="${MEFPP_SOURCE_REVISION}")
      set_target_properties(mefpp_bpm_linearity_recipe PROPERTIES
        C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO
        BUILD_RPATH "${MEFPP_ASDF_PREFIX}/lib")
      target_compile_options(mefpp_bpm_linearity_recipe PRIVATE -Wall -Wextra -pedantic-errors)

      # One native public executable; compatibility binaries keep their entry points.
      get_target_property(bias_recipe_sources mefpp_bias_recipe SOURCES)
      get_target_property(bpm_linearity_sources mefpp_bpm_linearity_recipe SOURCES)
      add_executable(mefpp_recipe ins/mef/recipes/mefpp_recipe.c
        ins/mef/common/mef_recipe_help.c ${bias_recipe_sources} ${bpm_linearity_sources})
      target_include_directories(mefpp_recipe PRIVATE ../third_party/tomlc17)
      target_link_libraries(mefpp_recipe PRIVATE mefpp_bias_product_qc
        mefpp_recipe_run mefpp_bpm_product_qc mefpp_product_qc mefpp_config_toml
        mefpp_mef_assembly mefpp_linearity_files mefpp_linearity_archive mefpp_roi_config)
      target_compile_definitions(mefpp_recipe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
        MEFPP_RECIPE_ENTRY_LIBRARY=1 MEFPP_RECIPE_LIBRARY=1 MEFPP_NATIVE_PRODUCT_QC=1
        MEFPP_CANDIDATE_REVISION="${MEFPP_SOURCE_REVISION}")
      set_target_properties(mefpp_recipe PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES
        C_EXTENSIONS NO BUILD_RPATH "${MEFPP_ASDF_PREFIX}/lib")
      target_compile_options(mefpp_recipe PRIVATE -Wall -Wextra -pedantic-errors)

      foreach(recipe_target IN ITEMS mefpp_product_qc mefpp_bias_product_qc mefpp_bias_recipe)
        set_target_properties(${recipe_target} PROPERTIES C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
        target_compile_definitions(${recipe_target} PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
        target_compile_options(${recipe_target} PRIVATE -Wall -Wextra -Werror -pedantic-errors)
      endforeach()
    endif()
    add_executable(operation_template_probe tests/operation_template_probe.c)
    target_link_libraries(operation_template_probe PRIVATE mefpp_bias_files)
    target_compile_options(operation_template_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  endif()
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
  add_executable(qfits_discovery_probe tests/qfits_discovery_probe.c)
  target_link_libraries(qfits_discovery_probe PRIVATE qfits)
  add_executable(measurement_stats_probe tests/measurement_stats_probe.c)
  if(MEFPP_BUILD_BIAS_ADAPTER)
    add_executable(linearity_fit_probe tests/linearity_fit_probe.c)
    target_link_libraries(linearity_fit_probe PRIVATE eclipse)
    target_compile_options(linearity_fit_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
    add_library(linearity_fit_allocation_units OBJECT src/iproc/detector_linearity_fit.c)
    target_include_directories(linearity_fit_allocation_units PRIVATE src/include qfits5/include
      "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(linearity_fit_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
    add_executable(linearity_fit_allocation_probe tests/linearity_fit_allocation_probe.c
      $<TARGET_OBJECTS:linearity_fit_allocation_units>)
    target_compile_definitions(linearity_fit_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
    target_compile_options(linearity_fit_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
    target_link_libraries(linearity_fit_allocation_probe PRIVATE eclipse)
    add_executable(detector_noise_probe tests/detector_noise_probe.c)
    target_link_libraries(detector_noise_probe PRIVATE eclipse)
    target_compile_options(detector_noise_probe PRIVATE -UNDEBUG -Wall -Wextra)
    add_library(detector_noise_allocation_units OBJECT src/iproc/detector_noise.c src/math/matrix.c)
    target_include_directories(detector_noise_allocation_units PRIVATE src/include qfits5/include
      "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(detector_noise_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
    add_executable(detector_noise_allocation_probe tests/detector_noise_allocation_probe.c
      $<TARGET_OBJECTS:detector_noise_allocation_units>)
    target_compile_definitions(detector_noise_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
    target_compile_options(detector_noise_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra)
    target_link_libraries(detector_noise_allocation_probe PRIVATE eclipse)
    add_executable(roi_aggregation_probe tests/roi_aggregation_probe.c)
    target_link_libraries(roi_aggregation_probe PRIVATE eclipse)
    target_compile_options(roi_aggregation_probe PRIVATE -UNDEBUG -Wall -Wextra)
    add_library(roi_aggregation_allocation_units OBJECT src/iproc/detector_roi.c
      src/math/matrix.c)
    target_include_directories(roi_aggregation_allocation_units PRIVATE src/include qfits5/include
      "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(roi_aggregation_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
    add_executable(roi_aggregation_allocation_probe tests/roi_aggregation_allocation_probe.c
      $<TARGET_OBJECTS:roi_aggregation_allocation_units>)
    target_compile_definitions(roi_aggregation_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
    target_compile_options(roi_aggregation_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra)
    target_link_libraries(roi_aggregation_allocation_probe PRIVATE eclipse)
    add_executable(shutter_profile_probe tests/shutter_profile_probe.c)
    target_link_libraries(shutter_profile_probe PRIVATE eclipse)
    target_compile_options(shutter_profile_probe PRIVATE -UNDEBUG -Wall -Wextra)
    add_library(shutter_profile_allocation_units OBJECT src/iproc/detector_joint.c
      src/math/optimization.c src/math/matrix.c)
    target_include_directories(shutter_profile_allocation_units PRIVATE src/include qfits5/include
      "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(shutter_profile_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
    add_executable(shutter_profile_allocation_probe tests/shutter_profile_allocation_probe.c
      $<TARGET_OBJECTS:shutter_profile_allocation_units>)
    target_compile_definitions(shutter_profile_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
    target_compile_options(shutter_profile_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra)
    target_link_libraries(shutter_profile_allocation_probe PRIVATE eclipse)
    add_executable(detector_joint_probe tests/detector_joint_probe.c)
    target_link_libraries(detector_joint_probe PRIVATE eclipse)
    target_compile_options(detector_joint_probe PRIVATE -UNDEBUG -Wall -Wextra)
    add_library(detector_joint_allocation_units OBJECT src/iproc/detector_joint.c
      src/math/optimization.c src/math/matrix.c)
    target_include_directories(detector_joint_allocation_units PRIVATE src/include qfits5/include
      "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(detector_joint_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
    add_executable(detector_joint_allocation_probe tests/detector_joint_allocation_probe.c
      $<TARGET_OBJECTS:detector_joint_allocation_units>)
    target_compile_definitions(detector_joint_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
    target_compile_options(detector_joint_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra)
    target_link_libraries(detector_joint_allocation_probe PRIVATE eclipse)
    add_executable(simplex_probe tests/simplex_probe.c)
    target_link_libraries(simplex_probe PRIVATE eclipse)
    target_compile_options(simplex_probe PRIVATE -UNDEBUG -Wall -Wextra)
    add_library(simplex_allocation_units OBJECT src/math/optimization.c src/math/matrix.c)
    target_include_directories(simplex_allocation_units PRIVATE src/include qfits5/include
      "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(simplex_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
    add_executable(simplex_allocation_probe tests/simplex_allocation_probe.c
      $<TARGET_OBJECTS:simplex_allocation_units>)
    target_compile_definitions(simplex_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
    target_compile_options(simplex_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra)
    target_link_libraries(simplex_allocation_probe PRIVATE eclipse)
    add_executable(matrix_qr_probe tests/matrix_qr_probe.c)
    target_link_libraries(matrix_qr_probe PRIVATE eclipse)
    target_compile_options(matrix_qr_probe PRIVATE -UNDEBUG -Wall -Wextra)
    add_library(matrix_qr_allocation_units OBJECT src/math/matrix.c)
    target_include_directories(matrix_qr_allocation_units PRIVATE src/include qfits5/include
      "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(matrix_qr_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
    add_executable(matrix_qr_allocation_probe tests/matrix_qr_allocation_probe.c
      $<TARGET_OBJECTS:matrix_qr_allocation_units>)
    target_compile_definitions(matrix_qr_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
    target_compile_options(matrix_qr_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra)
    target_link_libraries(matrix_qr_allocation_probe PRIVATE eclipse)
    add_executable(gain_pair_probe tests/gain_pair_probe.c)
    target_link_libraries(gain_pair_probe PRIVATE mefpp_bias_files)
    target_compile_options(gain_pair_probe PRIVATE -UNDEBUG -Wall -Wextra)
    # Reuse accepted test-only NULL-return seams and qfits owner accounting.
    add_library(gain_pair_allocation_units OBJECT src/iproc/detector.c
      src/iproc/image_stats.c src/iproc/image_handling.c src/iproc/pixelmaps.c
      src/math/dstats.c)
    target_include_directories(gain_pair_allocation_units PRIVATE src/include
      qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(gain_pair_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
    add_executable(gain_pair_allocation_probe tests/gain_pair_allocation_probe.c
      $<TARGET_OBJECTS:gain_pair_allocation_units>)
    target_compile_definitions(gain_pair_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
      XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
    target_compile_options(gain_pair_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra)
    target_link_libraries(gain_pair_allocation_probe PRIVATE mefpp_bias_files)
  endif()
  add_executable(bpm_response_probe tests/bpm_response_probe.c)
  target_link_libraries(bpm_response_probe PRIVATE eclipse)
  target_compile_options(bpm_response_probe PRIVATE -UNDEBUG -Wall -Wextra)
  target_link_libraries(measurement_stats_probe PRIVATE eclipse)
  target_compile_options(measurement_stats_probe PRIVATE -UNDEBUG -Wall -Wextra)
  add_executable(bias_service_probe tests/bias_service_probe.c tests/bias_legacy_reference.c)
  # Redirect only the test copy of the kernel to observe stack release order.
  add_library(bias_memory_kernel OBJECT ins/mef/common/mef_bias_kernel.c)
  target_include_directories(bias_memory_kernel PRIVATE ins/mef/common src/include
    qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(bias_memory_kernel PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
    cube_del=mef_memory_cube_del image_getmedian_checked=mef_memory_master_stats)
  add_executable(bias_memory_probe tests/bias_memory_probe.c
    $<TARGET_OBJECTS:bias_memory_kernel>)
  target_link_libraries(bias_memory_probe PRIVATE mefpp_config_snapshot)
  target_compile_definitions(bias_memory_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_compile_options(bias_memory_probe PRIVATE -UNDEBUG -Wall -Wextra -pedantic-errors)
  set_target_properties(bias_memory_kernel bias_memory_probe PROPERTIES
    C_STANDARD 17 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_link_libraries(bias_service_probe PRIVATE mefpp_config_snapshot)
  target_compile_definitions(bias_service_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  add_executable(large_file_io_probe tests/large_file_io_probe.c)
  target_link_libraries(large_file_io_probe PRIVATE mefpp_config_snapshot)
  target_compile_definitions(large_file_io_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  add_executable(layout_probe tests/layout_probe.c)
  target_link_libraries(layout_probe PRIVATE mefpp_config_snapshot)
  target_compile_definitions(layout_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})
  target_compile_options(layout_probe PRIVATE -UNDEBUG)
  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(bias_service_probe PRIVATE -UNDEBUG -Wall -Wextra)
  endif()
  # NULL-return seams exist only in these test copies of the actual dependency
  # units. Normal Eclipse/qfits targets and allocator policy remain unchanged.
  add_library(eclipse_allocation_units OBJECT
    src/iproc/image_handling.c src/iproc/cube_handling.c src/iproc/cube2image.c
    src/iproc/extraction.c src/iproc/pixel_handling.c src/iproc/image_stats.c
    src/math/function_1d.c ins/mef/common/mefp_lib.c ins/mef/common/mef_bias_kernel.c)
  target_include_directories(eclipse_allocation_units PRIVATE src/include
    ins/mef/common qfits5/include "${CMAKE_CURRENT_BINARY_DIR}/generated")
  target_compile_definitions(eclipse_allocation_units PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
    xmemory_malloc=mef_test_dependency_malloc xmemory_calloc=mef_test_dependency_calloc)
  add_executable(eclipse_allocation_probe tests/eclipse_allocation_probe.c
    tests/bias_legacy_reference.c $<TARGET_OBJECTS:eclipse_allocation_units>)
  target_compile_definitions(eclipse_allocation_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
    XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
  target_compile_options(eclipse_allocation_probe PRIVATE -UNDEBUG -Wall -Wextra)
  target_link_libraries(eclipse_allocation_probe PRIVATE mefpp_config_snapshot)
  add_executable(format_safety_probe tests/format_safety_probe.c)
  target_compile_definitions(format_safety_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
    XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
  target_compile_options(format_safety_probe PRIVATE -UNDEBUG -Wall -Wextra
    -Werror=implicit-function-declaration)
  target_link_libraries(format_safety_probe PRIVATE mefpp_common)
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
  if(TARGET recipe_file_hash_probe)
    add_test(NAME native_recipe_file_identity
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/recipe_file_hash_contract.py"
        --probe "$<TARGET_FILE:recipe_file_hash_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_recipe_file_identity PROPERTIES TIMEOUT 60 LABELS "native;recipe;ownership")
  endif()

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
  # Test-local syscall seams compile the actual allocator, without adding a
  # production fault API or changing its default memory mode/table size.
  add_executable(qfits_swap_probe tests/qfits_swap_probe.c)
  target_compile_definitions(qfits_swap_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS}
    XMEMORY_MODE=2 XMEMORY_MAXPTRS=2000000)
  target_compile_options(qfits_swap_probe PRIVATE -Wall -Wextra)
  add_test(NAME native_qfits_swap
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/qfits_swap_contract.py"
      --probe "$<TARGET_FILE:qfits_swap_probe>"
      --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
  set_tests_properties(native_qfits_swap PROPERTIES TIMEOUT 120 LABELS "native;swap;ownership;failure")
  if(MEFPP_BUILD_CONFIG_PROBES)
    if(MEFPP_BUILD_BIAS_ADAPTER)
      add_test(NAME native_operation_template COMMAND operation_template_probe)
      add_test(NAME native_bpm_service
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/bpm_service_contract.py"
          --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
          --probe "$<TARGET_FILE:bpm_service_probe>"
          --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
      set_tests_properties(native_bpm_service PROPERTIES TIMEOUT 180 LABELS "native;bpm;ownership;mask")
      add_test(NAME native_linearity_files
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/linearity_files_contract.py"
          --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
          --probe "$<TARGET_FILE:linearity_files_probe>" --bpm-probe "$<TARGET_FILE:bpm_files_probe>"
          --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
      set_tests_properties(native_linearity_files PROPERTIES TIMEOUT 300 LABELS "native;linearity;layout;ownership;mask")
      add_test(NAME native_bpm_product_qc
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/bpm_native_qc_contract.py"
          --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
          --probe "$<TARGET_FILE:bpm_native_qc_probe>"
          --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
      set_tests_properties(native_bpm_product_qc PROPERTIES TIMEOUT 180 LABELS "native;bpm;qc;publication")
      add_test(NAME native_bpm_files
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/bpm_files_contract.py"
          --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
          --probe "$<TARGET_FILE:bpm_files_probe>"
          --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
      set_tests_properties(native_bpm_files PROPERTIES TIMEOUT 300 LABELS "native;bpm;layout;coverage;mask")
      add_test(NAME native_bias_files
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/bias_files_contract.py"
          --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
          --adapter "$<TARGET_FILE:mefpp_m5>" --legacy "$<TARGET_FILE:mefpp>"
          --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
      set_tests_properties(native_bias_files PROPERTIES TIMEOUT 600 LABELS "native;bias;template;publication")
    endif()
    add_test(NAME pair_runner_orchestration
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/pair_runner_contract.py"
        --command "$<TARGET_FILE:mefpp_pair_measure>"
        --runner "${CMAKE_CURRENT_SOURCE_DIR}/../tools/run-pair-measurements.py"
        --paf "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(pair_runner_orchestration PROPERTIES TIMEOUT 180 LABELS "linearity;command;provenance;configuration")
    add_test(NAME native_linearity_preparation_command
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/linearity_preparation_command_contract.py"
        --command "$<TARGET_FILE:mefpp_linearity_prepare_command>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_linearity_preparation_command PROPERTIES TIMEOUT 180 LABELS "native;linearity;command;overscan")
    add_test(NAME native_linearity_preparation_archive_metadata
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/linearity_native_archive_contract.py"
        --command "$<TARGET_FILE:linearity_archive_metadata_probe>" --metadata-only
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_linearity_preparation_archive_metadata PROPERTIES TIMEOUT 180 LABELS "native;linearity;qc;publication")
    add_test(NAME native_sample_command
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/sample_command_contract.py"
        --command "$<TARGET_FILE:mefpp_sample_extract>"
        --paf "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_sample_command PROPERTIES TIMEOUT 180 LABELS "native;linearity;command;configuration")
    add_test(NAME native_pair_command
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/pair_command_contract.py"
        --command "$<TARGET_FILE:mefpp_pair_measure>"
        --paf "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_pair_command PROPERTIES TIMEOUT 180 LABELS "native;linearity;command;configuration")
    add_test(NAME native_linearity_raw_files
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/linearity_raw_files_contract.py"
        --probe "$<TARGET_FILE:linearity_raw_files_probe>"
        --paf "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_linearity_raw_files PROPERTIES TIMEOUT 180 LABELS "native;linearity;layout;ownership;mask")
    add_test(NAME native_linearity_pairs_export
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/linearity_pairs_export_contract.py"
        --probe "$<TARGET_FILE:linearity_pairs_export_probe>"
        --paf "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_linearity_pairs_export PROPERTIES TIMEOUT 120 LABELS "native;linearity;export")
    add_test(NAME native_linearity_pairs COMMAND linearity_pairs_probe
      "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf")
    set_tests_properties(native_linearity_pairs PROPERTIES TIMEOUT 180 LABELS "native;linearity;gain;statistics;ownership")
    add_test(NAME native_linearity_samples COMMAND linearity_samples_probe
      "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf")
    set_tests_properties(native_linearity_samples PROPERTIES TIMEOUT 120 LABELS "native;linearity;mask;ownership")
    add_test(NAME native_roi_config
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/roi_config_contract.py"
        --probe "$<TARGET_FILE:roi_config_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_roi_config PROPERTIES TIMEOUT 120 LABELS "native;configuration;roi;ownership")
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
    add_test(NAME native_config_project_composition
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/project_composition_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --reader "$<TARGET_FILE:mef_config_read>"
        --cli-probe "$<TARGET_FILE:cli_capture_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_config_project_composition PROPERTIES TIMEOUT 300 LABELS "native;configuration;project;composition;provenance")
    add_test(NAME native_large_file_io
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/large_file_io_contract.py"
        --probe "$<TARGET_FILE:large_file_io_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work" --phase focused)
    set_tests_properties(native_large_file_io PROPERTIES TIMEOUT 300 LABELS "native;io;large-file;bounds")
    add_test(NAME native_qfits_discovery
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/qfits_discovery_contract.py"
        --probe "$<TARGET_FILE:qfits_discovery_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_qfits_discovery PROPERTIES TIMEOUT 120 LABELS "native;qfits;layout;bounds")
    add_test(NAME native_layout
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/layout_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --probe "$<TARGET_FILE:layout_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_layout PROPERTIES TIMEOUT 180 LABELS "native;layout;detector;ownership")
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
    # These tests are opt-in; normal native builds need no ASDF installation.
    set(MEFPP_QC_PYTHON "" CACHE FILEPATH "Qualified ASDF QC interpreter (enables handoff tests)")
    if(MEFPP_QC_PYTHON)
      if(MEFPP_BUILD_BIAS_ADAPTER)
        add_test(NAME native_bpm_completion
          COMMAND "${Python3_EXECUTABLE}" -B "${CMAKE_CURRENT_SOURCE_DIR}/tests/bpm_completion_contract.py"
            --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
            --adapter "$<TARGET_FILE:mefpp_m5>"
            --asdf-python "${MEFPP_QC_PYTHON}"
            --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
        set_tests_properties(native_bpm_completion PROPERTIES TIMEOUT 600 LABELS "native;bpm;asdf;completion;cli")
        add_test(NAME native_bpm_publication
          COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/bpm_publication_contract.py"
            --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
            --probe "$<TARGET_FILE:bpm_publication_probe>"
            --asdf-python "${MEFPP_QC_PYTHON}"
            --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
        set_tests_properties(native_bpm_publication PROPERTIES TIMEOUT 300 LABELS "native;bpm;asdf;publication;mask")
      endif()
      if(MEFPP_BUILD_BIAS_ADAPTER)
        add_test(NAME native_bias_qc_asdf
          COMMAND "${Python3_EXECUTABLE}" -B "${CMAKE_CURRENT_SOURCE_DIR}/tests/bias_qc_asdf_contract.py"
            --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.." --adapter "$<TARGET_FILE:mefpp_m5>"
            --asdf-python "${MEFPP_QC_PYTHON}"
            --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
        set_tests_properties(native_bias_qc_asdf PROPERTIES TIMEOUT 300 LABELS "native;bias;asdf;mask")
      endif()
      add_test(NAME shared_qc_asdf
        COMMAND "${MEFPP_QC_PYTHON}" -B "${CMAKE_CURRENT_SOURCE_DIR}/../Pycavi2/tests/test_shared_qc.py"
          --work "${CMAKE_CURRENT_BINARY_DIR}/test-work")
      set_tests_properties(shared_qc_asdf PROPERTIES TIMEOUT 120 LABELS "asdf;qc")
    endif()
    add_test(NAME native_measurement_stats COMMAND measurement_stats_probe)
    if(MEFPP_BUILD_BIAS_ADAPTER)
      add_test(NAME native_linearity_fit COMMAND linearity_fit_probe)
      add_test(NAME native_linearity_fit_allocation COMMAND linearity_fit_allocation_probe)
      set_tests_properties(native_linearity_fit native_linearity_fit_allocation PROPERTIES
        TIMEOUT 180 LABELS "native;detector;linearity;composition;ownership")
      add_test(NAME native_detector_noise COMMAND detector_noise_probe)
      add_test(NAME native_detector_noise_allocation COMMAND detector_noise_allocation_probe)
      set_tests_properties(native_detector_noise native_detector_noise_allocation
        PROPERTIES TIMEOUT 180 LABELS "native;detector;covariance;ownership")
      add_test(NAME native_roi_aggregation COMMAND roi_aggregation_probe)
      set_tests_properties(native_roi_aggregation PROPERTIES TIMEOUT 60 LABELS "native;detector;roi;covariance")
      add_test(NAME native_roi_aggregation_allocation COMMAND roi_aggregation_allocation_probe)
      set_tests_properties(native_roi_aggregation_allocation PROPERTIES TIMEOUT 180 LABELS "native;detector;roi;allocation;ownership")
      add_test(NAME native_shutter_profile COMMAND shutter_profile_probe)
      set_tests_properties(native_shutter_profile PROPERTIES TIMEOUT 180 LABELS "native;detector;linearity;profile")
      add_test(NAME native_shutter_profile_allocation COMMAND shutter_profile_allocation_probe)
      set_tests_properties(native_shutter_profile_allocation PROPERTIES TIMEOUT 600 LABELS "native;detector;profile;allocation;ownership")
      add_test(NAME native_detector_joint COMMAND detector_joint_probe)
      set_tests_properties(native_detector_joint PROPERTIES TIMEOUT 180 LABELS "native;detector;linearity")
      add_test(NAME native_detector_joint_allocation COMMAND detector_joint_allocation_probe)
      set_tests_properties(native_detector_joint_allocation PROPERTIES TIMEOUT 300 LABELS "native;detector;allocation;ownership")
      add_test(NAME native_simplex COMMAND simplex_probe)
      set_tests_properties(native_simplex PROPERTIES TIMEOUT 30 LABELS "native;optimization;statistics")
      add_test(NAME native_simplex_allocation COMMAND simplex_allocation_probe)
      set_tests_properties(native_simplex_allocation PROPERTIES TIMEOUT 120 LABELS "native;optimization;allocation;ownership")
      add_test(NAME native_matrix_qr COMMAND matrix_qr_probe)
      set_tests_properties(native_matrix_qr PROPERTIES TIMEOUT 30 LABELS "native;matrix;statistics")
      add_test(NAME native_matrix_qr_allocation COMMAND matrix_qr_allocation_probe)
      set_tests_properties(native_matrix_qr_allocation PROPERTIES TIMEOUT 120 LABELS "native;matrix;allocation;ownership")
      add_test(NAME native_gain_pair COMMAND gain_pair_probe)
      set_tests_properties(native_gain_pair PROPERTIES TIMEOUT 30 LABELS "native;gain;statistics;mask")
      add_test(NAME native_gain_pair_allocation COMMAND gain_pair_allocation_probe)
      set_tests_properties(native_gain_pair_allocation PROPERTIES TIMEOUT 120 LABELS "native;gain;allocation;ownership")
    endif()
    add_test(NAME native_bpm_response
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/bpm_response_contract.py"
        --probe "$<TARGET_FILE:bpm_response_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_bpm_response PROPERTIES TIMEOUT 180 LABELS "native;bpm;statistics;mask")
    set_tests_properties(native_measurement_stats PROPERTIES TIMEOUT 30 LABELS "native;statistics;bias")
    add_test(NAME native_bias_service
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/bias_service_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --probe "$<TARGET_FILE:bias_service_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_bias_service PROPERTIES TIMEOUT 300 LABELS "native;bias;ownership")
    foreach(profile IN ITEMS legacy full)
      add_test(NAME native_bias_stack_lifetime_${profile}
        COMMAND bias_memory_probe "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf"
          ${profile} small - 1)
      set_tests_properties(native_bias_stack_lifetime_${profile} PROPERTIES
        TIMEOUT 30 LABELS "native;bias;ownership;memory")
      add_test(NAME native_bias_raw_lifetime_${profile}
        COMMAND bias_memory_probe "${CMAKE_CURRENT_SOURCE_DIR}/ins/mef/config/wfi.paf"
          ${profile} small - 1 owned)
      set_tests_properties(native_bias_raw_lifetime_${profile} PROPERTIES
        TIMEOUT 30 LABELS "native;bias;ownership;memory")
    endforeach()
    add_test(NAME native_eclipse_allocation
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/eclipse_allocation_contract.py"
        --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
        --probe "$<TARGET_FILE:eclipse_allocation_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_eclipse_allocation PROPERTIES TIMEOUT 300 LABELS "native;bias;allocation;ownership;failure")
    add_test(NAME native_format_safety
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/format_safety_contract.py"
        --probe "$<TARGET_FILE:format_safety_probe>"
        --work-parent "${CMAKE_CURRENT_BINARY_DIR}/test-work")
    set_tests_properties(native_format_safety PROPERTIES TIMEOUT 90 LABELS "native;format;bounds;failure")
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
  set(MEFPP_PATH_TEST_WORK_PARENT "${CMAKE_CURRENT_BINARY_DIR}/test-work" CACHE PATH
    "Existing parent for private native path fixtures (may use a local filesystem)")
  add_test(NAME native_explicit_paths
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/native_paths_contract.py"
      --executable "$<TARGET_FILE:mefpp>"
      --source-root "${CMAKE_CURRENT_SOURCE_DIR}/.."
      --work-parent "${MEFPP_PATH_TEST_WORK_PARENT}")
  set_tests_properties(native_explicit_paths PROPERTIES TIMEOUT 300 LABELS "native;paths;integration;provenance")
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
