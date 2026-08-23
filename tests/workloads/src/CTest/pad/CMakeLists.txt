add_custom_target(pad-ctests-build)
set(SOC_CTEST_GROUP_TARGET pad-ctests-build)

add_soc_ctests(
  i2c_eeprom_test.c
  spi_flash_test.c
)
