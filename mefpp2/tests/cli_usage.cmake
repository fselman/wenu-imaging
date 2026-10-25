# CLI usage: no arguments must return nonzero and display usage without a PAF.
execute_process(COMMAND "${EXECUTABLE}" RESULT_VARIABLE status OUTPUT_VARIABLE output ERROR_VARIABLE error)
if("${status}" STREQUAL "0" OR NOT "${output}${error}" MATCHES "options")
  message(FATAL_ERROR "Unexpected no-argument status/output: ${status}: ${output}${error}")
endif()
