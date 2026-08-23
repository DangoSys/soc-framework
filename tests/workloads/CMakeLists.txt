set(WORKLOAD_LIB_DIR ${CMAKE_CURRENT_SOURCE_DIR}/lib)

if(NOT DEFINED ELF_CC)
  set(ELF_CC "riscv64-unknown-elf-gcc")
endif()

set(SOC_CTEST_C_FLAGS
  -g -fno-common -O2 -static -march=rv64gc -mabi=lp64d -mcmodel=medany
  -fno-builtin-printf -std=gnu99
  -specs=htif_nano.specs
)

function(add_soc_ctest SOURCE_FILE)
  get_filename_component(_stem ${SOURCE_FILE} NAME_WE)
  set(TEST_NAME ${_stem})
  set(EXECUTABLE ${TEST_NAME}-baremetal)
  set(SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR})

  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${EXECUTABLE}
    COMMAND ${ELF_CC} ${SOC_CTEST_C_FLAGS}
      -o ${EXECUTABLE}
      ${SOURCE_DIR}/${SOURCE_FILE}
      -I${WORKLOAD_LIB_DIR}
      -I${SOURCE_DIR}
    DEPENDS
      ${SOURCE_DIR}/${SOURCE_FILE}
      ${WORKLOAD_LIB_DIR}/mmio.h
    COMMENT "Building SoC baremetal test: ${EXECUTABLE}"
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    VERBATIM)

  add_custom_target(${TEST_NAME}-baremetal-build
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${EXECUTABLE})

  if(DEFINED SOC_CTEST_GROUP_TARGET)
    add_dependencies(${SOC_CTEST_GROUP_TARGET} ${TEST_NAME}-baremetal-build)
  endif()
endfunction()

function(add_soc_ctests)
  foreach(SOURCE_FILE ${ARGV})
    add_soc_ctest(${SOURCE_FILE})
  endforeach()
endfunction()

add_subdirectory(src/CTest)
